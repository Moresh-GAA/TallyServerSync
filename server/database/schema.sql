-- Tally Sync Database Schema
-- MySQL 5.7+ / MariaDB 10.3+

-- Create database
CREATE DATABASE IF NOT EXISTS tally_sync
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE tally_sync;

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    guid VARCHAR(255) UNIQUE,
    gstin VARCHAR(50),
    pan VARCHAR(20),
    address TEXT,
    email VARCHAR(255),
    phone VARCHAR(50),
    last_synced DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_guid (guid),
    INDEX idx_gstin (gstin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ledgers table
CREATE TABLE IF NOT EXISTS ledgers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    guid VARCHAR(255) UNIQUE,
    parent VARCHAR(255),
    opening_balance DECIMAL(15, 2) DEFAULT 0,
    closing_balance DECIMAL(15, 2) DEFAULT 0,
    gstin VARCHAR(50),
    phone VARCHAR(50),
    email VARCHAR(255),
    address TEXT,
    last_synced DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_guid (guid),
    INDEX idx_parent (parent),
    INDEX idx_last_synced (last_synced)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Stock items table
CREATE TABLE IF NOT EXISTS stock_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    guid VARCHAR(255) UNIQUE,
    parent VARCHAR(255),
    base_units VARCHAR(50),
    opening_balance DECIMAL(15, 3) DEFAULT 0,
    opening_value DECIMAL(15, 2) DEFAULT 0,
    closing_balance DECIMAL(15, 3) DEFAULT 0,
    closing_value DECIMAL(15, 2) DEFAULT 0,
    hsn_code VARCHAR(50),
    gst_applicable VARCHAR(10),
    last_synced DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_guid (guid),
    INDEX idx_parent (parent),
    INDEX idx_hsn (hsn_code),
    INDEX idx_last_synced (last_synced)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Vouchers table
CREATE TABLE IF NOT EXISTS vouchers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    guid VARCHAR(255) UNIQUE,
    date DATE NOT NULL,
    voucher_type VARCHAR(100) NOT NULL,
    voucher_number VARCHAR(100),
    reference VARCHAR(255),
    reference_date DATE,
    narration TEXT,
    party_name VARCHAR(255),
    amount DECIMAL(15, 2) DEFAULT 0,
    is_invoice VARCHAR(10),
    last_synced DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_guid (guid),
    INDEX idx_date (date),
    INDEX idx_voucher_type (voucher_type),
    INDEX idx_voucher_number (voucher_number),
    INDEX idx_party_name (party_name),
    INDEX idx_last_synced (last_synced)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sync log table
CREATE TABLE IF NOT EXISTS sync_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,
    records_inserted INT DEFAULT 0,
    records_updated INT DEFAULT 0,
    records_total INT DEFAULT 0,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    sync_started DATETIME,
    sync_completed DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sync_type (sync_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
