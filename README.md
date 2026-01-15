# Tally Server Sync

Automatically sync data from Tally Prime/ERP 9 to your server at regular intervals. Complete solution with Windows client and server backends (Node.js + Laravel).

## 🌟 Features

### Client (Windows Application)
✅ **System Tray Application** - Runs in background  
✅ **Auto-Sync** - Configurable interval (default: 1 hour)  
✅ **Password Protection** - Secure your settings with password  
✅ **User Authentication** - Login with email/password for SaaS  
✅ **Tally Prime & ERP 9 Support** - Works with both versions  
✅ **Multi-Company Support** - Sync specific or current company  
✅ **Comprehensive Data Sync** - Company info, ledgers, stock items, vouchers  
✅ **Batch Processing** - Efficient handling of large datasets  
✅ **Detailed Logging** - Track all operations  
✅ **Connection Testing** - Verify Tally and server connectivity  
✅ **Windows Startup** - Optional auto-start with Windows  

### Server Options

#### Option 1: Laravel (Multi-Tenant SaaS) ⭐ **Recommended for SaaS**
✅ **Multi-Tenant Architecture** - Each user has isolated data  
✅ **Laravel Sanctum Authentication** - Token-based API auth  
✅ **RESTful API** - Clean and well-documented  
✅ **Eloquent ORM** - Clean database interactions  
✅ **Automatic Upsert** - Insert new, update existing  
✅ **Transaction Support** - Data consistency  
✅ **Sync Logging** - Track all operations  
✅ **User Management** - Built-in registration/login  

#### Option 2: Node.js + MySQL (Single Tenant)
✅ **RESTful API** - Clean API endpoints  
✅ **MySQL Database** - Robust data storage  
✅ **API Key Authentication** - Secure access  
✅ **Rate Limiting** - Prevent abuse  
✅ **Automatic Upsert** - Insert/update logic  
✅ **Transaction Support** - Data consistency  
✅ **Comprehensive Logging** - Track operations  

## 📦 What's Included

### Client Files
- `tally_sync_app.py` - Main Windows application
- `requirements.txt` - Python dependencies
- `install.bat` - Easy installation
- `run.bat` - Quick run script
- `build.py` - Build Windows executable
- `add_to_startup.bat` - Add to Windows startup

### Laravel Server (Multi-Tenant SaaS)
- `laravel-server/routes/api.php` - API routes
- `laravel-server/app/Http/Controllers/Api/` - Controllers
  - `AuthController.php` - User authentication
  - `TallySyncController.php` - Tally sync operations
- `laravel-server/app/Models/` - Eloquent models
  - `Company.php`, `Ledger.php`, `StockItem.php`, `Voucher.php`, `SyncLog.php`
- `laravel-server/database/migrations/` - Database migrations
- `laravel-server/README.md` - Laravel setup guide

### Node.js Server (Single Tenant)
- `server/app.js` - Express server application
- `server/package.json` - Node.js dependencies
- `server/setup-database.js` - Database setup script
- `server/database/schema.sql` - SQL schema
- `server/database/queries.sql` - Useful SQL queries
- `server/.env.example` - Environment configuration template

## 🚀 Quick Start

### Part 1: Setup Server

#### Option A: Laravel Server (Multi-Tenant SaaS) ⭐

1. **Prerequisites:**
   - PHP 8.1+
   - Composer
   - MySQL 5.7+

2. **Copy Files to Laravel Project:**
   ```bash
   # Copy routes
   cp laravel-server/routes/api.php your-laravel/routes/
   
   # Copy controllers
   cp -r laravel-server/app/Http/Controllers/Api your-laravel/app/Http/Controllers/
   
   # Copy models
   cp -r laravel-server/app/Models/* your-laravel/app/Models/
   
   # Copy migrations
   cp laravel-server/database/migrations/* your-laravel/database/migrations/
   ```

3. **Install Sanctum:**
   ```bash
   composer require laravel/sanctum
   php artisan vendor:publish --provider="Laravel\Sanctum\SanctumServiceProvider"
   ```

