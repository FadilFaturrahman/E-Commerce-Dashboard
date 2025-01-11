import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

class EcommerceDashboard:
    def __init__(self, df):
        self.df = df

    def create_sum_order_items_df(self):
        sum_order_items_df = self.df.groupby("product_category_name_english")["product_id"].count().reset_index()
        sum_order_items_df.rename(columns={"product_id": "products"}, inplace=True)
        sum_order_items_df = sum_order_items_df.sort_values(by='products', ascending=False)
        return sum_order_items_df

    def review_score_df(self):
        review_scores = self.df['review_score'].value_counts().sort_index()
        most_common_score = review_scores.idxmax()
        return review_scores, most_common_score

    def create_daily_orders_df(self):
        daily_orders_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "order_id": "nunique",
            "payment_value": "sum"
        }).reset_index()
        daily_orders_df.rename(columns={"order_id": "order_count", "payment_value": "revenue"}, inplace=True)
        return daily_orders_df

    def create_city_df(self):
        city_df = self.df.groupby("customer_city")["customer_id"].nunique().reset_index()
        city_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
        most_common_city = city_df.loc[city_df['customer_count'].idxmax(), 'customer_city']
        city_df = city_df.sort_values(by='customer_count', ascending=False)
        return city_df, most_common_city

    def payment_methods_df(self):
        payment_methods = self.df['payment_type'].value_counts().sort_values(ascending=False)
        most_common_payment = payment_methods.idxmax()
        return payment_methods, most_common_payment


# Dataset
all_df = pd.read_csv("dashboard/all_data0.csv")
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

