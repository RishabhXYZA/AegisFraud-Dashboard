-- ============================================================
-- MERCHANTS TABLE
-- ============================================================

USE fraud_detection;


CREATE TABLE merchants (
    merchant_id INT NOT NULL,
    merchant_source_id INT,
    merchant_city VARCHAR(150),
    merchant_state VARCHAR(50),
    zip DECIMAL(10,2),
    mcc INT,

    PRIMARY KEY (merchant_id)
);