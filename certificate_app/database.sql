CREATE DATABASE IF NOT EXISTS certificates_db;
USE certificates_db;

CREATE TABLE IF NOT EXISTS certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    certificate_type VARCHAR(50),
    income DECIMAL(10,2),
    community VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
