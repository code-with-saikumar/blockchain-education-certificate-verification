-- ====================================================
-- Database: edu_blockchain_certification
-- NOTE: Using 'cation' as found in your original app2.py
-- ====================================================

CREATE DATABASE IF NOT EXISTS changee;
USE changee;

-- ====================================================
-- Table: users (CORRECTED)
-- ====================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'institution', 'student', 'verifier') NOT NULL,
    -- CRITICAL NEW COLUMN: account_status for overall access control
    account_status ENUM('pending', 'approved', 'rejected', 'hold') DEFAULT 'pending' NOT NULL, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================
-- Table: institutions
-- ====================================================
CREATE TABLE IF NOT EXISTS institutions (
    id INT PRIMARY KEY,  -- same as users.id
    name VARCHAR(150) NOT NULL,
    approved_by INT DEFAULT NULL,
    -- Keep status here for historical/secondary tracking, but primary check is users.account_status
    status ENUM('pending','approved','rejected') DEFAULT 'pending', 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE, -- Ensure CASCADE delete
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- ====================================================
-- Table: certificates
-- ====================================================
CREATE TABLE IF NOT EXISTS certificates (
    id VARCHAR(8) PRIMARY KEY, -- New: AR + 6-digit number
    student_id INT NOT NULL,
    institution_id INT NOT NULL,
    course_name VARCHAR(150) NOT NULL,
    cgpa VARCHAR(50),
    issue_year YEAR NOT NULL,
    roll_number VARCHAR(50),
    father_name VARCHAR(100),
    mother_name VARCHAR(100),
    gender VARCHAR(20),
    mobile_number VARCHAR(20),
    year_of_joining YEAR,
    certificate_data TEXT NOT NULL,
    pdf_content LONGBLOB, -- New: to store PDF binary data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (institution_id) REFERENCES institutions(id)
);

-- ====================================================
-- Table: blockchain
-- ====================================================
CREATE TABLE IF NOT EXISTS blockchain (
    block_id INT AUTO_INCREMENT PRIMARY KEY,
    certificate_id VARCHAR(8) NOT NULL,
    previous_hash VARCHAR(64) NOT NULL,
    current_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (certificate_id) REFERENCES certificates(id)
);

-- ====================================================
-- Table: verifications
-- ====================================================
CREATE TABLE IF NOT EXISTS verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    verifier_id INT NOT NULL,
    certificate_id VARCHAR(8) NOT NULL,
    result ENUM('valid','invalid') NOT NULL,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (verifier_id) REFERENCES users(id),
    FOREIGN KEY (certificate_id) REFERENCES certificates(id)
);