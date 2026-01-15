<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\TallySyncController;
use App\Http\Controllers\Api\AuthController;

/*
|--------------------------------------------------------------------------
| API Routes for Tally Sync (Multi-Tenant SaaS)
|--------------------------------------------------------------------------
*/

// Authentication routes
Route::prefix('auth')->group(function () {
    Route::post('login', [AuthController::class, 'login']);
    Route::post('register', [AuthController::class, 'register']);
    Route::middleware('auth:sanctum')->group(function () {
        Route::post('logout', [AuthController::class, 'logout']);
        Route::get('user', [AuthController::class, 'user']);
    });
});

// Public health check
Route::get('health', function () {
    return response()->json([
        'status' => 'ok',
        'timestamp' => now()->toIso8601String(),
        'version' => '1.0.0'
    ]);
});

// Protected Tally Sync routes (requires authentication)
Route::middleware('auth:sanctum')->prefix('tally')->group(function () {
    
    // Company data
    Route::post('company', [TallySyncController::class, 'syncCompany']);
    
    // Ledgers
    Route::post('ledgers', [TallySyncController::class, 'syncLedgers']);
    
    // Stock items
    Route::post('stock-items', [TallySyncController::class, 'syncStockItems']);
    
    // Vouchers
    Route::post('vouchers', [TallySyncController::class, 'syncVouchers']);
    
    // Sync status
    Route::get('sync-status', [TallySyncController::class, 'getSyncStatus']);
    
    // Sync history
    Route::get('sync-history', [TallySyncController::class, 'getSyncHistory']);
    
    // Get data
    Route::get('companies', [TallySyncController::class, 'getCompanies']);
    Route::get('ledgers', [TallySyncController::class, 'getLedgers']);
    Route::get('stock-items', [TallySyncController::class, 'getStockItems']);
    Route::get('vouchers', [TallySyncController::class, 'getVouchers']);
});
