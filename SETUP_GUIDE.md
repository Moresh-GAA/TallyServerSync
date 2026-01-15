# Complete Setup Guide

## Step-by-Step Installation

### Step 1: Install Python

1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. **IMPORTANT:** Check "Add Python to PATH" during installation
3. Complete installation
4. Verify: Open Command Prompt and type:
   ```
   python --version
   ```

### Step 2: Download Project Files

**Option A: Using Git**
```bash
git clone https://github.com/Moresh-GAA/TallyServerSync.git
cd TallyServerSync
```

**Option B: Download ZIP**
1. Go to https://github.com/Moresh-GAA/TallyServerSync
2. Click "Code" → "Download ZIP"
3. Extract to `C:\TallyServerSync`

### Step 3: Install Dependencies

1. Open Command Prompt in project folder
2. Run:
   ```batch
   install.bat
   ```
3. Wait for installation to complete

### Step 4: Configure Tally

#### For Tally Prime:

1. Open Tally Prime
2. Press `F12` (Configure)
3. Click `Advanced Configuration`
4. Find `Enable Tally API`
5. Set to `Yes`
6. Port should be `9000`
7. Press `Ctrl+A` to save
8. Restart Tally Prime

#### For Tally.ERP 9:

1. Open Tally.ERP 9
2. Press `F12` (Configure)
3. Go to `Advanced Configuration`
4. Set `Enable XML` to `Yes`
5. Port: `9000`
6. Save and restart

### Step 5: Verify Tally XML API

1. Open browser
2. Go to: `http://localhost:9000`
3. You should see XML response from Tally
4. If not, check firewall settings

### Step 6: Run Application

#### Option A: Run from Source
```batch
run.bat
```

#### Option B: Build Executable
```batch
python build.py
```
Then run: `dist\TallyServerSync.exe`

### Step 7: Configure Application

1. Application opens → Go to **Configuration** tab

2. **Setup Password Protection:**
   - You'll be prompted to set up a password
   - Choose a strong password (minimum 4 characters)
   - Confirm the password
   - This password will be required to change settings

3. **Tally Settings:**
   - Host: `localhost`
   - Port: `9000`
   - Company: (leave empty for current)

4. **Server Settings:**
   - Server URL: `https://your-server.com/api`
   - API Key: (your key if required)

5. Click **Test Tally Connection** ✅
6. Click **Test Server Connection** ✅
7. Click **Save Configuration** 💾

### Step 8: Start Syncing

1. Go to **Sync** tab
2. Click **Start Auto Sync** 🔄
3. First sync starts immediately
4. Subsequent syncs every hour (configurable)

### Step 9: Minimize to Tray

1. Minimize the window
2. Application runs in system tray
3. Double-click tray icon to open
4. Right-click for quick menu

### Step 10: Add to Startup (Optional)

```batch
add_to_startup.bat
```

Application will now start with Windows!

## Server Setup

Your server needs these endpoints:

### 1. Company Info Endpoint
```
POST /company
Content-Type: application/json

{
  "BODY": {
    "DATA": {
      "FldCompanyName": "ABC Company",
      "FldGSTIN": "27XXXXX1234X1ZX"
    }
  }
}
```

### 2. Ledgers Endpoint
```
POST /ledgers
Content-Type: application/json

[
  {
    "NAME": "Cash",
    "PARENT": "Cash-in-Hand",
    "OPENINGBALANCE": "10000.00"
  }
]
```

### 3. Stock Items Endpoint
```
POST /stock-items
Content-Type: application/json

[
  {
    "NAME": "Product A",
    "PARENT": "Primary",
    "BASEUNITS": "Nos",
    "OPENINGBALANCE": "100"
  }
]
```

### 4. Vouchers Endpoint
```
POST /vouchers
Content-Type: application/json

[
  {
    "DATE": "20240115",
    "VOUCHERTYPENAME": "Sales",
    "VOUCHERNUMBER": "1",
    "AMOUNT": "5000.00"
  }
]
```

## Example Server (Node.js/Express)

```javascript
const express = require('express');
const app = express();

app.use(express.json());

// Company endpoint
app.post('/company', (req, res) => {
  console.log('Company data:', req.body);
  // Save to database
  res.json({ success: true });
});

// Ledgers endpoint
app.post('/ledgers', (req, res) => {
  console.log('Ledgers count:', req.body.length);
  // Save to database
  res.json({ success: true, count: req.body.length });
});

// Stock items endpoint
app.post('/stock-items', (req, res) => {
  console.log('Stock items count:', req.body.length);
  // Save to database
  res.json({ success: true, count: req.body.length });
});

// Vouchers endpoint
app.post('/vouchers', (req, res) => {
  console.log('Vouchers count:', req.body.length);
  // Save to database
  res.json({ success: true, count: req.body.length });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

## Firewall Configuration

If Tally is on a different machine:

### Windows Firewall:

1. Open Windows Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules"
4. Click "New Rule"
5. Select "Port"
6. TCP, Port 9000
7. Allow connection
8. Apply to all profiles
9. Name: "Tally XML API"

## Common Issues

### Issue 1: "Python not found"
**Solution:** Reinstall Python with "Add to PATH" checked

### Issue 2: "Module not found"
**Solution:** Run `install.bat` again

### Issue 3: "Tally connection failed"
**Solution:** 
- Check Tally is running
- Verify XML API is enabled
- Check port 9000 is not blocked

### Issue 4: "Server connection failed"
**Solution:**
- Verify server URL
- Check internet connection
- Test server manually in browser

### Issue 5: "No data synced"
**Solution:**
- Open a company in Tally
- Check date range has data
- View logs for errors

### Issue 6: "Forgot password"
**Solution:**
- Navigate to: `%USERPROFILE%\TallySync\`
- Open `config.json` in text editor
- Remove the line: `"settings_password": "..."`
- Save and restart application

## Testing

### Test Tally Connection:
```batch
curl http://localhost:9000
```

### Test Server Connection:
```batch
curl https://your-server.com/api/health
```

## Monitoring

### View Logs:
1. Open application
2. Go to **Logs** tab
3. Click **Refresh Logs**

### Log Location:
```
%USERPROFILE%\TallySync\logs\
```

### Config Location:
```
%USERPROFILE%\TallySync\config.json
```

## Security Best Practices

1. **Use Strong Password:** Minimum 8 characters with mix of letters, numbers, symbols
2. **Secure API Key:** Keep your server API key confidential
3. **HTTPS Only:** Always use HTTPS for server URL
4. **Regular Updates:** Keep the application updated
5. **Backup Config:** Backup your config file regularly

## Uninstallation

1. Stop the application
2. Remove from startup:
   - Delete shortcut from: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`
3. Delete application folder
4. Delete config folder: `%USERPROFILE%\TallySync\`

## Support

For help:
1. Check README.md
2. Review logs
3. Test connections
4. Verify Tally XML API
5. Open an issue on GitHub

## Updates

To update:
1. Download new files from GitHub
2. Replace old files
3. Run `install.bat` again
4. Restart application

---

**You're all set! 🎉**

The application will now sync your Tally data to your server every hour automatically with password-protected settings.
