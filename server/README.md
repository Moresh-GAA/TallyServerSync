# Tally Sync Server

Node.js + Express + MySQL server for receiving and storing Tally data.

## Features

- ✅ RESTful API endpoints for Tally data
- ✅ MySQL database with proper indexing
- ✅ API key authentication
- ✅ Rate limiting
- ✅ CORS support
- ✅ Comprehensive logging
- ✅ Automatic upsert (insert/update)
- ✅ Transaction support
- ✅ Error handling

## Prerequisites

- Node.js 14+ 
- MySQL 5.7+ or MariaDB 10.3+
- npm or yarn

## Installation

### 1. Install Dependencies

```bash
cd server
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
PORT=3000
NODE_ENV=production

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=tally_sync

API_KEY=your_secure_api_key_here
```

### 3. Setup Database

```bash
npm run setup
```

This will:
- Create database `tally_sync`
- Create all required tables
- Set up indexes

### 4. Start Server

**Production:**
```bash
npm start
```

**Development (with auto-reload):**
```bash
npm run dev
```

Server will start on `http://localhost:3000`

## API Endpoints

### Health Check
```
GET /api/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0.0"
}
```

### Company Data
```
POST /api/company
Authorization: Bearer your_api_key
Content-Type: application/json
```

### Ledgers
```
POST /api/ledgers
Authorization: Bearer your_api_key
Content-Type: application/json
```

### Stock Items
```
POST /api/stock-items
Authorization: Bearer your_api_key
Content-Type: application/json
```

### Vouchers
```
POST /api/vouchers
Authorization: Bearer your_api_key
Content-Type: application/json
```

### Sync Status
```
GET /api/sync-status
Authorization: Bearer your_api_key
```

Response:
```json
{
  "success": true,
  "data": {
    "companies": 1,
    "ledgers": 150,
    "stock_items": 75,
    "vouchers": 500,
    "last_sync": "2024-01-15T10:30:00.000Z"
  }
}
```

## Database Schema

### companies
- id (PK)
- name (UNIQUE)
- guid (UNIQUE)
- gstin
- pan
- address
- email
- phone
- last_synced
- created_at
- updated_at

### ledgers
- id (PK)
- name
- guid (UNIQUE)
- parent
- opening_balance
- closing_balance
- gstin
- phone
- email
- address
- last_synced
- created_at
- updated_at

### stock_items
- id (PK)
- name
- guid (UNIQUE)
- parent
- base_units
- opening_balance
- opening_value
- closing_balance
- closing_value
- hsn_code
- gst_applicable
- last_synced
- created_at
- updated_at

### vouchers
- id (PK)
- guid (UNIQUE)
- date
- voucher_type
- voucher_number
- reference
- reference_date
- narration
- party_name
- amount
- is_invoice
- last_synced
- created_at
- updated_at

### sync_log
- id (PK)
- sync_type
- records_inserted
- records_updated
- records_total
- status
- error_message
- sync_started
- sync_completed
- created_at

## Security

### API Key Authentication

All endpoints (except `/api/health`) require API key:

```
Authorization: Bearer your_api_key_here
```

### Rate Limiting

- 100 requests per 15 minutes per IP
- Applies to all `/api/*` endpoints

### CORS

Configure allowed origins in `.env`:

```env
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Logging

Logs are stored in:
- `error.log` - Error level logs
- `combined.log` - All logs

## Data Handling

### Upsert Logic

All endpoints use **UPSERT** (INSERT ... ON DUPLICATE KEY UPDATE):

- **New records:** Inserted
- **Existing records:** Updated based on GUID or name
- **Ensures:** No duplicates, always latest data

### Transactions

Batch operations use transactions:
- All or nothing
- Rollback on error
- Data consistency

## Testing

### Test Health Endpoint

```bash
curl http://localhost:3000/api/health
```

### Test Company Endpoint

```bash
curl -X POST http://localhost:3000/api/company \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "BODY": {
      "DATA": {
        "FldCompanyName": "Test Company",
        "FldGSTIN": "27XXXXX1234X1ZX"
      }
    }
  }'
```

### Test Sync Status

```bash
curl http://localhost:3000/api/sync-status \
  -H "Authorization: Bearer your_api_key"
```

## Deployment

### Using PM2 (Recommended)

```bash
npm install -g pm2
pm2 start app.js --name tally-sync
pm2 save
pm2 startup
```

### Using Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables for Production

```env
NODE_ENV=production
PORT=3000
DB_HOST=your_db_host
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
DB_NAME=tally_sync
API_KEY=your_very_secure_api_key
```

## Monitoring

### Check Server Status

```bash
curl http://your-server.com/api/health
```

### View Logs

```bash
tail -f combined.log
tail -f error.log
```

### Database Queries

```sql
-- Check record counts
SELECT 
  (SELECT COUNT(*) FROM companies) as companies,
  (SELECT COUNT(*) FROM ledgers) as ledgers,
  (SELECT COUNT(*) FROM stock_items) as stock_items,
  (SELECT COUNT(*) FROM vouchers) as vouchers;

-- Check last sync times
SELECT 
  'companies' as table_name, MAX(last_synced) as last_sync FROM companies
UNION ALL
SELECT 'ledgers', MAX(last_synced) FROM ledgers
UNION ALL
SELECT 'stock_items', MAX(last_synced) FROM stock_items
UNION ALL
SELECT 'vouchers', MAX(last_synced) FROM vouchers;
```

## Troubleshooting

### Database Connection Failed

- Check MySQL is running
- Verify credentials in `.env`
- Check firewall allows port 3306

### API Key Invalid

- Ensure `Authorization` header format: `Bearer your_key`
- Check API_KEY in `.env` matches client

### Rate Limit Exceeded

- Wait 15 minutes
- Increase limit in `app.js` if needed

## Support

For issues, check:
1. Server logs (`combined.log`, `error.log`)
2. Database connectivity
3. API key configuration
4. Firewall settings

## License

MIT
