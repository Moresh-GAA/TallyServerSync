# Tally Server Sync

Automatically sync data from Tally Prime/ERP 9 to your server at regular intervals. Complete solution with Windows client and Node.js server.

## 🌟 Features

### Client (Windows Application)
✅ **System Tray Application** - Runs in background  
✅ **Auto-Sync** - Configurable interval (default: 1 hour)  
✅ **Password Protection** - Secure your settings with password  
✅ **Tally Prime & ERP 9 Support** - Works with both versions  
✅ **Multi-Company Support** - Sync specific or current company  
✅ **Comprehensive Data Sync** - Company info, ledgers, stock items, vouchers  
✅ **Batch Processing** - Efficient handling of large datasets  
✅ **Detailed Logging** - Track all operations  
✅ **Connection Testing** - Verify Tally and server connectivity  
✅ **Windows Startup** - Optional auto-start with Windows  

### Server (Node.js + MySQL)
✅ **RESTful API** - Clean API endpoints  
✅ **MySQL Database** - Robust data storage with proper indexing  
✅ **API Key Authentication** - Secure access  
✅ **Rate Limiting** - Prevent abuse  
✅ **Automatic Upsert** - Insert new, update existing records  
✅ **Transaction Support** - Data consistency  
✅ **Comprehensive Logging** - Track all operations  
✅ **Sync Status API** - Monitor sync progress  

## 📦 What's Included

### Client Files
- `tally_sync_app.py` - Main Windows application
- `requirements.txt` - Python dependencies
- `install.bat` - Easy installation
- `run.bat` - Quick run script
- `build.py` - Build Windows executable
- `add_to_startup.bat` - Add to Windows startup

### Server Files
- `server/app.js` - Express server application
- `server/package.json` - Node.js dependencies
- `server/setup-database.js` - Database setup script
- `server/database/schema.sql` - SQL schema
- `server/database/queries.sql` - Useful SQL queries
- `server/.env.example` - Environment configuration template

## 🚀 Quick Start

### Part 1: Setup Server

