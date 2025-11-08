# ChickFlow API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication

All API endpoints (except login/register) require JWT authentication.

### Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Authentication Endpoints

### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "role": "customer",
  "customer_id": "F001" // Optional, to link to existing customer
}
```

**Response:** `201 Created`
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "customer",
    "is_active": true,
    "created_at": "2025-11-08T10:00:00"
  }
}
```

### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "customer"
  }
}
```

### Get Current User
```http
GET /auth/me
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "customer",
  "customer": {
    "id": 1,
    "customer_id": "F001",
    "farm_name": "Green Acres",
    "tier": "Loyal"
  }
}
```

## Customer Endpoints

### List Customers
```http
GET /customers?tier=Loyal&zone=North&is_active=true
```

**Query Parameters:**
- `tier` (optional): Filter by tier (Contract, Loyal, New)
- `zone` (optional): Filter by zone
- `is_active` (optional): Filter by active status (default: true)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "customer_id": "F001",
    "farm_name": "Green Acres",
    "phone": "+254712345678",
    "email": "green@example.com",
    "zone": "North",
    "tier": "Loyal",
    "address": "123 Farm Road",
    "coordinates": "-1.2921,36.8219",
    "last_fulfilled_date": "2025-11-01T00:00:00",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00"
  }
]
```

### Create Customer
```http
POST /customers
```

**Request Body:**
```json
{
  "customer_id": "F010",
  "farm_name": "Sunrise Poultry",
  "phone": "+254700000000",
  "email": "sunrise@example.com",
  "zone": "South",
  "tier": "New",
  "address": "456 Poultry Lane",
  "coordinates": "-1.2921,36.8219"
}
```

**Response:** `201 Created`

### Get Customer Details
```http
GET /customers/:id
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "customer_id": "F001",
  "farm_name": "Green Acres",
  "phone": "+254712345678",
  "tier": "Loyal",
  "recent_orders": [
    {
      "id": 1,
      "order_number": "ORD-20251108100000",
      "order_qty": 500,
      "status": "allocated",
      "order_date": "2025-11-08T10:00:00"
    }
  ]
}
```

### Update Customer
```http
PUT /customers/:id
```

**Request Body:**
```json
{
  "tier": "Contract",
  "phone": "+254711111111"
}
```

**Response:** `200 OK`

## Order Endpoints

### List Orders
```http
GET /orders?status=pending&customer_id=1&date_from=2025-11-01&date_to=2025-11-30
```

