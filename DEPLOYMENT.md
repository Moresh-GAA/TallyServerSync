# Deployment Guide

Complete guide for deploying Tally Server Sync in production.

## 📋 Table of Contents

1. [Server Deployment](#server-deployment)
2. [Client Deployment](#client-deployment)
3. [Security Hardening](#security-hardening)
4. [Monitoring & Maintenance](#monitoring--maintenance)
5. [Backup & Recovery](#backup--recovery)

---

## Server Deployment

### Option 1: VPS/Cloud Server (Recommended)

#### Prerequisites
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- 2GB RAM minimum
- 20GB disk space
- Root or sudo access

#### Step 1: Install Node.js

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# CentOS/RHEL
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Verify installation
node --version
npm --version
```

#### Step 2: Install MySQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server -y

# CentOS/RHEL
sudo yum install mysql-server -y

# Start MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Secure installation
sudo mysql_secure_installation
```

#### Step 3: Create Database User

```bash
sudo mysql -u root -p
```

```sql
CREATE DATABASE tally_sync CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'tallyuser'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON tally_sync.* TO 'tallyuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### Step 4: Deploy Application

```bash
# Create application directory
sudo mkdir -p /var/www/tally-sync
cd /var/www/tally-sync

# Clone repository
git clone https://github.com/Moresh-GAA/TallyServerSync.git .

# Navigate to server directory
cd server

# Install dependencies
npm install --production

# Create .env file
cp .env.example .env
nano .env
```

Edit `.env`:
```env
PORT=3000
NODE_ENV=production

DB_HOST=localhost
DB_USER=tallyuser
DB_PASSWORD=strong_password_here
DB_NAME=tally_sync

API_KEY=generate_secure_random_key_here
```

#### Step 5: Setup Database

```bash
npm run setup
```

#### Step 6: Install PM2

```bash
# Install PM2 globally
sudo npm install -g pm2

# Start application
pm2 start app.js --name tally-sync

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Follow the command it outputs

# Check status
pm2 status
pm2 logs tally-sync
```

#### Step 7: Configure Nginx (Reverse Proxy)

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/tally-sync
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/tally-sync /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### Step 8: Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

#### Step 9: Configure Firewall

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Option 2: Docker Deployment

#### Create Dockerfile

Create `server/Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy application files
COPY . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start application
CMD ["npm", "start"]
```

#### Create docker-compose.yml

Create `server/docker-compose.yml`:
```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: tally-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - mysql-data:/var/lib/mysql
      - ./database/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "3306:3306"
    networks:
      - tally-network

  app:
    build: .
    container_name: tally-app
    restart: always
    depends_on:
      - mysql
    environment:
      - NODE_ENV=production
      - PORT=3000
      - DB_HOST=mysql
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_NAME=${DB_NAME}
      - API_KEY=${API_KEY}
    ports:
      - "3000:3000"
    networks:
      - tally-network
    volumes:
      - ./logs:/app/logs

volumes:
  mysql-data:

networks:
  tally-network:
    driver: bridge
```

#### Deploy with Docker

```bash
# Create .env file
cp .env.example .env
nano .env

# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f

# Check status
docker-compose ps
```

---

## Client Deployment

### Option 1: Run from Source

1. **Install Python 3.8+** on all client machines

2. **Clone repository:**
   ```bash
   git clone https://github.com/Moresh-GAA/TallyServerSync.git
   cd TallyServerSync
   ```

3. **Install dependencies:**
   ```batch
   install.bat
   ```

4. **Configure:**
   - Run `run.bat`
   - Setup password
   - Configure Tally and Server settings
   - Save configuration

5. **Add to startup:**
   ```batch
   add_to_startup.bat
   ```

### Option 2: Distribute Executable

1. **Build executable:**
   ```batch
   python build.py
   ```

2. **Create installer package:**
   - Copy `dist/TallyServerSync.exe`
   - Create `config-template.json` with default settings
   - Create installation script

3. **Distribute to users:**
   - Share executable
   - Provide configuration instructions
   - Include server URL and API key

### Mass Deployment Script

Create `deploy-client.bat`:
```batch
@echo off
echo Tally Server Sync - Client Deployment
echo =====================================

REM Set server details
set SERVER_URL=https://your-server.com/api
set API_KEY=your_api_key_here

REM Create config directory
mkdir "%USERPROFILE%\TallySync" 2>nul

REM Copy executable
copy TallyServerSync.exe "%USERPROFILE%\TallySync\" /Y

REM Create default config
(
echo {
echo   "tally_host": "localhost",
echo   "tally_port": 9000,
echo   "server_url": "%SERVER_URL%",
echo   "api_key": "%API_KEY%",
echo   "sync_interval": 60,
echo   "auto_start": true,
echo   "start_minimized": true
echo }
) > "%USERPROFILE%\TallySync\config.json"

REM Add to startup
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%STARTUP_FOLDER%\TallyServerSync.lnk'); $SC.TargetPath = '%USERPROFILE%\TallySync\TallyServerSync.exe'; $SC.Save()"

echo.
echo Deployment completed!
echo Application will start on next login.
pause
```

---

## Security Hardening

### Server Security

#### 1. Use Strong API Key

```bash
# Generate secure API key
openssl rand -base64 32
```

#### 2. Enable HTTPS Only

In Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Strong SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    location /api {
        proxy_pass http://localhost:3000;
        # ... rest of configuration
    }
}
```

#### 3. Database Security

```sql
-- Use strong password
ALTER USER 'tallyuser'@'localhost' IDENTIFIED BY 'very_strong_password_123!@#';

-- Restrict to localhost only
REVOKE ALL PRIVILEGES ON *.* FROM 'tallyuser'@'%';
GRANT ALL PRIVILEGES ON tally_sync.* TO 'tallyuser'@'localhost';
FLUSH PRIVILEGES;
```

#### 4. Firewall Rules

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### 5. Fail2Ban (Prevent Brute Force)

```bash
# Install Fail2Ban
sudo apt install fail2ban -y

# Create jail for Nginx
sudo nano /etc/fail2ban/jail.local
```

Add:
```ini
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 5
findtime = 600
bantime = 3600
```

```bash
# Restart Fail2Ban
sudo systemctl restart fail2ban
```

### Client Security

1. **Enable Password Protection** - Always use password
2. **Secure API Key Storage** - Never share API key
3. **Use HTTPS** - Always use HTTPS server URL
4. **Regular Updates** - Keep application updated

---

## Monitoring & Maintenance

### Server Monitoring

#### 1. PM2 Monitoring

```bash
# Check status
pm2 status

# View logs
pm2 logs tally-sync

# Monitor resources
pm2 monit

# Restart if needed
pm2 restart tally-sync
```

#### 2. Database Monitoring

```sql
-- Check table sizes
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_mb
FROM information_schema.TABLES
WHERE table_schema = 'tally_sync'
ORDER BY (data_length + index_length) DESC;

-- Check recent syncs
SELECT * FROM sync_log
ORDER BY created_at DESC
LIMIT 10;

-- Check record counts
SELECT 
    (SELECT COUNT(*) FROM companies) as companies,
    (SELECT COUNT(*) FROM ledgers) as ledgers,
    (SELECT COUNT(*) FROM stock_items) as stock_items,
    (SELECT COUNT(*) FROM vouchers) as vouchers;
```

#### 3. Log Monitoring

```bash
# Server logs
tail -f /var/www/tally-sync/server/combined.log
tail -f /var/www/tally-sync/server/error.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# MySQL logs
tail -f /var/log/mysql/error.log
```

#### 4. Setup Monitoring Tools

**Install Netdata:**
```bash
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

Access at: `http://your-server:19999`

### Automated Maintenance

Create `/etc/cron.daily/tally-sync-maintenance`:
```bash
#!/bin/bash

# Optimize database tables
mysql -u tallyuser -p'password' tally_sync -e "OPTIMIZE TABLE companies, ledgers, stock_items, vouchers, sync_log;"

# Delete old logs (older than 30 days)
find /var/www/tally-sync/server/*.log -mtime +30 -delete

# Backup database
mysqldump -u tallyuser -p'password' tally_sync > /backups/tally_sync_$(date +%Y%m%d).sql

# Keep only last 7 backups
find /backups/tally_sync_*.sql -mtime +7 -delete
```

```bash
# Make executable
chmod +x /etc/cron.daily/tally-sync-maintenance
```

---

## Backup & Recovery

### Database Backup

#### Automated Daily Backup

Create `/usr/local/bin/backup-tally-db.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/backups/tally-sync"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="tally_sync"
DB_USER="tallyuser"
DB_PASS="your_password"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_DIR/tally_sync_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "tally_sync_*.sql.gz" -mtime +30 -delete

echo "Backup completed: tally_sync_$DATE.sql.gz"
```

```bash
# Make executable
chmod +x /usr/local/bin/backup-tally-db.sh

# Add to crontab (daily at 2 AM)
crontab -e
```

Add:
```
0 2 * * * /usr/local/bin/backup-tally-db.sh
```

#### Manual Backup

```bash
# Backup database
mysqldump -u tallyuser -p tally_sync > tally_sync_backup.sql

# Backup with compression
mysqldump -u tallyuser -p tally_sync | gzip > tally_sync_backup.sql.gz
```

### Database Recovery

```bash
# Restore from backup
mysql -u tallyuser -p tally_sync < tally_sync_backup.sql

# Restore from compressed backup
gunzip < tally_sync_backup.sql.gz | mysql -u tallyuser -p tally_sync
```

### Application Backup

```bash
# Backup entire application
tar -czf tally-sync-app-backup.tar.gz /var/www/tally-sync

# Restore application
tar -xzf tally-sync-app-backup.tar.gz -C /
```

### Client Configuration Backup

```batch
REM Backup client config
xcopy "%USERPROFILE%\TallySync" "D:\Backups\TallySync\" /E /I /Y

REM Restore client config
xcopy "D:\Backups\TallySync\" "%USERPROFILE%\TallySync\" /E /I /Y
```

---

## Performance Optimization

### Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_voucher_date_type ON vouchers(date, voucher_type);
CREATE INDEX idx_ledger_balance ON ledgers(closing_balance);
CREATE INDEX idx_stock_value ON stock_items(closing_value);

-- Optimize tables
OPTIMIZE TABLE companies, ledgers, stock_items, vouchers;

-- Analyze tables
ANALYZE TABLE companies, ledgers, stock_items, vouchers;
```

### Server Optimization

In `app.js`, adjust connection pool:
```javascript
const pool = mysql.createPool({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
    waitForConnections: true,
    connectionLimit: 20,  // Increase for high traffic
    queueLimit: 0
});
```

### Nginx Optimization

```nginx
# Enable gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types application/json text/plain text/css application/javascript;

# Enable caching
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m inactive=60m;

location /api {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    # ... rest of configuration
}
```

---

## Troubleshooting Production Issues

### Server Not Responding

```bash
# Check if process is running
pm2 status

# Check logs
pm2 logs tally-sync --lines 100

# Restart application
pm2 restart tally-sync

# Check Nginx
sudo systemctl status nginx
sudo nginx -t
```

### Database Connection Issues

```bash
# Check MySQL status
sudo systemctl status mysql

# Check connections
mysql -u tallyuser -p -e "SHOW PROCESSLIST;"

# Check for locks
mysql -u tallyuser -p -e "SHOW OPEN TABLES WHERE In_use > 0;"
```

### High CPU/Memory Usage

```bash
# Check resource usage
pm2 monit

# Check database queries
mysql -u tallyuser -p -e "SHOW FULL PROCESSLIST;"

# Optimize database
mysql -u tallyuser -p tally_sync -e "OPTIMIZE TABLE companies, ledgers, stock_items, vouchers;"
```

---

## Support & Maintenance

For production support:
1. Monitor logs regularly
2. Setup automated backups
3. Keep system updated
4. Monitor resource usage
5. Test disaster recovery plan

---

**Deployment Complete! 🎉**

Your Tally Server Sync is now running in production.
