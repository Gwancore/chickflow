from datetime import datetime, timedelta, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Order, Customer, Allocation, Inventory, Waitlist
from sqlalchemy import func, and_, extract
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
from io import BytesIO
import base64

reports = Blueprint('reports', __name__)

@reports.route('/reports/daily-summary', methods=['GET'])
@jwt_required()
def daily_summary():
    """Get daily allocation summary"""
    report_date = request.args.get('date', date.today().isoformat())
    report_date = datetime.fromisoformat(report_date).date()
    
    # Inventory
    inventory = Inventory.query.filter_by(date=report_date).first()
    
    # Allocations
    allocations = Allocation.query.filter_by(allocation_date=report_date).all()
    
    # Orders
    orders = Order.query.filter_by(requested_delivery_date=report_date).all()
    
    # Waitlist
    waitlist = Waitlist.query.filter(
        and_(
            Waitlist.added_date >= datetime.combine(report_date, datetime.min.time()),
            Waitlist.added_date < datetime.combine(report_date + timedelta(days=1), datetime.min.time())
        )
    ).all()
    
    # Calculate metrics
    total_allocated = sum(a.allocated_qty for a in allocations)
    allocation_count = len(allocations)
    waitlist_count = len([w for w in waitlist if w.status == 'waiting'])
    
    # By tier breakdown
    tier_breakdown = db.session.query(
        Customer.tier,
        func.count(Allocation.id).label('count'),
        func.sum(Allocation.allocated_qty).label('total_qty')
    ).join(Allocation).filter(
        Allocation.allocation_date == report_date
    ).group_by(Customer.tier).all()
    
    summary = {
        'date': report_date.isoformat(),
        'inventory': {
            'expected_supply': inventory.expected_supply if inventory else 0,
            'actual_supply': inventory.actual_supply if inventory else 0,
            'allocated': total_allocated,
            'remaining': inventory.remaining if inventory else 0
        },
        'allocations': {
            'total_count': allocation_count,
            'total_qty': total_allocated,
            'by_tier': [
                {
                    'tier': tier,
                    'count': count,
                    'total_qty': total_qty
                } for tier, count, total_qty in tier_breakdown
            ]
        },
        'orders': {
            'total': len(orders),
            'pending': len([o for o in orders if o.status == 'pending']),
            'allocated': len([o for o in orders if o.status == 'allocated']),
            'waitlisted': len([o for o in orders if o.status == 'waitlisted'])
        },
        'waitlist': {
            'total': len(waitlist),
            'waiting': waitlist_count,
            'fulfilled': len([w for w in waitlist if w.status == 'fulfilled'])
        }
    }
    
    return jsonify(summary), 200


@reports.route('/reports/weekly-summary', methods=['GET'])
@jwt_required()
def weekly_summary():
    """Get weekly summary"""
    end_date = request.args.get('end_date', date.today().isoformat())
    end_date = datetime.fromisoformat(end_date).date()
    start_date = end_date - timedelta(days=6)
    
    # Daily breakdown
    daily_data = []
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        
        inventory = Inventory.query.filter_by(date=current_date).first()
        allocations = Allocation.query.filter_by(allocation_date=current_date).all()
        
        daily_data.append({
            'date': current_date.isoformat(),
            'supply': inventory.actual_supply or inventory.expected_supply if inventory else 0,
            'allocated': sum(a.allocated_qty for a in allocations),
            'allocation_count': len(allocations)
        })
    
    # Weekly totals
    total_supply = sum(d['supply'] for d in daily_data)
    total_allocated = sum(d['allocated'] for d in daily_data)
    total_allocations = sum(d['allocation_count'] for d in daily_data)
    
    summary = {
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'totals': {
            'supply': total_supply,
            'allocated': total_allocated,
            'allocation_count': total_allocations,
            'remaining': total_supply - total_allocated
        },
        'daily_breakdown': daily_data
    }
    
    return jsonify(summary), 200


