/**
 * Tally Server Sync - Server Side Application
 * Node.js + Express + MySQL
 */

const express = require('express');
const mysql = require('mysql2/promise');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const winston = require('winston');
require('dotenv').config();

const app = express();

// Logger configuration
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
    ),
    transports: [
        new winston.transports.File({ filename: 'error.log', level: 'error' }),
        new winston.transports.File({ filename: 'combined.log' }),
        new winston.transports.Console({
            format: winston.format.simple()
        })
    ]
});

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api/', limiter);

// Database connection pool
const pool = mysql.createPool({
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'tally_sync',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

// API Key authentication middleware
const authenticateApiKey = (req, res, next) => {
    const apiKey = req.headers['authorization'];
    
    if (!apiKey) {
        return res.status(401).json({ error: 'API key required' });
    }
    
    const expectedKey = `Bearer ${process.env.API_KEY}`;
    
    if (apiKey !== expectedKey) {
        return res.status(403).json({ error: 'Invalid API key' });
    }
    
    next();
};

// Apply authentication to all API routes (except health check)
app.use('/api/', (req, res, next) => {
    if (req.path === '/health') {
        return next();
    }
    authenticateApiKey(req, res, next);
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        timestamp: new Date().toISOString(),
        version: '1.0.0'
    });
});

// Company endpoint
app.post('/api/company', async (req, res) => {
    try {
        const companyData = req.body;
        logger.info('Received company data');
        
        const connection = await pool.getConnection();
        
        try {
            // Extract company info from nested structure
            const data = companyData.BODY?.DATA || companyData;
            
            const company = {
                name: data.FldCompanyName || data.NAME || 'Unknown',
                guid: data.FldGUID || data.GUID || null,
                gstin: data.FldGSTIN || data.GSTREGISTRATIONNO || null,
                pan: data.FldPAN || data.PAN || null,
                address: data.FldAddress || data.ADDRESS || null,
                email: data.FldEmail || data.EMAIL || null,
                phone: data.FldPhone || data.PHONE || null,
                last_synced: new Date()
            };
            
            // Upsert company data
            const [result] = await connection.query(
                `INSERT INTO companies (name, guid, gstin, pan, address, email, phone, last_synced)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                 ON DUPLICATE KEY UPDATE
                 gstin = VALUES(gstin),
                 pan = VALUES(pan),
                 address = VALUES(address),
                 email = VALUES(email),
                 phone = VALUES(phone),
                 last_synced = VALUES(last_synced)`,
                [company.name, company.guid, company.gstin, company.pan, 
                 company.address, company.email, company.phone, company.last_synced]
            );
            
            logger.info(`Company data saved: ${company.name}`);
            
            res.json({ 
                success: true, 
                message: 'Company data saved successfully',
                company_id: result.insertId || result.affectedRows
            });
            
        } finally {
            connection.release();
        }
        
    } catch (error) {
        logger.error('Error saving company data:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Failed to save company data',
            details: error.message 
        });
    }
});

// Ledgers endpoint
app.post('/api/ledgers', async (req, res) => {
    try {
        const ledgers = Array.isArray(req.body) ? req.body : [req.body];
        logger.info(`Received ${ledgers.length} ledgers`);
        
        const connection = await pool.getConnection();
        
        try {
            await connection.beginTransaction();
            
            let inserted = 0;
            let updated = 0;
            
            for (const ledger of ledgers) {
                const ledgerData = {
                    name: ledger.NAME || ledger.name,
                    guid: ledger.GUID || ledger.guid || null,
                    parent: ledger.PARENT || ledger.parent || null,
                    opening_balance: parseFloat(ledger.OPENINGBALANCE || ledger.opening_balance || 0),
                    closing_balance: parseFloat(ledger.CLOSINGBALANCE || ledger.closing_balance || 0),
                    gstin: ledger.PARTYGSTIN || ledger.gstin || null,
                    phone: ledger.LEDGERPHONE || ledger.phone || null,
                    email: ledger.LEDGEREMAIL || ledger.email || null,
                    address: ledger.ADDRESS || ledger.address || null,
                    last_synced: new Date()
                };
                
                const [result] = await connection.query(
                    `INSERT INTO ledgers (name, guid, parent, opening_balance, closing_balance, 
                                         gstin, phone, email, address, last_synced)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                     ON DUPLICATE KEY UPDATE
                     parent = VALUES(parent),
                     opening_balance = VALUES(opening_balance),
                     closing_balance = VALUES(closing_balance),
                     gstin = VALUES(gstin),
                     phone = VALUES(phone),
                     email = VALUES(email),
                     address = VALUES(address),
                     last_synced = VALUES(last_synced)`,
                    [ledgerData.name, ledgerData.guid, ledgerData.parent, 
                     ledgerData.opening_balance, ledgerData.closing_balance,
                     ledgerData.gstin, ledgerData.phone, ledgerData.email, 
                     ledgerData.address, ledgerData.last_synced]
                );
                
                if (result.insertId) {
                    inserted++;
                } else {
                    updated++;
                }
            }
            
            await connection.commit();
            
            logger.info(`Ledgers saved: ${inserted} inserted, ${updated} updated`);
            
            res.json({ 
                success: true, 
                message: 'Ledgers saved successfully',
                inserted,
                updated,
                total: ledgers.length
            });
            
        } catch (error) {
            await connection.rollback();
            throw error;
        } finally {
            connection.release();
        }
        
    } catch (error) {
        logger.error('Error saving ledgers:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Failed to save ledgers',
            details: error.message 
        });
    }
});

