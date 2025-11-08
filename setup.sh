#!/bin/bash

# ChickFlow Database Setup and Migration Script

echo "=== ChickFlow Database Setup ==="
echo ""

# Database configuration
DB_NAME="chickflow"
DB_USER="chickflow"
DB_PASS="chickflow123"  # Change this!

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Creating PostgreSQL database and user...${NC}"
sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\q
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database created successfully${NC}"
else
    echo -e "${RED}✗ Failed to create database${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Setting up Python virtual environment...${NC}"
cd backend
python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN}✓ Virtual environment created${NC}"

echo ""
echo -e "${YELLOW}Step 3: Installing Python dependencies...${NC}"
pip install -r requirements.txt

echo ""
echo -e "${YELLOW}Step 4: Creating .env file...${NC}"
cat > .env <<EOF
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
JWT_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost/$DB_NAME
REDIS_URL=redis://localhost:6379/0

# Twilio (add your credentials)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# SendGrid (add your credentials)
SENDGRID_API_KEY=
FROM_EMAIL=noreply@chickflow.com

# Firebase (add your credentials)
FCM_SERVER_KEY=

# Business Settings
MAX_PER_CUSTOMER=1000
WAITING_PERIOD_DAYS=7
PICKUP_DEADLINE_HOUR=14
EOF

echo -e "${GREEN}✓ .env file created${NC}"

echo ""
echo -e "${YELLOW}Step 5: Initializing database migrations...${NC}"
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

echo -e "${GREEN}✓ Database migrations completed${NC}"

echo ""
echo -e "${YELLOW}Step 6: Migrating legacy data...${NC}"

# Create migration script
python3 <<EOF
from app import create_app
from models import db, Customer, Order, Inventory
import csv
from datetime import datetime, date

app = create_app()
with app.app_context():
    # Migrate customers from CSV
    try:
        with open('../customers.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                customer = Customer.query.filter_by(customer_id=row['customer_id']).first()
                if not customer:
                    customer = Customer(
                        customer_id=row['customer_id'],
                        farm_name=row['farm_name'],
                        phone=row['phone'],
                        zone=row['zone'],
                        tier=row['tier'],
                        last_fulfilled_date=datetime.strptime(row['last_fulfilled_date'], '%Y-%m-%d') if row['last_fulfilled_date'] else None
                    )
                    db.session.add(customer)
        
        db.session.commit()
        print("✓ Customers migrated successfully")
    except FileNotFoundError:
        print("! customers.csv not found, skipping migration")
    except Exception as e:
        print(f"✗ Error migrating customers: {e}")
    
    # Create default admin user
    from models import User
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@chickflow.com',
            role='admin'
        )
        admin.set_password('admin123')  # Change this immediately!
        db.session.add(admin)
        db.session.commit()
        print("✓ Default admin user created (username: admin, password: admin123)")
    
    # Create today's inventory
    today = date.today()
    inventory = Inventory.query.filter_by(date=today).first()
    if not inventory:
        try:
            with open('../supply.txt', 'r') as f:
                supply = int(f.read().strip())
                inventory = Inventory(
                    date=today,
                    expected_supply=supply,
                    actual_supply=supply,
                    status='confirmed'
                )
                db.session.add(inventory)
                db.session.commit()
                print(f"✓ Today's inventory created: {supply} chicks")
        except FileNotFoundError:
            print("! supply.txt not found, skipping inventory creation")
EOF

echo ""
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo "Next steps:"
echo "1. Update .env file with your API credentials (Twilio, SendGrid, etc.)"
echo "2. Change the default admin password (username: admin, password: admin123)"
echo "3. Start the backend: cd backend && source venv/bin/activate && python app.py"
echo "4. Setup frontend: cd frontend && npm install && npm run dev"
echo "5. Setup mobile: cd mobile && npm install && npm start"
echo ""
echo -e "${YELLOW}Important: Change the database password in this script and .env!${NC}"
