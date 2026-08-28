USE fraud_detection;

-- 1. Fraud rate by card
-- This identifies cards with unusually high fraud activity.
SELECT
    c.card_id,
    c.user_id,
    c.card_brand,
    c.card_type,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraudulent_transactions,
    ROUND(
        SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(t.transaction_id),
        2
    ) AS fraud_rate,
    ROUND(SUM(t.amount), 2) AS total_transaction_value
FROM cards c
JOIN transactions t
    ON c.card_id = t.card_id
GROUP BY
    c.card_id,
    c.user_id,
    c.card_brand,
    c.card_type
HAVING COUNT(t.transaction_id) >= 10
ORDER BY fraud_rate DESC;


-- 2. Top high-risk cards
SELECT
    c.card_id,
    c.user_id,
    c.card_brand,
    c.card_type,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(
        SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(t.transaction_id),
        2
    ) AS fraud_rate,
    ROUND(SUM(t.amount), 2) AS total_spending
FROM cards c
JOIN transactions t
    ON c.card_id = t.card_id
GROUP BY
    c.card_id,
    c.user_id,
    c.card_brand,
    c.card_type
HAVING
    COUNT(t.transaction_id) >= 20
    AND SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) >= 3
ORDER BY fraud_rate DESC, fraud_count DESC
LIMIT 20;

-- This gives you a much stronger list of suspicious cards.

-- 3. Customer-level fraud analysis
SELECT
    u.user_id,
    u.person,
    u.current_age,
    u.yearly_income_person,
    u.total_debt,
    u.fico_score,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(
        SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(t.transaction_id),
        2
    ) AS fraud_rate,
    ROUND(SUM(t.amount), 2) AS total_spending
FROM users u
JOIN cards c
    ON u.user_id = c.user_id
JOIN transactions t
    ON c.card_id = t.card_id
GROUP BY
    u.user_id,
    u.person,
    u.current_age,
    u.yearly_income_person,
    u.total_debt,
    u.fico_score
HAVING COUNT(t.transaction_id) >= 20
ORDER BY fraud_rate DESC, fraud_count DESC;

-- 4. High-risk customers based on financial profile
SELECT
    u.user_id,
    u.person,
    u.yearly_income_person,
    u.total_debt,
    u.fico_score,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(t.amount), 2) AS total_spending,
    ROUND(SUM(t.amount) / NULLIF(u.yearly_income_person, 0) * 100,2) AS spending_to_income_pct
FROM users u
JOIN cards c
    ON u.user_id = c.user_id
JOIN transactions t
    ON c.card_id = t.card_id
GROUP BY
    u.user_id,
    u.person,
    u.yearly_income_person,
    u.total_debt,
    u.fico_score
HAVING
    u.fico_score < 670
    AND u.total_debt > u.yearly_income_person
    AND SUM(t.amount) > 10000
ORDER BY total_spending DESC;


-- 5. Fraud by merchant with statistical filtering
-- This is better than simply ranking every merchant.
SELECT
    m.merchant_id,
    m.merchant_city,
    m.merchant_state,
    m.mcc,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)* 100.0 / COUNT(t.transaction_id),2) AS fraud_rate,
    ROUND(AVG(t.amount), 2) AS average_transaction
FROM merchants m
JOIN transactions t
    ON m.merchant_id = t.merchant_id
GROUP BY
    m.merchant_id,
    m.merchant_city,
    m.merchant_state,
    m.mcc
HAVING
    COUNT(t.transaction_id) >= 20
    AND SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) >= 3
ORDER BY fraud_rate DESC
LIMIT 30;


-- 6. Fraud by MCC category
-- This can identify merchant categories associated with more fraud.
SELECT
    m.mcc,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(
        SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(t.transaction_id),
        2
    ) AS fraud_rate,
    ROUND(AVG(t.amount), 2) AS average_transaction
FROM merchants m
JOIN transactions t
    ON m.merchant_id = t.merchant_id
