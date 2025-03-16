import streamlit as st
import pandas as pd
import plotly.express as px

# Load datasets
@st.cache_data
def load_data():
    orders_product_df = pd.read_csv("orders_products_df.csv")
    orders_sellers_df = pd.read_csv("orders_sellers_df.csv")
    return orders_product_df, orders_sellers_df

orders_product_df, orders_sellers_df = load_data()

# Convert date columns to datetime format
orders_sellers_df['order_purchase_timestamp'] = pd.to_datetime(orders_sellers_df['order_purchase_timestamp'])
orders_sellers_df['order_delivered_customer_date'] = pd.to_datetime(orders_sellers_df['order_delivered_customer_date'])
orders_sellers_df['order_estimated_delivery_date'] = pd.to_datetime(orders_sellers_df['order_estimated_delivery_date'])

# Sidebar filters
st.sidebar.header("Filter Options")

# Filter berdasarkan kategori produk
selected_category = st.sidebar.multiselect("Select Product Category", orders_product_df['product_category_name'].unique())
filtered_data = orders_product_df[orders_product_df['product_category_name'].isin(selected_category)] if selected_category else orders_product_df

# Filter berdasarkan rentang tanggal
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [])
if date_range:
    start_date, end_date = date_range if len(date_range) == 2 else (date_range[0], date_range[0])
    filtered_orders = orders_sellers_df[
        (orders_sellers_df['order_purchase_timestamp'] >= pd.Timestamp(start_date)) &
        (orders_sellers_df['order_purchase_timestamp'] <= pd.Timestamp(end_date))
    ]
else:
    filtered_orders = orders_sellers_df

# Filter berdasarkan seller
seller_options = filtered_orders['seller_id'].unique()
selected_seller = st.sidebar.selectbox("Pilih Seller", ['Semua'] + list(seller_options))
if selected_seller != 'Semua':
    filtered_orders = filtered_orders[filtered_orders['seller_id'] == selected_seller]

# Analisis Nilai Pesanan
st.subheader("Top Product Categories by Average Order Value")
avg_order_value = filtered_data.groupby('product_category_name')['price'].mean().reset_index()
avg_order_value = avg_order_value.sort_values(by='price', ascending=False).head(10)
fig1 = px.bar(avg_order_value, x='product_category_name', y='price', title='Top Categories by Average Order Value', labels={'price': 'Avg Order Value'})
st.plotly_chart(fig1)

# Analisis Keterlambatan Pengiriman
st.subheader("Delivery Delay Analysis")
filtered_orders['delay_days'] = (filtered_orders['order_delivered_customer_date'] - filtered_orders['order_estimated_delivery_date']).dt.days
fig2 = px.histogram(filtered_orders, x='delay_days', title='Distribution of Delivery Delays')
st.plotly_chart(fig2)

st.write("Data source: E-commerce orders dataset")
