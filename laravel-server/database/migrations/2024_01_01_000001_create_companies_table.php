<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('companies', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->string('name');
            $table->string('guid')->nullable()->unique();
            $table->string('gstin', 50)->nullable();
            $table->string('pan', 20)->nullable();
            $table->text('address')->nullable();
            $table->string('email')->nullable();
            $table->string('phone', 50)->nullable();
            $table->timestamp('last_synced')->nullable();
            $table->timestamps();
            
            $table->unique(['user_id', 'name']);
            $table->index('user_id');
            $table->index('gstin');
        });
    }

    public function down()
    {
        Schema::dropIfExists('companies');
    }
};
