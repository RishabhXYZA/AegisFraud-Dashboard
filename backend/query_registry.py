"""
Query Registry - Enterprise Business Query Catalog for Fraud Detection
Maps technical SQL scripts to professional enterprise business intelligence modules.
"""

SQL_MODULES = [
    {
        "id": "core_fraud_detection",
        "name": "Core Fraud Detection Engine",
        "icon": "bi-shield-shaded",
        "badge": "Real-Time Rules",
        "description": "Deterministic fraud rule checks, rapid velocity spikes, high-amount anomalies, and dark web card flags.",
        "queries": [
            {
                "id": "rapid_velocity_spikes",
                "name": "Rapid Velocity & Multi-Swipe Spike Detection",
                "description": "Identifies cards exhibiting 5 or more transactions on the same day with at least one fraudulent occurrence.",
                "sql": """SELECT 
    t.card_id, 
    c.card_brand, 
    c.card_type, 
    t.year, 
    t.month, 
    t.day, 
    COUNT(t.transaction_id) AS daily_transaction_count,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(t.amount), 2) AS total_daily_spending
FROM transactions t
JOIN cards c ON t.card_id = c.card_id
GROUP BY t.card_id, c.card_brand, c.card_type, t.year, t.month, t.day
HAVING COUNT(t.transaction_id) >= 5 
   AND SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) >= 1
ORDER BY daily_transaction_count DESC, total_daily_spending DESC
LIMIT 50;"""
            },
            {
                "id": "dark_web_compromise_impact",
                "name": "Dark Web Leaked Card Exposure & Fraud Ratio",
                "description": "Analyzes whether cards flagged on the dark web experience statistically higher fraud occurrence rates.",
                "sql": """SELECT 
    c.card_on_dark_web AS dark_web_flag,
    COUNT(DISTINCT c.card_id) AS total_cards,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_transactions,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.transaction_id), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN t.amount ELSE 0 END), 2) AS total_fraud_loss
FROM cards c
JOIN transactions t ON c.card_id = t.card_id
GROUP BY c.card_on_dark_web
ORDER BY fraud_rate_pct DESC;"""
            },
            {
                "id": "online_error_fraud_correlation",
                "name": "Payment Method & Error Code Anomaly Matrix",
                "description": "Evaluates transaction error codes across payment methods to detect failed authentication patterns in fraud.",
                "sql": """SELECT 
    t.use_chip AS payment_channel,
    COALESCE(NULLIF(t.errors, ''), 'No Error') AS error_type,
    COUNT(*) AS total_attempts,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN t.amount ELSE 0 END), 2) AS fraud_value
FROM transactions t
GROUP BY t.use_chip, error_type
HAVING COUNT(*) >= 50
ORDER BY fraud_rate_pct DESC, fraud_count DESC
LIMIT 30;"""
            },
            {
                "id": "high_ticket_anomalies",
                "name": "High-Ticket Transaction Outlier Audit ($500+)",
                "description": "Isolates high-ticket transactions exceeding $500 to evaluate ticket size vs fraud probability.",
                "sql": """SELECT 
    t.transaction_id,
    t.card_id,
    t.merchant_id,
    t.year,
    t.month,
    t.day,
    t.amount,
    t.use_chip,
    t.is_fraud,
    m.merchant_city,
    m.merchant_state
FROM transactions t
JOIN merchants m ON t.merchant_id = m.merchant_id
WHERE t.amount >= 500.00
ORDER BY t.amount DESC
LIMIT 50;"""
            }
        ]
    },
    {
        "id": "advanced_risk_scoring",
        "name": "Multi-Factor Risk & Anomaly Scoring",
        "icon": "bi-cpu-fill",
        "badge": "Risk Engine",
        "description": "Sophisticated multi-attribute risk calculation combining 99th percentile amount thresholds, CNP channel, and daily velocity.",
        "queries": [
            {
                "id": "multifactor_risk_tiering",
                "name": "Multi-Factor Risk Engine Performance by Tier",
                "description": "Evaluates the 4-factor risk algorithm (P99 Amount + Online CNP + Errors + Daily Velocity >= 10) against actual fraud rates.",
                "sql": """WITH ranked_amounts AS (
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
       ROUND(SUM(CASE WHEN is_fraud='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS fraud_rate_pct
FROM risk_data
GROUP BY risk_level
ORDER BY CASE risk_level WHEN 'High Risk' THEN 1 WHEN 'Medium Risk' THEN 2 ELSE 3 END;"""
            },
            {
                "id": "top_high_risk_cards",
                "name": "Top High-Risk Cards Ranked by Fraud Concentration",
                "description": "Surfaces cards with the highest historical incidence of fraudulent charges requiring proactive blocklists.",
                "sql": """SELECT 
    c.card_id,
    c.user_id,
    c.card_brand,
    c.card_type,
    c.credit_limit,
    c.card_on_dark_web,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.transaction_id), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN t.amount ELSE 0 END), 2) AS total_fraud_amount
FROM cards c
JOIN transactions t ON c.card_id = t.card_id
GROUP BY c.card_id, c.user_id, c.card_brand, c.card_type, c.credit_limit, c.card_on_dark_web
HAVING COUNT(t.transaction_id) >= 20 AND SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) >= 3
ORDER BY fraud_rate_pct DESC, fraud_count DESC
LIMIT 25;"""
            },
            {
                "id": "customer_financial_risk_profile",
                "name": "Customer Financial Health vs Fraud Exposure Profile",
                "description": "Cross-examines customer income, debt load, and FICO score with fraud frequency and loss magnitude.",
                "sql": """SELECT 
    u.user_id,
    u.person AS customer_name,
    u.current_age,
    u.yearly_income_person,
    u.total_debt,
    u.fico_score,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.transaction_id), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN t.amount ELSE 0 END), 2) AS total_fraud_loss
FROM users u
JOIN cards c ON u.user_id = c.user_id
JOIN transactions t ON c.card_id = t.card_id
GROUP BY u.user_id, u.person, u.current_age, u.yearly_income_person, u.total_debt, u.fico_score
HAVING COUNT(t.transaction_id) >= 20 AND SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) >= 2
ORDER BY fraud_rate_pct DESC, total_fraud_loss DESC
LIMIT 25;"""
            },
            {
                "id": "pin_change_recency_vulnerability",
                "name": "PIN Reset Recency vs Fraud Compromise Probability",
                "description": "Determines whether cards with stale PINs or recently altered PINs experience higher fraud likelihood.",
                "sql": """SELECT 
    c.year_pin_last_changed,
    COUNT(DISTINCT c.card_id) AS card_count,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.transaction_id), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN t.amount ELSE 0 END), 2) AS total_fraud_loss
FROM cards c
JOIN transactions t ON c.card_id = t.card_id
WHERE c.year_pin_last_changed IS NOT NULL
GROUP BY c.year_pin_last_changed
ORDER BY c.year_pin_last_changed DESC;"""
            }
        ]
    },
    {
        "id": "executive_insights_strategy",
        "name": "Executive Business Insights & Strategy",
        "icon": "bi-graph-up-arrow",
        "badge": "Strategy",
        "description": "Executive summaries, loss ratios, channel vulnerabilities, and top merchant category exposures.",
        "queries": [
            {
                "id": "executive_kpi_summary",
                "name": "Executive Fraud Loss & Portfolio Exposure Summary",
                "description": "Overall enterprise KPIs: total volume, gross fraud value, legitimate volume, and net fraud rate.",
                "sql": """SELECT
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraudulent_transactions,
    SUM(CASE WHEN is_fraud = 'No' THEN 1 ELSE 0 END) AS legitimate_transactions,
    ROUND(SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN is_fraud = 'Yes' THEN amount ELSE 0 END), 2) AS fraudulent_transaction_value,
    ROUND(SUM(CASE WHEN is_fraud = 'No' THEN amount ELSE 0 END), 2) AS legitimate_transaction_value,
    ROUND(SUM(amount), 2) AS total_transaction_value
FROM transactions;"""
            },
            {
                "id": "channel_vulnerability_breakdown",
                "name": "Channel Vulnerability & Loss Concentration",
                "description": "Compares Online (CNP), Chip, and Swipe transaction channels by fraud rate, volume, and average ticket size.",
                "sql": """SELECT
    use_chip AS transaction_channel,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS fraud_rate_pct,
    ROUND(AVG(amount), 2) AS avg_transaction_amount,
    ROUND(SUM(CASE WHEN is_fraud = 'Yes' THEN amount ELSE 0 END), 2) AS total_fraud_value
FROM transactions
GROUP BY use_chip
ORDER BY fraud_rate_pct DESC;"""
            },
            {
                "id": "mcc_risk_categories",
                "name": "Top Merchant Category Codes (MCC) by Fraud Vulnerability",
                "description": "Ranks merchant category codes (MCCs) by fraud rate and total value lost to isolate vulnerable sectors.",
                "sql": """SELECT
    m.mcc AS merchant_category_code,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.transaction_id), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN t.amount ELSE 0 END), 2) AS fraudulent_value
FROM merchants m
JOIN transactions t ON m.merchant_id = t.merchant_id
GROUP BY m.mcc
HAVING COUNT(t.transaction_id) >= 50
ORDER BY fraud_rate_pct DESC, fraudulent_value DESC
LIMIT 20;"""
            },
            {
                "id": "annual_fraud_loss_trend",
                "name": "Annual Transaction Growth vs Net Fraud Loss Trajectory",
                "description": "Tracks yearly trajectory of total transaction amounts vs fraudulent amounts to benchmark loss trends.",
                "sql": """SELECT
    year,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_amount,
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN is_fraud = 'Yes' THEN amount ELSE 0 END), 2) AS fraud_amount,
    ROUND(SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS fraud_rate_pct
FROM transactions
GROUP BY year
ORDER BY year;"""
            }
        ]
    },
    {
        "id": "card_portfolio_intelligence",
        "name": "Card Portfolio & Security Intelligence",
        "icon": "bi-credit-card-2-front-fill",
        "badge": "Card Security",
        "description": "Card brand vulnerability, debit vs credit risk differential, credit limit tiering, and chip presence impact.",
        "queries": [
            {
                "id": "card_brand_breakdown",
                "name": "Card Brand Risk & Volume Distribution",
                "description": "Examines fraud count and loss magnitude across Visa, Mastercard, American Express, and Discover.",
                "sql": """SELECT 
    c.card_brand,
    COUNT(DISTINCT c.card_id) AS total_cards,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.transaction_id), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN t.amount ELSE 0 END), 2) AS total_fraud_amount
FROM cards c
JOIN transactions t ON c.card_id = t.card_id
GROUP BY c.card_brand
ORDER BY fraud_count DESC;"""
            },
            {
                "id": "card_type_debit_credit",
                "name": "Debit vs Credit Card Fraud Rate Comparison",
                "description": "Quantifies the risk disparity between Debit cards (direct account debit) and Credit cards.",
                "sql": """SELECT 
    c.card_type,
    COUNT(DISTINCT c.card_id) AS card_count,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.transaction_id), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN t.amount ELSE 0 END), 2) AS total_fraud_amount
FROM cards c
JOIN transactions t ON c.card_id = t.card_id
GROUP BY c.card_type
ORDER BY fraud_count DESC;"""
            },
            {
                "id": "credit_limit_tier_analysis",
                "name": "Credit Limit Tiers vs Fraud Incidence",
                "description": "Categorizes credit limits into financial bands to assess if high-limit cards attract higher fraud attempts.",
                "sql": """SELECT 
    CASE 
        WHEN c.credit_limit < 5000 THEN 'Low Limit (<$5K)'
        WHEN c.credit_limit < 15000 THEN 'Medium Limit ($5K-$15K)'
        WHEN c.credit_limit < 30000 THEN 'High Limit ($15K-$30K)'
        ELSE 'Ultra High Limit ($30K+)'
    END AS credit_limit_tier,
    COUNT(DISTINCT c.card_id) AS total_cards,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.transaction_id), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN t.amount ELSE 0 END), 2) AS total_fraud_loss
FROM cards c
JOIN transactions t ON c.card_id = t.card_id
WHERE c.credit_limit IS NOT NULL
GROUP BY credit_limit_tier
ORDER BY total_fraud_loss DESC;"""
            }
        ]
    },
    {
        "id": "merchant_geographic_intelligence",
        "name": "Merchant Network & Geographic Hotspots",
        "icon": "bi-shop",
        "badge": "Geospatial",
        "description": "Geographic concentration of fraudulent transactions by state, city, and top merchant outliers.",
        "queries": [
            {
                "id": "top_fraudulent_merchants",
                "name": "Top 10 Merchants Ranked by Fraud Volume",
                "description": "Isolates specific merchants with the highest recorded fraudulent transaction counts and financial loss.",
                "sql": """SELECT 
    m.merchant_id,
    m.merchant_city,
    m.merchant_state,
    m.mcc,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.transaction_id), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN t.amount ELSE 0 END), 2) AS total_fraud_loss
FROM merchants m
JOIN transactions t ON m.merchant_id = t.merchant_id
GROUP BY m.merchant_id, m.merchant_city, m.merchant_state, m.mcc
ORDER BY fraud_count DESC
LIMIT 10;"""
            },
            {
                "id": "state_fraud_concentration",
                "name": "U.S. State Geographic Fraud Density",
                "description": "Aggregates fraud volume and transaction totals across US states to highlight regional hotspots.",
                "sql": """SELECT 
    m.merchant_state,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.transaction_id), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN t.amount ELSE 0 END), 2) AS total_fraud_amount
FROM merchants m
JOIN transactions t ON m.merchant_id = t.merchant_id
WHERE m.merchant_state IS NOT NULL AND m.merchant_state <> ''
GROUP BY m.merchant_state
ORDER BY fraud_count DESC;"""
            }
        ]
    },
    {
        "id": "customer_demographic_intelligence",
        "name": "Customer Financial Health & Demographics",
        "icon": "bi-people-fill",
        "badge": "Demographics",
        "description": "FICO credit bands, age demographics, income tiers, and customer victimization patterns.",
        "queries": [
            {
                "id": "fico_score_tier_fraud",
                "name": "FICO Credit Score Tiers vs Fraud Incident Rate",
                "description": "Groups cardholders by FICO tier (Poor, Fair, Good, Very Good, Exceptional) to measure fraud risk.",
                "sql": """SELECT 
    CASE
        WHEN u.fico_score < 580 THEN 'Poor (<580)'
        WHEN u.fico_score BETWEEN 580 AND 669 THEN 'Fair (580-669)'
        WHEN u.fico_score BETWEEN 670 AND 739 THEN 'Good (670-739)'
        WHEN u.fico_score BETWEEN 740 AND 799 THEN 'Very Good (740-799)'
        ELSE 'Exceptional (800+)'
    END AS fico_category,
    COUNT(DISTINCT u.user_id) AS user_count,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.transaction_id), 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN t.amount ELSE 0 END), 2) AS total_fraud_loss
FROM users u
JOIN cards c ON u.user_id = c.user_id
JOIN transactions t ON c.card_id = t.card_id
GROUP BY fico_category
ORDER BY CASE fico_category 
    WHEN 'Poor (<580)' THEN 1 
    WHEN 'Fair (580-669)' THEN 2 
    WHEN 'Good (670-739)' THEN 3 
    WHEN 'Very Good (740-799)' THEN 4 
    ELSE 5 END;"""
            },
            {
                "id": "top_victimized_users",
                "name": "Top 10 Customers Most Impacted by Fraud",
                "description": "Ranks cardholders by number of compromised transactions and financial damage.",
                "sql": """SELECT 
    u.user_id,
    u.person AS customer_name,
    u.city,
    u.state,
    u.fico_score,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN t.amount ELSE 0 END), 2) AS total_fraud_amount
FROM users u
JOIN cards c ON u.user_id = c.user_id
JOIN transactions t ON c.card_id = t.card_id
WHERE t.is_fraud = 'Yes'
GROUP BY u.user_id, u.person, u.city, u.state, u.fico_score
ORDER BY fraud_count DESC
LIMIT 10;"""
            }
        ]
    }
]

def get_all_modules():
    return SQL_MODULES

def get_module_by_id(module_id):
    for m in SQL_MODULES:
        if m["id"] == module_id:
            return m
    return None

def get_query_by_id(query_id):
    for m in SQL_MODULES:
        for q in m["queries"]:
            if q["id"] == query_id:
                return q
    return None
