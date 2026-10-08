# 🤖 AI Business Intelligence

### AI-Powered Retail Analytics & Business Intelligence Platform

An interactive Business Intelligence platform that transforms retail transaction data into meaningful business insights using **Data Analytics, Machine Learning, Forecasting, and Recommendation Systems**.

---

## 🚀 Live Demo

👉 **[Open the Live Dashboard](https://ai-business-intelligence-prafulla.streamlit.app/)**

> No installation or download required. Open the link and explore the dashboard directly in your browser.

---

## 📌 Project Overview

Businesses generate large amounts of transaction data, but raw data alone does not provide actionable insights.

This project converts retail transaction data into an interactive dashboard that helps businesses understand:

- 📊 Sales performance
- 👥 Customer behavior
- 🛍️ Product performance
- 🔮 Future sales trends
- 🎯 Customer segments
- 🤝 Product relationships
- 💡 Business opportunities

The platform combines **Python, Data Analytics, Machine Learning, and Streamlit** to create an end-to-end Business Intelligence solution.

---

# ✨ Key Features

## 📊 Sales Analytics

Analyze important business KPIs and sales trends:

- Total Revenue
- Total Orders
- Total Customers
- Total Products
- Monthly Revenue
- Country-wise Sales
- Top Products
- Top Customers

---

## 👥 Customer Segmentation

Customers are analyzed using **RFM-style behavioral metrics**:

- Recency
- Frequency
- Monetary Value

Machine Learning is then used to group customers into meaningful business segments:

| Segment | Business Meaning |
|---|---|
| 🏆 VIP / Loyal Customers | Highly valuable and frequent customers |
| 💎 Potential High Value | Customers with strong growth potential |
| 👤 Regular Customers | Normal recurring customers |
| ⚠️ At Risk / Inactive | Customers who may require re-engagement |

### Machine Learning Algorithm

**K-Means Clustering**

---

# 🔮 Sales Forecasting

The platform analyzes historical monthly revenue and generates future sales forecasts.

The forecasting module provides:

- Historical revenue trends
- Future revenue predictions
- Expected revenue
- Average monthly forecast
- Forecast visualization
- Model performance metrics

### Current Model Performance

| Metric | Value |
|---|---:|
| MAE | £152,357.90 |
| RMSE | £188,093.39 |

### Example Forecast

| Month | Forecast Revenue |
|---|---:|
| January 2012 | £875,191.72 |
| February 2012 | £762,275.41 |
| March 2012 | £677,489.54 |

---

# 🛍️ Product Recommendation Engine

The recommendation engine identifies useful product relationships and customer-specific opportunities.

### Includes:

- 🤝 Frequently Bought Together
- 👤 Personalized Customer Recommendations
- 🎯 Segment-based Product Strategies
- 🛒 Cross-selling Opportunities
- 📦 Product Promotion Strategies

The system can recommend products based on customer behavior and purchasing patterns.

---

# 🤖 AI Business Insight Engine

The dashboard automatically generates business insights from the analyzed data.

Examples include:

- High-performing products
- Customer opportunities
- At-risk customer strategies
- Revenue trends
- Product promotion opportunities
- Cross-selling opportunities

The current insight engine uses **data-driven business rules and analytics** to generate actionable recommendations.

---

# 🌍 Interactive Dashboard

The Streamlit dashboard provides:

- 📊 Interactive Plotly charts
- 🌍 Country filters
- 📅 Date filters
- 💱 Multi-currency support
- 👤 Customer ID lookup
- 🔍 Customer verification
- 🌙 Dark / Light mode
- 📈 Sales forecasting
- 🛍️ Product recommendations
- 🤖 Business insights

---

# 💱 Supported Currencies

The dashboard supports multiple currencies:

- 🇬🇧 GBP
- 🇮🇳 INR
- 🇺🇸 USD
- 🇪🇺 EUR
- 🇯🇵 JPY
- 🇦🇪 AED
- 🇦🇺 AUD
- 🇨🇦 CAD
- 🇸🇬 SGD

---

# 🧠 Technology Stack

### Programming Language

- Python

### Data Analysis

- Pandas
- NumPy

### Machine Learning

- Scikit-learn
- K-Means Clustering

### Data Visualization

- Plotly
- Matplotlib

### Web Application

- Streamlit

### Data Processing

- OpenPyXL

### APIs

- Frankfurter Exchange Rate API

### Version Control & Deployment

- Git
- GitHub
- Git LFS
- Streamlit Community Cloud

---

# 📁 Project Structure

```text
AI-Business-Intelligence/
│
├── app.py
│
├── ai_insight_engine.py
├── business_analysis.py
├── check_data.py
├── clean_data.py
├── customer_intelligence.py
├── customer_segmentation.py
├── feature_engineering.py
├── recommendation_engine.py
├── sales_forecasting.py
├── segment_visualization.py
├── visualize.py
│
├── requirements.txt
├── .gitignore
├── .gitattributes
│
├── data/
│   ├── raw/
│   └── processed/
│
└── README.md
