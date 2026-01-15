-- Useful SQL Queries for Tally Sync Database

-- ============================================
-- SUMMARY QUERIES
-- ============================================

-- Get record counts for all tables
SELECT 
    (SELECT COUNT(*) FROM companies) as companies,
    (SELECT COUNT(*) FROM ledgers) as ledgers,
    (SELECT COUNT(*) FROM stock_items) as stock_items,
    (SELECT COUNT(*) FROM vouchers) as vouchers;

-- Get last sync times for all tables
SELECT 
    'companies' as table_name, 
    MAX(last_synced) as last_sync,
    COUNT(*) as total_records
FROM companies
UNION ALL
SELECT 'ledgers', MAX(last_synced), COUNT(*) FROM ledgers
UNION ALL
SELECT 'stock_items', MAX(last_synced), COUNT(*) FROM stock_items
UNION ALL
SELECT 'vouchers', MAX(last_synced), COUNT(*) FROM vouchers;

-- ============================================
-- COMPANY QUERIES
-- ============================================

-- Get all companies
SELECT * FROM companies ORDER BY name;

-- Get company with GSTIN
SELECT * FROM companies WHERE gstin IS NOT NULL;

-- ============================================
-- LEDGER QUERIES
-- ============================================

-- Get all ledgers with balances
SELECT 
    name,
    parent,
    opening_balance,
    closing_balance,
    (closing_balance - opening_balance) as change
FROM ledgers
ORDER BY name;

-- Get ledgers by parent group
SELECT * FROM ledgers 
WHERE parent = 'Sundry Debtors'
ORDER BY name;

-- Get ledgers with non-zero balances
SELECT * FROM ledgers 
WHERE closing_balance != 0
ORDER BY ABS(closing_balance) DESC;

-- Get top 10 ledgers by balance
SELECT 
    name,
    parent,
    closing_balance
FROM ledgers
ORDER BY ABS(closing_balance) DESC
LIMIT 10;

-- ============================================
-- STOCK ITEM QUERIES
-- ============================================

-- Get all stock items with values
SELECT 
    name,
    parent,
    base_units,
    closing_balance,
    closing_value,
    CASE 
        WHEN closing_balance > 0 THEN closing_value / closing_balance
        ELSE 0
    END as unit_price
FROM stock_items
WHERE closing_balance > 0
ORDER BY name;

-- Get stock items by category
SELECT * FROM stock_items
WHERE parent = 'Finished Goods'
ORDER BY name;

-- Get low stock items (closing balance < 10)
SELECT 
    name,
    base_units,
    closing_balance,
    closing_value
FROM stock_items
WHERE closing_balance < 10 AND closing_balance > 0
ORDER BY closing_balance;

-- Get stock value summary by category
SELECT 
    parent as category,
    COUNT(*) as item_count,
    SUM(closing_balance) as total_quantity,
    SUM(closing_value) as total_value
FROM stock_items
GROUP BY parent
ORDER BY total_value DESC;

-- ============================================
-- VOUCHER QUERIES
-- ============================================

-- Get vouchers by date range
SELECT * FROM vouchers
WHERE date BETWEEN '2024-01-01' AND '2024-01-31'
ORDER BY date DESC;

-- Get vouchers by type
SELECT 
    voucher_type,
    COUNT(*) as count,
    SUM(amount) as total_amount
FROM vouchers
GROUP BY voucher_type
ORDER BY total_amount DESC;

-- Get sales vouchers
SELECT * FROM vouchers
WHERE voucher_type = 'Sales'
ORDER BY date DESC;

-- Get purchase vouchers
SELECT * FROM vouchers
WHERE voucher_type = 'Purchase'
ORDER BY date DESC;

-- Get payment vouchers
SELECT * FROM vouchers
WHERE voucher_type = 'Payment'
ORDER BY date DESC;

-- Get receipt vouchers
SELECT * FROM vouchers
WHERE voucher_type = 'Receipt'
ORDER BY date DESC;

-- Get vouchers by party
SELECT * FROM vouchers
WHERE party_name = 'ABC Company'
ORDER BY date DESC;

-- Get monthly voucher summary
SELECT 
    DATE_FORMAT(date, '%Y-%m') as month,
    voucher_type,
    COUNT(*) as count,
    SUM(amount) as total_amount
FROM vouchers
GROUP BY DATE_FORMAT(date, '%Y-%m'), voucher_type
ORDER BY month DESC, voucher_type;

-- Get daily sales summary
SELECT 
    date,
    COUNT(*) as voucher_count,
    SUM(amount) as total_sales
FROM vouchers
WHERE voucher_type = 'Sales'
GROUP BY date
ORDER BY date DESC;

-- Get top customers by sales
SELECT 
    party_name,
    COUNT(*) as transaction_count,
    SUM(amount) as total_sales
FROM vouchers
WHERE voucher_type = 'Sales' AND party_name IS NOT NULL
GROUP BY party_name
ORDER BY total_sales DESC
LIMIT 10;

-- ============================================
-- SYNC LOG QUERIES
-- ============================================

-- Get recent sync operations
SELECT * FROM sync_log
ORDER BY created_at DESC
LIMIT 20;

-- Get sync statistics
SELECT 
    sync_type,
    COUNT(*) as total_syncs,
    SUM(records_inserted) as total_inserted,
    SUM(records_updated) as total_updated,
    SUM(records_total) as total_records
FROM sync_log
WHERE status = 'success'
GROUP BY sync_type;

-- Get failed syncs
SELECT * FROM sync_log
WHERE status = 'failed'
ORDER BY created_at DESC;

-- ============================================
-- MAINTENANCE QUERIES
-- ============================================

-- Check table sizes
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_mb
FROM information_schema.TABLES
WHERE table_schema = 'tally_sync'
ORDER BY (data_length + index_length) DESC;

-- Optimize all tables
OPTIMIZE TABLE companies, ledgers, stock_items, vouchers, sync_log;

-- Check for duplicate GUIDs
SELECT guid, COUNT(*) as count
FROM ledgers
WHERE guid IS NOT NULL
GROUP BY guid
HAVING count > 1;

-- Delete old sync logs (older than 30 days)
DELETE FROM sync_log
WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- ============================================
-- REPORTING QUERIES
-- ============================================

-- Profit & Loss Summary (simplified)
SELECT 
    'Sales' as particulars,
    SUM(amount) as amount
FROM vouchers
WHERE voucher_type = 'Sales'
UNION ALL
SELECT 
    'Purchases',
    SUM(amount)
FROM vouchers
WHERE voucher_type = 'Purchase';

-- Cash Flow Summary
SELECT 
    voucher_type,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as inflow,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as outflow
FROM vouchers
WHERE voucher_type IN ('Receipt', 'Payment')
GROUP BY voucher_type;

-- Inventory Valuation
SELECT 
    SUM(closing_value) as total_inventory_value,
    COUNT(*) as total_items,
    AVG(closing_value) as avg_item_value
FROM stock_items
WHERE closing_balance > 0;
