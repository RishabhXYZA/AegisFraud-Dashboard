USE fraud_detection;

-- 1. Executive fraud summary
SELECT
    COUNT(*) AS total_transactions,
    SUM(
        CASE
            WHEN is_fraud = 'Yes' THEN 1
            ELSE 0
        END
    ) AS fraudulent_transactions,

    SUM(
        CASE
            WHEN is_fraud = 'No' THEN 1
            ELSE 0
        END
    ) AS legitimate_transactions,

    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_rate,

    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN amount ELSE 0 END),
        2
    ) AS fraudulent_transaction_value,

    ROUND(
        SUM(CASE WHEN is_fraud = 'No' THEN amount ELSE 0 END),
        2
    ) AS legitimate_transaction_value

FROM transactions;

-- 2. Fraud by transaction channel
SELECT
    use_chip,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        AS fraud_count,
    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_rate,

    ROUND(AVG(amount), 2) AS average_transaction

FROM transactions
GROUP BY use_chip
ORDER BY fraud_rate DESC;

-- Business question
-- Which transaction channel requires the strongest monitoring?

-- 3. Top fraud-prone merchant categories
SELECT
    m.mcc,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        AS fraud_count,

    ROUND(
        SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(t.transaction_id),
        2
    ) AS fraud_rate,

    ROUND(
        SUM(
            CASE
                WHEN t.is_fraud = 'Yes' THEN t.amount
                ELSE 0
            END
        ),
        2
    ) AS fraudulent_value

FROM merchants m
JOIN transactions t
    ON m.merchant_id = t.merchant_id
GROUP BY m.mcc
HAVING COUNT(t.transaction_id) >= 50
ORDER BY fraud_rate DESC
LIMIT 20;

-- Business question
-- Which merchant categories show elevated fraud risk?


-- 4. Top suspicious merchants
SELECT
    m.merchant_id,
    m.merchant_city,
    m.merchant_state,
    m.mcc,

    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        AS fraud_count,
    ROUND(
        SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(t.transaction_id),
        2
    ) AS fraud_rate,

    ROUND(SUM(t.amount), 2) AS total_transaction_value

FROM merchants m
JOIN transactions t
    ON m.merchant_id = t.merchant_id
GROUP BY
    m.merchant_id,
    m.merchant_city,
    m.merchant_state,
    m.mcc

HAVING
    COUNT(t.transaction_id) >= 50
    AND SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) >= 5

ORDER BY fraud_rate DESC
LIMIT 20;


-- 5. Customers with highest fraud exposure
SELECT
    u.user_id,
    u.person,
    u.fico_score,
    u.yearly_income_person,
    u.total_debt,

    COUNT(t.transaction_id) AS total_transactions,

    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        AS fraud_count,

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
    u.fico_score,
    u.yearly_income_person,
    u.total_debt
HAVING
    COUNT(t.transaction_id) >= 20
    AND SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) >= 3

ORDER BY fraud_count DESC, fraud_rate DESC

LIMIT 20;


-- 6. Highest financial exposure from fraud
SELECT
    u.user_id,
    u.person,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        AS fraud_count,

    ROUND(
        SUM(
            CASE
                WHEN t.is_fraud = 'Yes'
                THEN t.amount
                ELSE 0
            END
        ),
        2
    ) AS fraudulent_amount

FROM users u
JOIN cards c
    ON u.user_id = c.user_id
JOIN transactions t
    ON c.card_id = t.card_id
GROUP BY
    u.user_id,
    u.person

HAVING fraudulent_amount > 0
ORDER BY fraudulent_amount DESC
LIMIT 20;

-- This answers:
-- Which customers have the greatest monetary exposure to fraudulent transactions?



-- 7. Fraud by FICO category
SELECT
    CASE
        WHEN u.fico_score < 580 THEN 'Poor'
        WHEN u.fico_score BETWEEN 580 AND 669 THEN 'Fair'
        WHEN u.fico_score BETWEEN 670 AND 739 THEN 'Good'
        WHEN u.fico_score BETWEEN 740 AND 799 THEN 'Very Good'
        ELSE 'Exceptional'
    END AS fico_category,

    COUNT(t.transaction_id) AS total_transactions,

    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        AS fraud_count,

    ROUND(
        SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(t.transaction_id),
        2
    ) AS fraud_rate

FROM users u

JOIN cards c
    ON u.user_id = c.user_id

JOIN transactions t
    ON c.card_id = t.card_id

GROUP BY fico_category

ORDER BY fraud_rate DESC;


-- 8. Fraud vs debt-to-income ratio
SELECT
    CASE
        WHEN u.total_debt / NULLIF(u.yearly_income_person, 0) < 0.25
            THEN 'Low Debt'
        WHEN u.total_debt / NULLIF(u.yearly_income_person, 0) < 0.50
            THEN 'Moderate Debt'
        WHEN u.total_debt / NULLIF(u.yearly_income_person, 0) < 1.00
            THEN 'High Debt'
        ELSE 'Very High Debt'
    END AS debt_category,

    COUNT(t.transaction_id) AS total_transactions,

    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        AS fraud_count,

    ROUND(
        SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(t.transaction_id),
        2
    ) AS fraud_rate

FROM users u

JOIN cards c
    ON u.user_id = c.user_id

JOIN transactions t
    ON c.card_id = t.card_id
GROUP BY debt_category
ORDER BY fraud_rate DESC;


-- 9. Fraud by month
SELECT
    month,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        AS fraud_count,

    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_rate,

    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN amount ELSE 0 END),
        2
    ) AS fraudulent_value

FROM transactions
GROUP BY month
ORDER BY fraud_rate DESC;


-- 10. Fraud involving transaction errors
SELECT
    CASE
        WHEN errors IS NULL OR errors = ''
            THEN 'No Error'
        ELSE 'Error Present'
    END AS error_status,

    COUNT(*) AS total_transactions,

    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        AS fraud_count,

    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_rate

FROM transactions
GROUP BY error_status
ORDER BY fraud_rate DESC;

-- 11. High-value fraud exposure
SELECT
    CASE
        WHEN amount < 100 THEN 'Below $100'
        WHEN amount < 500 THEN '$100-$499'
        WHEN amount < 1000 THEN '$500-$999'
        WHEN amount < 5000 THEN '$1,000-$4,999'
        ELSE '$5,000+'
    END AS transaction_band,

    COUNT(*) AS total_transactions,

    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        AS fraud_count,

    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_rate,

    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN amount ELSE 0 END),
        2
    ) AS fraudulent_value

FROM transactions
GROUP BY transaction_band
ORDER BY fraudulent_value DESC;

-- 12. Final "Top Risk Areas" query
-- This produces a compact result that you can use in your project report.
SELECT
    'Overall Fraud Rate' AS risk_area,
    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS risk_value
FROM transactions

UNION ALL

SELECT
    'Total Fraudulent Transactions',
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
FROM transactions

UNION ALL

SELECT
    'Total Fraudulent Amount',
    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN amount ELSE 0 END),
        2
    )
FROM transactions;