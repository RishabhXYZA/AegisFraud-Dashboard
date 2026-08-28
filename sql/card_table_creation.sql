-- ============================================================
-- CARDS TABLE
-- ============================================================

USE fraud_detection;

CREATE TABLE cards (
    card_id INT NOT NULL,
    card_index INT,
    card_brand VARCHAR(50),
    card_type VARCHAR(50),
    has_chip VARCHAR(20),
    cards_issued INT,
    credit_limit DECIMAL(15,2),
    year_pin_last_changed INT,
    card_on_dark_web VARCHAR(20),
    expire_month INT,
    expire_year INT,
    opening_month INT,
    opening_year INT,
    user_id INT,
    card_last4 INT,

    PRIMARY KEY (card_id),

    CONSTRAINT fk_cards_users
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
);