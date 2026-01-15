<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('ledgers', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->string('name');
            $table->string('guid')->nullable();
            $table->string('parent')->nullable();
            $table->decimal('opening_balance', 15, 2)->default(0);
            $table->decimal('closing_balance', 15, 2)->default(0);
            $table->string('gstin', 50)->nullable();
            $table->string('phone', 50)->nullable();
            $table->string('email')->nullable();
            $table->text('address')->nullable();
            $table->timestamp('last_synced')->nullable();
            $table->timestamps();
            
            $table->unique(['user_id', 'guid']);
            $table->index('user_id');
            $table->index('name');
            $table->index('parent');
            $table->index('last_synced');
        });
    }

    public function down()
    {
        Schema::dropIfExists('ledgers');
    }
};
