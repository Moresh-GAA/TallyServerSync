# Tally Server Sync

Automatically sync data from Tally Prime/ERP 9 to your server at regular intervals.

## 🌟 Features

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

## 🚀 Quick Start

### Option 1: Run from Source

1. **Install Python 3.8+** from [python.org](https://python.org)

2. **Clone the repository:**
   ```bash
   git clone https://github.com/Moresh-GAA/TallyServerSync.git
   cd TallyServerSync
   ```

3. **Install dependencies:**
   ```batch
   install.bat
   ```

4. **Run the application:**
   ```batch
   run.bat
   ```

### Option 2: Build Executable

1. **Install dependencies:**
   ```batch
   install.bat
   ```

2. **Build executable:**
   ```batch
   python build.py
   ```

3. **Run executable:**
   ```batch
   dist\TallyServerSync.exe
   ```

## ⚙️ Configuration

### 1. Enable Tally XML API

**In Tally Prime/ERP 9:**
- Press `F12` (Configure)
- Go to `Advanced Configuration`
- Set `Enable Tally API` to `Yes`
- Set `Port` to `9000`
- Save and restart Tally

### 2. Configure Application

1. Open the application
2. Go to **Configuration** tab
3. **Setup Password Protection** (optional but recommended)
4. Enter:
   - **Tally Host:** `localhost` (or IP if remote)
   - **Tally Port:** `9000`
   - **Company:** Leave empty for current company
   - **Server URL:** Your API endpoint
   - **API Key:** Your authentication key (optional)
   - **Sync Interval:** How often to sync (minutes)
5. Click **Test Connections**
6. Click **Save Configuration**

### 3. Start Syncing

1. Go to **Sync** tab
2. Click **Start Auto Sync** 🔄
3. First sync starts immediately
4. Subsequent syncs every hour (configurable)

## 🔒 Password Protection

The application includes password protection for settings:

- **Setup Password:** On first run, you'll be prompted to set up a password
- **Unlock Settings:** Click "Unlock Settings" and enter password
- **Change Password:** Use "Change Password" button
- **Remove Password:** Use "Remove Password" button (requires current password)

Password is hashed using SHA-256 for security.

## 📡 Server API Endpoints

Your server should implement these endpoints:

```
POST /company        - Receive company info
POST /ledgers        - Receive ledgers (batch)
POST /stock-items    - Receive stock items (batch)
POST /vouchers       - Receive vouchers (batch)
GET  /health         - Health check (optional)
```

### Example Request Format

```json
{
  "data": [
    {
      "NAME": "Cash",
      "PARENT": "Cash-in-Hand",
      "OPENINGBALANCE": "10000.00"
    }
  ]
}
```

## 📖 Usage

### Manual Sync
- Open application → Sync tab → Click "Sync Now"

### Auto Sync
- Configure interval → Click "Start Auto Sync"
- Runs in background every X minutes

### System Tray
- **Double-click icon:** Show window
- **Right-click icon:** Quick menu
  - Sync Now
  - Show Window
  - Quit

## 📝 Logs

- **Location:** `%USERPROFILE%\TallySync\logs\`
- **View:** Logs tab in application
- **Rotation:** Daily log files

## 🔧 Add to Windows Startup

```batch
add_to_startup.bat
```

## 🐛 Troubleshooting

### Tally Connection Failed
- ✅ Ensure Tally is running
- ✅ Enable XML API (F12 → Advanced Config)
- ✅ Check firewall allows port 9000
- ✅ Verify host/port settings

### Server Connection Failed
- ✅ Check server URL is correct
- ✅ Verify API key
- ✅ Test server endpoint manually
- ✅ Check internet connection

### No Data Synced
- ✅ Open a company in Tally
- ✅ Ensure date range has data
- ✅ Check logs for errors
- ✅ Verify sync options are enabled

### Forgot Password
- Configuration file is stored at: `%USERPROFILE%\TallySync\config.json`
- You can manually edit this file to remove the `settings_password` field
- Or delete the entire config file to reset to defaults

## 📁 File Structure

```
TallyServerSync/
├── tally_sync_app.py      # Main application with password protection
├── requirements.txt        # Dependencies
├── install.bat            # Installation script
├── run.bat                # Quick run script
├── build.py               # Build executable
├── add_to_startup.bat     # Startup script
└── README.md              # This file
```

## 🔐 Configuration File

Stored at: `%USERPROFILE%\TallySync\config.json`

```json
{
  "tally_host": "localhost",
  "tally_port": 9000,
  "server_url": "https://your-server.com/api",
  "api_key": "your-key",
  "sync_interval": 60,
  "batch_size": 100,
  "sync_company": true,
  "sync_ledgers": true,
  "sync_stock": true,
  "sync_vouchers": true,
  "auto_start": false,
  "start_minimized": false,
  "settings_password": "hashed_password_here"
}
```

## 💻 System Requirements

- **OS:** Windows 7/8/10/11
- **Python:** 3.8 or higher (for source)
- **Tally:** Tally Prime or Tally.ERP 9 (Release 6.0+)
- **RAM:** 2GB minimum
- **Disk:** 100MB free space

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

Free to use for personal and commercial purposes.

## 📧 Support

For issues:
1. Check logs in `%USERPROFILE%\TallySync\logs\`
2. Verify Tally XML API is enabled
3. Test connections in Configuration tab
4. Check server endpoint is accessible

## 🎯 Version

**1.0.0** - Initial Release with Password Protection

---

Made with ❤️ for Tally users
