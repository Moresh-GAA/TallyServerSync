<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('sync_logs', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->string('sync_type', 50);
            $table->integer('records_inserted')->default(0);
            $table->integer('records_updated')->default(0);
            $table->integer('records_total')->default(0);
            $table->string('status', 20);
            $table->text('error_message')->nullable();
            $table->timestamp('sync_started')->nullable();
            $table->timestamp('sync_completed')->nullable();
            $table->timestamps();
            
            $table->index('user_id');
            $table->index('sync_type');
            $table->index('status');
            $table->index('created_at');
        });
    }

    public function down()
    {
        Schema::dropIfExists('sync_logs');
    }
};
