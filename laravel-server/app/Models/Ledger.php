<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Ledger extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'name',
        'guid',
        'parent',
        'opening_balance',
        'closing_balance',
        'gstin',
        'phone',
        'email',
        'address',
        'last_synced',
    ];

    protected $casts = [
        'opening_balance' => 'decimal:2',
        'closing_balance' => 'decimal:2',
        'last_synced' => 'datetime',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
