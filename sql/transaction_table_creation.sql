-- ============================================================
-- TRANSACTIONS TABLE
-- ============================================================

USE fraud_detection;


CREATE TABLE transactions (
    transaction_id BIGINT NOT NULL,
    card_id INT,
    merchant_id INT,
    year INT,
    month INT,
    day INT,
    time VARCHAR(20),
    amount DECIMAL(15,2),
    use_chip VARCHAR(100),
    errors VARCHAR(255),
    is_fraud VARCHAR(10),

    PRIMARY KEY (transaction_id),

    CONSTRAINT fk_transactions_cards
        FOREIGN KEY (card_id)
        REFERENCES cards(card_id),

    CONSTRAINT fk_transactions_merchants
        FOREIGN KEY (merchant_id)
        REFERENCES merchants(merchant_id)
);

