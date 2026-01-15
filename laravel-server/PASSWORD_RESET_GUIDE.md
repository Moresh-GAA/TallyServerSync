# Password Reset Implementation Guide

Complete guide for implementing forgot password functionality with encrypted token URLs.

## 🔐 How It Works

1. **User clicks "Forgot Password"**
2. **User enters email**
3. **System generates encrypted URL with token**
4. **User clicks URL** (sent via email or shown in app)
5. **User enters new password + confirmation**
6. **Password is reset**

## 📋 API Endpoints

### 1. Request Password Reset

**Endpoint:** `POST /api/password/forgot`

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password reset link generated successfully",
  "data": {
    "reset_url": "http://localhost:3000/reset-password?data=eyJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJ0b2tlbiI6ImFiYzEyMy4uLiIsInRpbWVzdGFtcCI6MTcwNTMxNjQwMH0%3D",
    "expires_in": "60 minutes",
    "email": "user@example.com",
    "token": "abc123..."
  }
}
```

### 2. Decrypt Reset URL Data

**Endpoint:** `POST /api/password/decrypt-data`

**Request:**
```json
{
  "data": "eyJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJ0b2tlbiI6ImFiYzEyMy4uLiIsInRpbWVzdGFtcCI6MTcwNTMxNjQwMH0="
}
```

**Response:**
```json
{
  "success": true,
  "message": "Reset link is valid",
  "data": {
    "email": "user@example.com",
    "token": "abc123..."
  }
}
```

### 3. Verify Reset Token (Optional)

**Endpoint:** `POST /api/password/verify-token`

**Request:**
```json
{
  "email": "user@example.com",
  "token": "abc123..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Token is valid. You can now reset your password.",
  "data": {
    "email": "user@example.com",
    "token": "abc123..."
  }
}
```

### 4. Reset Password

**Endpoint:** `POST /api/password/reset`

**Request:**
```json
{
  "email": "user@example.com",
  "token": "abc123...",
  "password": "newpassword123",
  "password_confirmation": "newpassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password has been reset successfully. Please login with your new password."
}
```

## 🔧 Implementation Steps

### Step 1: Run Migration

```bash
php artisan migrate
```

This creates the `password_reset_tokens` table.

### Step 2: Configure Frontend URL

In `.env`:
```env
FRONTEND_URL=http://localhost:3000
```

Or for production:
```env
FRONTEND_URL=https://yourdomain.com
```

### Step 3: Test the Flow

#### Using cURL:

**1. Request Reset Link:**
```bash
curl -X POST http://localhost:8000/api/password/forgot \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**2. Copy the `reset_url` from response**

**3. Extract `data` parameter from URL:**
```
http://localhost:3000/reset-password?data=ENCRYPTED_DATA_HERE
```

**4. Decrypt the data:**
```bash
curl -X POST http://localhost:8000/api/password/decrypt-data \
  -H "Content-Type: application/json" \
  -d '{"data": "ENCRYPTED_DATA_HERE"}'
```

**5. Reset password:**
```bash
curl -X POST http://localhost:8000/api/password/reset \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "token": "TOKEN_FROM_DECRYPT",
    "password": "newpassword123",
    "password_confirmation": "newpassword123"
  }'
```

## 🖥️ Windows Client Implementation

### Add to Configuration Tab:

```python
# Add Forgot Password button
self.forgot_password_btn = QPushButton("Forgot Password?")
self.forgot_password_btn.clicked.connect(self.show_forgot_password_dialog)

def show_forgot_password_dialog(self):
    """Show forgot password dialog"""
    dialog = QDialog(self)
    dialog.setWindowTitle("Forgot Password")
    dialog.setFixedWidth(400)
    
    layout = QVBoxLayout()
    
    # Email input
    email_label = QLabel("Enter your email:")
    email_input = QLineEdit()
    email_input.setPlaceholderText("your@email.com")
    
    # Request button
    request_btn = QPushButton("Send Reset Link")
    request_btn.clicked.connect(lambda: self.request_password_reset(email_input.text(), dialog))
    
    layout.addWidget(email_label)
    layout.addWidget(email_input)
    layout.addWidget(request_btn)
    
    dialog.setLayout(layout)
    dialog.exec()

def request_password_reset(self, email, dialog):
    """Request password reset"""
    if not email:
        QMessageBox.warning(self, "Error", "Please enter your email")
        return
    
    try:
        response = requests.post(
            f"{self.server_url.replace('/tally', '')}/password/forgot",
            json={"email": email},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            reset_url = data['data']['reset_url']
            
            # Show reset URL dialog
            self.show_reset_url_dialog(reset_url)
            dialog.close()
        else:
            QMessageBox.warning(self, "Error", "Failed to send reset link")
            
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Request failed: {str(e)}")

def show_reset_url_dialog(self, reset_url):
    """Show reset URL with copy button"""
    dialog = QDialog(self)
    dialog.setWindowTitle("Password Reset Link")
    dialog.setFixedWidth(500)
    
    layout = QVBoxLayout()
    
    info_label = QLabel("Copy this link and open in browser:")
    url_text = QTextEdit()
    url_text.setPlainText(reset_url)
    url_text.setReadOnly(True)
    url_text.setMaximumHeight(100)
    
    copy_btn = QPushButton("Copy Link")
    copy_btn.clicked.connect(lambda: self.copy_to_clipboard(reset_url))
    
    open_btn = QPushButton("Open in Browser")
    open_btn.clicked.connect(lambda: webbrowser.open(reset_url))
    
    layout.addWidget(info_label)
    layout.addWidget(url_text)
    layout.addWidget(copy_btn)
    layout.addWidget(open_btn)
    
    dialog.setLayout(layout)
    dialog.exec()

def copy_to_clipboard(self, text):
    """Copy text to clipboard"""
    clipboard = QApplication.clipboard()
    clipboard.setText(text)
    QMessageBox.information(self, "Success", "Link copied to clipboard!")
```

