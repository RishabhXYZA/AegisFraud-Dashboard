-- 1. Overall transaction statistics
SELECT
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_transaction_value,
    ROUND(AVG(amount), 2) AS average_transaction,
    MIN(amount) AS minimum_transaction,
    MAX(amount) AS maximum_transaction
FROM transactions;


-- 2. Transactions by year
SELECT
    year,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_value,
    ROUND(AVG(amount), 2) AS average_value
FROM transactions
GROUP BY year
ORDER BY year;


-- 3.Transactions by month
SELECT
    month,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_value
FROM transactions
GROUP BY month
ORDER BY month;


-- 4.Transactions by payment method
-- Your dataset has use_chip, so:
SELECT
    use_chip,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_value,
    ROUND(AVG(amount), 2) AS average_amount
FROM transactions
GROUP BY use_chip
ORDER BY transaction_count DESC;


-- 5. Transactions with errors
SELECT
    errors,
    COUNT(*) AS transaction_count
FROM transactions
WHERE errors IS NOT NULL
GROUP BY errors
ORDER BY transaction_count DESC;