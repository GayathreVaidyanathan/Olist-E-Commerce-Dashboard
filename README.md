# 🛒 Olist E-Commerce Dashboard

An end-to-end interactive business intelligence dashboard built on the **Brazilian E-Commerce Public Dataset** by Olist. Built with Python, Streamlit and Plotly.

🔗 **[Live Demo]([your-streamlit-url-here](https://olist-e-commerce-dashboard-sutwe6djkp3iu9lz74dxxl.streamlit.app/))**·
📦 **[Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)**

---

## 📊 Dashboard Pages

### 🏠 Executive Overview
- Total GMV, Orders, Customers, Avg Review Score, Avg Delivery Days
- Monthly revenue trend (area chart)
- Order status mix and payment method breakdown
- Year filter across all KPIs

### 💰 Sales Analytics
- Monthly GMV vs Order Volume (dual-axis chart)
- Top 10 product categories by revenue
- Orders by day of week
- Payment installments distribution

### 👥 Customer Analytics
- RFM segmentation (Champions / Loyal / At Risk / Lost)
- Recency vs Monetary scatter plot by segment
- Orders and avg spend by Brazilian state
- Review score distribution

### 🏪 Seller Analytics
- Top 20 sellers leaderboard
- Revenue vs Rating quadrant plot (Star / High Revenue Low Rating / Low Revenue High Rating / Underperformer)
- Seller distribution by state

### 🚚 Logistics Analytics
- Actual vs promised delivery day distributions
- Delivery delay histogram
- Late order rate by state
- Avg delivery days by state
- Monthly late order rate trend

---

## 🗂️ Project Structure

```
olist-dashboard/
├── app.py                  # Home page — Executive Overview
├── pages/
│   ├── 1_Sales.py
│   ├── 2_Customers.py
│   ├── 3_Sellers.py
│   └── 4_Logistics.py
├── utils/
│   ├── __init__.py
│   └── data_loader.py      # Data pipeline — downloads, merges, feature engineering
├── requirements.txt
└── README.md
```

---

## ⚙️ Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Core language |
| Streamlit | Dashboard framework |
| Pandas | Data wrangling and feature engineering |
| Plotly | Interactive charts |
| Kaggle API | Automated dataset download |
| Matplotlib | Dataframe styling |

---

## 🚀 Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/your-username/olist-dashboard.git
cd olist-dashboard
```

**2. Create and activate virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up Kaggle credentials**

Get your `kaggle.json` from [kaggle.com/settings](https://www.kaggle.com/settings) → API → Create New Token.

Place it at:
- Windows: `C:\Users\<you>\.kaggle\kaggle.json`
- Mac/Linux: `~/.kaggle/kaggle.json`

**5. Run the dashboard**
```bash
streamlit run app.py
```

The dataset will be downloaded automatically on first run (~50MB). The app will open at `http://localhost:8501`.

---

## 📐 Data Pipeline

The `utils/data_loader.py` module handles the full pipeline:

- **Download** — Kaggle API pulls all 9 CSVs on first run, caches locally
- **Merge** — Orders joined with customers, items, payments, reviews and sellers
- **Feature engineering** — Delivery delay, late flag, order month/year
- **RFM scoring** — Recency, Frequency, Monetary quartile scoring with segment labels
- **Seller stats** — Revenue, items sold and avg rating per seller
- **Caching** — `@st.cache_data` ensures data loads once per session

---

## 📁 Dataset

**Brazilian E-Commerce Public Dataset by Olist** · [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)**

| File | Description |
|---|---|
| olist_orders_dataset.csv | Order lifecycle and timestamps |
| olist_customers_dataset.csv | Customer location data |
| olist_order_items_dataset.csv | Items, prices, freight per order |
| olist_order_payments_dataset.csv | Payment type and installments |
| olist_order_reviews_dataset.csv | Review scores and comments |
| olist_products_dataset.csv | Product dimensions and category |
| olist_sellers_dataset.csv | Seller location data |
| olist_geolocation_dataset.csv | Zip code to lat/lng mapping |
| product_category_name_translation.csv | Portuguese to English category names |

> 99,441 orders · 3,095 sellers · 96,478 delivered orders · 2016–2018

---

## 🙋 Author

**Gayathre Vaidyanathan**  
Integrated M.Sc. Data Science · Amrita Vishwa Vidyapeetham  
[GitHub](https://github.com/GayathreVaidyanathan) · [LinkedIn](https://www.linkedin.com/in/gayathre-vaidyanathan-567b4a30a/) ·
[Kaggle](https://kaggle.com/gayathrevaidya)

---

*Built as part of final year portfolio project · 2026*
