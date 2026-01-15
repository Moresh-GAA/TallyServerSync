/**
 * Database Setup Script
 * Creates all necessary tables for Tally Sync
 */

const mysql = require('mysql2/promise');
require('dotenv').config();

const createTables = async () => {
    let connection;
    
    try {
        // Connect to MySQL server (without database)
        connection = await mysql.createConnection({
            host: process.env.DB_HOST || 'localhost',
            user: process.env.DB_USER || 'root',
            password: process.env.DB_PASSWORD || ''
        });
        
        console.log('Connected to MySQL server');
        
        // Create database if not exists
        const dbName = process.env.DB_NAME || 'tally_sync';
        await connection.query(`CREATE DATABASE IF NOT EXISTS ${dbName}`);
        console.log(`Database '${dbName}' created or already exists`);
        
        // Use the database
        await connection.query(`USE ${dbName}`);
        
        // Create companies table
        await connection.query(`
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        `);
        console.log('✓ Companies table created');
        
        // Create ledgers table
        await connection.query(`
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        `);
        console.log('✓ Ledgers table created');
        
        // Create stock_items table
        await connection.query(`
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        `);
        console.log('✓ Stock items table created');
        
        // Create vouchers table
        await connection.query(`
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        `);
        console.log('✓ Vouchers table created');
        
        // Create sync_log table for tracking sync operations
        await connection.query(`
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        `);
        console.log('✓ Sync log table created');
        
        console.log('\n✅ Database setup completed successfully!');
        console.log('\nTables created:');
        console.log('  - companies');
        console.log('  - ledgers');
        console.log('  - stock_items');
        console.log('  - vouchers');
        console.log('  - sync_log');
        console.log('\nYou can now start the server with: npm start');
        
    } catch (error) {
        console.error('❌ Error setting up database:', error.message);
        process.exit(1);
    } finally {
        if (connection) {
            await connection.end();
        }
    }
};

// Run setup
createTables();
