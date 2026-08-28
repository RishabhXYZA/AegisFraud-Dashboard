USE fraud_detection;

-- 1. Total records
SELECT COUNT(*) AS total_users
FROM users

UNION ALL

SELECT COUNT(*) AS total_cards
FROM cards

UNION ALL

SELECT COUNT(*) AS total_merchants
FROM merchants

UNION ALL

SELECT COUNT(*) AS total_transactions
FROM transactions;


-- 2. Basic user demographics
SELECT gender,COUNT(*) AS user_count
FROM users
GROUP BY gender
ORDER BY user_count DESC;

-- Users by state
SELECT state,COUNT(*) AS user_count
FROM users
GROUP BY state
ORDER BY user_count DESC;


-- Users by city
SELECT city,COUNT(*) AS user_count
FROM users
GROUP BY city
ORDER BY user_count DESC
LIMIT 20;

-- 3. Age analysis
SELECT
    MIN(current_age) AS minimum_age,
    MAX(current_age) AS maximum_age,
    ROUND(AVG(current_age), 2) AS average_age
FROM users;

-- Age Groups
SELECT
    CASE
        WHEN current_age < 25 THEN 'Under 25'
        WHEN current_age BETWEEN 25 AND 34 THEN '25-34'
        WHEN current_age BETWEEN 35 AND 44 THEN '35-44'
        WHEN current_age BETWEEN 45 AND 54 THEN '45-54'
        WHEN current_age BETWEEN 55 AND 64 THEN '55-64'
        ELSE '65+'
    END AS age_group,
    COUNT(*) AS user_count
FROM users
GROUP BY age_group
ORDER BY user_count DESC;

-- 4. Income analysis
SELECT
    MIN(yearly_income_person) AS minimum_income,
    MAX(yearly_income_person) AS maximum_income,
    ROUND(AVG(yearly_income_person), 2) AS average_income
FROM users;

-- Top 20 highest-income users
SELECT
    user_id,
    person,
    yearly_income_person,
    total_debt,
    fico_score
FROM users
ORDER BY yearly_income_person DESC
LIMIT 20;

-- 5. Debt analysis
SELECT
    MIN(total_debt) AS minimum_debt,
    MAX(total_debt) AS maximum_debt,
    ROUND(AVG(total_debt), 2) AS average_debt
FROM users;

-- Top 20 users by debt:
SELECT
    user_id,
    person,
    yearly_income_person,
    total_debt,
    fico_score
FROM users
ORDER BY total_debt DESC
LIMIT 20;

-- 6. FICO score analysis
SELECT
    MIN(fico_score) AS minimum_fico,
    MAX(fico_score) AS maximum_fico,
    ROUND(AVG(fico_score), 2) AS average_fico
FROM users;

-- FICO score categories:
SELECT
    CASE
        WHEN fico_score < 580 THEN 'Poor'
        WHEN fico_score BETWEEN 580 AND 669 THEN 'Fair'
        WHEN fico_score BETWEEN 670 AND 739 THEN 'Good'
        WHEN fico_score BETWEEN 740 AND 799 THEN 'Very Good'
        ELSE 'Exceptional'
    END AS fico_category,
    COUNT(*) AS user_count
FROM users
GROUP BY fico_category
ORDER BY user_count DESC;