@reports.route('/reports/monthly-summary', methods=['GET'])
@jwt_required()
def monthly_summary():
    """Get monthly summary"""
    year = request.args.get('year', type=int, default=date.today().year)
    month = request.args.get('month', type=int, default=date.today().month)
    
    # Get all data for the month
    inventory_data = Inventory.query.filter(
        extract('year', Inventory.date) == year,
        extract('month', Inventory.date) == month
    ).all()
    
    allocations = db.session.query(
        Allocation.allocation_date,
        func.count(Allocation.id).label('count'),
        func.sum(Allocation.allocated_qty).label('total_qty')
    ).filter(
        extract('year', Allocation.allocation_date) == year,
        extract('month', Allocation.allocation_date) == month
    ).group_by(Allocation.allocation_date).all()
    
    # Calculate totals
    total_supply = sum(inv.actual_supply or inv.expected_supply for inv in inventory_data)
    total_allocated = sum(alloc.total_qty for alloc in allocations if alloc.total_qty)
    total_allocation_count = sum(alloc.count for alloc in allocations)
    
    # Customer tier breakdown
    tier_stats = db.session.query(
        Customer.tier,
        func.count(Allocation.id).label('allocation_count'),
        func.sum(Allocation.allocated_qty).label('total_qty')
    ).join(Allocation).filter(
        extract('year', Allocation.allocation_date) == year,
        extract('month', Allocation.allocation_date) == month
    ).group_by(Customer.tier).all()
    
    summary = {
        'period': {
            'year': year,
            'month': month
        },
        'totals': {
            'supply': total_supply,
            'allocated': total_allocated,
            'allocation_count': total_allocation_count,
            'remaining': total_supply - total_allocated,
            'working_days': len(inventory_data)
        },
        'tier_breakdown': [
            {
                'tier': tier,
                'allocation_count': count,
                'total_qty': total_qty
            } for tier, count, total_qty in tier_stats
        ],
        'daily_average': {
            'supply': total_supply / len(inventory_data) if inventory_data else 0,
            'allocated': total_allocated / len(inventory_data) if inventory_data else 0
        }
    }
    
    return jsonify(summary), 200


@reports.route('/reports/customer-analytics', methods=['GET'])
@jwt_required()
def customer_analytics():
    """Get customer analytics"""
    days = request.args.get('days', type=int, default=30)
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Top customers by volume
    top_customers = db.session.query(
        Customer.id,
        Customer.customer_id,
        Customer.farm_name,
        Customer.tier,
        func.count(Allocation.id).label('allocation_count'),
        func.sum(Allocation.allocated_qty).label('total_qty')
    ).join(Allocation).filter(
        Allocation.allocation_date >= start_date
    ).group_by(Customer.id).order_by(
        func.sum(Allocation.allocated_qty).desc()
    ).limit(20).all()
    
    # Customer tier distribution
    tier_distribution = db.session.query(
        Customer.tier,
        func.count(Customer.id).label('count')
    ).filter(Customer.is_active == True).group_by(Customer.tier).all()
    
    # Fulfillment rate by tier
    fulfillment_stats = db.session.query(
        Customer.tier,
        func.count(Order.id).label('total_orders'),
        func.sum(func.case((Order.status == 'allocated', 1), else_=0)).label('fulfilled_orders')
    ).join(Order).filter(
        Order.order_date >= datetime.combine(start_date, datetime.min.time())
    ).group_by(Customer.tier).all()
    
    analytics = {
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': days
        },
        'top_customers': [
            {
                'customer_id': cid,
                'farm_name': name,
                'tier': tier,
                'allocation_count': count,
                'total_qty': total_qty
            } for _, cid, name, tier, count, total_qty in top_customers
        ],
        'tier_distribution': [
            {'tier': tier, 'count': count}
            for tier, count in tier_distribution
        ],
        'fulfillment_by_tier': [
            {
                'tier': tier,
                'total_orders': total,
                'fulfilled_orders': fulfilled,
                'fulfillment_rate': (fulfilled / total * 100) if total > 0 else 0
            } for tier, total, fulfilled in fulfillment_stats
        ]
    }
    
    return jsonify(analytics), 200


