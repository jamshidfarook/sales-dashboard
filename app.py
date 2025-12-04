import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Global Sales Performance Dashboard",
    layout="wide"
)

# ---------------- MAIN TITLE ----------------
st.title("📊 Global Sales Performance Dashboard")
st.markdown("Executive-level analytics for sales performance, revenue, and trends.")

# ---------------- LOAD & CLEAN DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")

    # Clean column names
    df.columns = df.columns.str.strip()

    # Clean currency columns
    df["Unit_Price"] = df["Unit_Price"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False)
    df["Total_Sale"] = df["Total_Sale"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False)
    df["Sales_After_Discount"] = df["Sales_After_Discount"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False)

    df["Unit_Price"] = pd.to_numeric(df["Unit_Price"], errors="coerce")
    df["Total_Sale"] = pd.to_numeric(df["Total_Sale"], errors="coerce")
    df["Sales_After_Discount"] = pd.to_numeric(df["Sales_After_Discount"], errors="coerce")

    # Convert Date
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

    return df.dropna()

df = load_data()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("📁 Sales Data Filters")

start_date, end_date = st.sidebar.date_input(
    "Select Reporting Period",
    [df["Date"].min(), df["Date"].max()]
)

country_filter = st.sidebar.multiselect(
    "Select Country",
    df["Country"].unique()
)

product_filter = st.sidebar.multiselect(
    "Select Product",
    df["Product"].unique()
)

filtered_df = df.copy()

filtered_df = filtered_df[
    (filtered_df["Date"] >= pd.to_datetime(start_date)) &
    (filtered_df["Date"] <= pd.to_datetime(end_date))
]

if country_filter:
    filtered_df = filtered_df[filtered_df["Country"].isin(country_filter)]

if product_filter:
    filtered_df = filtered_df[filtered_df["Product"].isin(product_filter)]

# ---------------- KPI SUMMARY ----------------
st.subheader("📌 Executive Revenue Summary")

total_sales = filtered_df["Total_Sale"].sum()
total_after_discount = filtered_df["Sales_After_Discount"].sum()
total_units = filtered_df["Units_Sold"].sum()

col1, col2, col3 = st.columns(3)

col1.metric("💰 Gross Revenue", f"${total_sales:,.0f}")
col2.metric("🏷️ Net Revenue (After Discount)", f"${total_after_discount:,.0f}")
col3.metric("📦 Total Units Sold", f"{int(total_units):,}")

# ---------------- CHART 1: COUNTRY PERFORMANCE ----------------
st.subheader("🌍 Market Performance by Country")

country_sales = filtered_df.groupby("Country")["Sales_After_Discount"].sum().reset_index()

fig1 = px.bar(
    country_sales,
    x="Country",
    y="Sales_After_Discount",
    title="Net Revenue by Country"
)

st.plotly_chart(fig1, use_container_width=True)

# ---------------- CHART 2: PRODUCT PERFORMANCE ----------------
st.subheader("🛒 Product Revenue Contribution")

product_sales = filtered_df.groupby("Product")["Sales_After_Discount"].sum().reset_index()

fig2 = px.pie(
    product_sales,
    names="Product",
    values="Sales_After_Discount",
    title="Product Contribution to Total Revenue"
)

st.plotly_chart(fig2, use_container_width=True)

# ---------------- CHART 3: MONTHLY TREND ----------------
st.subheader("📈 Revenue Growth Trend")

filtered_df["Month"] = filtered_df["Date"].dt.to_period("M").astype(str)

monthly_sales = filtered_df.groupby("Month")["Sales_After_Discount"].sum().reset_index()

fig3 = px.line(
    monthly_sales,
    x="Month",
    y="Sales_After_Discount",
    markers=True,
    title="Monthly Net Revenue Trend"
)

st.plotly_chart(fig3, use_container_width=True)

# ---------------- DATA TABLE ----------------
st.subheader("📄 Detailed Sales Transaction View")
st.dataframe(filtered_df, use_container_width=True)

# ---------------- EXPORT OPTION ----------------
st.download_button(
    label="⬇️ Export Filtered Sales Report",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_sales_report.csv",
    mime="text/csv"
)
