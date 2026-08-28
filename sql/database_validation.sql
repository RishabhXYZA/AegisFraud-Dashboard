USE fraud_detection;

-- ============================================
-- 1. Check total records
-- ============================================

SELECT 'users' AS table_name, COUNT(*) AS total_records
FROM users

UNION ALL

SELECT 'cards', COUNT(*)
FROM cards

UNION ALL

SELECT 'merchants', COUNT(*)
FROM merchants

UNION ALL

SELECT 'transactions', COUNT(*)
FROM transactions;


-- ============================================
-- 2. Check NULL values in users
-- ============================================

SELECT
    SUM(user_id IS NULL) AS missing_user_id,
    SUM(person IS NULL) AS missing_person,
    SUM(current_age IS NULL) AS missing_age,
    SUM(gender IS NULL) AS missing_gender,
    SUM(yearly_income_person IS NULL) AS missing_income,
    SUM(total_debt IS NULL) AS missing_debt,
    SUM(fico_score IS NULL) AS missing_fico
FROM users;


-- ============================================
-- 3. Check NULL values in cards
-- ============================================

SELECT
    SUM(card_id IS NULL) AS missing_card_id,
    SUM(user_id IS NULL) AS missing_user_id,
    SUM(card_brand IS NULL) AS missing_brand,
    SUM(card_type IS NULL) AS missing_card_type,
    SUM(credit_limit IS NULL) AS missing_credit_limit
FROM cards;


-- ============================================
-- 4. Check NULL values in merchants
-- ============================================

SELECT
    SUM(merchant_id IS NULL) AS missing_merchant_id,
    SUM(merchant_source_id IS NULL) AS missing_source_id,
    SUM(merchant_city IS NULL) AS missing_city,
    SUM(merchant_state IS NULL) AS missing_state,
    SUM(mcc IS NULL) AS missing_mcc
FROM merchants;


-- ============================================
-- 5. Check NULL values in transactions
-- ============================================
SELECT
    SUM(transaction_id IS NULL) AS missing_transaction_id,
    SUM(card_id IS NULL) AS missing_card_id,
    SUM(merchant_id IS NULL) AS missing_merchant_id,
    SUM(year IS NULL) AS missing_year,
    SUM(month IS NULL) AS missing_month,
    SUM(day IS NULL) AS missing_day,
    SUM(time IS NULL) AS missing_time,
    SUM(amount IS NULL) AS missing_amount,
    SUM(use_chip IS NULL) AS missing_use_chip,
    SUM(errors IS NULL) AS missing_errors,
    SUM(is_fraud IS NULL) AS missing_is_fraud
FROM transactions;

-- =====================================================
-- PRIMARY KEY VALIDATION
-- =====================================================

-- Users
SELECT user_id, COUNT(*) AS occurrences
FROM users
GROUP BY user_id
HAVING COUNT(*) > 1;

-- Cards
SELECT card_id, COUNT(*) AS occurrences
FROM cards
GROUP BY card_id
HAVING COUNT(*) > 1;

-- Merchants
SELECT merchant_id, COUNT(*) AS occurrences
FROM merchants
GROUP BY merchant_id
HAVING COUNT(*) > 1;

-- Transactions
SELECT transaction_id, COUNT(*) AS occurrences
FROM transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;


-- =====================================================
-- FOREIGN KEY VALIDATION
-- =====================================================
SELECT COUNT(*) AS orphan_cards
FROM cards c
LEFT JOIN users u
    ON c.user_id = u.user_id
WHERE u.user_id IS NULL;


SELECT COUNT(*) AS orphan_transaction_cards
FROM transactions t
LEFT JOIN cards c
    ON t.card_id = c.card_id
WHERE c.card_id IS NULL;


SELECT COUNT(*) AS orphan_transaction_merchants
FROM transactions t
LEFT JOIN merchants m
    ON t.merchant_id = m.merchant_id
WHERE m.merchant_id IS NULL;


SELECT COUNT(*) AS transactions_without_valid_user
FROM transactions t
LEFT JOIN cards c
    ON t.card_id = c.card_id
LEFT JOIN users u
    ON c.user_id = u.user_id
WHERE u.user_id IS NULL;


SELECT
    TABLE_NAME,
    CONSTRAINT_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'fraud_detection'
  AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME, CONSTRAINT_NAME;

SELECT
    TABLE_NAME,
    COLUMN_NAME,
    CONSTRAINT_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'fraud_detection'
  AND CONSTRAINT_NAME = 'PRIMARY'
ORDER BY TABLE_NAME;