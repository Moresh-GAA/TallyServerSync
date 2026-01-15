<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class SyncLog extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'sync_type',
        'records_inserted',
        'records_updated',
        'records_total',
        'status',
        'error_message',
        'sync_started',
        'sync_completed',
    ];

    protected $casts = [
        'sync_started' => 'datetime',
        'sync_completed' => 'datetime',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
