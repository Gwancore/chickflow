# ChickFlow - Day-Old Chicks Management System

A comprehensive management system for day-old chick allocation, distribution, and customer management with support for both web and mobile platforms.

## 🌟 Features

### Core Features
- **Smart Allocation Engine**: Prioritizes customers based on tier (Contract, Loyal, New), waiting time, and order history
- **Complete Date Tracking**: Tracks order placement, waiting periods, delivery dates, and pickup deadlines
- **Multi-Channel Notifications**: SMS, Email, and Push notifications for all stakeholders
- **Comprehensive Reporting**: Daily, weekly, and monthly reports with analytics and export capabilities
- **Waitlist Management**: Automatic waitlist handling with priority-based fulfillment
- **Inventory Management**: Track daily supply, allocations, and remaining stock
- **Customer Tiers**: Contract, Loyal, and New customer management with different priority levels

### Platform Support
- **Web Dashboard**: Full-featured admin dashboard built with React
- **Mobile App**: Customer-facing mobile app built with React Native/Expo
- **REST API**: Complete backend API for integration

## 📁 Project Structure

```
beams/
├── backend/                    # Flask API Backend
│   ├── app.py                 # Main application
│   ├── config.py              # Configuration
│   ├── models.py              # Database models
│   ├── routes.py              # API routes
│   ├── auth_routes.py         # Authentication routes
│   ├── reports_routes.py      # Reporting routes
│   ├── allocation_engine.py   # Allocation logic
│   ├── notifications.py       # Notification service
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React Web Dashboard
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Page components
│   │   ├── context/          # Context providers
│   │   └── api/              # API client
│   ├── package.json
│   └── vite.config.js
├── mobile/                     # React Native Mobile App
│   ├── src/
│   │   ├── screens/          # App screens
│   │   ├── context/          # Context providers
│   │   └── api/              # API client
│   ├── App.js
│   ├── app.json
│   └── package.json
└── docs/                       # Documentation
    ├── API.md                 # API documentation
    ├── DEPLOYMENT.md          # Deployment guide
    └── USER_GUIDE.md          # User guide
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL (or SQLite for development)
- Redis (optional, for background tasks)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. Run the server:
```bash
python app.py
```

Backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

### Mobile Setup

1. Navigate to mobile directory:
```bash
cd mobile
```

2. Install dependencies:
```bash
npm install
```

3. Start Expo:
```bash
npm start
```

4. Scan QR code with Expo Go app on your phone

## 🔑 Key Components

### Database Models
- **User**: Authentication and authorization
- **Customer**: Farm/customer profiles with tier management
- **Order**: Order tracking with comprehensive date fields
- **Inventory**: Daily supply tracking
- **Allocation**: Allocation records with pickup deadlines
- **Waitlist**: Priority-based waitlist management
- **Delivery**: Delivery tracking with proof of delivery
- **Notification**: Multi-channel notification logs

### Allocation Engine
- Priority-based allocation using customer tiers
- Automatic waitlist management
- Fair rotation for loyal customers
- Contract customer fulfillment priority
- Configurable business rules

### Date Tracking
- **Order Date**: When order was placed
- **Requested Delivery Date**: Customer's preferred date
- **Expected Delivery Date**: Allocated delivery date
- **Actual Delivery Date**: When actually delivered
- **Pickup Deadline**: Time limit for pickup
- **Waiting Period**: Time in waitlist

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Customers
- `GET /api/customers` - List customers
- `POST /api/customers` - Create customer
- `GET /api/customers/:id` - Get customer details
- `PUT /api/customers/:id` - Update customer

### Orders
- `GET /api/orders` - List orders
- `POST /api/orders` - Create order
- `GET /api/orders/:id` - Get order details
- `PUT /api/orders/:id` - Update order
- `DELETE /api/orders/:id` - Cancel order

### Inventory
- `GET /api/inventory` - List inventory
- `POST /api/inventory` - Create inventory record
- `PUT /api/inventory/:id` - Update inventory

### Allocations
- `POST /api/allocations/run` - Run allocation
- `GET /api/allocations` - List allocations
- `POST /api/allocations/:id/confirm-pickup` - Confirm pickup

### Reports
- `GET /api/reports/daily-summary` - Daily summary
- `GET /api/reports/weekly-summary` - Weekly summary
- `GET /api/reports/monthly-summary` - Monthly summary
- `GET /api/reports/customer-analytics` - Customer analytics
- `GET /api/reports/waitlist-analysis` - Waitlist analysis
- `GET /api/reports/export/allocations` - Export allocations

### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics

## 🔐 Security

- JWT-based authentication
- Role-based access control (Admin, Manager, Customer, Driver)
- Password hashing with Werkzeug
- Environment-based configuration
- CORS protection

## 📱 Mobile Features

- Customer login and profile management
- Order placement and tracking
- Real-time notifications
- Order history
- Allocation status

## 🎨 Web Dashboard Features

- Real-time dashboard with statistics
- Order management
- Customer management
- Inventory tracking
- Allocation management
- Waitlist monitoring
- Comprehensive reports and analytics
- Data export to Excel

## 🔔 Notifications

### SMS (Twilio)
- Order confirmations
- Allocation notifications
- Waitlist updates
- Delivery updates

### Email (SendGrid)
- Detailed order confirmations
- Allocation details
- Reports and summaries

### Push Notifications (Firebase)
- Mobile app notifications
- Real-time updates

## 📈 Reports & Analytics

- Daily allocation summaries
- Weekly and monthly trends
- Customer analytics
- Tier-based performance
- Waitlist analysis
- Fulfillment rates
- Export to Excel/CSV

## 🔧 Configuration

Edit `.env` file in backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chickflow

# Redis
REDIS_URL=redis://localhost:6379/0

# Twilio
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890

# SendGrid
SENDGRID_API_KEY=your-api-key
FROM_EMAIL=noreply@chickflow.com

# Firebase
FCM_SERVER_KEY=your-fcm-key

# Business Rules
MAX_PER_CUSTOMER=1000
WAITING_PERIOD_DAYS=7
PICKUP_DEADLINE_HOUR=14
```

## 🚢 Deployment

### Backend (Heroku/AWS/DigitalOcean)
```bash
# Using gunicorn
gunicorn app:app
```

### Frontend (Vercel/Netlify)
```bash
npm run build
# Deploy dist/ folder
```

### Mobile (Expo)
```bash
expo build:android
expo build:ios
```

## 📝 License

MIT License

## 👥 Support

For support, email support@chickflow.com or open an issue in the repository.

## 🔄 Migration from Legacy System

To migrate from the old CSV-based system:

1. Run the backend setup
2. Use the import script to migrate customers from `customers.csv`
3. Historical data will be preserved in the new system

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Mobile tests
cd mobile
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📞 Contact

- Website: https://chickflow.com
- Email: info@chickflow.com
- Phone: +254-XXX-XXXXX
