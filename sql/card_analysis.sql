-- 1. Card distribution
SELECT
    card_brand,
    COUNT(*) AS card_count
FROM cards
GROUP BY card_brand
ORDER BY card_count DESC;


-- 2. Card type distribution
SELECT
    card_type,
    COUNT(*) AS card_count
FROM cards
GROUP BY card_type
ORDER BY card_count DESC;


-- 3. Credit limit statistics
SELECT
    MIN(credit_limit) AS minimum_limit,
    MAX(credit_limit) AS maximum_limit,
    ROUND(AVG(credit_limit), 2) AS average_limit
FROM cards;


-- 4. Highest credit limits
SELECT
    card_id,
    user_id,
    card_brand,
    card_type,
    credit_limit
FROM cards
ORDER BY credit_limit DESC
LIMIT 20;


-- 5. Card transaction activity
SELECT
    c.card_id,
    c.user_id,
    c.card_brand,
    c.card_type,
    COUNT(t.transaction_id) AS transaction_count,
    ROUND(SUM(t.amount), 2) AS total_spent
FROM cards c
JOIN transactions t
    ON c.card_id = t.card_id
GROUP BY
    c.card_id,
    c.user_id,
    c.card_brand,
    c.card_type
ORDER BY total_spent DESC
LIMIT 20;