1. **Install Prerequisites:**
   - Node.js 14+ ([Download](https://nodejs.org/))
   - MySQL 5.7+ or MariaDB 10.3+ ([Download](https://dev.mysql.com/downloads/))

2. **Clone Repository:**
   ```bash
   git clone https://github.com/Moresh-GAA/TallyServerSync.git
   cd TallyServerSync/server
   ```

3. **Install Dependencies:**
   ```bash
   npm install
   ```

4. **Configure Environment:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env`:
   ```env
   PORT=3000
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=tally_sync
   API_KEY=your_secure_api_key_here
   ```

5. **Setup Database:**
   ```bash
   npm run setup
   ```

6. **Start Server:**
   ```bash
   npm start
   ```
   
   Server runs at: `http://localhost:3000`

### Part 2: Setup Client

1. **Install Python 3.8+** from [python.org](https://python.org)

2. **Navigate to Client:**
   ```bash
   cd ..  # Back to root directory
   ```

3. **Install Dependencies:**
   ```batch
   install.bat
   ```

4. **Run Application:**
   ```batch
   run.bat
   ```

5. **Configure Application:**
   - Setup password protection (optional)
   - **Tally Settings:**
     - Host: `localhost`
     - Port: `9000`
   - **Server Settings:**
     - Server URL: `http://localhost:3000/api`
     - API Key: (same as in server `.env`)
   - Test connections
   - Save configuration

6. **Start Syncing:**
   - Go to Sync tab
   - Click "Start Auto Sync"

## ⚙️ Configuration

### Enable Tally XML API

**In Tally Prime/ERP 9:**
1. Press `F12` (Configure)
2. Go to `Advanced Configuration`
3. Set `Enable Tally API` to `Yes`
4. Set `Port` to `9000`
5. Save and restart Tally

### Server Configuration

Edit `server/.env`:

```env
# Server port
PORT=3000

# Database connection
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=tally_sync

# API security (use strong random key)
API_KEY=your_very_secure_random_api_key_here

# Environment
NODE_ENV=production
```

### Client Configuration

In the application:
- **Server URL:** `http://your-server.com:3000/api`
- **API Key:** Same as server `API_KEY`
- **Sync Interval:** 60 minutes (configurable)

## 🔒 Password Protection

The client includes password protection for settings:

- **Setup Password:** On first run
- **Unlock Settings:** Required to change configuration
- **Change Password:** Update your password
- **Remove Password:** Disable protection
- **SHA-256 Hashing:** Secure password storage

## 📡 API Endpoints

### Health Check
```
GET /api/health
```

### Company Data
```
POST /api/company
Authorization: Bearer your_api_key
```

### Ledgers
```
POST /api/ledgers
Authorization: Bearer your_api_key
```

### Stock Items
```
POST /api/stock-items
Authorization: Bearer your_api_key
```

### Vouchers
```
POST /api/vouchers
Authorization: Bearer your_api_key
```

### Sync Status
```
GET /api/sync-status
Authorization: Bearer your_api_key
```

## 💾 Database Schema

### Tables Created

1. **companies** - Company information
2. **ledgers** - All ledger accounts
3. **stock_items** - Inventory items
4. **vouchers** - All transactions
5. **sync_log** - Sync operation history

See `server/database/schema.sql` for complete schema.

## 📊 Data Synchronization

### How It Works

1. **Client** fetches data from Tally via XML API
2. **Client** sends data to server via REST API
3. **Server** validates and stores in MySQL
4. **Upsert Logic:** New records inserted, existing updated
5. **Incremental Sync:** Only changed data synced

### Sync Frequency

- Default: Every 1 hour
- Configurable: 1 minute to 24 hours
- Manual sync: Anytime via "Sync Now" button

### Data Handling

- **New Records:** Inserted into database
- **Updated Records:** Existing records updated
- **Deleted Records:** Marked as inactive (optional)
- **Transactions:** All operations in transactions
- **Rollback:** On error, no partial data

## 📝 Logs

### Client Logs
- **Location:** `%USERPROFILE%\TallySync\logs\`
- **View:** Logs tab in application
- **Rotation:** Daily

### Server Logs
- **Location:** `server/error.log`, `server/combined.log`
- **View:** `tail -f combined.log`
- **Rotation:** Automatic

## 🔧 Deployment

### Deploy Server

**Using PM2:**
```bash
npm install -g pm2
cd server
pm2 start app.js --name tally-sync
pm2 save
pm2 startup
```

**Using Docker:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY server/package*.json ./
RUN npm install --production
COPY server/ .
EXPOSE 3000
CMD ["npm", "start"]
```

### Deploy Client

**Build Executable:**
```batch
python build.py
```

**Add to Startup:**
```batch
add_to_startup.bat
```

## 🐛 Troubleshooting

### Client Issues

**Tally Connection Failed:**
- ✅ Ensure Tally is running
- ✅ Enable XML API (F12 → Advanced Config)
- ✅ Check firewall allows port 9000

**Server Connection Failed:**
- ✅ Check server is running
- ✅ Verify server URL is correct
- ✅ Check API key matches
- ✅ Test with: `curl http://your-server:3000/api/health`

### Server Issues

**Database Connection Failed:**
- ✅ Check MySQL is running
- ✅ Verify credentials in `.env`
- ✅ Check firewall allows port 3306

**API Key Invalid:**
- ✅ Ensure header format: `Authorization: Bearer your_key`
- ✅ Check API_KEY in `.env`

## 📖 Documentation

- **Client Setup:** `SETUP_GUIDE.md`
- **Server Setup:** `server/README.md`
- **Database Schema:** `server/database/schema.sql`
- **SQL Queries:** `server/database/queries.sql`

## 🔐 Security Best Practices

1. **Use Strong API Key:** Generate random 32+ character key
2. **HTTPS Only:** Use SSL/TLS for production
3. **Firewall:** Restrict database access
4. **Password Protection:** Enable on client
5. **Regular Backups:** Backup database regularly
6. **Update Regularly:** Keep dependencies updated

## 📊 Monitoring

### Check Sync Status

**Via API:**
```bash
curl http://your-server:3000/api/sync-status \
  -H "Authorization: Bearer your_api_key"
```

**Via Database:**
```sql
SELECT 
  (SELECT COUNT(*) FROM companies) as companies,
  (SELECT COUNT(*) FROM ledgers) as ledgers,
  (SELECT COUNT(*) FROM stock_items) as stock_items,
  (SELECT COUNT(*) FROM vouchers) as vouchers;
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - Free to use for personal and commercial purposes.

## 📧 Support

For issues:
1. Check logs (client and server)
2. Verify Tally XML API is enabled
3. Test connections
4. Check firewall settings
5. Review documentation
6. Open GitHub issue

## 🎯 Version

**1.0.0** - Initial Release
- Windows client with password protection
- Node.js server with MySQL
- Complete sync solution
- Comprehensive documentation

---

## 📚 Quick Links

- **Repository:** https://github.com/Moresh-GAA/TallyServerSync
- **Client Setup Guide:** [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Server Documentation:** [server/README.md](server/README.md)
- **Database Schema:** [server/database/schema.sql](server/database/schema.sql)

---

Made with ❤️ for Tally users
