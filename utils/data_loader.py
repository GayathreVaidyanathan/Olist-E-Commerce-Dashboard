import os
import pandas as pd
import streamlit as st

DATASET   = "olistbr/brazilian-ecommerce"
DATA_PATH = "data/"

def _download_if_needed():
    os.environ["KAGGLE_USERNAME"] = "YOUR_KAGGLE_USERNAME"  # your kaggle username
    os.environ["KAGGLE_KEY"]      = "YOUR_KAGGLE_KEY"  # the "key" value from kaggle.json
    
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH, exist_ok=True)
    marker = os.path.join(DATA_PATH, ".downloaded")
    if not os.path.exists(marker):
        import kaggle
        print("Downloading dataset from Kaggle...")
        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(DATASET, path=DATA_PATH, unzip=True)
        open(marker, "w").close()
        print("Download complete.")

def load_raw():
    _download_if_needed()
    orders = pd.read_csv(DATA_PATH + "olist_orders_dataset.csv", parse_dates=[
                "order_purchase_timestamp", "order_approved_at",
                "order_delivered_carrier_date", "order_delivered_customer_date",
                "order_estimated_delivery_date"])
    customers = pd.read_csv(DATA_PATH + "olist_customers_dataset.csv")
    items     = pd.read_csv(DATA_PATH + "olist_order_items_dataset.csv",
                            parse_dates=["shipping_limit_date"])
    payments  = pd.read_csv(DATA_PATH + "olist_order_payments_dataset.csv")
    reviews   = pd.read_csv(DATA_PATH + "olist_order_reviews_dataset.csv", parse_dates=[
                    "review_creation_date", "review_answer_timestamp"])
    products  = pd.read_csv(DATA_PATH + "olist_products_dataset.csv")
    sellers   = pd.read_csv(DATA_PATH + "olist_sellers_dataset.csv")
    geo       = pd.read_csv(DATA_PATH + "olist_geolocation_dataset.csv")
    cat_trans = pd.read_csv(DATA_PATH + "product_category_name_translation.csv")
    return orders, customers, items, payments, reviews, products, sellers, geo, cat_trans


def build_master(orders, customers, items, payments, reviews, products, sellers, cat_trans):
    products = products.merge(cat_trans, on="product_category_name", how="left")

    items_agg = items.groupby("order_id").agg(
        order_item_count     =("order_item_id",    "count"),
        order_products_value =("price",            "sum"),
        order_freight_value  =("freight_value",    "sum"),
        seller_id            =("seller_id",        "first")
    ).reset_index()

    payments_agg = payments.groupby("order_id").agg(
        payment_value        =("payment_value",       "sum"),
        payment_type         =("payment_type",        lambda x: x.mode()[0]),
        payment_installments =("payment_installments","max")
    ).reset_index()

    reviews_agg = reviews.groupby("order_id").agg(
        review_score=("review_score", "mean")
    ).reset_index()

    df = (orders
          .merge(customers,    on="customer_id",  how="left")
          .merge(items_agg,    on="order_id",     how="left")
          .merge(payments_agg, on="order_id",     how="left")
          .merge(reviews_agg,  on="order_id",     how="left")
          .merge(sellers,      on="seller_id",    how="left"))

    df["delivery_days_actual"]   = (df["order_delivered_customer_date"] -
                                    df["order_purchase_timestamp"]).dt.days
    df["delivery_days_promised"] = (df["order_estimated_delivery_date"] -
                                    df["order_purchase_timestamp"]).dt.days
    df["delivery_delay"]         = df["delivery_days_actual"] - df["delivery_days_promised"]
    df["is_late"]                = df["delivery_delay"] > 0
    df["order_month"]            = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    df["order_year"]             = df["order_purchase_timestamp"].dt.year
    return df


def build_rfm(df):
    snapshot = df["order_purchase_timestamp"].max()
    rfm = (df[df["order_status"] == "delivered"]
           .groupby("customer_unique_id")
           .agg(
               Recency  =("order_purchase_timestamp", lambda x: (snapshot - x.max()).days),
               Frequency=("order_id",                 "count"),
               Monetary =("payment_value",             "sum")
           ).reset_index())

    def safe_qcut(series, ascending=True):
        for q in [4, 3, 2]:
            try:
                base_labels = [4, 3, 2, 1] if ascending else [1, 2, 3, 4]
                labels = base_labels[:q]
                return pd.qcut(series, q=q, labels=labels, duplicates="drop").astype(int)
            except ValueError:
                continue
        if ascending:
            return series.rank(ascending=True,  pct=True).apply(lambda x: 4 - int(x * 3.99))
        else:
            return series.rank(ascending=False, pct=True).apply(lambda x: 4 - int(x * 3.99))

    rfm["R"] = safe_qcut(rfm["Recency"],   ascending=True)
    rfm["F"] = safe_qcut(rfm["Frequency"], ascending=False)
    rfm["M"] = safe_qcut(rfm["Monetary"],  ascending=False)

    rfm["RFM_Score"]   = rfm["R"] + rfm["F"] + rfm["M"]
    rfm["RFM_Segment"] = rfm["RFM_Score"].apply(
        lambda s: "Champions" if s >= 10 else
                  "Loyal"     if s >= 8  else
                  "At Risk"   if s >= 5  else "Lost"
    )
    return rfm


def build_seller_stats(df, items):
    seller_stats = (items.groupby("seller_id")
                    .agg(total_items_sold=("order_item_id", "count"),
                         total_revenue   =("price",         "sum"))
                    .reset_index())
    reviews_per_seller = (df.dropna(subset=["seller_id", "review_score"])
                          .groupby("seller_id")["review_score"].mean()
                          .reset_index()
                          .rename(columns={"review_score": "avg_rating"}))
    seller_stats = seller_stats.merge(reviews_per_seller, on="seller_id", how="left")
    return seller_stats


@st.cache_data
def get_all_data():
    orders, customers, items, payments, reviews, products, sellers, geo, cat_trans = load_raw()
    master       = build_master(orders, customers, items, payments, reviews, products, sellers, cat_trans)
    rfm          = build_rfm(master)
    seller_stats = build_seller_stats(master, items)
    return master, rfm, seller_stats, geo
