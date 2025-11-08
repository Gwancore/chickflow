from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, manager, customer, driver
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Customer(db.Model):
    """Customer/Farm model"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    farm_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    zone = db.Column(db.String(50))
    tier = db.Column(db.String(20), nullable=False)  # Contract, Loyal, New
    address = db.Column(db.Text)
    coordinates = db.Column(db.String(100))  # latitude,longitude
    last_fulfilled_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    allocations = db.relationship('Allocation', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'farm_name': self.farm_name,
            'phone': self.phone,
            'email': self.email,
            'zone': self.zone,
            'tier': self.tier,
            'address': self.address,
            'coordinates': self.coordinates,
            'last_fulfilled_date': self.last_fulfilled_date.isoformat() if self.last_fulfilled_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Order(db.Model):
    """Order model with comprehensive date tracking"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    order_qty = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # pending, allocated, waitlisted, delivered, cancelled
    
    # Date tracking
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    requested_delivery_date = db.Column(db.Date, nullable=False)
    expected_delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)
    
    # Additional fields
    notes = db.Column(db.Text)
    priority_level = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    allocations = db.relationship('Allocation', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    deliveries = db.relationship('Delivery', backref='order', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'customer': self.customer.to_dict() if self.customer else None,
            'order_qty': self.order_qty,
            'status': self.status,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'requested_delivery_date': self.requested_delivery_date.isoformat() if self.requested_delivery_date else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'notes': self.notes,
            'priority_level': self.priority_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Inventory(db.Model):
    """Daily inventory/supply tracking"""
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    expected_supply = db.Column(db.Integer, nullable=False)
    actual_supply = db.Column(db.Integer)
    allocated = db.Column(db.Integer, default=0)
    remaining = db.Column(db.Integer)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, delivered
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'expected_supply': self.expected_supply,
            'actual_supply': self.actual_supply,
            'allocated': self.allocated,
            'remaining': self.remaining,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Allocation(db.Model):
    """Allocation tracking"""
    __tablename__ = 'allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    allocation_date = db.Column(db.Date, nullable=False)
    allocated_qty = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, picked_up, cancelled
    
    # Timing
    allocation_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    pickup_deadline = db.Column(db.DateTime)
    pickup_time = db.Column(db.DateTime)
    
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'customer': self.customer.to_dict() if self.customer else None,
            'allocation_date': self.allocation_date.isoformat() if self.allocation_date else None,
            'allocated_qty': self.allocated_qty,
            'status': self.status,
            'allocation_timestamp': self.allocation_timestamp.isoformat() if self.allocation_timestamp else None,
            'pickup_deadline': self.pickup_deadline.isoformat() if self.pickup_deadline else None,
            'pickup_time': self.pickup_time.isoformat() if self.pickup_time else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Delivery(db.Model):
    """Delivery tracking"""
    __tablename__ = 'deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, unique=True)
    driver_name = db.Column(db.String(100))
    driver_phone = db.Column(db.String(20))
    vehicle_number = db.Column(db.String(20))
    
    # Delivery tracking
    dispatch_time = db.Column(db.DateTime)
    estimated_arrival = db.Column(db.DateTime)
    actual_arrival = db.Column(db.DateTime)
    delivery_status = db.Column(db.String(20), default='pending')  # pending, in_transit, delivered, failed
    
    # Proof of delivery
    received_by = db.Column(db.String(100))
    signature = db.Column(db.Text)  # Base64 encoded signature
    delivery_photo = db.Column(db.Text)  # Base64 encoded photo or URL
    
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'driver_name': self.driver_name,
            'driver_phone': self.driver_phone,
            'vehicle_number': self.vehicle_number,
            'dispatch_time': self.dispatch_time.isoformat() if self.dispatch_time else None,
            'estimated_arrival': self.estimated_arrival.isoformat() if self.estimated_arrival else None,
            'actual_arrival': self.actual_arrival.isoformat() if self.actual_arrival else None,
            'delivery_status': self.delivery_status,
            'received_by': self.received_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Waitlist(db.Model):
    """Waitlist tracking"""
    __tablename__ = 'waitlist'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    requested_qty = db.Column(db.Integer, nullable=False)
    priority_score = db.Column(db.Float, default=0.0)
    
    # Date tracking
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    target_fulfillment_date = db.Column(db.Date)
    actual_fulfillment_date = db.Column(db.Date)
    
    status = db.Column(db.String(20), default='waiting')  # waiting, fulfilled, cancelled
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', backref='waitlist_entries')
    customer = db.relationship('Customer', backref='waitlist_entries')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'customer': self.customer.to_dict() if self.customer else None,
            'requested_qty': self.requested_qty,
            'priority_score': self.priority_score,
            'added_date': self.added_date.isoformat() if self.added_date else None,
            'target_fulfillment_date': self.target_fulfillment_date.isoformat() if self.target_fulfillment_date else None,
            'actual_fulfillment_date': self.actual_fulfillment_date.isoformat() if self.actual_fulfillment_date else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Notification(db.Model):
    """Notification log"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    recipient_type = db.Column(db.String(20), nullable=False)  # customer, driver, admin
    recipient_id = db.Column(db.Integer)
    recipient_contact = db.Column(db.String(100), nullable=False)
    
    notification_type = db.Column(db.String(20), nullable=False)  # sms, email, push
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed
    sent_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'recipient_type': self.recipient_type,
            'recipient_contact': self.recipient_contact,
            'notification_type': self.notification_type,
            'subject': self.subject,
            'message': self.message,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