GROUP BY m.mcc
HAVING COUNT(t.transaction_id) >= 50
ORDER BY fraud_rate DESC;


-- 7. Fraud by transaction channel
SELECT
    use_chip,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_rate,
    ROUND(AVG(amount), 2) AS average_transaction
FROM transactions
GROUP BY use_chip
ORDER BY fraud_rate DESC;

-- This is an important business insight because it tells a bank which transaction channel deserves more monitoring.


-- 8. Fraud by transaction amount band
SELECT
    CASE
        WHEN amount < 50 THEN 'Below $50'
        WHEN amount < 100 THEN '$50-$99'
        WHEN amount < 500 THEN '$100-$499'
        WHEN amount < 1000 THEN '$500-$999'
        WHEN amount < 5000 THEN '$1,000-$4,999'
        ELSE '$5,000+'
    END AS amount_band,

    COUNT(*) AS total_transactions,

    SUM(
        CASE
            WHEN is_fraud = 'Yes' THEN 1
            ELSE 0
        END
    ) AS fraud_count,

    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_rate

FROM transactions
GROUP BY amount_band
ORDER BY fraud_rate DESC;


-- 9. High-value fraudulent transactions using ranking
-- Using a window function:
WITH fraudulent_transactions AS (
    SELECT
        transaction_id,
        card_id,
        merchant_id,
        amount,
        year,
        month,
        day,
        use_chip,
        ROW_NUMBER() OVER (
            ORDER BY amount DESC
        ) AS transaction_rank
    FROM transactions
    WHERE is_fraud = 'Yes'
)

SELECT *
FROM fraudulent_transactions
WHERE transaction_rank <= 20
ORDER BY transaction_rank;

-- This demonstrates a window function, which is useful for your project/viva.


-- 10. Fraud concentration by year
SELECT
    year,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_rate,
    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN amount ELSE 0 END),
        2
    ) AS fraudulent_transaction_value
FROM transactions
GROUP BY year
ORDER BY year;


-- 11. Fraud concentration by day of month
SELECT
    day,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_rate
FROM transactions
GROUP BY day
ORDER BY fraud_rate DESC;


-- 12. Error-related fraud analysis
-- Your transactions table contains an errors column, so this is particularly valuable.
SELECT
    CASE
        WHEN errors IS NULL OR errors = '' THEN 'No Error'
        ELSE 'Error Present'
    END AS error_status,

    COUNT(*) AS total_transactions,
    SUM(
        CASE
            WHEN is_fraud = 'Yes' THEN 1
            ELSE 0
        END
    ) AS fraud_count,

    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_rate
FROM transactions
GROUP BY error_status;

-- This can tell us whether transactions associated with errors have a different fraud rate.

-- 13. Rapid transaction activity
-- We can look for cards making many transactions on the same day.
SELECT
    card_id,
    year,
    month,
    day,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount,
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count
FROM transactions
GROUP BY
    card_id,
    year,
    month,
    day
HAVING COUNT(*) >= 10
ORDER BY transaction_count DESC;

-- This is a useful velocity-based fraud indicator.

-- 14. High transaction velocity + fraud
-- A stronger version:
SELECT
    card_id,
    year,
    month,
    day,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount,
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_rate
FROM transactions
GROUP BY
    card_id,
    year,
    month,
    day
HAVING
    COUNT(*) >= 10
    AND SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) > 0
ORDER BY fraud_count DESC, transaction_count DESC;


-- 15. Transaction-level risk scoring
-- This is the most important advanced query.
-- Risk factors
-- i. Condition	Score
-- ii.Transaction amount ≥ 99th percentile	+3
-- iii. Fraud-prone channel	+2
-- iv. Transaction has error	+1
-- v. High card velocity	+2
-- vi. Already labeled fraudulent	+5
WITH ranked_amounts AS (
    SELECT
        amount,
        ROW_NUMBER() OVER (ORDER BY amount) AS rn,
        COUNT(*) OVER () AS total_count
    FROM transactions
),

