import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import get_all_data

st.set_page_config(page_title="Seller Analytics", page_icon="🏪", layout="wide")

master, rfm, seller_stats, geo = get_all_data()
delivered = master[master["order_status"] == "delivered"].copy()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🏪 Seller Analytics")
years = sorted(delivered["order_year"].dropna().unique().astype(int))
selected_years = st.sidebar.multiselect("Filter by year", years, default=years)
filtered = delivered[delivered["order_year"].isin(selected_years)]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏪 Seller Analytics")
st.caption("Seller performance, revenue distribution and ratings")
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sellers",       f"{filtered['seller_id'].nunique():,}")
k2.metric("Avg Revenue/Seller",  f"R$ {seller_stats['total_revenue'].mean():,.2f}")
k3.metric("Avg Rating",          f"{seller_stats['avg_rating'].mean():.2f} ⭐")
k4.metric("Avg Items Sold",      f"{seller_stats['total_items_sold'].mean():,.1f}")
st.divider()

# ── Top Sellers Table ─────────────────────────────────────────────────────────
st.subheader("Top 20 Sellers by Revenue")

# filter seller_stats to only orders in selected years
filtered_seller_ids = filtered["seller_id"].dropna().unique()
filtered_seller_stats = seller_stats[seller_stats["seller_id"].isin(filtered_seller_ids)].copy()

top_sellers = (filtered_seller_stats
               .sort_values("total_revenue", ascending=False)
               .head(20)
               .reset_index(drop=True))
top_sellers.index += 1
top_sellers.columns = ["Seller ID", "Items Sold", "Revenue (R$)", "Avg Rating"]
top_sellers["Revenue (R$)"] = top_sellers["Revenue (R$)"].round(2)
top_sellers["Avg Rating"]   = top_sellers["Avg Rating"].round(2)
top_sellers["Seller ID"]    = top_sellers["Seller ID"].str[:8] + "..."  # truncate for display

st.dataframe(
    top_sellers.style.background_gradient(subset=["Revenue (R$)"], cmap="Purples")
                     .background_gradient(subset=["Avg Rating"],   cmap="Greens"),
    use_container_width=True
)
st.divider()

# ── Revenue vs Rating Quadrant ────────────────────────────────────────────────
st.subheader("Revenue vs Rating — Seller Quadrant")
st.caption("Each dot is a seller · size = items sold · use this to identify high-value and at-risk sellers")

quad_data = filtered_seller_stats.dropna(subset=["avg_rating"]).copy()
med_rev    = quad_data["total_revenue"].median()
med_rating = quad_data["avg_rating"].median()

def quadrant(row):
    if row["total_revenue"] >= med_rev and row["avg_rating"] >= med_rating:
        return "⭐ Star"
    elif row["total_revenue"] >= med_rev and row["avg_rating"] < med_rating:
        return "⚠️ High Revenue, Low Rating"
    elif row["total_revenue"] < med_rev and row["avg_rating"] >= med_rating:
        return "🌱 Low Revenue, High Rating"
    else:
        return "❌ Underperformer"

quad_data["Quadrant"] = quad_data.apply(quadrant, axis=1)

color_map = {
    "⭐ Star":                    "#7F77DD",
    "⚠️ High Revenue, Low Rating": "#EF9F27",
    "🌱 Low Revenue, High Rating":  "#1D9E75",
    "❌ Underperformer":            "#E24B4A"
}

fig1 = px.scatter(
    quad_data.sample(min(1000, len(quad_data)), random_state=42),
    x="avg_rating", y="total_revenue",
    color="Quadrant", size="total_items_sold",
    color_discrete_map=color_map,
    labels={"avg_rating": "Avg Rating", "total_revenue": "Total Revenue (R$)",
            "total_items_sold": "Items Sold"},
    opacity=0.7
)
fig1.add_vline(x=med_rating, line_dash="dash", line_color="gray", opacity=0.5)
fig1.add_hline(y=med_rev,    line_dash="dash", line_color="gray", opacity=0.5)
fig1.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
    yaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
    margin=dict(l=0, r=0, t=10, b=0)
)
st.plotly_chart(fig1, use_container_width=True)

# ── Quadrant Summary ──────────────────────────────────────────────────────────
quad_summary = (quad_data.groupby("Quadrant")
                .agg(Sellers=("seller_id","count"),
                     Avg_Revenue=("total_revenue","mean"),
                     Avg_Rating=("avg_rating","mean"))
                .reset_index().round(2))
quad_summary.columns = ["Quadrant","Sellers","Avg Revenue (R$)","Avg Rating"]
st.dataframe(quad_summary, use_container_width=True, hide_index=True)
st.divider()

# ── Sellers by State ──────────────────────────────────────────────────────────
st.subheader("Seller Distribution by State")
state_sellers = (filtered.dropna(subset=["seller_state"])
                 .groupby("seller_state")
                 .agg(Sellers=("seller_id","nunique"),
                      Revenue=("payment_value","sum"))
                 .reset_index().sort_values("Sellers", ascending=False))

col1, col2 = st.columns(2)

with col1:
    fig2 = px.bar(
        state_sellers.head(15),
        x="Sellers", y="seller_state", orientation="h",
        color="Sellers", color_continuous_scale="Purples",
        labels={"seller_state": "State"}
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
    fig3 = px.bar(
        state_sellers.head(15),
        x="Revenue", y="seller_state", orientation="h",
        color="Revenue", color_continuous_scale="Teal",
        labels={"seller_state": "State", "Revenue": "Revenue (R$)"}
    )
    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.caption("Data source: Olist Brazilian E-Commerce Public Dataset · Kaggle")