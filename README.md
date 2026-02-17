# 📦 Parcel Tracking System - DBMS Project

A comprehensive parcel tracking system built with MySQL, Python, and Streamlit featuring real-time tracking, automated triggers, stored procedures, and functions.

## 🎯 Features

### Core Functionality
- **Customer Management**: Register and manage customer information
- **Order Placement**: Create orders with multiple products
- **Payment Processing**: Handle payments with multiple methods (Cash, Card, UPI, Net Banking)
- **Real-time Tracking**: Track parcels with location updates and estimated delivery
- **Vehicle Management**: Assign and manage delivery vehicles
- **Product Catalog**: Manage products with categories and pricing

### Database Features
- **5 Triggers**:
  - Auto-update payment status when payment is made
  - Log order status changes to history
  - Auto-set expected delivery dates
  - Update vehicle status on assignment
  - Free up vehicles when delivery is complete

- **4 Stored Procedures**:
  - `PlaceOrder`: Create new orders with products
  - `ProcessPayment`: Handle payment transactions
  - `UpdateTracking`: Update tracking information
  - `GetCustomerOrders`: Retrieve customer order history

- **4 Functions**:
  - `CalculateOrderTotal`: Calculate total order amount
  - `GetOrderLocation`: Get current parcel location
  - `IsOrderDelayed`: Check if order is delayed
  - `GetAvailableVehicles`: Count available vehicles

## 📁 Project Structure

```
parcel_tracking_system/
├── database.py          # Database connection and operations
├── app.py              # Streamlit frontend application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── schema.sql         # Database schema with triggers, procedures, functions
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- MySQL Server 8.0 or higher
- pip (Python package manager)

### Step 1: Install MySQL
1. Download and install MySQL from [mysql.com](https://dev.mysql.com/downloads/mysql/)
2. Start MySQL service
3. Note down your MySQL root password

### Step 2: Create Database
1. Open MySQL Command Line or MySQL Workbench
2. Execute the SQL schema file:
```bash
mysql -u root -p < schema.sql
```
Or copy and paste the contents of the SQL artifact into MySQL Workbench and execute.

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Database Connection
Edit `database.py` and update the database credentials:
```python
def init_connection():
    db = Database(
        host='localhost',
        user='root',
        password='your_mysql_password',  # Change this
        database='parcel_tracking'
    )
```

Also update the same in `app.py` in the `init_connection()` function.

### Step 5: Run the Application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📊 Database Schema

### Main Tables
- **Customer**: Customer information
- **Products**: Product catalog
- **Orders**: Order details and status
- **Order_Product**: Many-to-many relationship between orders and products
- **Payment**: Payment transactions
- **Tracking_Info**: Location tracking history
- **Order_History**: Order status change logs
- **Vehicle_Info**: Delivery vehicle information

### Entity Relationships
- Customer (1) → (N) Orders
- Orders (N) → (N) Products (through Order_Product)
- Orders (1) → (1) Payment
- Orders (1) → (N) Tracking_Info
- Orders (1) → (N) Order_History
- Vehicle_Info (1) → (N) Tracking_Info

## 🎨 Application Pages

### 1. Dashboard
- Overview statistics (Total orders, pending, delivered, customers, vehicles)
- Recent orders list
- Quick access to all features

### 2. Track Parcel
- Enter Order ID to track parcels
- View order details, products, payment status
- Real-time tracking history with locations
- Vehicle and driver information
- Expected delivery time and delay alerts

### 3. Place Order
- Register new customers or select existing
- Add multiple products to cart
- Calculate total automatically
- Process payments
- Special delivery instructions

### 4. Manage Orders
- View all orders with filters
- Update tracking information
- Assign vehicles to deliveries
- Update order status

### 5. Customers
- View all customers
- Add new customers
- View customer order history

### 6. Vehicles
- View all vehicles and their status
- Add new vehicles
- Track availability statistics

### 7. Products
- View product catalog
- Add new products with categories and pricing

## 🔧 Key Features Implementation

### Tracking System
The tracking system shows:
- Current location of the parcel
- Timestamp of each location update
- Vehicle and driver assigned
- Status progression (Dispatched → In Transit → Out for Delivery → Delivered)
- Estimated delivery time

### Automated Workflows
1. **Order Placement**: Automatically sets expected delivery date (3 days from order)
2. **Payment**: Automatically updates order payment status
3. **Status Changes**: All status changes are logged in Order_History
4. **Vehicle Assignment**: Automatically changes vehicle status to "On Delivery"
5. **Delivery Completion**: Automatically frees up vehicles for new deliveries

## 📝 Sample Data
The database comes pre-loaded with:
- 3 sample customers
- 5 sample products (Electronics, Books, Accessories)
- 3 delivery vehicles

## 🔐 Security Notes
- Change default MySQL password
- Use environment variables for sensitive data in production
- Implement user authentication for production use
- Add input validation and sanitization

## 📈 Future Enhancements
- Real-time GPS tracking integration
- SMS/Email notifications
- Mobile app integration
- Advanced analytics and reporting
- Multi-language support
- Route optimization for delivery vehicles

## 🤝 Contributing
This is a DBMS course project. Feel free to extend and enhance the features.

## 📄 License
Educational project for DBMS course.

## 👨‍💻 Author
DBMS Project 2024

---

**Note**: Make sure MySQL server is running before starting the application. Test with sample data before going live.
