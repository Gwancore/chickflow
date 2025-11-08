from datetime import datetime, timedelta, date
from typing import List, Tuple, Dict
from models import db, Order, Customer, Inventory, Allocation, Waitlist
from config import Config

class AllocationEngine:
    """Enhanced allocation engine with comprehensive date and priority handling"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.max_per_customer = self.config.MAX_PER_CUSTOMER
        self.waiting_period_days = self.config.WAITING_PERIOD_DAYS
        self.pickup_deadline_hour = self.config.PICKUP_DEADLINE_HOUR
    
    def allocate_for_date(self, allocation_date: date) -> Dict:
        """Main allocation function for a specific date"""
        
        # Get inventory for the date
        inventory = Inventory.query.filter_by(date=allocation_date).first()
        if not inventory:
            raise ValueError(f"No inventory found for {allocation_date}")
        
        supply = inventory.actual_supply or inventory.expected_supply
        
        # Get pending orders for this date
        orders = Order.query.filter(
            Order.requested_delivery_date == allocation_date,
            Order.status == 'pending'
        ).all()
        
        if not orders:
            return {
                'allocated': [],
                'waitlisted': [],
                'remaining': supply,
                'total_orders': 0,
                'allocation_date': allocation_date.isoformat()
            }
        
        # Calculate priority scores for all orders
        scored_orders = self._calculate_priority_scores(orders)
        
        # Allocate by tier and priority
        allocated, waitlisted, remaining = self._allocate_by_tiers(
            scored_orders, supply, allocation_date
        )
        
        # Update inventory
        inventory.allocated = supply - remaining
        inventory.remaining = remaining
        
        # Update order statuses
        for order in allocated:
            order.status = 'allocated'
            order.expected_delivery_date = allocation_date
        
        for order in waitlisted:
            order.status = 'waitlisted'
            # Add to waitlist table
            waitlist_entry = Waitlist(
                order_id=order.id,
                customer_id=order.customer_id,
                requested_qty=order.order_qty,
                target_fulfillment_date=allocation_date + timedelta(days=1),
                priority_score=order.priority_score
            )
            db.session.add(waitlist_entry)
        
        db.session.commit()
        
        return {
            'allocated': [self._order_to_allocation_dict(o) for o in allocated],
            'waitlisted': [self._order_to_allocation_dict(o) for o in waitlisted],
            'remaining': remaining,
            'total_orders': len(orders),
            'allocation_date': allocation_date.isoformat()
        }
    
    def _calculate_priority_scores(self, orders: List[Order]) -> List[Order]:
        """Calculate priority scores for orders based on multiple factors"""
        for order in orders:
            customer = order.customer
            score = 0.0
            
            # Tier-based base score
            tier_scores = {'Contract': 100, 'Loyal': 50, 'New': 10}
            score += tier_scores.get(customer.tier, 0)
            
            # Time since last fulfillment (for Loyal customers)
            if customer.last_fulfilled_date:
                days_since = (datetime.utcnow().date() - customer.last_fulfilled_date.date()).days
                score += min(days_since * 2, 100)  # Cap at 100
            else:
                score += 30  # New customers get baseline
            
            # Waiting time for this specific order
            days_waiting = (datetime.utcnow().date() - order.order_date.date()).days
            score += days_waiting * 5
            
            # Priority level from order
            score += order.priority_level * 10
            
            # Check if on waitlist previously
            previous_waitlist = Waitlist.query.filter_by(
                customer_id=customer.id,
                status='waiting'
            ).count()
            score += previous_waitlist * 20
            
            order.priority_score = score
        
        return orders
    
    def _allocate_by_tiers(self, orders: List[Order], supply: int, 
                          allocation_date: date) -> Tuple[List[Order], List[Order], int]:
        """Allocate supply based on tiers and priority scores"""
        
        allocated = []
        waitlisted = []
        remaining = supply
        
        # Group by tier
        contract_orders = [o for o in orders if o.customer.tier == 'Contract']
        loyal_orders = [o for o in orders if o.customer.tier == 'Loyal']
        new_orders = [o for o in orders if o.customer.tier == 'New']
        
        # Sort each tier by priority score
        contract_orders.sort(key=lambda x: x.priority_score, reverse=True)
        loyal_orders.sort(key=lambda x: x.priority_score, reverse=True)
        new_orders.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Allocate Contract farms first (100% fulfillment priority)
        for order in contract_orders:
            qty = min(order.order_qty, self.max_per_customer)
            if remaining >= qty:
                order.allocated_qty = qty
                allocated.append(order)
                remaining -= qty
                
                # Create allocation record
                self._create_allocation(order, qty, allocation_date)
                
                # Update customer's last fulfilled date
                order.customer.last_fulfilled_date = datetime.utcnow()
            else:
                waitlisted.append(order)
        
        # Allocate Loyal customers
        for order in loyal_orders:
            qty = min(order.order_qty, self.max_per_customer)
            if remaining >= qty:
                order.allocated_qty = qty
                allocated.append(order)
                remaining -= qty
                
                self._create_allocation(order, qty, allocation_date)
                order.customer.last_fulfilled_date = datetime.utcnow()
            else:
                waitlisted.append(order)
        
        # Allocate New customers
        for order in new_orders:
            qty = min(order.order_qty, self.max_per_customer)
            if remaining >= qty:
                order.allocated_qty = qty
                allocated.append(order)
                remaining -= qty
                
                self._create_allocation(order, qty, allocation_date)
                order.customer.last_fulfilled_date = datetime.utcnow()
            else:
                waitlisted.append(order)
        
        return allocated, waitlisted, remaining
    
    def _create_allocation(self, order: Order, qty: int, allocation_date: date):
        """Create allocation record with pickup deadline"""
        pickup_deadline = datetime.combine(
            allocation_date, 
            datetime.min.time()
        ) + timedelta(hours=self.pickup_deadline_hour)
        
        allocation = Allocation(
            order_id=order.id,
            customer_id=order.customer_id,
            allocation_date=allocation_date,
            allocated_qty=qty,
            pickup_deadline=pickup_deadline,
            status='pending'
        )
        db.session.add(allocation)
    
    def _order_to_allocation_dict(self, order: Order) -> Dict:
        """Convert order to allocation dictionary"""
        return {
            'order_id': order.id,
            'order_number': order.order_number,
            'customer_id': order.customer_id,
            'customer_name': order.customer.farm_name,
            'phone': order.customer.phone,
            'zone': order.customer.zone,
            'tier': order.customer.tier,
            'requested_qty': order.order_qty,
            'allocated_qty': getattr(order, 'allocated_qty', 0),
            'priority_score': getattr(order, 'priority_score', 0)
        }
    
    def process_waitlist_fulfillment(self, allocation_date: date) -> Dict:
        """Process waitlist when new supply becomes available"""
        
        # Get waiting entries
        waiting = Waitlist.query.filter_by(status='waiting').order_by(
            Waitlist.priority_score.desc(),
            Waitlist.added_date.asc()
        ).all()
        
        if not waiting:
            return {'fulfilled': 0, 'remaining_waitlist': 0}
        
        # Get available supply
        inventory = Inventory.query.filter_by(date=allocation_date).first()
        if not inventory or not inventory.remaining:
            return {'fulfilled': 0, 'remaining_waitlist': len(waiting)}
        
        remaining = inventory.remaining
        fulfilled_count = 0
        
        for entry in waiting:
            order = entry.order
            qty = min(entry.requested_qty, self.max_per_customer)
            
            if remaining >= qty:
                # Create allocation
                self._create_allocation(order, qty, allocation_date)
                
                # Update order and waitlist entry
                order.status = 'allocated'
                order.expected_delivery_date = allocation_date
                entry.status = 'fulfilled'
                entry.actual_fulfillment_date = allocation_date
                
                # Update customer
                order.customer.last_fulfilled_date = datetime.utcnow()
                
                remaining -= qty
                fulfilled_count += 1
        
        # Update inventory
        inventory.remaining = remaining
        db.session.commit()
        
        return {
            'fulfilled': fulfilled_count,
            'remaining_waitlist': len([w for w in waiting if w.status == 'waiting'])
        }
