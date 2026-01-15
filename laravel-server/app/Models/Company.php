<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Company extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'name',
        'guid',
        'gstin',
        'pan',
        'address',
        'email',
        'phone',
        'last_synced',
    ];

    protected $casts = [
        'last_synced' => 'datetime',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