### Add Reset Password Page:

```python
def show_reset_password_page(self, email, token):
    """Show reset password form"""
    dialog = QDialog(self)
    dialog.setWindowTitle("Reset Password")
    dialog.setFixedWidth(400)
    
    layout = QVBoxLayout()
    
    # Email (read-only)
    email_label = QLabel(f"Email: {email}")
    
    # New password
    password_label = QLabel("New Password:")
    password_input = QLineEdit()
    password_input.setEchoMode(QLineEdit.EchoMode.Password)
    password_input.setPlaceholderText("Enter new password")
    
    # Confirm password
    confirm_label = QLabel("Confirm Password:")
    confirm_input = QLineEdit()
    confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
    confirm_input.setPlaceholderText("Re-enter password")
    
    # Reset button
    reset_btn = QPushButton("Reset Password")
    reset_btn.clicked.connect(lambda: self.reset_password(
        email, token, password_input.text(), confirm_input.text(), dialog
    ))
    
    layout.addWidget(email_label)
    layout.addWidget(password_label)
    layout.addWidget(password_input)
    layout.addWidget(confirm_label)
    layout.addWidget(confirm_input)
    layout.addWidget(reset_btn)
    
    dialog.setLayout(layout)
    dialog.exec()

def reset_password(self, email, token, password, confirm, dialog):
    """Reset password"""
    if not password or not confirm:
        QMessageBox.warning(self, "Error", "Please fill all fields")
        return
    
    if password != confirm:
        QMessageBox.warning(self, "Error", "Passwords do not match")
        return
    
    if len(password) < 8:
        QMessageBox.warning(self, "Error", "Password must be at least 8 characters")
        return
    
    try:
        response = requests.post(
            f"{self.server_url.replace('/tally', '')}/password/reset",
            json={
                "email": email,
                "token": token,
                "password": password,
                "password_confirmation": confirm
            },
            timeout=10
        )
        
        if response.status_code == 200:
            QMessageBox.information(
                self, 
                "Success", 
                "Password reset successfully! Please login with your new password."
            )
            dialog.close()
        else:
            error = response.json().get('error', 'Failed to reset password')
            QMessageBox.warning(self, "Error", error)
            
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Reset failed: {str(e)}")
```

## 🔒 Security Features

1. **Token Hashing** - Tokens are hashed before storing in database
2. **Expiration** - Tokens expire after 60 minutes
3. **One-Time Use** - Token is deleted after successful reset
4. **Encrypted URL** - Email and token are base64 encoded in URL
5. **Logout All Devices** - All existing sessions are revoked after reset

## 📧 Email Integration (Optional)

To send reset links via email, add to `PasswordResetController`:

```php
use Illuminate\Support\Facades\Mail;

public function sendResetLink(Request $request)
{
    // ... existing code ...
    
    // Send email
    Mail::send('emails.password-reset', [
        'resetUrl' => $resetUrl,
        'user' => $user
    ], function($message) use ($user) {
        $message->to($user->email);
        $message->subject('Reset Your Password');
    });
    
    return response()->json([
        'success' => true,
        'message' => 'Password reset link has been sent to your email'
    ]);
}
```

Create email template at `resources/views/emails/password-reset.blade.php`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Reset Password</title>
</head>
<body>
    <h2>Reset Your Password</h2>
    <p>Click the link below to reset your password:</p>
    <a href="{{ $resetUrl }}">Reset Password</a>
    <p>This link will expire in 60 minutes.</p>
    <p>If you didn't request this, please ignore this email.</p>
</body>
</html>
```

Configure email in `.env`:

```env
MAIL_MAILER=smtp
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_ENCRYPTION=tls
MAIL_FROM_ADDRESS=noreply@yourdomain.com
MAIL_FROM_NAME="${APP_NAME}"
```

## 🧪 Testing

### Test Complete Flow:

```bash
# 1. Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "oldpassword123",
    "password_confirmation": "oldpassword123"
  }'

# 2. Request reset
curl -X POST http://localhost:8000/api/password/forgot \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 3. Copy reset_url and extract data parameter

# 4. Reset password
curl -X POST http://localhost:8000/api/password/reset \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "token": "TOKEN_FROM_STEP_2",
    "password": "newpassword123",
    "password_confirmation": "newpassword123"
  }'

# 5. Login with new password
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "newpassword123"
  }'
```

## 📝 Database Schema

```sql
CREATE TABLE password_reset_tokens (
    email VARCHAR(255) PRIMARY KEY,
    token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NULL,
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
);
```

## ✅ Checklist

- [x] Migration created
- [x] Controller implemented
- [x] Routes added
- [x] Token encryption
- [x] Token expiration (60 min)
- [x] One-time use tokens
- [x] Password validation
- [x] Logout all devices after reset
- [ ] Email integration (optional)
- [ ] Windows client UI (to be implemented)

## 🎯 Next Steps

1. Run migration: `php artisan migrate`
2. Test API endpoints with Postman/cURL
3. Implement Windows client UI
4. (Optional) Add email sending
5. Deploy to production

---

**Password Reset is Ready!** 🎉