4. **Update User Model:**
   ```php
   use Laravel\Sanctum\HasApiTokens;
   
   class User extends Authenticatable
   {
       use HasApiTokens, HasFactory, Notifiable;
   }
   ```

5. **Run Migrations:**
   ```bash
   php artisan migrate
   ```

6. **Start Server:**
   ```bash
   php artisan serve
   ```
   
   Server runs at: `http://localhost:8000`

#### Option B: Node.js Server (Single Tenant)

1. **Prerequisites:**
   - Node.js 14+
   - MySQL 5.7+

2. **Setup:**
   ```bash
   cd server
   npm install
   cp .env.example .env
   # Edit .env with your settings
   npm run setup
   npm start
   ```
   
   Server runs at: `http://localhost:3000`

### Part 2: Setup Client

1. **Install Python 3.8+** from [python.org](https://python.org)

2. **Install Dependencies:**
   ```batch
   install.bat
   ```

3. **Run Application:**
   ```batch
   run.bat
   ```

4. **Configure Application:**

   **For Laravel (SaaS):**
   - Setup password protection (optional)
   - **Server Settings:**
     - Server URL: `http://localhost:8000/api/tally`
     - Email: `your@email.com`
     - Password: `your_password`
   - Click "Login" to authenticate
   - **Tally Settings:**
     - Host: `localhost`
     - Port: `9000`
   - Test connections
   - Save configuration

   **For Node.js:**
   - Setup password protection (optional)
   - **Server Settings:**
     - Server URL: `http://localhost:3000/api`
     - API Key: (from server `.env`)
   - **Tally Settings:**
     - Host: `localhost`
     - Port: `9000`
   - Test connections
   - Save configuration

5. **Start Syncing:**
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

### Laravel Server Configuration

**Multi-Tenant with User Authentication:**

1. **Register User:**
   ```http
   POST /api/auth/register
   {
     "name": "John Doe",
     "email": "john@example.com",
     "password": "password123",
     "password_confirmation": "password123"
   }
   ```

2. **Login:**
   ```http
   POST /api/auth/login
   {
     "email": "john@example.com",
     "password": "password123"
   }
   ```
   
   Returns token for API access.

3. **Use Token:**
   ```http
   Authorization: Bearer {token}
   ```

### Node.js Server Configuration

Edit `server/.env`:

```env
PORT=3000
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=tally_sync
API_KEY=your_secure_api_key
```

## 🔒 Authentication

### Laravel (Multi-Tenant)
- **Method:** Email/Password
- **Token:** Laravel Sanctum personal access token
- **Isolation:** Each user's data is completely isolated
- **Registration:** Users can self-register
- **Security:** Token-based, automatic expiration

### Node.js (Single Tenant)
- **Method:** API Key
- **Token:** Static API key in `.env`
- **Isolation:** Single database for all data
- **Registration:** Manual setup
- **Security:** API key validation

## 📡 API Endpoints

### Laravel Endpoints

```
POST   /api/auth/register       - Register new user
POST   /api/auth/login          - Login user
POST   /api/auth/logout         - Logout user
GET    /api/auth/user           - Get user info

POST   /api/tally/company       - Sync company
POST   /api/tally/ledgers       - Sync ledgers
POST   /api/tally/stock-items   - Sync stock items
POST   /api/tally/vouchers      - Sync vouchers
GET    /api/tally/sync-status   - Get sync status
GET    /api/tally/sync-history  - Get sync history
```

### Node.js Endpoints

```
GET    /api/health              - Health check
POST   /api/company             - Sync company
POST   /api/ledgers             - Sync ledgers
POST   /api/stock-items         - Sync stock items
POST   /api/vouchers            - Sync vouchers
GET    /api/sync-status         - Get sync status
```

## 💾 Database Schema

### Multi-Tenant (Laravel)

All tables include `user_id` for data isolation:

- **users** - User accounts
- **companies** - User's companies
- **ledgers** - User's ledgers
- **stock_items** - User's stock items
- **vouchers** - User's vouchers
- **sync_logs** - User's sync history

### Single Tenant (Node.js)

- **companies** - All companies
- **ledgers** - All ledgers
- **stock_items** - All stock items
- **vouchers** - All vouchers
- **sync_log** - All sync history

## 📊 Data Synchronization

### How It Works

1. **Client** fetches data from Tally via XML API
2. **Client** authenticates with server (email/password or API key)
3. **Client** sends data to server via REST API
4. **Server** validates and stores in MySQL (isolated by user for Laravel)
5. **Upsert Logic:** New records inserted, existing updated
6. **Incremental Sync:** Only changed data synced

### Sync Frequency

- Default: Every 1 hour
- Configurable: 1 minute to 24 hours
- Manual sync: Anytime via "Sync Now" button

## 📝 Logs

### Client Logs
- **Location:** `%USERPROFILE%\TallySync\logs\`
- **View:** Logs tab in application
- **Rotation:** Daily

### Laravel Server Logs
- **Location:** `storage/logs/laravel.log`
- **View:** `tail -f storage/logs/laravel.log`

### Node.js Server Logs
- **Location:** `server/error.log`, `server/combined.log`
- **View:** `tail -f combined.log`

## 🔧 Deployment

### Laravel Deployment

```bash
# Optimize for production
php artisan config:cache
php artisan route:cache
php artisan view:cache
php artisan optimize

# Use supervisor for queue workers
php artisan queue:work --daemon
```

### Node.js Deployment

```bash
# Using PM2
npm install -g pm2
pm2 start app.js --name tally-sync
pm2 save
pm2 startup
```

### Client Deployment

```batch
# Build executable
python build.py

# Add to startup
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
- ✅ Check credentials (email/password or API key)
- ✅ Test with: `curl http://your-server/api/health`

### Laravel Server Issues

**Authentication Failed:**
- ✅ Check email/password are correct
- ✅ Verify Sanctum is installed
- ✅ Check CORS configuration

**Database Connection Failed:**
- ✅ Check MySQL is running
- ✅ Verify credentials in `.env`
- ✅ Run migrations: `php artisan migrate`

### Node.js Server Issues

**Database Connection Failed:**
- ✅ Check MySQL is running
- ✅ Verify credentials in `.env`
- ✅ Check firewall allows port 3306

**API Key Invalid:**
- ✅ Ensure header format: `Authorization: Bearer your_key`
- ✅ Check API_KEY in `.env`

## 📖 Documentation

- **Main README:** This file
- **Client Setup:** `SETUP_GUIDE.md`
- **Laravel Server:** `laravel-server/README.md`
- **Node.js Server:** `server/README.md`
- **Deployment:** `DEPLOYMENT.md`
- **Database Schema:** `server/database/schema.sql`

## 🔐 Security Best Practices

1. **Use HTTPS** in production
2. **Strong Passwords** for user accounts
3. **Secure API Keys** (32+ characters)
4. **Firewall** restrict database access
5. **Regular Backups** of database
6. **Update Dependencies** regularly
7. **Monitor Logs** for suspicious activity

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
- Laravel server with multi-tenant support
- Node.js server with single-tenant support
- Complete sync solution
- Comprehensive documentation

---

## 📚 Quick Links

- **Repository:** https://github.com/Moresh-GAA/TallyServerSync
- **Client Setup Guide:** [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Laravel Server:** [laravel-server/README.md](laravel-server/README.md)
- **Node.js Server:** [server/README.md](server/README.md)
- **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🌟 Choose Your Server

### Laravel (Multi-Tenant SaaS) ⭐
**Best for:**
- SaaS platforms
- Multiple users/tenants
- User registration/login
- Data isolation required
- Modern PHP stack

### Node.js (Single Tenant)
**Best for:**
- Single company
- Simple deployment
- API key authentication
- Node.js stack preference
- Lightweight solution

---

Made with ❤️ for Tally users
