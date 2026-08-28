-- 1. Customer transaction summary
SELECT
    u.user_id,
    u.person,
    COUNT(t.transaction_id) AS transaction_count,
    ROUND(SUM(t.amount), 2) AS total_spent,
    ROUND(AVG(t.amount), 2) AS average_transaction
FROM users u
JOIN cards c
    ON u.user_id = c.user_id
JOIN transactions t
    ON c.card_id = t.card_id
GROUP BY
    u.user_id,
    u.person
ORDER BY total_spent DESC;

-- Top 20 customers by spending
SELECT
    u.user_id,
    u.person,
    COUNT(t.transaction_id) AS transaction_count,
    ROUND(SUM(t.amount), 2) AS total_spent
FROM users u
JOIN cards c
    ON u.user_id = c.user_id
JOIN transactions t
    ON c.card_id = t.card_id
GROUP BY
    u.user_id,
    u.person
ORDER BY total_spent DESC
LIMIT 20;


-- 2. Highest transaction frequency
SELECT
    u.user_id,
    u.person,
    COUNT(t.transaction_id) AS transaction_count
FROM users u
JOIN cards c
    ON u.user_id = c.user_id
JOIN transactions t
    ON c.card_id = t.card_id
GROUP BY
    u.user_id,
    u.person
ORDER BY transaction_count DESC
LIMIT 20;


-- 3. Customer spending vs income
-- This is particularly useful for fraud analysis.
SELECT
    u.user_id,
    u.person,
    u.yearly_income_person,
    ROUND(SUM(t.amount), 2) AS total_spent,
    ROUND((SUM(t.amount) / NULLIF(u.yearly_income_person, 0)) * 100,2) AS spending_income_percentage
FROM users u
JOIN cards c
    ON u.user_id = c.user_id
JOIN transactions t
    ON c.card_id = t.card_id
GROUP BY
    u.user_id,
    u.person,
    u.yearly_income_person
ORDER BY spending_income_percentage DESC;


-- 4. High debt + high spending
SELECT
    u.user_id,
    u.person,
    u.yearly_income_person,
    u.total_debt,
    u.fico_score,
    ROUND(SUM(t.amount), 2) AS total_spent
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
    u.total_debt > u.yearly_income_person
    AND SUM(t.amount) > 10000
ORDER BY total_spent DESC;