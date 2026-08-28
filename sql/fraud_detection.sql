USE fraud_detection;
-- 1. Overall fraud distribution
SELECT
    is_fraud,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY is_fraud;

-- Once we know whether your values are 0/1, True/False, etc., we can write the exact fraud queries.

-- 2. Fraud rate
SELECT
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraudulent_transactions,
    SUM(CASE WHEN is_fraud = 'No' THEN 1 ELSE 0 END) AS legitimate_transactions,
    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_percentage
FROM transactions;


-- 3. Fraud by payment method
SELECT
    use_chip,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraudulent_transactions,
    SUM(CASE WHEN is_fraud = 'No' THEN 1 ELSE 0 END) AS legitimate_transactions,
    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_rate
FROM transactions
GROUP BY use_chip
ORDER BY fraud_rate DESC;


-- 4. Fraud by year
SELECT
    year,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraudulent_transactions,
    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_rate
FROM transactions
GROUP BY year
ORDER BY year;

-- This can show whether fraud activity increased or decreased over time.


-- 4. Fraud by month
SELECT
    month,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraudulent_transactions,
    ROUND(
        SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS fraud_rate
FROM transactions
GROUP BY month
ORDER BY month;


-- 5. Fraud by transaction amount
-- Let's compare legitimate and fraudulent transaction values:
SELECT
    is_fraud,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(AVG(amount), 2) AS average_amount,
    ROUND(MIN(amount), 2) AS minimum_amount,
    ROUND(MAX(amount), 2) AS maximum_amount
FROM transactions
GROUP BY is_fraud;

-- This is particularly important because it tells us whether fraudulent transactions tend to have different amounts from legitimate transactions.

-- 6. High-value fraudulent transactions
SELECT
    transaction_id,
    card_id,
    merchant_id,
    year,
    month,
    day,
    time,
    amount,
    use_chip,
    errors
FROM transactions
WHERE is_fraud = 'Yes'
ORDER BY amount DESC
LIMIT 20;


-- 7. Fraud by merchant
-- Once we have the basic transaction-level results, we'll connect transactions with merchants:
SELECT
    m.merchant_id,
    m.merchant_city,
    m.merchant_state,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END) AS fraudulent_transactions,
    ROUND(
        SUM(CASE WHEN t.is_fraud = 'Yes' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(t.transaction_id),
        2
    ) AS fraud_rate
FROM merchants m
JOIN transactions t
    ON m.merchant_id = t.merchant_id
GROUP BY
    m.merchant_id,
    m.merchant_city,
    m.merchant_state
HAVING fraudulent_transactions > 0
ORDER BY fraud_rate DESC;