// Stock items endpoint
app.post('/api/stock-items', async (req, res) => {
    try {
        const stockItems = Array.isArray(req.body) ? req.body : [req.body];
        logger.info(`Received ${stockItems.length} stock items`);
        
        const connection = await pool.getConnection();
        
        try {
            await connection.beginTransaction();
            
            let inserted = 0;
            let updated = 0;
            
            for (const item of stockItems) {
                const stockData = {
                    name: item.NAME || item.name,
                    guid: item.GUID || item.guid || null,
                    parent: item.PARENT || item.parent || null,
                    base_units: item.BASEUNITS || item.base_units || null,
                    opening_balance: parseFloat(item.OPENINGBALANCE || item.opening_balance || 0),
                    opening_value: parseFloat(item.OPENINGVALUE || item.opening_value || 0),
                    closing_balance: parseFloat(item.CLOSINGBALANCE || item.closing_balance || 0),
                    closing_value: parseFloat(item.CLOSINGVALUE || item.closing_value || 0),
                    hsn_code: item.HSNCODE || item.hsn_code || null,
                    gst_applicable: item.GSTAPPLICABLE || item.gst_applicable || null,
                    last_synced: new Date()
                };
                
                const [result] = await connection.query(
                    `INSERT INTO stock_items (name, guid, parent, base_units, opening_balance, 
                                              opening_value, closing_balance, closing_value, 
                                              hsn_code, gst_applicable, last_synced)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                     ON DUPLICATE KEY UPDATE
                     parent = VALUES(parent),
                     base_units = VALUES(base_units),
                     opening_balance = VALUES(opening_balance),
                     opening_value = VALUES(opening_value),
                     closing_balance = VALUES(closing_balance),
                     closing_value = VALUES(closing_value),
                     hsn_code = VALUES(hsn_code),
                     gst_applicable = VALUES(gst_applicable),
                     last_synced = VALUES(last_synced)`,
                    [stockData.name, stockData.guid, stockData.parent, stockData.base_units,
                     stockData.opening_balance, stockData.opening_value, 
                     stockData.closing_balance, stockData.closing_value,
                     stockData.hsn_code, stockData.gst_applicable, stockData.last_synced]
                );
                
                if (result.insertId) {
                    inserted++;
                } else {
                    updated++;
                }
            }
            
            await connection.commit();
            
            logger.info(`Stock items saved: ${inserted} inserted, ${updated} updated`);
            
            res.json({ 
                success: true, 
                message: 'Stock items saved successfully',
                inserted,
                updated,
                total: stockItems.length
            });
            
        } catch (error) {
            await connection.rollback();
            throw error;
        } finally {
            connection.release();
        }
        
    } catch (error) {
        logger.error('Error saving stock items:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Failed to save stock items',
            details: error.message 
        });
    }
});

