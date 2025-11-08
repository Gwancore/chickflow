#!/usr/bin/env python3
"""
ChickFlow Data Migration Script
Migrates data from legacy CSV/text files to the new database system
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from app import create_app
from models import db, Customer, Order, Inventory, User

def migrate_customers(csv_file='customers.csv'):
    """Migrate customers from CSV to database"""
    print(f"\n📊 Migrating customers from {csv_file}...")
    
    if not Path(csv_file).exists():
        print(f"❌ File not found: {csv_file}")
        return 0
    
    count = 0
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if customer already exists
            existing = Customer.query.filter_by(customer_id=row['customer_id']).first()
            if existing:
                print(f"⚠️  Customer {row['customer_id']} already exists, skipping...")
                continue
            
            # Parse last fulfilled date
            last_fulfilled = None
            if row.get('last_fulfilled_date'):
                try:
                    last_fulfilled = datetime.strptime(row['last_fulfilled_date'], '%Y-%m-%d')
                except ValueError:
                    print(f"⚠️  Invalid date for {row['customer_id']}, skipping date...")
            
            # Create customer
            customer = Customer(
                customer_id=row['customer_id'],
                farm_name=row['farm_name'],
                phone=row['phone'],
                email=row.get('email', ''),
                zone=row.get('zone', ''),
                tier=row['tier'],
                last_fulfilled_date=last_fulfilled,
                is_active=True
            )
            
            db.session.add(customer)
            count += 1
            print(f"✅ Added customer: {row['farm_name']} ({row['customer_id']})")
    
    db.session.commit()
    print(f"\n✨ Successfully migrated {count} customers")
    return count

def migrate_supply(supply_file='supply.txt'):
    """Migrate today's supply to inventory"""
    print(f"\n📦 Migrating supply from {supply_file}...")
    
    if not Path(supply_file).exists():
        print(f"❌ File not found: {supply_file}")
        return 0
    
    with open(supply_file, 'r') as f:
        supply = int(f.read().strip())
    
    today = datetime.now().date()
    
    # Check if inventory already exists for today
    existing = Inventory.query.filter_by(date=today).first()
    if existing:
        print(f"⚠️  Inventory for {today} already exists")
        existing.expected_supply = supply
        existing.actual_supply = supply
        db.session.commit()
        print(f"✅ Updated today's inventory: {supply} chicks")
    else:
        inventory = Inventory(
            date=today,
            expected_supply=supply,
            actual_supply=supply,
            status='confirmed',
            notes='Migrated from legacy system'
        )
        db.session.add(inventory)
        db.session.commit()
        print(f"✅ Created today's inventory: {supply} chicks")
    
    return 1

def create_default_users():
    """Create default admin and test users"""
    print("\n👤 Creating default users...")
    
    users_to_create = [
        {
            'username': 'admin',
            'email': 'admin@chickflow.com',
            'password': 'admin123',
            'role': 'admin'
        },
        {
            'username': 'manager',
            'email': 'manager@chickflow.com',
            'password': 'manager123',
            'role': 'manager'
        }
    ]
    
    count = 0
    for user_data in users_to_create:
        existing = User.query.filter_by(username=user_data['username']).first()
        if existing:
            print(f"⚠️  User {user_data['username']} already exists, skipping...")
            continue
        
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            role=user_data['role'],
            is_active=True
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        count += 1
        print(f"✅ Created user: {user_data['username']} (password: {user_data['password']})")
    
    db.session.commit()
    print(f"\n✨ Created {count} default users")
    print("\n⚠️  IMPORTANT: Change these passwords immediately after first login!")
    return count

def link_customers_to_users():
    """Create user accounts for existing customers"""
    print("\n🔗 Linking customers to user accounts...")
    
    customers = Customer.query.filter(
        Customer.user_id.is_(None),
        Customer.is_active == True
    ).limit(5).all()  # Limit to first 5 for demo
    
    count = 0
    for customer in customers:
        # Create username from customer_id
        username = f"customer_{customer.customer_id.lower()}"
        
        # Check if user already exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            customer.user_id = existing.id
            continue
        
        # Create user account
        user = User(
            username=username,
            email=customer.email or f"{username}@chickflow.com",
            role='customer',
            is_active=True
        )
        user.set_password('customer123')  # Default password
        db.session.add(user)
        db.session.flush()  # Get user.id
        
        # Link to customer
        customer.user_id = user.id
        count += 1
        print(f"✅ Created account for {customer.farm_name}: {username}")
    
    db.session.commit()
    print(f"\n✨ Created {count} customer accounts")
    if count > 0:
        print("📧 Default password: customer123 (customers should change this)")
    return count

def generate_summary():
    """Generate migration summary"""
    print("\n" + "="*60)
    print("📊 MIGRATION SUMMARY")
    print("="*60)
    
    # Count records
    customer_count = Customer.query.count()
    user_count = User.query.count()
    inventory_count = Inventory.query.count()
    order_count = Order.query.count()
    
    print(f"\nDatabase Statistics:")
    print(f"  👥 Customers: {customer_count}")
    print(f"  👤 Users: {user_count}")
    print(f"  📦 Inventory records: {inventory_count}")
    print(f"  🛒 Orders: {order_count}")
    
    # Customer tier breakdown
    print(f"\nCustomer Tier Breakdown:")
    for tier in ['Contract', 'Loyal', 'New']:
        count = Customer.query.filter_by(tier=tier).count()
        print(f"  {tier}: {count}")
    
    # User role breakdown
    print(f"\nUser Role Breakdown:")
    for role in ['admin', 'manager', 'customer']:
        count = User.query.filter_by(role=role).count()
        print(f"  {role.title()}: {count}")
    
    print("\n" + "="*60)
    print("✅ Migration completed successfully!")
    print("="*60)
    
    print("\n📝 Next Steps:")
    print("  1. Review migrated data in the database")
    print("  2. Change default passwords (admin123, manager123, customer123)")
    print("  3. Start the backend: cd backend && python app.py")
    print("  4. Start the frontend: cd frontend && npm run dev")
    print("  5. Login with admin/admin123 and explore the system")
    print("\n")

def main():
    """Main migration function"""
    print("="*60)
    print("🚀 ChickFlow Data Migration")
    print("="*60)
    print("\nThis script will migrate your legacy data to the new system.")
    print("Make sure you have:")
    print("  1. Set up the database (run setup.sh first)")
    print("  2. Legacy files in the project root:")
    print("     - customers.csv")
    print("     - supply.txt")
    print("\n" + "="*60)
    
    response = input("\nProceed with migration? (yes/no): ").lower()
    if response not in ['yes', 'y']:
        print("Migration cancelled.")
        return
    
    # Create Flask app context
    app = create_app()
    with app.app_context():
        try:
            # Run migrations
            print("\n🔄 Starting migration...\n")
            
            # 1. Create default users
            create_default_users()
            
            # 2. Migrate customers
            migrate_customers()
            
            # 3. Migrate supply
            migrate_supply()
            
            # 4. Link customers to users
            link_customers_to_users()
            
            # 5. Generate summary
            generate_summary()
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
