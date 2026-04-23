import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import get_all_data

st.set_page_config(page_title="Customer Analytics", page_icon="👥", layout="wide")

master, rfm, seller_stats, geo = get_all_data()
delivered = master[master["order_status"] == "delivered"].copy()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("👥 Customer Analytics")
years = sorted(delivered["order_year"].dropna().unique().astype(int))
selected_years = st.sidebar.multiselect("Filter by year", years, default=years)
filtered = delivered[delivered["order_year"].isin(selected_years)]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("👥 Customer Analytics")
st.caption("RFM segmentation, retention patterns and geographic distribution")
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Unique Customers",   f"{filtered['customer_unique_id'].nunique():,}")
k2.metric("Avg Review Score",   f"{filtered['review_score'].mean():.2f} ⭐")
k3.metric("Repeat Purchase Rate", f"{(filtered.groupby('customer_unique_id')['order_id'].count() > 1).mean() * 100:.1f}%")
k4.metric("Avg Monetary Value", f"R$ {rfm['Monetary'].mean():,.2f}")
st.divider()

# ── RFM Segment Distribution ──────────────────────────────────────────────────
st.subheader("RFM Customer Segments")
col1, col2 = st.columns(2)

with col1:
    seg_counts = rfm["RFM_Segment"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Count"]
    color_map = {
        "Champions": "#7F77DD",
        "Loyal":     "#1D9E75",
        "At Risk":   "#EF9F27",
        "Lost":      "#E24B4A"
    }
    fig1 = px.pie(
        seg_counts, names="Segment", values="Count",
        hole=0.45, color="Segment", color_discrete_map=color_map
    )
    fig1.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    seg_stats = rfm.groupby("RFM_Segment").agg(
        Customers =("customer_unique_id", "count"),
        Avg_Monetary=("Monetary", "mean"),
        Avg_Frequency=("Frequency", "mean"),
        Avg_Recency=("Recency", "mean")
    ).reset_index().round(2)
    seg_stats.columns = ["Segment","Customers","Avg Spend (R$)","Avg Orders","Avg Recency (days)"]
    st.dataframe(seg_stats, use_container_width=True, hide_index=True)

    st.markdown("**Segment definitions**")
    st.markdown("""
    - 🏆 **Champions** — bought recently, buy often, spend the most  
    - 💚 **Loyal** — regular buyers with good spend  
    - ⚠️ **At Risk** — used to buy but haven't recently  
    - ❌ **Lost** — lowest recency, frequency and spend  
    """)

st.divider()

# ── RFM Scatter ───────────────────────────────────────────────────────────────
st.subheader("Recency vs Monetary Value by Segment")
fig2 = px.scatter(
    rfm.sample(min(5000, len(rfm)), random_state=42),
    x="Recency", y="Monetary",
    color="RFM_Segment", size="Frequency",
    color_discrete_map=color_map,
    labels={"Recency": "Recency (days)", "Monetary": "Total Spend (R$)"},
    opacity=0.6
)
fig2.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
    yaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
    margin=dict(l=0, r=0, t=10, b=0)
)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Geographic Distribution ───────────────────────────────────────────────────
st.subheader("Orders by State")
state_orders = (filtered.groupby("customer_state")
                .agg(Orders=("order_id", "count"),
                     Avg_Spend=("payment_value", "mean"))
                .reset_index().sort_values("Orders", ascending=False))

col3, col4 = st.columns(2)

with col3:
    fig3 = px.bar(
        state_orders.head(15),
        x="Orders", y="customer_state", orientation="h",
        color="Orders", color_continuous_scale="Purples",
        labels={"customer_state": "State"}
    )
    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    fig4 = px.bar(
        state_orders.head(15),
        x="Avg_Spend", y="customer_state", orientation="h",
        color="Avg_Spend", color_continuous_scale="Teal",
        labels={"customer_state": "State", "Avg_Spend": "Avg Spend (R$)"}
    )
    fig4.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig4, use_container_width=True)

# ── Review Score Distribution ─────────────────────────────────────────────────
st.divider()
st.subheader("Review Score Distribution")
review_counts = (filtered["review_score"].dropna()
                 .value_counts().reset_index()
                 .rename(columns={"review_score": "Score", "count": "Count"})
                 .sort_values("Score"))

fig5 = px.bar(
    review_counts, x="Score", y="Count",
    color="Score",
    color_continuous_scale=["#E24B4A","#EF9F27","#EF9F27","#1D9E75","#7F77DD"],
    labels={"Score": "Review Score (1-5)"}
)
fig5.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    coloraxis_showscale=False,
    xaxis=dict(dtick=1),
    margin=dict(l=0, r=0, t=10, b=0)
)
st.plotly_chart(fig5, use_container_width=True)

st.divider()
st.caption("Data source: Olist Brazilian E-Commerce Public Dataset · Kaggle")