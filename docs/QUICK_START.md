# Quick Start Guide - ChickFlow

## For Administrators

### Initial Setup (5 minutes)

1. **Run the setup script**
```bash
cd /home/gwancore/Documents/beams
chmod +x setup.sh
./setup.sh
```

2. **Start the backend**
```bash
cd backend
source venv/bin/activate
python app.py
```
Backend runs at: http://localhost:5000

3. **Start the web dashboard** (new terminal)
```bash
cd frontend
npm install
npm run dev
```
Dashboard runs at: http://localhost:3000

4. **Login to dashboard**
- URL: http://localhost:3000
- Username: `admin`
- Password: `admin123` (change this immediately!)

### Daily Operations

**Morning Routine (10 minutes)**

1. **Add Today's Inventory**
   - Navigate to Inventory section
   - Click "Add Inventory"
   - Enter expected supply for today
   - Save

2. **Review Pending Orders**
   - Navigate to Orders section
   - Filter by status: "pending"
   - Review order details

3. **Run Allocation**
   - Navigate to Allocations section
   - Click "Run Allocation"
   - Select today's date
   - Click "Allocate"
   - System automatically:
     - Allocates chicks by priority
     - Sends SMS/Email notifications
     - Creates dispatch list
     - Updates waitlist

4. **Review Results**
   - Check allocated farms list
   - Review waitlist
   - Download dispatch list
   - Print for warehouse team

**Throughout the Day**

- Monitor pickup confirmations
- Update actual supply if different
- Handle customer inquiries
- Process new orders

**End of Day (5 minutes)**

- Review daily summary report
- Confirm all pickups
- Check waitlist for tomorrow
- Update inventory status

## For Customers

### Mobile App Usage

1. **Download & Install**
   - Install Expo Go from App Store/Play Store
   - Scan QR code provided by admin
   - App opens automatically

2. **Login**
   - Open ChickFlow app
   - Enter your username and password
   - Tap "Login"

3. **Place Order**
   - Tap "+" button or "Place New Order"
   - Enter quantity needed
   - Select delivery date
   - Add any notes
   - Submit order

4. **Track Order**
   - View order status on home screen
   - Receive notifications for:
     - Order confirmation
     - Allocation confirmation
     - Waitlist updates
     - Delivery updates

5. **Pickup**
   - Check allocated quantity
   - Note pickup deadline (2 PM)
   - Collect chicks from warehouse
   - Confirm pickup in app

## Common Tasks

### Adding a New Customer

**Web Dashboard:**
1. Navigate to Customers
2. Click "Add Customer"
3. Fill in details:
   - Customer ID (e.g., F100)
   - Farm Name
   - Phone Number
   - Email
   - Zone
   - Tier (Contract/Loyal/New)
4. Save

### Processing Waitlist

**When new supply becomes available:**
1. Navigate to Waitlist
2. Click "Process Waitlist"
3. Enter available quantity
4. System auto-allocates by priority
5. Notifications sent automatically

### Generating Reports

**Daily Report:**
1. Navigate to Reports
2. Select "Daily Summary"
3. Choose date
4. View or Download

**Monthly Report:**
1. Navigate to Reports
2. Select "Monthly Summary"
3. Choose month and year
4. View or Export to Excel

### Changing Customer Tier

1. Navigate to Customers
2. Find customer
3. Click Edit
4. Change Tier dropdown
5. Save
6. System automatically adjusts priority

## Troubleshooting

### Backend won't start
```bash
# Check if virtual environment is activated
source venv/bin/activate

# Check for errors
python app.py

# Common fix: reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Reinstall dependencies
rm -rf node_modules
npm install

# Clear cache
npm run dev -- --force
```

### Can't login
- Verify username/password
- Check backend is running
- Clear browser cache
- Reset password via admin

### Notifications not sending
- Check .env file has API keys
- Verify Twilio/SendGrid credentials
- Check notification logs in backend
- For testing, check console output

### Database errors
```bash
# Restart PostgreSQL
sudo systemctl restart postgresql

# Check connection
psql -U chickflow -d chickflow

# Rerun migrations
flask db upgrade
```

## Tips & Best Practices

### For Administrators

1. **Daily Backups**
   - Automatic backup runs at 2 AM
   - Manual backup: `pg_dump chickflow > backup.sql`

2. **Monitor Waitlist**
   - Keep waitlist under 5 customers
   - Process daily when supply available
   - Communicate with waiting customers

3. **Inventory Accuracy**
   - Update actual supply when confirmed
   - Account for mortality/rejects
   - Note any supply issues

4. **Customer Tiers**
   - Review quarterly
   - Promote loyal customers
   - Update based on order frequency

5. **Regular Reports**
   - Weekly: Review fulfillment rates
   - Monthly: Customer analytics
   - Quarterly: System performance

### For Customers

1. **Order Early**
   - Place orders 2-3 days in advance
   - Higher priority for early orders

2. **Accurate Quantities**
   - Order what you need
   - Max 1000 chicks per order
   - Multiple orders if needed

3. **Pickup on Time**
   - Deadline is 2 PM
   - Late pickup may result in cancellation
   - Call ahead if delayed

4. **Update Profile**
   - Keep phone number current
   - Check email regularly
   - Update delivery address

## Security Best Practices

1. **Change Default Password**
   - Admin password: admin123 → strong password
   - Update in Settings

2. **Regular Updates**
   - Apply security patches
   - Update dependencies monthly
   - Monitor for vulnerabilities

3. **Backup Strategy**
   - Daily automated backups
   - Weekly manual verification
   - Off-site backup storage

4. **Access Control**
   - Limit admin accounts
   - Review user permissions
   - Deactivate unused accounts

## Getting Help

### Documentation
- Full API docs: `/docs/API.md`
- Deployment guide: `/docs/DEPLOYMENT.md`
- System overview: `/docs/SYSTEM_OVERVIEW.md`

### Support Channels
- Email: support@chickflow.com
- Phone: +254-XXX-XXXXX
- GitHub Issues: [repo-url]/issues

### Training
- Admin training: 2 hours
- Customer onboarding: 30 minutes
- Video tutorials: Available in app

## Next Steps

After completing quick start:

1. **Configure Notifications**
   - Add Twilio credentials to .env
   - Add SendGrid API key
   - Test notification sending

2. **Import Existing Data**
   - Migrate customers from CSV
   - Import historical orders
   - Set up inventory

3. **Customize Settings**
   - Adjust pickup deadline
   - Set max per customer
   - Configure waiting period

4. **Train Staff**
   - Admin training
   - Warehouse training
   - Customer support training

5. **Launch**
   - Notify customers
   - Start daily operations
   - Monitor and optimize

---

**Congratulations! You're ready to use ChickFlow.**

For detailed information, refer to the complete documentation in the `/docs` folder.
