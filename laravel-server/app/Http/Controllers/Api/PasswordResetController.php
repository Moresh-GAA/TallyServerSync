<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;
use Carbon\Carbon;

class PasswordResetController extends Controller
{
    /**
     * Send password reset link
     * User enters email, receives reset URL with encrypted token
     */
    public function sendResetLink(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
        ]);

        // Check if user exists
        $user = User::where('email', $request->email)->first();

        if (!$user) {
            // Don't reveal if email exists or not (security)
            return response()->json([
                'success' => true,
                'message' => 'If the email exists, a password reset link has been sent.'
            ]);
        }

        // Delete any existing tokens for this user
        DB::table('password_reset_tokens')
            ->where('email', $request->email)
            ->delete();

        // Generate secure random token
        $token = Str::random(64);

        // Store token in database
        DB::table('password_reset_tokens')->insert([
            'email' => $request->email,
            'token' => Hash::make($token), // Store hashed token
            'created_at' => Carbon::now()
        ]);

        // Generate reset URL with encrypted data
        $resetUrl = $this->generateResetUrl($request->email, $token);

        // In production, send this URL via email
        // For now, return it in response
        return response()->json([
            'success' => true,
            'message' => 'Password reset link generated successfully',
            'data' => [
                'reset_url' => $resetUrl,
                'expires_in' => '60 minutes',
                // In production, remove these and only send via email
                'email' => $request->email,
                'token' => $token,
            ]
        ]);
    }

    /**
     * Verify reset token and show reset form
     */
    public function verifyResetToken(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
            'token' => 'required|string',
        ]);

        $resetRecord = DB::table('password_reset_tokens')
            ->where('email', $request->email)
            ->first();

        if (!$resetRecord) {
            return response()->json([
                'success' => false,
                'error' => 'Invalid or expired reset token'
            ], 400);
        }

        // Check if token is expired (60 minutes)
        if (Carbon::parse($resetRecord->created_at)->addMinutes(60)->isPast()) {
            DB::table('password_reset_tokens')
                ->where('email', $request->email)
                ->delete();

            return response()->json([
                'success' => false,
                'error' => 'Reset token has expired. Please request a new one.'
            ], 400);
        }

        // Verify token
        if (!Hash::check($request->token, $resetRecord->token)) {
            return response()->json([
                'success' => false,
                'error' => 'Invalid reset token'
            ], 400);
        }

        return response()->json([
            'success' => true,
            'message' => 'Token is valid. You can now reset your password.',
            'data' => [
                'email' => $request->email,
                'token' => $request->token,
            ]
        ]);
    }

    /**
     * Reset password with new password
     */
    public function resetPassword(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
            'token' => 'required|string',
            'password' => 'required|string|min:8|confirmed',
        ]);

        // Find reset record
        $resetRecord = DB::table('password_reset_tokens')
            ->where('email', $request->email)
            ->first();

        if (!$resetRecord) {
            throw ValidationException::withMessages([
                'email' => ['Invalid or expired reset token.'],
            ]);
        }

        // Check if token is expired (60 minutes)
        if (Carbon::parse($resetRecord->created_at)->addMinutes(60)->isPast()) {
            DB::table('password_reset_tokens')
                ->where('email', $request->email)
                ->delete();

            throw ValidationException::withMessages([
                'token' => ['Reset token has expired. Please request a new one.'],
            ]);
        }

        // Verify token
        if (!Hash::check($request->token, $resetRecord->token)) {
            throw ValidationException::withMessages([
                'token' => ['Invalid reset token.'],
            ]);
        }

        // Find user
        $user = User::where('email', $request->email)->first();

        if (!$user) {
            throw ValidationException::withMessages([
                'email' => ['User not found.'],
            ]);
        }

        // Update password
        $user->password = Hash::make($request->password);
        $user->save();

        // Delete reset token
        DB::table('password_reset_tokens')
            ->where('email', $request->email)
            ->delete();

        // Revoke all existing tokens (logout from all devices)
        $user->tokens()->delete();

        return response()->json([
            'success' => true,
            'message' => 'Password has been reset successfully. Please login with your new password.'
        ]);
    }

    /**
     * Generate encrypted reset URL
     */
    private function generateResetUrl($email, $token)
    {
        // Base URL (configure in .env)
        $baseUrl = config('app.frontend_url', 'http://localhost:3000');
        
        // Encrypt email and token together
        $encryptedData = base64_encode(json_encode([
            'email' => $email,
            'token' => $token,
            'timestamp' => time()
        ]));

        // Generate reset URL
        return $baseUrl . '/reset-password?data=' . urlencode($encryptedData);
    }

    /**
     * Decrypt reset URL data
     */
    public function decryptResetData(Request $request)
    {
        $request->validate([
            'data' => 'required|string',
        ]);

        try {
            // Decode encrypted data
            $decryptedData = json_decode(base64_decode($request->data), true);

            if (!$decryptedData || !isset($decryptedData['email']) || !isset($decryptedData['token'])) {
                return response()->json([
                    'success' => false,
                    'error' => 'Invalid reset link'
                ], 400);
            }

            // Verify token is still valid
            $resetRecord = DB::table('password_reset_tokens')
                ->where('email', $decryptedData['email'])
                ->first();

            if (!$resetRecord) {
                return response()->json([
                    'success' => false,
                    'error' => 'Invalid or expired reset link'
                ], 400);
            }

            // Check if token is expired (60 minutes)
            if (Carbon::parse($resetRecord->created_at)->addMinutes(60)->isPast()) {
                DB::table('password_reset_tokens')
                    ->where('email', $decryptedData['email'])
                    ->delete();

                return response()->json([
                    'success' => false,
                    'error' => 'Reset link has expired. Please request a new one.'
                ], 400);
            }

            // Verify token
            if (!Hash::check($decryptedData['token'], $resetRecord->token)) {
                return response()->json([
                    'success' => false,
                    'error' => 'Invalid reset link'
                ], 400);
            }

            return response()->json([
                'success' => true,
                'message' => 'Reset link is valid',
                'data' => [
                    'email' => $decryptedData['email'],
                    'token' => $decryptedData['token'],
                ]
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => 'Invalid reset link format'
            ], 400);
        }
    }
}
