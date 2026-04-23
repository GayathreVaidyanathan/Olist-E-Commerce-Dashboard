import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import get_all_data

st.set_page_config(page_title="Logistics Analytics", page_icon="🚚", layout="wide")

master, rfm, seller_stats, geo = get_all_data()
delivered = master[master["order_status"] == "delivered"].copy()
delivered = delivered.dropna(subset=["delivery_days_actual", "delivery_days_promised"])

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🚚 Logistics Analytics")
years = sorted(delivered["order_year"].dropna().unique().astype(int))
selected_years = st.sidebar.multiselect("Filter by year", years, default=years)
filtered = delivered[delivered["order_year"].isin(selected_years)]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🚚 Logistics Analytics")
st.caption("Delivery performance, delays and regional shipping patterns")
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Avg Actual Delivery",   f"{filtered['delivery_days_actual'].mean():.1f} days")
k2.metric("Avg Promised Delivery", f"{filtered['delivery_days_promised'].mean():.1f} days")
k3.metric("Late Orders",           f"{filtered['is_late'].mean() * 100:.1f}%")
k4.metric("Avg Delay (late only)", f"{filtered[filtered['is_late']]['delivery_delay'].mean():.1f} days")
st.divider()

# ── Promised vs Actual Delivery ───────────────────────────────────────────────
st.subheader("Promised vs Actual Delivery Days Distribution")
col1, col2 = st.columns(2)

with col1:
    fig1 = px.histogram(
        filtered, x="delivery_days_actual",
        nbins=50, color_discrete_sequence=["#7F77DD"],
        labels={"delivery_days_actual": "Actual Delivery Days"}
    )
    fig1.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
        yaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.histogram(
        filtered, x="delivery_delay",
        nbins=50, color_discrete_sequence=["#E24B4A"],
        labels={"delivery_delay": "Delivery Delay (days, negative = early)"}
    )
    fig2.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.7)
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
        yaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Late Orders by State ──────────────────────────────────────────────────────
st.subheader("Delivery Performance by State")
state_delivery = (filtered.groupby("customer_state")
                  .agg(
                      Avg_Actual   =("delivery_days_actual",   "mean"),
                      Avg_Promised =("delivery_days_promised", "mean"),
                      Late_Rate    =("is_late",                "mean"),
                      Orders       =("order_id",               "count")
                  ).reset_index().round(2))
state_delivery["Late_Rate_%"] = (state_delivery["Late_Rate"] * 100).round(1)
state_delivery = state_delivery.sort_values("Late_Rate_%", ascending=False)

col3, col4 = st.columns(2)

with col3:
    fig3 = px.bar(
        state_delivery.head(15),
        x="Late_Rate_%", y="customer_state", orientation="h",
        color="Late_Rate_%", color_continuous_scale="Reds",
        labels={"customer_state": "State", "Late_Rate_%": "Late Order Rate (%)"}
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
        state_delivery.sort_values("Avg_Actual", ascending=False).head(15),
        x="Avg_Actual", y="customer_state", orientation="h",
        color="Avg_Actual", color_continuous_scale="Oranges",
        labels={"customer_state": "State", "Avg_Actual": "Avg Delivery Days"}
    )
    fig4.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig4, use_container_width=True)

# ── State Summary Table ───────────────────────────────────────────────────────
st.subheader("Full State Delivery Summary")
display_cols = state_delivery[["customer_state","Orders","Avg_Actual",
                                "Avg_Promised","Late_Rate_%"]].copy()
display_cols.columns = ["State","Orders","Avg Actual (days)",
                         "Avg Promised (days)","Late Rate (%)"]
st.dataframe(display_cols, use_container_width=True, hide_index=True)

st.divider()

# ── Monthly Late Rate Trend ───────────────────────────────────────────────────
st.subheader("Monthly Late Order Rate Trend")
monthly_late = (filtered.groupby("order_month")
                .agg(Late_Rate=("is_late", "mean"))
                .reset_index().sort_values("order_month"))
monthly_late["Late_Rate_%"] = (monthly_late["Late_Rate"] * 100).round(2)

fig5 = px.line(
    monthly_late, x="order_month", y="Late_Rate_%",
    markers=True, color_discrete_sequence=["#E24B4A"],
    labels={"order_month": "Month", "Late_Rate_%": "Late Order Rate (%)"}
)
fig5.add_hline(
    y=monthly_late["Late_Rate_%"].mean(),
    line_dash="dash", line_color="gray",
    annotation_text="Average", opacity=0.7
)
fig5.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
    hovermode="x unified",
    margin=dict(l=0, r=0, t=10, b=0)
)
st.plotly_chart(fig5, use_container_width=True)

st.divider()
st.caption("Data source: Olist Brazilian E-Commerce Public Dataset · Kaggle")