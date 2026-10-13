-- setup_database.sql
-- SQL script to manually set up the database
-- You can run this in MySQL Workbench or command line

-- Create database
CREATE DATABASE IF NOT EXISTS employee_db;

-- Use the database
USE employee_db;

-- Create employees table
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Verify table creation
DESCRIBE employees;

-- Insert sample data for testing
INSERT INTO employees (name, email, department, salary) 
VALUES 
    ('John Doe', 'john.doe@company.com', 'Engineering', 75000.00),
    ('Jane Smith', 'jane.smith@company.com', 'Marketing', 65000.00),
    ('Mike Johnson', 'mike.johnson@company.com', 'Sales', 60000.00)
ON DUPLICATE KEY UPDATE name=name;  -- Prevents error if data already exists

-- Verify data insertion
SELECT * FROM employees;

-- Show success message
SELECT '✅ Database setup completed successfully!' AS Status;
