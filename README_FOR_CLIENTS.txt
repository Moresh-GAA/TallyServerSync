================================================================================
                    TALLY SERVER SYNC - INSTALLATION GUIDE
================================================================================

Thank you for choosing Tally Server Sync!

This application automatically syncs your Tally data to the cloud server.

================================================================================
SYSTEM REQUIREMENTS
================================================================================

- Windows 7 or later (Windows 10/11 recommended)
- Tally Prime or Tally ERP 9
- Internet connection
- 100 MB free disk space

================================================================================
INSTALLATION OPTIONS
================================================================================

OPTION 1: Using Installer (Recommended)
----------------------------------------
1. Double-click "TallyServerSync_Setup.exe"
2. Follow the installation wizard
3. Choose installation location (default recommended)
4. Select additional options:
   - Create desktop icon (recommended)
   - Run at Windows startup (optional)
5. Click "Install"
6. Launch application from Start Menu or Desktop

OPTION 2: Standalone Executable
--------------------------------
1. Extract the ZIP file (if downloaded as ZIP)
2. Double-click "TallyServerSync.exe"
3. Application will start immediately
4. No installation required

================================================================================
FIRST TIME SETUP
================================================================================

Step 1: Configure Server Settings
----------------------------------
1. Click on "Settings" tab
2. Enter your server credentials (provided by your administrator):
   
   Server URL: https://yourserver.com/api/tally
   Email: your@email.com
   Password: your_password

3. Click "Login" button
4. Wait for "Login successful" message

Step 2: Configure Tally Settings
---------------------------------
1. Make sure Tally is running
2. In Tally, enable XML API:
   - Press F12 (Configure)
   - Go to Advanced Configuration
   - Set "Enable Tally API" to "Yes"
   - Set "Port" to "9000"
   - Save and restart Tally

3. In Tally Server Sync application:
   - Tally Host: localhost
   - Tally Port: 9000
   - Company: (Select from dropdown or leave as "Current Company")

4. Click "Test Tally Connection"
5. Wait for "Connection successful" message

Step 3: Test Server Connection
-------------------------------
1. Click "Test Server Connection"
2. Wait for "Connection successful" message

Step 4: Save Configuration
---------------------------
1. Click "Save Configuration"
2. Configuration is now saved

Step 5: Start Syncing
----------------------
1. Go to "Sync" tab
2. Click "Start Auto Sync"
3. Application will sync data every hour (default)
4. You can click "Sync Now" for immediate sync

================================================================================
USING THE APPLICATION
================================================================================

System Tray Icon
----------------
- Application runs in system tray (bottom-right corner)
- Right-click icon for quick actions:
  - Show/Hide window
  - Sync Now
  - Exit

Auto Sync
---------
- Syncs automatically every hour (configurable)
- Runs in background
- Shows notification on completion

Manual Sync
-----------
- Click "Sync Now" button anytime
- Useful for immediate data upload

View Logs
---------
- Click "Logs" tab to view sync history
- Check for any errors or issues

================================================================================
TROUBLESHOOTING
================================================================================

Issue: "Tally connection failed"
Solution:
  1. Make sure Tally is running
  2. Check if XML API is enabled in Tally (F12 → Advanced Config)
  3. Verify port is 9000
  4. Check Windows Firewall is not blocking

Issue: "Server connection failed"
Solution:
  1. Check internet connection
  2. Verify server URL is correct
  3. Check email and password are correct
  4. Contact your administrator

Issue: "Login failed"
Solution:
  1. Verify email and password
  2. Check if account is active
  3. Try "Forgot Password" if needed
  4. Contact support

Issue: Application won't start
Solution:
  1. Right-click exe → Run as Administrator
  2. Check antivirus is not blocking
  3. Reinstall application
  4. Contact support

================================================================================
FORGOT PASSWORD
================================================================================

1. Click "Forgot Password?" link in Settings
2. Enter your email address
3. Click "Send Reset Link"
4. Copy the reset link shown
5. Open link in browser
6. Enter new password
7. Login with new password in application

================================================================================
UNINSTALLATION
================================================================================

If installed via installer:
1. Go to Control Panel → Programs and Features
2. Find "Tally Server Sync"
3. Click "Uninstall"
4. Follow uninstallation wizard
5. Choose whether to keep settings

If using standalone exe:
1. Simply delete the TallyServerSync.exe file
2. Delete settings folder: %USERPROFILE%\TallySync (optional)

================================================================================
SUPPORT
================================================================================

For help and support:

Email: support@yourcompany.com
Website: https://yourwebsite.com
Phone: +1-XXX-XXX-XXXX

Documentation: https://docs.yourwebsite.com
Video Tutorials: https://yourwebsite.com/tutorials

================================================================================
PRIVACY & SECURITY
================================================================================

- All data is encrypted during transmission (HTTPS)
- Passwords are securely hashed
- Your data is isolated from other users
- No data is shared with third parties
- Regular backups are maintained

================================================================================
TIPS FOR BEST EXPERIENCE
================================================================================

1. Keep Tally running during business hours for automatic sync
2. Enable "Run at Windows startup" for seamless operation
3. Check sync logs regularly for any issues
4. Keep application updated to latest version
5. Contact support if you notice any sync failures

================================================================================
VERSION INFORMATION
================================================================================

Version: 1.0.0
Release Date: January 2024
Compatibility: Tally Prime, Tally ERP 9

================================================================================

Thank you for using Tally Server Sync!

For latest updates and news, visit: https://yourwebsite.com

================================================================================