@reports.route('/reports/waitlist-analysis', methods=['GET'])
@jwt_required()
def waitlist_analysis():
    """Analyze waitlist patterns"""
    days = request.args.get('days', type=int, default=30)
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Waitlist statistics
    total_waitlist = Waitlist.query.filter(
        Waitlist.added_date >= datetime.combine(start_date, datetime.min.time())
    ).count()
    
    fulfilled = Waitlist.query.filter(
        Waitlist.added_date >= datetime.combine(start_date, datetime.min.time()),
        Waitlist.status == 'fulfilled'
    ).count()
    
    waiting = Waitlist.query.filter(
        Waitlist.added_date >= datetime.combine(start_date, datetime.min.time()),
        Waitlist.status == 'waiting'
    ).count()
    
    # Average wait time
    fulfilled_entries = Waitlist.query.filter(
        Waitlist.added_date >= datetime.combine(start_date, datetime.min.time()),
        Waitlist.status == 'fulfilled',
        Waitlist.actual_fulfillment_date.isnot(None)
    ).all()
    
    wait_times = []
    for entry in fulfilled_entries:
        if entry.added_date and entry.actual_fulfillment_date:
            days_waited = (entry.actual_fulfillment_date - entry.added_date.date()).days
            wait_times.append(days_waited)
    
    avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0
    
    # By tier
    tier_waitlist = db.session.query(
        Customer.tier,
        func.count(Waitlist.id).label('total'),
        func.sum(func.case((Waitlist.status == 'fulfilled', 1), else_=0)).label('fulfilled')
    ).join(Customer).filter(
        Waitlist.added_date >= datetime.combine(start_date, datetime.min.time())
    ).group_by(Customer.tier).all()
    
    analysis = {
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': days
        },
        'overall': {
            'total_waitlist_entries': total_waitlist,
            'fulfilled': fulfilled,
            'still_waiting': waiting,
            'fulfillment_rate': (fulfilled / total_waitlist * 100) if total_waitlist > 0 else 0,
            'avg_wait_time_days': round(avg_wait_time, 1)
        },
        'by_tier': [
            {
                'tier': tier,
                'total': total,
                'fulfilled': fulfilled,
                'fulfillment_rate': (fulfilled / total * 100) if total > 0 else 0
            } for tier, total, fulfilled in tier_waitlist
        ]
    }
    
    return jsonify(analysis), 200


@reports.route('/reports/export/allocations', methods=['GET'])
@jwt_required()
def export_allocations():
    """Export allocations to Excel"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = db.session.query(
        Allocation.allocation_date,
        Allocation.allocated_qty,
        Allocation.status,
        Customer.customer_id,
        Customer.farm_name,
        Customer.phone,
        Customer.zone,
        Customer.tier,
        Order.order_number
    ).join(Customer).join(Order)
    
    if start_date:
        query = query.filter(Allocation.allocation_date >= datetime.fromisoformat(start_date).date())
    if end_date:
        query = query.filter(Allocation.allocation_date <= datetime.fromisoformat(end_date).date())
    
    data = query.all()
    
    if not PANDAS_AVAILABLE:
        return jsonify({
            'error': 'Excel export requires pandas and openpyxl libraries',
            'message': 'Install with: pip install pandas openpyxl'
        }), 501
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=[
        'Allocation Date', 'Quantity', 'Status', 'Customer ID', 
        'Farm Name', 'Phone', 'Zone', 'Tier', 'Order Number'
    ])
    
    # Convert to Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Allocations')
    
    output.seek(0)
    excel_data = base64.b64encode(output.read()).decode()
    
    return jsonify({
        'filename': f'allocations_{datetime.now().strftime("%Y%m%d")}.xlsx',
        'data': excel_data,
        'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }), 200
