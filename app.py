import streamlit as st
from utils.data_loader import get_all_data
import plotly.express as px

st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

master, rfm, seller_stats, geo = get_all_data()
delivered = master[master["order_status"] == "delivered"].copy()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🛒 Olist Dashboard")
st.sidebar.markdown("Brazilian E-Commerce · 2016–2018")
years = sorted(master["order_year"].dropna().unique().astype(int))
selected_years = st.sidebar.multiselect("Filter by year", years, default=years)
filtered = delivered[delivered["order_year"].isin(selected_years)]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📊 Executive Overview")
st.caption("Olist Brazilian E-Commerce · 2016–2018 · 99k orders")
st.divider()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total GMV",         f"R$ {filtered['payment_value'].sum():,.0f}")
k2.metric("Total Orders",      f"{filtered['order_id'].nunique():,}")
k3.metric("Unique Customers",  f"{filtered['customer_unique_id'].nunique():,}")
k4.metric("Avg Review Score",  f"{filtered['review_score'].mean():.2f} ⭐")
k5.metric("Avg Delivery Days", f"{filtered['delivery_days_actual'].mean():.1f} days")
st.divider()

# ── Revenue Trend ─────────────────────────────────────────────────────────────
st.subheader("Monthly Revenue Trend")
monthly = (filtered.groupby("order_month")
           .agg(GMV=("payment_value", "sum"), Orders=("order_id", "count"))
           .reset_index()
           .sort_values("order_month"))

fig = px.area(
    monthly, x="order_month", y="GMV",
    labels={"order_month": "Month", "GMV": "Revenue (R$)"},
    color_discrete_sequence=["#7F77DD"]
)
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
    hovermode="x unified",
    margin=dict(l=0, r=0, t=10, b=0)
)
st.plotly_chart(fig, use_container_width=True)

# ── Order Status + Payment Split ──────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Order Status Mix")
    status_counts = master["order_status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    fig2 = px.pie(
        status_counts, names="Status", values="Count",
        hole=0.45, color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0),
                       paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Payment Method Split")
    pay_counts = filtered["payment_type"].value_counts().reset_index()
    pay_counts.columns = ["Payment Type", "Count"]
    fig3 = px.bar(
        pay_counts, x="Payment Type", y="Count",
        color="Payment Type",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig3.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.caption("Data source: Olist Brazilian E-Commerce Public Dataset · Kaggle")