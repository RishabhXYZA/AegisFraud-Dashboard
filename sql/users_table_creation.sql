-- ============================================================
-- USERS TABLE
-- ============================================================

USE fraud_detection;

CREATE TABLE users (
    user_id INT NOT NULL,
    person VARCHAR(255),
    current_age INT,
    retirement_age INT,
    birth_year INT,
    birth_month INT,
    gender VARCHAR(20),
    city VARCHAR(100),
    state VARCHAR(50),
    zipcode INT,
    per_capita_income_zipcode DECIMAL(15,2),
    yearly_income_person DECIMAL(15,2),
    total_debt DECIMAL(15,2),
    fico_score INT,

    PRIMARY KEY (user_id)
);