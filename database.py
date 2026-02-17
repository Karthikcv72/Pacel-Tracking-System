import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime, timedelta

class Database:
    def __init__(self, host='localhost', user='root', password='', database='parcel_tracking'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error executing query: {e}")
            return False
        finally:
            cursor.close()
    
    def fetch_all(self, query, params=None):
        cursor = self.connection.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error fetching data: {e}")
            return []
        finally:
            cursor.close()
    
    def fetch_one(self, query, params=None):
        cursor = self.connection.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error fetching data: {e}")
            return None
        finally:
            cursor.close()
    
    def call_procedure(self, proc_name, params=None):
        cursor = self.connection.cursor(dictionary=True)
        try:
            if params:
                cursor.callproc(proc_name, params)
            else:
                cursor.callproc(proc_name)
            
            results = []
            for result in cursor.stored_results():
                results.extend(result.fetchall())
            
            self.connection.commit()
            return results
        except Error as e:
            print(f"Error calling procedure: {e}")
            return None
        finally:
            cursor.close()


class ParcelTrackingSystem:
    def __init__(self, db):
        self.db = db
    
    # Customer Operations
    def add_customer(self, first_name, middle_name, last_name, contact, address):
        query = """
        INSERT INTO Customer (First_Name, Middle_Name, Last_Name, Contact, Address)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (first_name, middle_name, last_name, contact, address)
        if self.db.execute_query(query, params):
            return self.db.connection.cursor().lastrowid
        return None
    
    def get_customer_by_contact(self, contact):
        query = "SELECT * FROM Customer WHERE Contact = %s"
        return self.db.fetch_one(query, (contact,))
    
    def get_all_customers(self):
        query = "SELECT * FROM Customer ORDER BY Created_At DESC"
        return self.db.fetch_all(query)
    
    # Product Operations
    def get_all_products(self):
        query = "SELECT * FROM Products ORDER BY Category, Product_name"
        return self.db.fetch_all(query)
    
    def add_product(self, product_name, category, price):
        query = """
        INSERT INTO Products (Product_name, Category, Price)
        VALUES (%s, %s, %s)
        """
        return self.db.execute_query(query, (product_name, category, price))
    
    # Order Operations
    def place_order(self, customer_id, product_ids, quantities, special_instructions=''):
        prod_ids_str = ','.join(map(str, product_ids))
        qty_str = ','.join(map(str, quantities))
        
        result = self.db.call_procedure('PlaceOrder', 
                                       [customer_id, prod_ids_str, qty_str, special_instructions])
        if result:
            return result[0]['Order_ID']
        return None
    
    def process_payment(self, order_id, amount, method):
        result = self.db.call_procedure('ProcessPayment', [order_id, amount, method])
        return result is not None
    
    def update_tracking(self, order_id, location, status, vehicle_id=None):
        result = self.db.call_procedure('UpdateTracking', 
                                       [order_id, location, status, vehicle_id])
        return result is not None
    
    def get_order_details(self, order_id):
        query = """
        SELECT 
            o.Order_ID,
            o.Order_Status,
            o.Expected_Delivery,
            o.Has_Paid,
            o.Spl_Instructions,
            o.Created_At,
            c.First_Name,
            c.Last_Name,
            c.Contact,
            c.Address,
            CalculateOrderTotal(o.Order_ID) as Total_Amount,
            GetOrderLocation(o.Order_ID) as Current_Location,
            IsOrderDelayed(o.Order_ID) as Is_Delayed
        FROM Orders o
        INNER JOIN Customer c ON o.Customer_ID = c.Customer_ID
        WHERE o.Order_ID = %s
        """
        return self.db.fetch_one(query, (order_id,))
    
    def get_order_products(self, order_id):
        query = """
        SELECT 
            p.Product_name,
            p.Category,
            p.Price,
            op.Quantity,
            (p.Price * op.Quantity) as Subtotal
        FROM Order_Product op
        INNER JOIN Products p ON op.Product_ID = p.Product_ID
        WHERE op.Order_ID = %s
        """
        return self.db.fetch_all(query, (order_id,))
    
    def get_customer_orders(self, customer_id):
        result = self.db.call_procedure('GetCustomerOrders', [customer_id])
        return result
    
    def get_all_orders(self):
        query = """
        SELECT 
            o.Order_ID,
            CONCAT(c.First_Name, ' ', c.Last_Name) as Customer_Name,
            o.Order_Status,
            o.Expected_Delivery,
            o.Has_Paid,
            CalculateOrderTotal(o.Order_ID) as Total_Amount,
            o.Created_At
        FROM Orders o
        INNER JOIN Customer c ON o.Customer_ID = c.Customer_ID
        ORDER BY o.Created_At DESC
        """
        return self.db.fetch_all(query)
    
    # Tracking Operations
    def get_tracking_history(self, order_id):
        query = """
        SELECT 
            t.Location,
            t.Status,
            t.TimeStamp,
            v.Vehicle_no,
            v.Driver_name
        FROM Tracking_Info t
        LEFT JOIN Vehicle_Info v ON t.Vehicle_ID = v.Vehicle_ID
        WHERE t.Order_ID = %s
        ORDER BY t.TimeStamp ASC
        """
        return self.db.fetch_all(query, (order_id,))
    
    def get_order_history(self, order_id):
        query = """
        SELECT Status, TimeStamp
        FROM Order_History
        WHERE Order_ID = %s
        ORDER BY TimeStamp ASC
        """
        return self.db.fetch_all(query, (order_id,))
    
    # Vehicle Operations
    def get_all_vehicles(self):
        query = "SELECT * FROM Vehicle_Info ORDER BY Status, Vehicle_no"
        return self.db.fetch_all(query)
    
    def get_available_vehicles(self):
        query = "SELECT * FROM Vehicle_Info WHERE Status = 'Available'"
        return self.db.fetch_all(query)
    
    def add_vehicle(self, vehicle_no, driver_name):
        query = """
        INSERT INTO Vehicle_Info (Vehicle_no, Driver_name)
        VALUES (%s, %s)
        """
        return self.db.execute_query(query, (vehicle_no, driver_name))
    
    # Dashboard Statistics
    def get_dashboard_stats(self):
        stats = {}
        
        # Total orders
        query = "SELECT COUNT(*) as count FROM Orders"
        result = self.db.fetch_one(query)
        stats['total_orders'] = result['count'] if result else 0
        
        # Pending orders
        query = "SELECT COUNT(*) as count FROM Orders WHERE Order_Status NOT IN ('Delivered', 'Cancelled')"
        result = self.db.fetch_one(query)
        stats['pending_orders'] = result['count'] if result else 0
        
        # Delivered orders
        query = "SELECT COUNT(*) as count FROM Orders WHERE Order_Status = 'Delivered'"
        result = self.db.fetch_one(query)
        stats['delivered_orders'] = result['count'] if result else 0
        
        # Total customers
        query = "SELECT COUNT(*) as count FROM Customer"
        result = self.db.fetch_one(query)
        stats['total_customers'] = result['count'] if result else 0
        
        # Available vehicles (using function)
        query = "SELECT GetAvailableVehicles() as count"
        result = self.db.fetch_one(query)
        stats['available_vehicles'] = result['count'] if result else 0
        
        return stats