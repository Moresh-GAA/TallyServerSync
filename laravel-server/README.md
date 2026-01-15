# Tally Sync - Laravel Server (Multi-Tenant SaaS)

Laravel backend for Tally Server Sync with multi-tenant support using Laravel Sanctum authentication.

## Features

- ✅ **Multi-Tenant Architecture** - Each user has isolated data
- ✅ **Laravel Sanctum Authentication** - Token-based API authentication
- ✅ **RESTful API** - Clean and well-documented endpoints
- ✅ **Automatic Upsert** - Insert new, update existing records
- ✅ **Transaction Support** - Data consistency guaranteed
- ✅ **Sync Logging** - Track all sync operations
- ✅ **Eloquent ORM** - Clean database interactions
- ✅ **Validation** - Request validation built-in

## Prerequisites

- PHP 8.1+
- Composer
- MySQL 5.7+ / MariaDB 10.3+
- Laravel 10.x

## Installation

### 1. Copy Files to Laravel Project

Copy all files from `laravel-server/` to your Laravel project:

```bash
# Routes
cp routes/api.php your-laravel-project/routes/

# Controllers
cp -r app/Http/Controllers/Api your-laravel-project/app/Http/Controllers/

# Models
cp -r app/Models/* your-laravel-project/app/Models/

# Migrations
cp database/migrations/* your-laravel-project/database/migrations/
```

### 2. Install Laravel Sanctum

```bash
composer require laravel/sanctum

php artisan vendor:publish --provider="Laravel\Sanctum\SanctumServiceProvider"
```

### 3. Configure Sanctum

In `config/sanctum.php`, ensure:

```php
'stateful' => explode(',', env('SANCTUM_STATEFUL_DOMAINS', sprintf(
    '%s%s',
    'localhost,localhost:3000,127.0.0.1,127.0.0.1:8000,::1',
    env('APP_URL') ? ','.parse_url(env('APP_URL'), PHP_URL_HOST) : ''
))),
```

### 4. Update User Model

In `app/Models/User.php`, add:

```php
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;
    
    // ... rest of the model
}
```

### 5. Run Migrations

```bash
php artisan migrate
```

### 6. Configure CORS

In `config/cors.php`:

```php
'paths' => ['api/*', 'sanctum/csrf-cookie'],

'allowed_methods' => ['*'],

'allowed_origins' => ['*'], // Or specify your client domains

'allowed_headers' => ['*'],

'supports_credentials' => true,
```

### 7. Start Server

```bash
php artisan serve
```

Server runs at: `http://localhost:8000`

## API Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "password_confirmation": "password123"
}
```

Response:
```json
{
  "success": true,
  "message": "Registration successful",
  "data": {
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    },
    "token": "1|abc123..."
  }
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    },
    "token": "2|xyz789..."
  }
}
```

#### Get User
```http
GET /api/auth/user
Authorization: Bearer {token}
```

#### Logout
```http
POST /api/auth/logout
Authorization: Bearer {token}
```

### Tally Sync Endpoints

All endpoints require authentication via Bearer token.

#### Sync Company
```http
POST /api/tally/company
Authorization: Bearer {token}
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

#### Sync Ledgers
```http
POST /api/tally/ledgers
Authorization: Bearer {token}
Content-Type: application/json

[
  {
    "NAME": "Cash",
    "PARENT": "Cash-in-Hand",
    "OPENINGBALANCE": "10000.00"
  }
]
```

#### Sync Stock Items
```http
POST /api/tally/stock-items
Authorization: Bearer {token}
Content-Type: application/json

[
  {
    "NAME": "Product A",
    "PARENT": "Finished Goods",
    "BASEUNITS": "Nos"
  }
]
```

#### Sync Vouchers
```http
POST /api/tally/vouchers
Authorization: Bearer {token}
Content-Type: application/json

[
  {
    "DATE": "20240115",
    "VOUCHERTYPENAME": "Sales",
    "AMOUNT": "5000.00"
  }
]
```

