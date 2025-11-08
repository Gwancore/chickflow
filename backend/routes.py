from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, Customer, Inventory, Allocation, Delivery, Waitlist
from allocation_engine import AllocationEngine
from notifications import NotificationService
import traceback

api = Blueprint('api', __name__)
allocation_engine = AllocationEngine()
notification_service = NotificationService()

# ============= Customer Routes =============

@api.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():
    """Get all customers with optional filtering"""
    tier = request.args.get('tier')
    zone = request.args.get('zone')
    is_active = request.args.get('is_active', 'true').lower() == 'true'
    
    query = Customer.query.filter_by(is_active=is_active)
    
    if tier:
        query = query.filter_by(tier=tier)
    if zone:
        query = query.filter_by(zone=zone)
    
    customers = query.all()
    return jsonify([c.to_dict() for c in customers]), 200


@api.route('/customers', methods=['POST'])
@jwt_required()
def create_customer():
    """Create a new customer"""
    try:
        data = request.get_json()
        
        customer = Customer(
            customer_id=data['customer_id'],
            farm_name=data['farm_name'],
            phone=data['phone'],
            email=data.get('email'),
            zone=data.get('zone'),
            tier=data['tier'],
            address=data.get('address'),
            coordinates=data.get('coordinates')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify(customer.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@api.route('/customers/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    """Get customer details"""
    customer = Customer.query.get_or_404(customer_id)
    
    # Include order history
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.order_date.desc()).limit(10).all()
    
    result = customer.to_dict()
    result['recent_orders'] = [o.to_dict() for o in orders]
    
    return jsonify(result), 200


@api.route('/customers/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """Update customer details"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        for key in ['farm_name', 'phone', 'email', 'zone', 'tier', 'address', 'coordinates', 'is_active']:
            if key in data:
                setattr(customer, key, data[key])
        
        db.session.commit()
        return jsonify(customer.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# ============= Order Routes =============

@api.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """Get all orders with filtering"""
    status = request.args.get('status')
    customer_id = request.args.get('customer_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Order.query
    
    if status:
        query = query.filter_by(status=status)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if date_from:
        query = query.filter(Order.requested_delivery_date >= datetime.fromisoformat(date_from).date())
    if date_to:
        query = query.filter(Order.requested_delivery_date <= datetime.fromisoformat(date_to).date())
    
    orders = query.order_by(Order.order_date.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200


@api.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new order"""
    try:
        data = request.get_json()
        
        # Generate order number
        order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        order = Order(
            order_number=order_number,
            customer_id=data['customer_id'],
            order_qty=data['order_qty'],
            requested_delivery_date=datetime.fromisoformat(data['requested_delivery_date']).date(),
            status='pending',
            notes=data.get('notes'),
            priority_level=data.get('priority_level', 0)
        )
        
        db.session.add(order)
        db.session.commit()
        
        # Send confirmation notification
        customer = Customer.query.get(data['customer_id'])
        notification_service.send_order_confirmation(customer, order)
        
        return jsonify(order.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@api.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get order details"""
    order = Order.query.get_or_404(order_id)
    
    result = order.to_dict()
    
    # Include allocation if exists
    allocation = Allocation.query.filter_by(order_id=order_id).first()
    if allocation:
        result['allocation'] = allocation.to_dict()
    
    # Include delivery if exists
    delivery = Delivery.query.filter_by(order_id=order_id).first()
    if delivery:
        result['delivery'] = delivery.to_dict()
    
    return jsonify(result), 200


@api.route('/orders/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    """Update order"""
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        for key in ['order_qty', 'requested_delivery_date', 'status', 'notes', 'priority_level']:
            if key in data:
                if key == 'requested_delivery_date':
                    setattr(order, key, datetime.fromisoformat(data[key]).date())
                else:
                    setattr(order, key, data[key])
        
        db.session.commit()
        return jsonify(order.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@api.route('/orders/<int:order_id>', methods=['DELETE'])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order"""
    try:
        order = Order.query.get_or_404(order_id)
        order.status = 'cancelled'
        
        # Cancel related allocations
        allocations = Allocation.query.filter_by(order_id=order_id).all()
        for alloc in allocations:
            alloc.status = 'cancelled'
        
        db.session.commit()
        return jsonify({'message': 'Order cancelled'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# ============= Inventory Routes =============

@api.route('/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    """Get inventory records"""
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Inventory.query
    
    if date_from:
        query = query.filter(Inventory.date >= datetime.fromisoformat(date_from).date())
    if date_to:
        query = query.filter(Inventory.date <= datetime.fromisoformat(date_to).date())
    
    inventory = query.order_by(Inventory.date.desc()).all()
    return jsonify([i.to_dict() for i in inventory]), 200


@api.route('/inventory', methods=['POST'])
@jwt_required()
def create_inventory():
    """Create inventory record for a date"""
    try:
        data = request.get_json()
        
        inventory_date = datetime.fromisoformat(data['date']).date()
        
        # Check if already exists
        existing = Inventory.query.filter_by(date=inventory_date).first()
        if existing:
            return jsonify({'error': 'Inventory for this date already exists'}), 400
        
        inventory = Inventory(
            date=inventory_date,
            expected_supply=data['expected_supply'],
            actual_supply=data.get('actual_supply'),
            status=data.get('status', 'pending'),
            notes=data.get('notes')
        )
        
        db.session.add(inventory)
        db.session.commit()
        
        return jsonify(inventory.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@api.route('/inventory/<int:inventory_id>', methods=['PUT'])
@jwt_required()
def update_inventory(inventory_id):
    """Update inventory record"""
    try:
        inventory = Inventory.query.get_or_404(inventory_id)
        data = request.get_json()
        
        for key in ['expected_supply', 'actual_supply', 'status', 'notes']:
            if key in data:
                setattr(inventory, key, data[key])
        
        db.session.commit()
        return jsonify(inventory.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# ============= Allocation Routes =============

@api.route('/allocations/run', methods=['POST'])
@jwt_required()
def run_allocation():
    """Run allocation for a specific date"""
    try:
        data = request.get_json()
        allocation_date = datetime.fromisoformat(data['date']).date()
        
        result = allocation_engine.allocate_for_date(allocation_date)
        
        # Send notifications
        for alloc in result['allocated']:
            customer = Customer.query.get(alloc['customer_id'])
            notification_service.send_allocation_notification(customer, alloc)
        
        for waitlist in result['waitlisted']:
            customer = Customer.query.get(waitlist['customer_id'])
            notification_service.send_waitlist_notification(customer, waitlist)
        
        return jsonify(result), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


@api.route('/allocations', methods=['GET'])
@jwt_required()
def get_allocations():
    """Get allocation records"""
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    customer_id = request.args.get('customer_id', type=int)
    status = request.args.get('status')
    
    query = Allocation.query
    
    if date_from:
        query = query.filter(Allocation.allocation_date >= datetime.fromisoformat(date_from).date())
    if date_to:
        query = query.filter(Allocation.allocation_date <= datetime.fromisoformat(date_to).date())
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if status:
        query = query.filter_by(status=status)
    
    allocations = query.order_by(Allocation.allocation_date.desc()).all()
    return jsonify([a.to_dict() for a in allocations]), 200


@api.route('/allocations/<int:allocation_id>/confirm-pickup', methods=['POST'])
@jwt_required()
def confirm_pickup(allocation_id):
    """Confirm chicks picked up"""
    try:
        allocation = Allocation.query.get_or_404(allocation_id)
        allocation.status = 'picked_up'
        allocation.pickup_time = datetime.utcnow()
        
        # Update order
        order = allocation.order
        order.status = 'delivered'
        order.actual_delivery_date = date.today()
        
        db.session.commit()
        return jsonify(allocation.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# ============= Waitlist Routes =============

@api.route('/waitlist', methods=['GET'])
@jwt_required()
def get_waitlist():
    """Get waitlist entries"""
    status = request.args.get('status', 'waiting')
    
    waitlist = Waitlist.query.filter_by(status=status).order_by(
        Waitlist.priority_score.desc(),
        Waitlist.added_date.asc()
    ).all()
    
    return jsonify([w.to_dict() for w in waitlist]), 200


@api.route('/waitlist/process', methods=['POST'])
@jwt_required()
def process_waitlist():
    """Process waitlist fulfillment"""
    try:
        data = request.get_json()
        allocation_date = datetime.fromisoformat(data['date']).date()
        
        result = allocation_engine.process_waitlist_fulfillment(allocation_date)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ============= Delivery Routes =============

@api.route('/deliveries', methods=['GET'])
@jwt_required()
def get_deliveries():
    """Get delivery records"""
    status = request.args.get('status')
    
    query = Delivery.query
    if status:
        query = query.filter_by(delivery_status=status)
    
    deliveries = query.order_by(Delivery.created_at.desc()).all()
    return jsonify([d.to_dict() for d in deliveries]), 200


@api.route('/deliveries', methods=['POST'])
@jwt_required()
def create_delivery():
    """Create delivery record"""
    try:
        data = request.get_json()
        
        delivery = Delivery(
            order_id=data['order_id'],
            driver_name=data.get('driver_name'),
            driver_phone=data.get('driver_phone'),
            vehicle_number=data.get('vehicle_number'),
            estimated_arrival=datetime.fromisoformat(data['estimated_arrival']) if data.get('estimated_arrival') else None,
            delivery_status='pending'
        )
        
        db.session.add(delivery)
        db.session.commit()
        
        return jsonify(delivery.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@api.route('/deliveries/<int:delivery_id>', methods=['PUT'])
@jwt_required()
def update_delivery(delivery_id):
    """Update delivery status"""
    try:
        delivery = Delivery.query.get_or_404(delivery_id)
        data = request.get_json()
        
        for key in ['driver_name', 'driver_phone', 'vehicle_number', 'dispatch_time', 
                    'estimated_arrival', 'actual_arrival', 'delivery_status', 'received_by', 'notes']:
            if key in data:
                if key in ['dispatch_time', 'estimated_arrival', 'actual_arrival']:
                    setattr(delivery, key, datetime.fromisoformat(data[key]) if data[key] else None)
                else:
                    setattr(delivery, key, data[key])
        
        db.session.commit()
        return jsonify(delivery.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# ============= Dashboard/Stats Routes =============

@api.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics"""
    today = date.today()
    
    # Today's stats
    today_inventory = Inventory.query.filter_by(date=today).first()
    today_allocations = Allocation.query.filter_by(allocation_date=today).all()
    today_orders = Order.query.filter_by(requested_delivery_date=today).all()
    
    # Overall stats
    total_customers = Customer.query.filter_by(is_active=True).count()
    pending_orders = Order.query.filter_by(status='pending').count()
    waitlist_count = Waitlist.query.filter_by(status='waiting').count()
    
    stats = {
        'today': {
            'date': today.isoformat(),
            'expected_supply': today_inventory.expected_supply if today_inventory else 0,
            'actual_supply': today_inventory.actual_supply if today_inventory else 0,
            'allocated': today_inventory.allocated if today_inventory else 0,
            'remaining': today_inventory.remaining if today_inventory else 0,
            'total_orders': len(today_orders),
            'allocations': len(today_allocations)
        },
        'overall': {
            'total_customers': total_customers,
            'pending_orders': pending_orders,
            'waitlist_count': waitlist_count
        }
    }
    
    return jsonify(stats), 200
