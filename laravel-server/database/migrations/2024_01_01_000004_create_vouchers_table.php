<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('vouchers', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->string('guid')->nullable();
            $table->date('date');
            $table->string('voucher_type', 100);
            $table->string('voucher_number', 100)->nullable();
            $table->string('reference')->nullable();
            $table->date('reference_date')->nullable();
            $table->text('narration')->nullable();
            $table->string('party_name')->nullable();
            $table->decimal('amount', 15, 2)->default(0);
            $table->string('is_invoice', 10)->nullable();
            $table->timestamp('last_synced')->nullable();
            $table->timestamps();
            
            $table->unique(['user_id', 'guid']);
            $table->index('user_id');
            $table->index('date');
            $table->index('voucher_type');
            $table->index('voucher_number');
            $table->index('party_name');
            $table->index('last_synced');
        });
    }

    public function down()
    {
        Schema::dropIfExists('vouchers');
    }
};
