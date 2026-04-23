import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import get_all_data

st.set_page_config(page_title="Sales Analytics", page_icon="💰", layout="wide")

master, rfm, seller_stats, geo = get_all_data()
delivered = master[master["order_status"] == "delivered"].copy()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("💰 Sales Analytics")
years = sorted(delivered["order_year"].dropna().unique().astype(int))
selected_years = st.sidebar.multiselect("Filter by year", years, default=years)
filtered = delivered[delivered["order_year"].isin(selected_years)]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("💰 Sales Analytics")
st.caption("Revenue trends, category performance and order patterns")
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total GMV",       f"R$ {filtered['payment_value'].sum():,.0f}")
k2.metric("Total Orders",    f"{filtered['order_id'].nunique():,}")
k3.metric("Avg Order Value", f"R$ {filtered['payment_value'].mean():,.2f}")
k4.metric("Avg Items/Order", f"{filtered['order_item_count'].mean():.2f}")
st.divider()

# ── Monthly GMV + Order Volume ────────────────────────────────────────────────
st.subheader("Monthly GMV vs Order Volume")
monthly = (filtered.groupby("order_month")
           .agg(GMV=("payment_value", "sum"), Orders=("order_id", "count"))
           .reset_index().sort_values("order_month"))

fig = px.bar(
    monthly, x="order_month", y="GMV",
    labels={"order_month": "Month", "GMV": "Revenue (R$)"},
    color_discrete_sequence=["#7F77DD"]
)
fig.add_scatter(
    x=monthly["order_month"], y=monthly["Orders"],
    mode="lines+markers", name="Orders",
    yaxis="y2", line=dict(color="#1D9E75", width=2),
    marker=dict(size=5)
)
fig.update_layout(
    yaxis2=dict(overlaying="y", side="right", showgrid=False, title="Order Count"),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor="rgba(128,128,128,0.15)", title="Revenue (R$)"),
    hovermode="x unified",
    legend=dict(orientation="h", y=1.1),
    margin=dict(l=0, r=0, t=30, b=0)
)
st.plotly_chart(fig, use_container_width=True)

# ── Top Categories + Avg Order Value by Category ──────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Categories by Revenue")
    # join items with products for category names
    from utils.data_loader import load_raw
    _, _, items, _, _, products, _, _, cat_trans = load_raw()
    products = products.merge(cat_trans, on="product_category_name", how="left")
    items_cat = items.merge(products[["product_id", "product_category_name_english"]],
                            on="product_id", how="left")
    items_cat = items_cat[items_cat["order_id"].isin(filtered["order_id"])]
    cat_rev = (items_cat.groupby("product_category_name_english")["price"]
               .sum().reset_index()
               .rename(columns={"product_category_name_english": "Category",
                                 "price": "Revenue"})
               .sort_values("Revenue", ascending=False).head(10))

    fig2 = px.bar(
        cat_rev, x="Revenue", y="Category", orientation="h",
        color="Revenue", color_continuous_scale="Purples"
    )
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Orders by Day of Week")
    filtered["day_of_week"] = pd.to_datetime(
        filtered["order_purchase_timestamp"]).dt.day_name()
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dow = (filtered.groupby("day_of_week")["order_id"]
           .count().reindex(day_order).reset_index())
    dow.columns = ["Day", "Orders"]

    fig3 = px.bar(
        dow, x="Day", y="Orders",
        color="Orders", color_continuous_scale="Teal"
    )
    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── Installments Distribution ─────────────────────────────────────────────────
st.subheader("Payment Installments Distribution")
inst = (filtered["payment_installments"]
        .value_counts().reset_index()
        .rename(columns={"payment_installments": "Installments", "count": "Orders"})
        .sort_values("Installments").head(12))

fig4 = px.bar(
    inst, x="Installments", y="Orders",
    color_discrete_sequence=["#1D9E75"]
)
fig4.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(dtick=1),
    margin=dict(l=0, r=0, t=10, b=0)
)
st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.caption("Data source: Olist Brazilian E-Commerce Public Dataset · Kaggle")