# AegisFraud Intelligence - Enterprise Fraud Analytical Dashboard

An enterprise-grade, dark-themed **Fraud Detection Analytical Dashboard** built with **Python (Flask)** on the backend and **HTML5/CSS3/JavaScript + Bootstrap 5 + Plotly.js** on the frontend, connected directly to **MySQL**.

---

## 🌟 Key Features

1. **Top Executive KPI Bar**:
   - Live metrics: Total Users (2,000), Active Cards (6,146), Transactions (200,000), Processed Volume ($10.67M), Fraudulent Volume (29,757), Fraud Rate (14.88%), and Net Fraud Loss ($3.23M).
2. **Minimalist 4-Tab Navigation**:
   - **Executive Overview**: Executive briefing narrative, 4-pillar threat matrix, and interactive 4-stage automated pipeline (*"From Signal to Investigation"*).
   - **Executive Insights**: 4 key risk signals (68.4% online channel loss, 8.7x risk score calibration, 3.4x dark web multiplier, 01:00-05:00 off-peak surge), macro trends, and strategic governance gaps.
   - **Graph Insights (5 - 4 - 4 Layout)**: 13 curated Plotly visualizations across Macro Trends, Entity Risk Heatmaps, and Geospatial Exposure (U.S. Choropleth Map with 0-1,000 scale).
   - **SQL Query Explorer ("The Big Shot")**: Interactive workbench with categorized business modules, formatted SQL editor, runtime metrics, paginated data grid, and CSV data export.
3. **Virtual Avatar AI Assistant**:
   - Floating bottom-right phone-ratio drawer ($380\text{px} \times 580\text{px}$) with instant conversational answers grounded in your fraud datasets, risk scores, and business intelligence.

---

## 📂 Project Structure

```
├── app.py                      # Flask Application Server & REST API
├── config.py                   # Environment & Database Configuration
├── database.py                 # MySQL Connector Engine (mysql.connector)
├── analytics.py                # Plotly Chart Generator (5-4-4 Scheme) & KPI Calculations
├── query_registry.py           # Enterprise Business SQL Query Catalog
├── chatbot_engine.py           # Virtual Avatar AI Domain Assistant Engine
├── requirements.txt            # Python Dependencies
├── .env                        # Environment Credentials (Ignored by Git)
├── .env.example                # Template Environment File
├── .gitignore                  # Git Ignore Specifications
├── static/
│   ├── css/
│   │   └── dashboard.css       # Dark Theme UI & Glassmorphism Styles
│   └── js/
│       ├── dashboard.js        # Tab Navigation, KPI Loader, Plotly Chart Renderers
│       ├── sql_explorer.js     # SQL Module Dropdowns, Query Runner, Table & CSV Exporter
│       └── chatbot.js          # Virtual Avatar Chat Drawer & Messaging
└── templates/
    └── index.html              # Main Single-Page Interface
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- MySQL Server (v8.0+)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-username/fraud-detection-dashboard.git
cd fraud-detection-dashboard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup (MySQL)
Create database and load tables:
```sql
CREATE DATABASE fraud_detection;
USE fraud_detection;

-- Execute table creation scripts:
-- users_table_creation.sql
-- card_table_creation.sql
-- merchant_table_creation.sql
-- transaction_table_creation.sql
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and set your credentials:
```ini
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=fraud_detection
SECRET_KEY=your_secret_key
PORT=5050
```

### 5. Run Application
```bash
python app.py
```
Open **[http://localhost:5050](http://localhost:5050)** in your browser!
