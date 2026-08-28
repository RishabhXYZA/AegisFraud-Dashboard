-- 1. Top merchants by transaction volume
SELECT
    m.merchant_id,
    m.merchant_city,
    m.merchant_state,
    COUNT(t.transaction_id) AS transaction_count
FROM merchants m
JOIN transactions t
    ON m.merchant_id = t.merchant_id
GROUP BY
    m.merchant_id,
    m.merchant_city,
    m.merchant_state
ORDER BY transaction_count DESC
LIMIT 20;


-- 2. Top merchants by transaction value
SELECT
    m.merchant_id,
    m.merchant_city,
    m.merchant_state,
    COUNT(t.transaction_id) AS transaction_count,
    ROUND(SUM(t.amount), 2) AS total_transaction_value
FROM merchants m
JOIN transactions t
    ON m.merchant_id = t.merchant_id
GROUP BY
    m.merchant_id,
    m.merchant_city,
    m.merchant_state
ORDER BY total_transaction_value DESC
LIMIT 20;


-- 3. MCC analysis
SELECT
    m.mcc,
    COUNT(t.transaction_id) AS transaction_count,
    ROUND(SUM(t.amount), 2) AS total_value,
    ROUND(AVG(t.amount), 2) AS average_transaction
FROM merchants m
JOIN transactions t
    ON m.merchant_id = t.merchant_id
GROUP BY m.mcc
ORDER BY total_value DESC;