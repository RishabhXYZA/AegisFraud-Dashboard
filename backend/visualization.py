# FRAUD DETECTION PROJECT - PHASE 5
# Updated MySQL + Pandas + Plotly visualization script
# Install: pip install mysql-connector-python pandas plotly

import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# MYSQL CONNECTION - ENTER YOUR NEW CREDENTIALS HERE
# ============================================================
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "Cos^2@+Sin^2@=1"
MYSQL_DATABASE = "fraud_detection"

connection = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)
print("MySQL connected successfully!")


def run_query(query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        return pd.DataFrame(rows, columns=columns)
    finally:
        cursor.close()


def numeric(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# ============================================================
# DARK ANALYTICS THEME
# Inspired by modern financial-analysis dashboards.
# ============================================================
DARK_BG = "#070B12"
DARK_PANEL = "#0B111A"
DARK_GRID = "#253246"
DARK_TEXT = "#E6EDF7"
DARK_MUTED = "#8FA0B5"


def apply_dark_theme(fig, height=None):
    """Apply a consistent dark, presentation-ready Plotly theme."""
    layout = dict(
        template="plotly_dark",
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_BG,
        font=dict(family="Inter, Arial, sans-serif", color=DARK_TEXT, size=11),
        title=dict(font=dict(size=18, color=DARK_TEXT), x=0.5, xanchor="center"),
        legend=dict(font=dict(color=DARK_TEXT, size=10), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#111827", font=dict(color="#F8FAFC")),
        margin=dict(l=60, r=35, t=70, b=55),
    )
    if height is not None:
        layout["height"] = height
    fig.update_layout(**layout)
    fig.update_xaxes(
        color=DARK_TEXT,
        title_font=dict(color=DARK_TEXT),
        tickfont=dict(color=DARK_MUTED),
        gridcolor=DARK_GRID,
        zerolinecolor=DARK_GRID,
        showgrid=True,
    )
    fig.update_yaxes(
        color=DARK_TEXT,
        title_font=dict(color=DARK_TEXT),
        tickfont=dict(color=DARK_MUTED),
        gridcolor=DARK_GRID,
        zerolinecolor=DARK_GRID,
        showgrid=True,
    )
    return fig


# ============================================================
# V01 - OVERALL FRAUD DISTRIBUTION
# Yes = dark blue, No = dark red
# ============================================================
df = run_query("""
SELECT
    CASE WHEN is_fraud = 'Yes' THEN 'Fraud Transaction'
         ELSE 'Non-Fraud Transaction' END AS transaction_status,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY is_fraud
ORDER BY transaction_count DESC;
""")
df = numeric(df, ["transaction_count"])
fig = px.pie(
    df,
    names="transaction_status",
    values="transaction_count",
    title="Overall Fraud vs Non-Fraud Transactions",
    hole=0.60,
    color="transaction_status",
    color_discrete_map={
        "Fraud Transaction": "#0B1F3A",
        "Non-Fraud Transaction": "#8B0000"
    }
)
fig.update_traces(
    textinfo="label+value+percent",
    texttemplate="%{label}<br>%{value:,}<br>(%{percent:.2%})",
    textfont=dict(size=11, color="#F8FAFC"),
    hovertemplate="<b>%{label}</b><br>Transactions: %{value:,}<br>Share: %{percent}<extra></extra>"
)
apply_dark_theme(fig, 560)
fig.show()


# ============================================================
# V02 - FRAUD RATE BY YEAR
# Line chart with visible grid
# ============================================================
df = run_query("""
SELECT year,
       COUNT(*) AS total_transactions,
       SUM(CASE WHEN is_fraud='Yes' THEN 1 ELSE 0 END) AS fraud_transactions,
       ROUND(SUM(CASE WHEN is_fraud='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS fraud_rate
FROM transactions
GROUP BY year ORDER BY year;
""")
df = numeric(df, ["year", "total_transactions", "fraud_transactions", "fraud_rate"])
fig = px.line(df, x="year", y="fraud_rate", markers=True,
              title="Fraud Rate by Year",
              labels={"year":"Year", "fraud_rate":"Fraud Rate (%)"})
fig.update_traces(line=dict(color="#7B2CBF", width=3), marker=dict(color="#7B2CBF", size=8))
fig.update_xaxes(showgrid=True, gridcolor=DARK_GRID)
fig.update_yaxes(showgrid=True, gridcolor=DARK_GRID)
fig.update_layout(title={"text":"Fraud Rate by Year", "x":0.5}, height=550)
apply_dark_theme(fig)
fig.show()


# ============================================================
# V03 - TOTAL VS FRAUD TRANSACTIONS BY YEAR
# ============================================================
df_long = df.melt(id_vars="year", value_vars=["total_transactions", "fraud_transactions"],
                  var_name="transaction_type", value_name="transaction_count")
df_long["transaction_type"] = df_long["transaction_type"].replace({
    "total_transactions":"Total Transactions",
    "fraud_transactions":"Fraudulent Transactions"})
fig = px.line(df_long, x="year", y="transaction_count", color="transaction_type",
              markers=True, title="Transaction Volume and Fraud Volume by Year",
              color_discrete_map={"Total Transactions":"#007F5F", "Fraudulent Transactions":"#FF6B35"})
fig.update_xaxes(showgrid=True, gridcolor=DARK_GRID)
fig.update_yaxes(showgrid=True, gridcolor=DARK_GRID)
fig.update_layout(title={"text":"Transaction Volume and Fraud Volume by Year", "x":0.5}, height=550)
apply_dark_theme(fig)
fig.show()


# ============================================================
# V04 - FRAUD BY PAYMENT METHOD
# ============================================================
df = run_query("""
SELECT use_chip, COUNT(*) AS fraud_count
FROM transactions
WHERE is_fraud='Yes'
GROUP BY use_chip ORDER BY fraud_count DESC;
""")
df = numeric(df, ["fraud_count"])
fig = px.pie(df, names="use_chip", values="fraud_count",
             title="Fraudulent Transactions by Payment Method", hole=0.55,
             color_discrete_sequence=["#E76F51","#264653","#F4A261","#2A9D8F","#E9C46A"])
fig.update_traces(textinfo="label+percent")
apply_dark_theme(fig)
fig.show()


# ============================================================
# V05 - FRAUD BY DAY AND HOUR
# ============================================================
df = run_query("""
SELECT DAYNAME(STR_TO_DATE(CONCAT(year,'-',LPAD(month,2,'0'),'-',LPAD(day,2,'0')),'%Y-%m-%d')) AS day_of_week,
       WEEKDAY(STR_TO_DATE(CONCAT(year,'-',LPAD(month,2,'0'),'-',LPAD(day,2,'0')),'%Y-%m-%d')) AS day_order,
       HOUR(time) AS transaction_hour,
       COUNT(*) AS fraud_count
FROM transactions
WHERE is_fraud='Yes'
GROUP BY day_of_week, day_order, transaction_hour
ORDER BY day_order, transaction_hour;
""")
df = numeric(df, ["day_order","transaction_hour","fraud_count"])
days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
heat = df.pivot(index="day_of_week", columns="transaction_hour", values="fraud_count")
heat = heat.reindex(days).reindex(columns=range(24)).fillna(0)
fig = px.imshow(heat, x=list(range(24)), y=days, aspect="auto",
                labels={"x":"Hour of Day","y":"Day of Week","color":"Fraudulent Transactions"},
                color_continuous_scale=["#FFF4E6","#FFD6A5","#FFB703","#FB8500","#D00000"],
                title="Fraud Activity by Day and Hour")
fig.update_xaxes(tickmode="linear", tick0=0, dtick=1)
fig.update_layout(title={"text":"Fraud Activity by Day and Hour", "x":0.5}, height=600)
apply_dark_theme(fig)
fig.show()


# ============================================================
# V06 - FRAUD BY ERROR TYPE
# ============================================================
df = run_query("""
SELECT COALESCE(NULLIF(errors,''),'No Error') AS error_type,
       COUNT(*) AS fraud_count
FROM transactions
WHERE is_fraud='Yes'
GROUP BY error_type ORDER BY fraud_count DESC;
""")
df = numeric(df, ["fraud_count"])
fig = px.bar(df, x="error_type", y="fraud_count", text="fraud_count",
             title="Fraudulent Transactions by Error Type", color="error_type",
             color_discrete_sequence=["#118AB2","#06D6A0","#EF476F","#8338EC","#FF9F1C","#6A4C93"])
fig.update_traces(textposition="outside")
apply_dark_theme(fig)
fig.show()


# ============================================================
# V07 - FRAUD BY CARD BRAND
# ============================================================
df = run_query("""
SELECT c.card_brand, COUNT(*) AS fraud_count
FROM transactions t JOIN cards c ON t.card_id=c.card_id
WHERE t.is_fraud='Yes'
GROUP BY c.card_brand ORDER BY fraud_count DESC;
""")
df = numeric(df, ["fraud_count"])
fig = px.bar(df.sort_values("fraud_count"), x="fraud_count", y="card_brand", orientation="h",
             text="fraud_count", title="Fraudulent Transactions by Card Brand",
             color="card_brand", color_discrete_sequence=["#4361EE","#F72585","#4CC9F0","#7209B7","#3A0CA3","#4895EF"])
fig.update_traces(textposition="outside")
apply_dark_theme(fig)
fig.show()


# ============================================================
# V08 - FRAUD BY CARD TYPE
# ============================================================
df = run_query("""
SELECT c.card_type, COUNT(*) AS fraud_count
FROM transactions t JOIN cards c ON t.card_id=c.card_id
WHERE t.is_fraud='Yes'
GROUP BY c.card_type ORDER BY fraud_count DESC;
""")
df = numeric(df, ["fraud_count"])
fig = px.pie(df, names="card_type", values="fraud_count", hole=0.55,
             title="Fraudulent Transactions by Card Type",
             color_discrete_sequence=["#8A5CF6","#00B4D8","#FF7A00","#2A9D8F","#D62828"])
fig.update_traces(textinfo="label+percent")
apply_dark_theme(fig)
fig.show()


# ============================================================
# V09 - FRAUD BY FICO CATEGORY
# ============================================================
df = run_query("""
SELECT CASE
         WHEN u.fico_score < 580 THEN 'Poor'
         WHEN u.fico_score BETWEEN 580 AND 669 THEN 'Fair'
         WHEN u.fico_score BETWEEN 670 AND 739 THEN 'Good'
         WHEN u.fico_score BETWEEN 740 AND 799 THEN 'Very Good'
         ELSE 'Exceptional'
       END AS fico_category,
       COUNT(*) AS fraud_count
FROM transactions t
JOIN cards c ON t.card_id=c.card_id
JOIN users u ON c.user_id=u.user_id
WHERE t.is_fraud='Yes'
GROUP BY fico_category
ORDER BY CASE fico_category WHEN 'Poor' THEN 1 WHEN 'Fair' THEN 2 WHEN 'Good' THEN 3 WHEN 'Very Good' THEN 4 ELSE 5 END;
""")
df = numeric(df, ["fraud_count"])
fig = px.bar(df.sort_values("fraud_count"), x="fraud_count", y="fico_category", orientation="h",
             text="fraud_count", title="Fraudulent Transactions by FICO Category",
             color="fico_category",
             color_discrete_sequence=["#C1121F","#F77F00","#FCBF49","#2A9D8F","#1D3557"])
fig.update_traces(textposition="outside")
apply_dark_theme(fig)
fig.show()


# ============================================================
# V10 - FRAUD BY U.S. STATE
# ============================================================
df = run_query("""
SELECT m.merchant_state, COUNT(*) AS fraud_count
FROM transactions t JOIN merchants m ON t.merchant_id=m.merchant_id
WHERE t.is_fraud='Yes' AND m.merchant_state IS NOT NULL
GROUP BY m.merchant_state ORDER BY fraud_count DESC;
""")
df = numeric(df, ["fraud_count"])
fig = px.choropleth(
    df,
    locations="merchant_state",
    locationmode="USA-states",
    color="fraud_count",
    scope="usa",
    title="Fraudulent Transactions by U.S. State",
    color_continuous_scale=["#0B111A", "#164E63", "#0891B2", "#22D3EE", "#67E8F9"],
    range_color=(0, 1000),
    labels={"fraud_count": "Fraudulent Transactions"}
)
apply_dark_theme(fig, 600)
fig.update_coloraxes(
    cmin=0,
    cmax=1000,
    colorbar=dict(
        title="Fraud Count",
        tickmode="array",
        tickvals=[0, 250, 500, 750, 1000],
        ticktext=["0", "250", "500", "750", "1,000"],
        tickfont=dict(color=DARK_TEXT),
        title_font=dict(color=DARK_TEXT)
    )
)
fig.show()


# ============================================================
# V11 - TOP 10 FRAUDULENT MERCHANTS
# ============================================================
df = run_query("""
SELECT m.merchant_id, m.merchant_city, m.merchant_state,
       COUNT(*) AS fraud_count, ROUND(SUM(t.amount),2) AS fraud_amount
FROM transactions t JOIN merchants m ON t.merchant_id=m.merchant_id
WHERE t.is_fraud='Yes'
GROUP BY m.merchant_id, m.merchant_city, m.merchant_state
ORDER BY fraud_count DESC LIMIT 10;
""")
df = numeric(df, ["fraud_count","fraud_amount"])
df["merchant_label"] = df["merchant_city"].astype(str)+", "+df["merchant_state"].astype(str)+" | ID "+df["merchant_id"].astype(str)
fig = px.bar(df.sort_values("fraud_count"), x="fraud_count", y="merchant_label", orientation="h",
             text="fraud_count", title="Top 10 Merchants by Fraudulent Transactions",
             color="fraud_count", color_continuous_scale=["#E0F2FE","#38BDF8","#0284C7","#075985"])
fig.update_traces(textposition="outside")
apply_dark_theme(fig)
fig.show()


# ============================================================
# V12 - TOP 10 USERS BY FRAUD
# ============================================================
df = run_query("""
SELECT u.user_id, COUNT(*) AS fraud_count, ROUND(SUM(t.amount),2) AS fraud_amount
FROM transactions t
JOIN cards c ON t.card_id=c.card_id
JOIN users u ON c.user_id=u.user_id
WHERE t.is_fraud='Yes'
GROUP BY u.user_id ORDER BY fraud_count DESC LIMIT 10;
""")
df = numeric(df, ["fraud_count","fraud_amount"])
df["user_label"] = "User "+df["user_id"].astype(str)
fig = px.bar(df.sort_values("fraud_count"), x="fraud_count", y="user_label", orientation="h",
             text="fraud_count", title="Top 10 Users by Fraudulent Transactions",
             color="fraud_count", color_continuous_scale=["#ECFDF5","#34D399","#059669","#065F46"])
fig.update_traces(textposition="outside")
apply_dark_theme(fig)
fig.show()


# ============================================================
# V13 - OVERALL TRANSACTION AMOUNT DISTRIBUTION
# ============================================================
df = run_query("""
SELECT CASE
         WHEN amount < 50 THEN 'Below $50'
         WHEN amount < 100 THEN '$50-$100'
         WHEN amount < 500 THEN '$100-$500'
         WHEN amount < 1000 THEN '$500-$1K'
         ELSE '$1K+'
       END AS amount_group,
       COUNT(*) AS transaction_count
FROM transactions
GROUP BY amount_group
ORDER BY CASE amount_group WHEN 'Below $50' THEN 1 WHEN '$50-$100' THEN 2 WHEN '$100-$500' THEN 3 WHEN '$500-$1K' THEN 4 ELSE 5 END;
""")
df = numeric(df, ["transaction_count"])
fig = px.pie(df, names="amount_group", values="transaction_count", hole=0.50,
             title="Overall Transaction Amount Distribution",
             color_discrete_sequence=["#003049","#669BBC","#FDF0D5","#C1121F","#780000"])
fig.update_traces(textinfo="label+percent")
apply_dark_theme(fig)
fig.show()


# ============================================================
# V14 - FRAUD AMOUNT DISTRIBUTION
# ============================================================
df = run_query("""
SELECT CASE
         WHEN amount < 50 THEN 'Below $50'
         WHEN amount < 100 THEN '$50-$100'
         WHEN amount < 500 THEN '$100-$500'
         WHEN amount < 1000 THEN '$500-$1K'
         ELSE '$1K+'
       END AS amount_group,
       COUNT(*) AS fraud_count
FROM transactions
WHERE is_fraud='Yes'
GROUP BY amount_group
ORDER BY CASE amount_group WHEN 'Below $50' THEN 1 WHEN '$50-$100' THEN 2 WHEN '$100-$500' THEN 3 WHEN '$500-$1K' THEN 4 ELSE 5 END;
""")
df = numeric(df, ["fraud_count"])
fig = px.bar(df, x="amount_group", y="fraud_count", text="fraud_count",
             title="Fraudulent Transactions by Amount Range", color="amount_group",
             color_discrete_sequence=["#5A189A","#7B2CBF","#9D4EDD","#C77DFF","#E0AAFF"])
fig.update_traces(textposition="outside")
apply_dark_theme(fig)
fig.show()


# ============================================================
# V15 - ADVANCED RISK LEVEL PERFORMANCE
# Uses corrected MySQL 8.0-compatible percentile calculation.
# is_fraud is NOT part of the risk score.
# ============================================================
risk_query = """
WITH ranked_amounts AS (
    SELECT amount, ROW_NUMBER() OVER (ORDER BY amount) AS rn,
           COUNT(*) OVER () AS total_count
    FROM transactions
),
percentile_value AS (
    SELECT MAX(amount) AS p99_amount
    FROM ranked_amounts
    WHERE rn = CEIL(total_count * 0.99)
),
card_daily_activity AS (
    SELECT card_id, year, month, day, COUNT(*) AS daily_transaction_count
    FROM transactions
    GROUP BY card_id, year, month, day
),
risk_data AS (
    SELECT t.transaction_id, t.is_fraud,
           (CASE WHEN t.amount >= p.p99_amount THEN 3 ELSE 0 END
            + CASE WHEN t.use_chip IN ('Online','Online Transaction') THEN 2 ELSE 0 END
            + CASE WHEN t.errors IS NOT NULL AND t.errors <> '' THEN 1 ELSE 0 END
            + CASE WHEN d.daily_transaction_count >= 10 THEN 2 ELSE 0 END) AS risk_score
    FROM transactions t
    CROSS JOIN percentile_value p
    LEFT JOIN card_daily_activity d
      ON t.card_id=d.card_id AND t.year=d.year AND t.month=d.month AND t.day=d.day
)
SELECT CASE WHEN risk_score >= 7 THEN 'High Risk'
            WHEN risk_score >= 4 THEN 'Medium Risk'
            ELSE 'Low Risk' END AS risk_level,
       COUNT(*) AS transaction_count,
       SUM(CASE WHEN is_fraud='Yes' THEN 1 ELSE 0 END) AS fraud_count,
       ROUND(SUM(CASE WHEN is_fraud='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS fraud_rate
FROM risk_data
GROUP BY risk_level
ORDER BY CASE risk_level WHEN 'High Risk' THEN 1 WHEN 'Medium Risk' THEN 2 ELSE 3 END;
"""

df_risk = run_query(risk_query)
df_risk = numeric(df_risk, ["transaction_count","fraud_count","fraud_rate"])
risk_order = ["Low Risk","Medium Risk","High Risk"]
df_risk["risk_level"] = pd.Categorical(df_risk["risk_level"], categories=risk_order, ordered=True)
df_risk = df_risk.sort_values("risk_level")

fig = go.Figure()
fig.add_trace(go.Bar(x=df_risk["risk_level"], y=df_risk["transaction_count"],
                     name="Transactions", marker_color="#4A4E69"))
fig.add_trace(go.Bar(x=df_risk["risk_level"], y=df_risk["fraud_count"],
                     name="Fraudulent Transactions", marker_color="#D00000"))
fig.update_layout(barmode="group", title={"text":"Risk Level Performance", "x":0.5},
                  xaxis_title="Risk Level", yaxis_title="Number of Transactions", height=550)
apply_dark_theme(fig)
fig.show()


# ============================================================
# V16 - FRAUD RATE BY RISK LEVEL
# Line chart with visible grid
# ============================================================
fig = px.line(df_risk, x="risk_level", y="fraud_rate", markers=True,
              title="Fraud Rate by Risk Level",
              labels={"risk_level":"Risk Level", "fraud_rate":"Fraud Rate (%)"})
fig.update_traces(line=dict(color="#00A6A6", width=4), marker=dict(color="#00A6A6", size=10))
fig.update_xaxes(showgrid=True, gridcolor=DARK_GRID)
fig.update_yaxes(showgrid=True, gridcolor=DARK_GRID)
fig.update_layout(title={"text":"Fraud Rate by Risk Level", "x":0.5}, height=550)
apply_dark_theme(fig)
fig.show()


# ============================================================
# V17 - NORMAL VS FRAUD TRANSACTION AMOUNTS
# Clean box plot: light blue = normal, light red = fraud
# Display range intentionally limited to $0-$4,000 for readability.
# ============================================================
df = run_query("""
SELECT is_fraud, amount
FROM transactions
WHERE amount IS NOT NULL AND amount >= 0;
""")
df = numeric(df, ["amount"])
df = df.dropna(subset=["amount"])
df["transaction_status"] = df["is_fraud"].replace({
    "No": "Normal Transactions",
    "Yes": "Fraudulent Transactions"
})
fig = px.box(
    df,
    x="transaction_status",
    y="amount",
    color="is_fraud",
    points="outliers",
    title="Transaction Amount Distribution: Normal vs Fraud",
    color_discrete_map={
        "No": "#93C5FD",
        "Yes": "#FCA5A5"
    }
)
fig.update_traces(
    boxmean=True,
    line=dict(width=2),
    marker=dict(size=4, opacity=0.75),
    jitter=0.10
)
apply_dark_theme(fig, 620)
fig.update_traces(
    selector=dict(name="Normal Transactions"),
    fillcolor="rgba(147,197,253,0.38)",
    line_color="#60A5FA",
    marker_color="#93C5FD"
)
fig.update_traces(
    selector=dict(name="Fraudulent Transactions"),
    fillcolor="rgba(252,165,165,0.38)",
    line_color="#F87171",
    marker_color="#FCA5A5"
)
fig.update_yaxes(
    range=[0, 4000],
    title="Transaction Amount ($)",
    tickprefix="$",
    dtick=500,
    showgrid=True,
    gridcolor=DARK_GRID
)
fig.update_layout(
    showlegend=False,
    boxmode="group",
    xaxis_title="Transaction Type",
    margin=dict(l=70, r=35, t=75, b=70)
)
fig.show()


# ============================================================
# V18 - YEARLY TOTAL AMOUNT VS FRAUD AMOUNT
# Combo chart with grid
# ============================================================
df = run_query("""
SELECT year,
       ROUND(SUM(amount),2) AS total_amount,
       ROUND(SUM(CASE WHEN is_fraud='Yes' THEN amount ELSE 0 END),2) AS fraud_amount
FROM transactions
GROUP BY year ORDER BY year;
""")
df = numeric(df, ["year","total_amount","fraud_amount"])
fig = go.Figure()
fig.add_trace(go.Bar(x=df["year"], y=df["total_amount"], name="Total Transaction Amount", marker_color="#2f4670"))
fig.add_trace(go.Scatter(x=df["year"], y=df["fraud_amount"], name="Fraud Amount",
                         mode="lines+markers", line=dict(color="#6e1d1d", width=4), marker=dict(size=8)))
fig.update_layout(title={"text":"Transaction Amount vs Fraud Amount Over Time", "x":0.5},
                  xaxis_title="Year", yaxis_title="Amount ($)", hovermode="x unified", height=600)
fig.update_xaxes(showgrid=True, gridcolor=DARK_GRID)
fig.update_yaxes(showgrid=True, gridcolor=DARK_GRID)
apply_dark_theme(fig)
fig.show()


# ============================================================
# V19 - KPI OUTPUT
# ============================================================
kpi = run_query("""
SELECT
    (SELECT COUNT(*) FROM users) AS total_users,
    (SELECT COUNT(*) FROM cards) AS total_cards,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount),2) AS total_amount,
    SUM(CASE WHEN is_fraud='Yes' THEN 1 ELSE 0 END) AS fraudulent_transactions,
    ROUND(SUM(CASE WHEN is_fraud='Yes' THEN amount ELSE 0 END),2) AS fraud_amount
FROM transactions;
""")
kpi = numeric(kpi, kpi.columns.tolist()).iloc[0]
print("\n" + "="*55)
print("                 DASHBOARD KPIs")
print("="*55)
print(f"Total Users:               {int(kpi['total_users']):,}")
print(f"Total Cards:               {int(kpi['total_cards']):,}")
print(f"Total Transactions:        {int(kpi['total_transactions']):,}")
print(f"Total Transaction Amount:  ${kpi['total_amount']:,.2f}")
print(f"Fraudulent Transactions:   {int(kpi['fraudulent_transactions']):,}")
print(f"Fraud Amount:              ${kpi['fraud_amount']:,.2f}")
print(f"Overall Fraud Rate:        {kpi['fraudulent_transactions']/kpi['total_transactions']*100:.2f}%")
print("="*55)

connection.close()
print("\nMySQL connection closed.")