percentile_value AS (
    SELECT
        MAX(amount) AS p99_amount
    FROM ranked_amounts
    WHERE rn = CEIL(total_count * 0.99)
),

card_daily_activity AS (
    SELECT
        card_id,
        year,
        month,
        day,
        COUNT(*) AS daily_transaction_count
    FROM transactions
    GROUP BY
        card_id,
        year,
        month,
        day
),

scored_transactions AS (
    SELECT
        t.transaction_id,
        t.card_id,
        t.merchant_id,
        t.amount,
        t.use_chip,
        t.errors,
        t.is_fraud,

        (
            CASE
                WHEN t.amount >= p.p99_amount
                THEN 3
                ELSE 0
            END

            +

            CASE
                WHEN t.use_chip IN ('Online', 'Online Transaction')
                THEN 2
                ELSE 0
            END

            +

            CASE
                WHEN t.errors IS NOT NULL
                     AND t.errors <> ''
                THEN 1
                ELSE 0
            END

            +

            CASE
                WHEN d.daily_transaction_count >= 10
                THEN 2
                ELSE 0
            END
        ) AS risk_score

    FROM transactions t

    CROSS JOIN percentile_value p

    LEFT JOIN card_daily_activity d
        ON t.card_id = d.card_id
        AND t.year = d.year
        AND t.month = d.month
        AND t.day = d.day
)

SELECT
    transaction_id,
    card_id,
    merchant_id,
    amount,
    use_chip,
    errors,
    is_fraud,
    risk_score,

    CASE
        WHEN risk_score >= 7 THEN 'High Risk'
        WHEN risk_score >= 4 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS risk_level
FROM scored_transactions
ORDER BY
    risk_score DESC,
    amount DESC;


-- 16. Risk-score performance
-- After creating the risk score logic, we can see how fraud is distributed across risk levels.
WITH ranked_amounts AS (
    SELECT
        amount,
        ROW_NUMBER() OVER (ORDER BY amount) AS rn,
        COUNT(*) OVER () AS total_count
    FROM transactions
),

percentile_value AS (
    SELECT
        MAX(amount) AS p99_amount
    FROM ranked_amounts
    WHERE rn = CEIL(total_count * 0.99)
),

card_daily_activity AS (
    SELECT
        card_id,
        year,
        month,
        day,
        COUNT(*) AS daily_transaction_count
    FROM transactions
    GROUP BY
        card_id,
        year,
        month,
        day
),

risk_data AS (
    SELECT
        t.transaction_id,
        t.is_fraud,

        (
            CASE
                WHEN t.amount >= p.p99_amount
                THEN 3
                ELSE 0
            END

            +

            CASE
                WHEN t.use_chip IN ('Online', 'Online Transaction')
                THEN 2
                ELSE 0
            END

            +

            CASE
                WHEN t.errors IS NOT NULL
                     AND t.errors <> ''
                THEN 1
                ELSE 0
            END

            +

            CASE
                WHEN d.daily_transaction_count >= 10
                THEN 2
                ELSE 0
            END
        ) AS risk_score

    FROM transactions t

    CROSS JOIN percentile_value p

    LEFT JOIN card_daily_activity d
        ON t.card_id = d.card_id
        AND t.year = d.year
        AND t.month = d.month
        AND t.day = d.day
)

SELECT
    CASE
        WHEN risk_score >= 7 THEN 'High Risk'
        WHEN risk_score >= 4 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS risk_level,

    COUNT(*) AS transaction_count,

    SUM(
        CASE
            WHEN is_fraud = 'Yes'
            THEN 1
            ELSE 0
        END
    ) AS fraud_count,

    ROUND(
        SUM(
            CASE
                WHEN is_fraud = 'Yes'
                THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) AS fraud_rate

FROM risk_data
GROUP BY risk_level
ORDER BY
    CASE risk_level
        WHEN 'High Risk' THEN 1
        WHEN 'Medium Risk' THEN 2
        WHEN 'Low Risk' THEN 3
    END;