**Query Parameters:**
- `status` (optional): Filter by status
- `customer_id` (optional): Filter by customer
- `date_from` (optional): Start date filter
- `date_to` (optional): End date filter

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "order_number": "ORD-20251108100000",
    "customer_id": 1,
    "customer": {
      "farm_name": "Green Acres",
      "tier": "Loyal"
    },
    "order_qty": 500,
    "status": "pending",
    "order_date": "2025-11-08T10:00:00",
    "requested_delivery_date": "2025-11-10",
    "expected_delivery_date": null,
    "actual_delivery_date": null,
    "notes": "Need early delivery",
    "priority_level": 0
  }
]
```

### Create Order
```http
POST /orders
```

**Request Body:**
```json
{
  "customer_id": 1,
  "order_qty": 500,
  "requested_delivery_date": "2025-11-10",
  "notes": "Urgent order",
  "priority_level": 1
}
```

**Response:** `201 Created`

### Get Order Details
```http
GET /orders/:id
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "order_number": "ORD-20251108100000",
  "customer": {...},
  "order_qty": 500,
  "status": "allocated",
  "allocation": {
    "id": 1,
    "allocated_qty": 500,
    "allocation_date": "2025-11-10",
    "pickup_deadline": "2025-11-10T14:00:00",
    "status": "pending"
  },
  "delivery": {
    "driver_name": "John Driver",
    "vehicle_number": "KXX 123Y",
    "delivery_status": "in_transit"
  }
}
```

### Update Order
```http
PUT /orders/:id
```

**Request Body:**
```json
{
  "order_qty": 600,
  "status": "pending"
}
```

**Response:** `200 OK`

### Cancel Order
```http
DELETE /orders/:id
```

**Response:** `200 OK`

## Inventory Endpoints

### List Inventory
```http
GET /inventory?date_from=2025-11-01&date_to=2025-11-30
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "date": "2025-11-08",
    "expected_supply": 10000,
    "actual_supply": 9800,
    "allocated": 9500,
    "remaining": 300,
    "status": "confirmed",
    "notes": "Slight shortage due to hatchery delay"
  }
]
```

### Create Inventory
```http
POST /inventory
```

**Request Body:**
```json
{
  "date": "2025-11-10",
  "expected_supply": 12000,
  "actual_supply": 12000,
  "status": "confirmed"
}
```

**Response:** `201 Created`

### Update Inventory
```http
PUT /inventory/:id
```

**Request Body:**
```json
{
  "actual_supply": 11500,
  "notes": "Updated after final count"
}
```

**Response:** `200 OK`

## Allocation Endpoints

### Run Allocation
```http
POST /allocations/run
```

**Request Body:**
```json
{
  "date": "2025-11-10"
}
```

**Response:** `200 OK`
```json
{
  "allocated": [
    {
      "order_id": 1,
      "order_number": "ORD-20251108100000",
      "customer_id": 1,
      "customer_name": "Green Acres",
      "phone": "+254712345678",
      "tier": "Loyal",
      "requested_qty": 500,
      "allocated_qty": 500,
      "priority_score": 150.5
    }
  ],
  "waitlisted": [
    {
      "order_id": 5,
      "customer_name": "New Farm",
      "tier": "New",
      "requested_qty": 200,
      "allocated_qty": 0
    }
  ],
  "remaining": 300,
  "total_orders": 15,
  "allocation_date": "2025-11-10"
}
```

### List Allocations
```http
GET /allocations?date_from=2025-11-01&customer_id=1&status=pending
```

**Response:** `200 OK`

### Confirm Pickup
```http
POST /allocations/:id/confirm-pickup
```

**Response:** `200 OK`

## Waitlist Endpoints

### Get Waitlist
```http
GET /waitlist?status=waiting
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "order_id": 5,
    "customer": {
      "farm_name": "New Farm",
      "tier": "New"
    },
    "requested_qty": 200,
    "priority_score": 35.0,
    "added_date": "2025-11-08T10:00:00",
    "target_fulfillment_date": "2025-11-09",
    "status": "waiting"
  }
]
```

### Process Waitlist
```http
POST /waitlist/process
```

**Request Body:**
```json
{
  "date": "2025-11-09"
}
```

**Response:** `200 OK`
```json
{
  "fulfilled": 3,
  "remaining_waitlist": 2
}
```

## Delivery Endpoints

### List Deliveries
```http
GET /deliveries?status=in_transit
```

**Response:** `200 OK`

### Create Delivery
```http
POST /deliveries
```

**Request Body:**
```json
{
  "order_id": 1,
  "driver_name": "John Driver",
  "driver_phone": "+254700000000",
  "vehicle_number": "KXX 123Y",
  "estimated_arrival": "2025-11-10T11:00:00"
}
```

**Response:** `201 Created`

### Update Delivery
```http
PUT /deliveries/:id
```

**Request Body:**
```json
{
  "delivery_status": "delivered",
  "actual_arrival": "2025-11-10T11:15:00",
  "received_by": "Farm Manager"
}
```

**Response:** `200 OK`

## Dashboard Endpoints

### Get Dashboard Stats
```http
GET /dashboard/stats
```

**Response:** `200 OK`
```json
{
  "today": {
    "date": "2025-11-08",
    "expected_supply": 10000,
    "actual_supply": 10000,
    "allocated": 9500,
    "remaining": 500,
    "total_orders": 20,
    "allocations": 18
  },
  "overall": {
    "total_customers": 150,
    "pending_orders": 5,
    "waitlist_count": 3
  }
}
```

## Reports Endpoints

### Daily Summary
```http
GET /reports/daily-summary?date=2025-11-08
```

**Response:** `200 OK`
```json
{
  "date": "2025-11-08",
  "inventory": {
    "expected_supply": 10000,
    "actual_supply": 10000,
    "allocated": 9500,
    "remaining": 500
  },
  "allocations": {
    "total_count": 18,
    "total_qty": 9500,
    "by_tier": [
      {"tier": "Contract", "count": 5, "total_qty": 3000},
      {"tier": "Loyal", "count": 10, "total_qty": 5500},
      {"tier": "New", "count": 3, "total_qty": 1000}
    ]
  },
  "orders": {
    "total": 20,
    "pending": 2,
    "allocated": 18,
    "waitlisted": 2
  },
  "waitlist": {
    "total": 3,
    "waiting": 2,
    "fulfilled": 1
  }
}
```

### Weekly Summary
```http
GET /reports/weekly-summary?end_date=2025-11-08
```

**Response:** `200 OK`

### Monthly Summary
```http
GET /reports/monthly-summary?year=2025&month=11
```

**Response:** `200 OK`

### Customer Analytics
```http
GET /reports/customer-analytics?days=30
```

**Response:** `200 OK`

### Waitlist Analysis
```http
GET /reports/waitlist-analysis?days=30
```

**Response:** `200 OK`

### Export Allocations
```http
GET /reports/export/allocations?start_date=2025-11-01&end_date=2025-11-30
```

**Response:** `200 OK`
```json
{
  "filename": "allocations_20251108.xlsx",
  "data": "base64_encoded_excel_data",
  "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid credentials"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per user

## Pagination

For endpoints returning lists, use:
```
?page=1&per_page=20
```

Default: `per_page=50`, `max_per_page=100`
