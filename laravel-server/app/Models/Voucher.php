<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Voucher extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'guid',
        'date',
        'voucher_type',
        'voucher_number',
        'reference',
        'reference_date',
        'narration',
        'party_name',
        'amount',
        'is_invoice',
        'last_synced',
    ];

    protected $casts = [
        'date' => 'date',
        'reference_date' => 'date',
        'amount' => 'decimal:2',
        'last_synced' => 'datetime',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
