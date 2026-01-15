<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class StockItem extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'name',
        'guid',
        'parent',
        'base_units',
        'opening_balance',
        'opening_value',
        'closing_balance',
        'closing_value',
        'hsn_code',
        'gst_applicable',
        'last_synced',
    ];

    protected $casts = [
        'opening_balance' => 'decimal:3',
        'opening_value' => 'decimal:2',
        'closing_balance' => 'decimal:3',
        'closing_value' => 'decimal:2',
        'last_synced' => 'datetime',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
