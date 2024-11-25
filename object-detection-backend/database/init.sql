CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_input TEXT,
    detected_object VARCHAR(100),
    matched_product VARCHAR(100),
    is_correct BOOLEAN,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE product_recognition_stats (
    product_name VARCHAR(100) PRIMARY KEY,
    total_attempts INT,
    correct_recognitions INT,
    recognition_rate FLOAT
);