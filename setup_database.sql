-- ========================================================
-- DIABETIC RETINOPATHY DETECTION - DATABASE SETUP SCRIPT
-- ========================================================
-- This script creates the complete database structure
-- ========================================================

-- Step 1: Create Database
CREATE DATABASE IF NOT EXISTS diabetic_retinopathy_db;

-- Step 2: Use the database
USE diabetic_retinopathy_db;

-- Step 3: Create the main table (matching the code requirements)
CREATE TABLE IF NOT EXISTS THEGREAT (
    USERNAME VARCHAR(100) PRIMARY KEY,
    PASSWORD VARCHAR(255) NOT NULL,
    PREDICT VARCHAR(50) DEFAULT NULL,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 4: Create a MySQL user for the application
CREATE USER IF NOT EXISTS 'dr_user'@'localhost' IDENTIFIED BY 'dr_password_2024';

-- Step 5: Grant all privileges to the user on this database
GRANT ALL PRIVILEGES ON diabetic_retinopathy_db.* TO 'dr_user'@'localhost';
FLUSH PRIVILEGES;

-- Step 6: Insert a test user for login testing
INSERT INTO THEGREAT (USERNAME, PASSWORD) VALUES ('admin', 'admin123') 
ON DUPLICATE KEY UPDATE USERNAME=USERNAME;

INSERT INTO THEGREAT (USERNAME, PASSWORD) VALUES ('testuser', 'test123') 
ON DUPLICATE KEY UPDATE USERNAME=USERNAME;

-- Step 7: Display confirmation
SELECT 'Database setup completed successfully!' AS Status;
SELECT 'Test users created: admin/admin123 and testuser/test123' AS Info;
SELECT * FROM THEGREAT;