dashboard = EcommerceDashboard(all_df)

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:

    # Title
    st.title("DICODING X Scothstore")
    
    # Logo Image
    st.image("dashboard/logo.png")

    # Date Range
    start_date, end_date = st.date_input(
        label="Pilih Tanggal",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Filter data based on selected date range
filtered_df = all_df[(all_df["order_approved_at"] >= pd.Timestamp(start_date)) & (all_df["order_approved_at"] <= pd.Timestamp(end_date))]

# Process data
dashboard_filtered = EcommerceDashboard(filtered_df)
sum_order_items_df = dashboard_filtered.create_sum_order_items_df()
review_score, common_score = dashboard_filtered.review_score_df()
daily_orders_df = dashboard_filtered.create_daily_orders_df()
city_df, most_common_city = dashboard_filtered.create_city_df()
payment_methods, common_payment = dashboard_filtered.payment_methods_df()

# Main Page
st.header("E-Commerce Dashboard")

# Tabs for different sections
tabs = st.selectbox('Select a section:', ['Order Items', 'Review Score', 'Total Revenue', 'Customer by City', 'Payment Methods'])

if tabs == 'Order Items':
    st.subheader("Order Items")
    col1, col2 = st.columns(2)

    with col1:
        total_items = sum_order_items_df["products"].sum()
        st.markdown(f"Total Items: **{total_items}**")

    with col2:
        avg_items = sum_order_items_df["products"].mean()
        st.markdown(f"Average Items: **{avg_items}**")

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

    colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(x="products", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Number of Sales", fontsize=30)
    ax[0].set_title("Produk paling banyak terjual", loc="center", fontsize=50)
    ax[0].tick_params(axis ='y', labelsize=35)
    ax[0].tick_params(axis ='x', labelsize=30)

    sns.barplot(x="products", y="product_category_name_english", data=sum_order_items_df.sort_values(by="products", ascending=True).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Number of Sales", fontsize=30)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Produk paling sedikit terjual", loc="center", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=35)
    ax[1].tick_params(axis='x', labelsize=30)

    st.pyplot(fig)

elif tabs == 'Review Score':
    st.subheader("Review Score")
    col1,col2 = st.columns(2)

    with col1:
        avg_review_score = review_score.mean()
        st.markdown(f"Average Review Score: **{avg_review_score}**")

    with col2:
        most_common_review_score = review_score.value_counts().index[0]
        st.markdown(f"Most Common Review Score: **{most_common_review_score}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=review_score.index, 
                y=review_score.values, 
                order=review_score.index,
                palette=["#068DA9" if score == common_score else "#D3D3D3" for score in review_score.index]
                )

    plt.title("Rating by customers", fontsize=15)
    plt.xlabel("Rating")
    plt.ylabel("Count")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

elif tabs == 'Total Revenue':
    st.subheader("Total Revenue")

    # Membuat kolom untuk menampilkan informasi
    col1, col2 = st.columns(2)

    with col1:
        total_revenue = daily_orders_df["revenue"].sum()
        st.markdown(f"Total Revenue: **{format_currency(total_revenue, 'IDR', locale='id_ID')}**")

    with col2:
        total_order = daily_orders_df["order_count"].sum()
        st.markdown(f"Total Orders: **{total_order}**")

    # Plotting total revenue by date
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        daily_orders_df["order_approved_at"],
        daily_orders_df["revenue"],
        marker="o",
        linewidth=2,
        color="#90CAF9"
    )
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", labelsize=15)
    ax.set_title("Total Revenue per Day", fontsize=15)
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Revenue (IDR)")

    # Menampilkan grafik
    st.pyplot(fig)

elif tabs == 'Customer by City':
    st.subheader("Customer By City")

    # Menghitung jumlah pelanggan per kota
    city_df = filtered_df['customer_city'].value_counts().head(10)
    most_common_city = city_df.idxmax()

    # Menetapkan label 'Most Common' dan 'Others'
    hue_values = ["Most Common" if city == most_common_city else "Others" for city in city_df.index]

    # Membuat kolom untuk menampilkan informasi kota
    col1, col2 = st.columns(2)

    with col1:
        total_customers = city_df.sum()
        st.markdown(f"Total Customers: **{total_customers}**")

    with col2:
        most_common_city_customers = city_df[most_common_city]
        st.markdown(f"Customers in {most_common_city}: **{most_common_city_customers}**")

    # Plotting Bar Chart for Customer Distribution by City
    fig, ax = plt.subplots(figsize=(12, 6))

    city_df = city_df.sort_values(ascending=False)

    sns.barplot(
        x=city_df.index,
        y=city_df.values,
        hue=hue_values,
        dodge=False,  # Tidak ada pergeseran
        palette={"Most Common": "#068DA9", "Others": "#D3D3D3"},
        ax=ax
    )

    ax.set_title("Customer by City", fontsize=15)
    ax.set_xlabel("City")
    ax.set_ylabel("Number of Customers")
    ax.tick_params(axis="x", rotation=45, labelsize=10)

    # Menampilkan grafik
    st.pyplot(fig)

elif tabs == 'Payment Methods':
    st.subheader("Most Frequently Used Payment Methods")

    # Membuat kolom untuk menampilkan informasi
    col1, col2 = st.columns(2)

    with col1:
        # Memanggil metode payment_methods_df untuk mendapatkan data
        payment_methods, most_common_payment = dashboard_filtered.payment_methods_df()
        st.markdown(f"Most Common Payment Method: **{most_common_payment}**")

    with col2:
        st.markdown(f"Total Payment Methods: **{len(payment_methods)}**")

    # Plotting payment methods
    fig, ax = plt.subplots(figsize=(12, 6))

    hue_values = ["Most Common" if payment == most_common_payment else "Others" for payment in payment_methods.index]

    sns.barplot(
        x=payment_methods.index,
        y=payment_methods.values,
        hue=hue_values,
        dodge=False,  # Tidak ada pergeseran
        palette={"Most Common": "#068DA9", "Others": "#D3D3D3"},
        ax=ax
    )

    ax.set_title("Most Frequently Used Payment Methods", fontsize=15)
    ax.set_xlabel("Payment Method")
    ax.set_ylabel("Number of Transactions")
    ax.tick_params(axis="x", rotation=45, labelsize=10)
    ax.legend(title="", fontsize=10)

    # Menampilkan grafik
    st.pyplot(fig)

st.caption('Copyright (C) Muhammad Fadil Faturrahman 2024')