#### Get Sync Status
```http
GET /api/tally/sync-status
Authorization: Bearer {token}
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
    "last_sync": "2024-01-15T10:30:00.000000Z"
  }
}
```

#### Get Sync History
```http
GET /api/tally/sync-history
Authorization: Bearer {token}
```

#### Get Data
```http
GET /api/tally/companies
GET /api/tally/ledgers
GET /api/tally/stock-items
GET /api/tally/vouchers
Authorization: Bearer {token}
```

## Database Schema

### Multi-Tenant Design

All tables include `user_id` foreign key for data isolation:

- **companies** - User's company information
- **ledgers** - User's ledger accounts
- **stock_items** - User's inventory items
- **vouchers** - User's transactions
- **sync_logs** - User's sync operation history

### Relationships

```
User
  ├── companies (hasMany)
  ├── ledgers (hasMany)
  ├── stock_items (hasMany)
  ├── vouchers (hasMany)
  └── sync_logs (hasMany)
```

## Client Configuration

Update your Windows client to use Laravel backend:

1. **Server URL:** `http://your-domain.com/api/tally`
2. **Authentication:** Use email/password instead of API key
3. **Token:** Stored after login, sent with each request

## Testing

### Using cURL

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "password_confirmation": "password123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Sync Company (use token from login)
curl -X POST http://localhost:8000/api/tally/company \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "BODY": {
      "DATA": {
        "FldCompanyName": "Test Company"
      }
    }
  }'
```

### Using Postman

1. Import collection from `postman_collection.json`
2. Set environment variable `base_url` to `http://localhost:8000/api`
3. Login to get token
4. Token auto-saved for subsequent requests

## Security

### Authentication

- Uses Laravel Sanctum for token-based authentication
- Tokens are personal access tokens
- Each user can only access their own data

### Data Isolation

- All queries automatically scoped to authenticated user
- Foreign key constraints ensure data integrity
- Cascade delete removes user data on account deletion

### Best Practices

1. **Use HTTPS** in production
2. **Rotate tokens** regularly
3. **Validate input** (already implemented)
4. **Rate limiting** (configure in `app/Http/Kernel.php`)
5. **Monitor logs** for suspicious activity

## Deployment

### Production Setup

1. **Environment:**
```env
APP_ENV=production
APP_DEBUG=false
APP_URL=https://your-domain.com

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=tally_sync
DB_USERNAME=your_user
DB_PASSWORD=your_password

SANCTUM_STATEFUL_DOMAINS=your-domain.com
SESSION_DOMAIN=.your-domain.com
```

2. **Optimize:**
```bash
php artisan config:cache
php artisan route:cache
php artisan view:cache
php artisan optimize
```

3. **Queue Workers** (optional):
```bash
php artisan queue:work --daemon
```

## Monitoring

### Check Sync Status

```sql
-- Total records per user
SELECT 
    u.email,
    (SELECT COUNT(*) FROM companies WHERE user_id = u.id) as companies,
    (SELECT COUNT(*) FROM ledgers WHERE user_id = u.id) as ledgers,
    (SELECT COUNT(*) FROM stock_items WHERE user_id = u.id) as stock_items,
    (SELECT COUNT(*) FROM vouchers WHERE user_id = u.id) as vouchers
FROM users u;

-- Recent sync operations
SELECT * FROM sync_logs
ORDER BY created_at DESC
LIMIT 20;
```

### Logs

```bash
# Application logs
tail -f storage/logs/laravel.log

# Query logs (enable in config/database.php)
DB::enableQueryLog();
```

## Troubleshooting

### Token Issues

```bash
# Clear cache
php artisan config:clear
php artisan cache:clear

# Regenerate key
php artisan key:generate
```

### Database Issues

```bash
# Fresh migration
php artisan migrate:fresh

# Rollback and re-migrate
php artisan migrate:rollback
php artisan migrate
```

## Support

For issues:
1. Check Laravel logs: `storage/logs/laravel.log`
2. Verify database connection
3. Check Sanctum configuration
4. Review API documentation

## License

MIT