// Vouchers endpoint
app.post('/api/vouchers', async (req, res) => {
    try {
        const vouchers = Array.isArray(req.body) ? req.body : [req.body];
        logger.info(`Received ${vouchers.length} vouchers`);
        
        const connection = await pool.getConnection();
        
        try {
            await connection.beginTransaction();
            
            let inserted = 0;
            let updated = 0;
            
            for (const voucher of vouchers) {
                const voucherData = {
                    guid: voucher.GUID || voucher.guid || null,
                    date: voucher.DATE || voucher.date,
                    voucher_type: voucher.VOUCHERTYPENAME || voucher.voucher_type,
                    voucher_number: voucher.VOUCHERNUMBER || voucher.voucher_number,
                    reference: voucher.REFERENCE || voucher.reference || null,
                    reference_date: voucher.REFERENCEDATE || voucher.reference_date || null,
                    narration: voucher.NARRATION || voucher.narration || null,
                    party_name: voucher.PARTYNAME || voucher.party_name || null,
                    amount: parseFloat(voucher.AMOUNT || voucher.amount || 0),
                    is_invoice: voucher.ISINVOICE || voucher.is_invoice || 'No',
                    last_synced: new Date()
                };
                
                const [result] = await connection.query(
                    `INSERT INTO vouchers (guid, date, voucher_type, voucher_number, reference, 
                                          reference_date, narration, party_name, amount, 
                                          is_invoice, last_synced)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                     ON DUPLICATE KEY UPDATE
                     date = VALUES(date),
                     voucher_type = VALUES(voucher_type),
                     voucher_number = VALUES(voucher_number),
                     reference = VALUES(reference),
                     reference_date = VALUES(reference_date),
                     narration = VALUES(narration),
                     party_name = VALUES(party_name),
                     amount = VALUES(amount),
                     is_invoice = VALUES(is_invoice),
                     last_synced = VALUES(last_synced)`,
                    [voucherData.guid, voucherData.date, voucherData.voucher_type, 
                     voucherData.voucher_number, voucherData.reference, voucherData.reference_date,
                     voucherData.narration, voucherData.party_name, voucherData.amount,
                     voucherData.is_invoice, voucherData.last_synced]
                );
                
                if (result.insertId) {
                    inserted++;
                } else {
                    updated++;
                }
            }
            
            await connection.commit();
            
            logger.info(`Vouchers saved: ${inserted} inserted, ${updated} updated`);
            
            res.json({ 
                success: true, 
                message: 'Vouchers saved successfully',
                inserted,
                updated,
                total: vouchers.length
            });
            
        } catch (error) {
            await connection.rollback();
            throw error;
        } finally {
            connection.release();
        }
        
    } catch (error) {
        logger.error('Error saving vouchers:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Failed to save vouchers',
            details: error.message 
        });
    }
});

// Get sync status
app.get('/api/sync-status', async (req, res) => {
    try {
        const connection = await pool.getConnection();
        
        try {
            const [companies] = await connection.query('SELECT COUNT(*) as count FROM companies');
            const [ledgers] = await connection.query('SELECT COUNT(*) as count FROM ledgers');
            const [stockItems] = await connection.query('SELECT COUNT(*) as count FROM stock_items');
            const [vouchers] = await connection.query('SELECT COUNT(*) as count FROM vouchers');
            
            const [lastSync] = await connection.query(
                `SELECT MAX(last_synced) as last_sync FROM (
                    SELECT last_synced FROM companies
                    UNION ALL
                    SELECT last_synced FROM ledgers
                    UNION ALL
                    SELECT last_synced FROM stock_items
                    UNION ALL
                    SELECT last_synced FROM vouchers
                ) as all_syncs`
            );
            
            res.json({
                success: true,
                data: {
                    companies: companies[0].count,
                    ledgers: ledgers[0].count,
                    stock_items: stockItems[0].count,
                    vouchers: vouchers[0].count,
                    last_sync: lastSync[0].last_sync
                }
            });
            
        } finally {
            connection.release();
        }
        
    } catch (error) {
        logger.error('Error getting sync status:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Failed to get sync status',
            details: error.message 
        });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    logger.error('Unhandled error:', err);
    res.status(500).json({ 
        success: false, 
        error: 'Internal server error',
        details: process.env.NODE_ENV === 'development' ? err.message : undefined
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ 
        success: false, 
        error: 'Endpoint not found' 
    });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    logger.info(`Tally Sync Server running on port ${PORT}`);
    logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
    logger.info('SIGTERM signal received: closing HTTP server');
    await pool.end();
    process.exit(0);
});
