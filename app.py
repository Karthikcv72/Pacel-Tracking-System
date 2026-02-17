import streamlit as st
import pandas as pd
from datetime import datetime
from database import Database, ParcelTrackingSystem

# Page configuration
st.set_page_config(
    page_title="Parcel Tracking System",
    page_icon="📦",
    layout="wide"
)

# Initialize database connection
@st.cache_resource
def init_connection():
    db = Database(
        host='localhost',
        user='root',
        password='your_password',  # Change this
        database='parcel_tracking'
    )
    if db.connect():
        return db
    return None

db = init_connection()

if db is None:
    st.error("❌ Failed to connect to database. Please check your credentials.")
    st.stop()

pts = ParcelTrackingSystem(db)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-box {
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 1rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📦 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Track Parcel", "Place Order", "Manage Orders", "Customers", "Vehicles", "Products"]
)

# ===== DASHBOARD PAGE =====
if page == "Dashboard":
    st.markdown("<h1 class='main-header'>📦 Parcel Tracking Dashboard</h1>", unsafe_allow_html=True)
    
    # Get statistics
    stats = pts.get_dashboard_stats()
    
    # Display statistics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Orders", stats['total_orders'])
    with col2:
        st.metric("Pending Orders", stats['pending_orders'])
    with col3:
        st.metric("Delivered", stats['delivered_orders'])
    with col4:
        st.metric("Total Customers", stats['total_customers'])
    with col5:
        st.metric("Available Vehicles", stats['available_vehicles'])
    
    st.markdown("---")
    
    # Recent orders
    st.subheader("📋 Recent Orders")
    orders = pts.get_all_orders()
    if orders:
        df = pd.DataFrame(orders)
        df['Expected_Delivery'] = pd.to_datetime(df['Expected_Delivery'])
        df['Created_At'] = pd.to_datetime(df['Created_At'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No orders found.")

# ===== TRACK PARCEL PAGE =====
elif page == "Track Parcel":
    st.markdown("<h1 class='main-header'>🔍 Track Your Parcel</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        order_id = st.number_input("Enter Order ID", min_value=1, step=1)
        track_btn = st.button("🔍 Track Order", type="primary")
    
    if track_btn:
        order = pts.get_order_details(order_id)
        
        if order:
            st.success("✅ Order found!")
            
            # Order details
            st.subheader("📦 Order Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Order ID", order['Order_ID'])
                st.metric("Status", order['Order_Status'])
            with col2:
                st.metric("Total Amount", f"₹{order['Total_Amount']:.2f}")
                payment_status = "✅ Paid" if order['Has_Paid'] else "⏳ Pending"
                st.metric("Payment", payment_status)
            with col3:
                st.metric("Expected Delivery", order['Expected_Delivery'].strftime("%d-%m-%Y %H:%M"))
                delay_status = "⚠️ Delayed" if order['Is_Delayed'] else "✅ On Time"
                st.metric("Delivery Status", delay_status)
            
            # Customer details
            st.subheader("👤 Customer Details")
            st.write(f"**Name:** {order['First_Name']} {order['Last_Name']}")
            st.write(f"**Contact:** {order['Contact']}")
            st.write(f"**Address:** {order['Address']}")
            
            if order['Spl_Instructions']:
                st.info(f"**Special Instructions:** {order['Spl_Instructions']}")
            
            # Products ordered
            st.subheader("🛍️ Products Ordered")
            products = pts.get_order_products(order_id)
            if products:
                df_products = pd.DataFrame(products)
                st.dataframe(df_products, use_container_width=True)
            
            # Tracking history
            st.subheader("📍 Tracking History")
            tracking = pts.get_tracking_history(order_id)
            
            if tracking:
                st.write(f"**Current Location:** {order['Current_Location']}")
                
                # Display tracking timeline
                for i, track in enumerate(tracking):
                    with st.expander(f"📍 {track['Status']} - {track['Location']}", expanded=(i == len(tracking)-1)):
                        st.write(f"**Time:** {track['TimeStamp']}")
                        if track['Vehicle_no']:
                            st.write(f"**Vehicle:** {track['Vehicle_no']}")
                            st.write(f"**Driver:** {track['Driver_name']}")
            else:
                st.info("📦 Parcel not yet dispatched. Current location: Warehouse")
            
            # Order history
            st.subheader("📊 Status History")
            history = pts.get_order_history(order_id)
            if history:
                df_history = pd.DataFrame(history)
                df_history['TimeStamp'] = pd.to_datetime(df_history['TimeStamp'])
                st.dataframe(df_history, use_container_width=True)
        else:
            st.error("❌ Order not found. Please check the Order ID.")

# =====