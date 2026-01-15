<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Company;
use App\Models\Ledger;
use App\Models\StockItem;
use App\Models\Voucher;
use App\Models\SyncLog;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class TallySyncController extends Controller
{
    /**
     * Sync company data
     */
    public function syncCompany(Request $request)
    {
        $syncLog = $this->createSyncLog('company');
        
        try {
            $data = $request->all();
            
            // Extract company info from nested structure
            $companyData = $data['BODY']['DATA'] ?? $data;
            
            $company = Company::updateOrCreate(
                [
                    'user_id' => $request->user()->id,
                    'name' => $companyData['FldCompanyName'] ?? $companyData['NAME'] ?? 'Unknown',
                ],
                [
                    'guid' => $companyData['FldGUID'] ?? $companyData['GUID'] ?? null,
                    'gstin' => $companyData['FldGSTIN'] ?? $companyData['GSTREGISTRATIONNO'] ?? null,
                    'pan' => $companyData['FldPAN'] ?? $companyData['PAN'] ?? null,
                    'address' => $companyData['FldAddress'] ?? $companyData['ADDRESS'] ?? null,
                    'email' => $companyData['FldEmail'] ?? $companyData['EMAIL'] ?? null,
                    'phone' => $companyData['FldPhone'] ?? $companyData['PHONE'] ?? null,
                    'last_synced' => now(),
                ]
            );
            
            $this->completeSyncLog($syncLog, $company->wasRecentlyCreated ? 1 : 0, $company->wasRecentlyCreated ? 0 : 1, 1);
            
            return response()->json([
                'success' => true,
                'message' => 'Company data synced successfully',
                'data' => [
                    'company_id' => $company->id,
                    'action' => $company->wasRecentlyCreated ? 'created' : 'updated'
                ]
            ]);
            
        } catch (\Exception $e) {
            $this->failSyncLog($syncLog, $e->getMessage());
            Log::error('Company sync failed: ' . $e->getMessage());
            
            return response()->json([
                'success' => false,
                'error' => 'Failed to sync company data',
                'details' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Sync ledgers
     */
    public function syncLedgers(Request $request)
    {
        $syncLog = $this->createSyncLog('ledgers');
        
        try {
            $ledgers = is_array($request->all()) && isset($request->all()[0]) 
                ? $request->all() 
                : [$request->all()];
            
            $inserted = 0;
            $updated = 0;
            
            DB::beginTransaction();
            
            foreach ($ledgers as $ledgerData) {
                $ledger = Ledger::updateOrCreate(
                    [
                        'user_id' => $request->user()->id,
                        'guid' => $ledgerData['GUID'] ?? $ledgerData['guid'] ?? null,
                    ],
                    [
                        'name' => $ledgerData['NAME'] ?? $ledgerData['name'],
                        'parent' => $ledgerData['PARENT'] ?? $ledgerData['parent'] ?? null,
                        'opening_balance' => $ledgerData['OPENINGBALANCE'] ?? $ledgerData['opening_balance'] ?? 0,
                        'closing_balance' => $ledgerData['CLOSINGBALANCE'] ?? $ledgerData['closing_balance'] ?? 0,
                        'gstin' => $ledgerData['PARTYGSTIN'] ?? $ledgerData['gstin'] ?? null,
                        'phone' => $ledgerData['LEDGERPHONE'] ?? $ledgerData['phone'] ?? null,
                        'email' => $ledgerData['LEDGEREMAIL'] ?? $ledgerData['email'] ?? null,
                        'address' => $ledgerData['ADDRESS'] ?? $ledgerData['address'] ?? null,
                        'last_synced' => now(),
                    ]
                );
                
                $ledger->wasRecentlyCreated ? $inserted++ : $updated++;
            }
            
            DB::commit();
            
            $this->completeSyncLog($syncLog, $inserted, $updated, count($ledgers));
            
            return response()->json([
                'success' => true,
                'message' => 'Ledgers synced successfully',
                'data' => [
                    'inserted' => $inserted,
                    'updated' => $updated,
                    'total' => count($ledgers)
                ]
            ]);
            
        } catch (\Exception $e) {
            DB::rollBack();
            $this->failSyncLog($syncLog, $e->getMessage());
            Log::error('Ledgers sync failed: ' . $e->getMessage());
            
            return response()->json([
                'success' => false,
                'error' => 'Failed to sync ledgers',
                'details' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Sync stock items
     */
    public function syncStockItems(Request $request)
    {
        $syncLog = $this->createSyncLog('stock_items');
        
        try {
            $stockItems = is_array($request->all()) && isset($request->all()[0]) 
                ? $request->all() 
                : [$request->all()];
            
            $inserted = 0;
            $updated = 0;
            
            DB::beginTransaction();
            
            foreach ($stockItems as $itemData) {
                $item = StockItem::updateOrCreate(
                    [
                        'user_id' => $request->user()->id,
                        'guid' => $itemData['GUID'] ?? $itemData['guid'] ?? null,
                    ],
                    [
                        'name' => $itemData['NAME'] ?? $itemData['name'],
                        'parent' => $itemData['PARENT'] ?? $itemData['parent'] ?? null,
                        'base_units' => $itemData['BASEUNITS'] ?? $itemData['base_units'] ?? null,
                        'opening_balance' => $itemData['OPENINGBALANCE'] ?? $itemData['opening_balance'] ?? 0,
                        'opening_value' => $itemData['OPENINGVALUE'] ?? $itemData['opening_value'] ?? 0,
                        'closing_balance' => $itemData['CLOSINGBALANCE'] ?? $itemData['closing_balance'] ?? 0,
                        'closing_value' => $itemData['CLOSINGVALUE'] ?? $itemData['closing_value'] ?? 0,
                        'hsn_code' => $itemData['HSNCODE'] ?? $itemData['hsn_code'] ?? null,
                        'gst_applicable' => $itemData['GSTAPPLICABLE'] ?? $itemData['gst_applicable'] ?? null,
                        'last_synced' => now(),
                    ]
                );
                
                $item->wasRecentlyCreated ? $inserted++ : $updated++;
            }
            
            DB::commit();
            
            $this->completeSyncLog($syncLog, $inserted, $updated, count($stockItems));
            
            return response()->json([
                'success' => true,
                'message' => 'Stock items synced successfully',
                'data' => [
                    'inserted' => $inserted,
                    'updated' => $updated,
                    'total' => count($stockItems)
                ]
            ]);
            
        } catch (\Exception $e) {
            DB::rollBack();
            $this->failSyncLog($syncLog, $e->getMessage());
            Log::error('Stock items sync failed: ' . $e->getMessage());
            
            return response()->json([
                'success' => false,
                'error' => 'Failed to sync stock items',
                'details' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Sync vouchers
     */
    public function syncVouchers(Request $request)
    {
        $syncLog = $this->createSyncLog('vouchers');
        
        try {
            $vouchers = is_array($request->all()) && isset($request->all()[0]) 
                ? $request->all() 
                : [$request->all()];
            
            $inserted = 0;
            $updated = 0;
            
            DB::beginTransaction();
            
            foreach ($vouchers as $voucherData) {
                $voucher = Voucher::updateOrCreate(
                    [
                        'user_id' => $request->user()->id,
                        'guid' => $voucherData['GUID'] ?? $voucherData['guid'] ?? null,
                    ],
                    [
                        'date' => $voucherData['DATE'] ?? $voucherData['date'],
                        'voucher_type' => $voucherData['VOUCHERTYPENAME'] ?? $voucherData['voucher_type'],
                        'voucher_number' => $voucherData['VOUCHERNUMBER'] ?? $voucherData['voucher_number'] ?? null,
                        'reference' => $voucherData['REFERENCE'] ?? $voucherData['reference'] ?? null,
                        'reference_date' => $voucherData['REFERENCEDATE'] ?? $voucherData['reference_date'] ?? null,
                        'narration' => $voucherData['NARRATION'] ?? $voucherData['narration'] ?? null,
                        'party_name' => $voucherData['PARTYNAME'] ?? $voucherData['party_name'] ?? null,
                        'amount' => $voucherData['AMOUNT'] ?? $voucherData['amount'] ?? 0,
                        'is_invoice' => $voucherData['ISINVOICE'] ?? $voucherData['is_invoice'] ?? 'No',
                        'last_synced' => now(),
                    ]
                );
                
                $voucher->wasRecentlyCreated ? $inserted++ : $updated++;
            }
            
            DB::commit();
            
            $this->completeSyncLog($syncLog, $inserted, $updated, count($vouchers));
            
            return response()->json([
                'success' => true,
                'message' => 'Vouchers synced successfully',
                'data' => [
                    'inserted' => $inserted,
                    'updated' => $updated,
                    'total' => count($vouchers)
                ]
            ]);
            
        } catch (\Exception $e) {
            DB::rollBack();
            $this->failSyncLog($syncLog, $e->getMessage());
            Log::error('Vouchers sync failed: ' . $e->getMessage());
            
            return response()->json([
                'success' => false,
                'error' => 'Failed to sync vouchers',
                'details' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get sync status
     */
    public function getSyncStatus(Request $request)
    {
        $userId = $request->user()->id;
        
        $status = [
            'companies' => Company::where('user_id', $userId)->count(),
            'ledgers' => Ledger::where('user_id', $userId)->count(),
            'stock_items' => StockItem::where('user_id', $userId)->count(),
            'vouchers' => Voucher::where('user_id', $userId)->count(),
            'last_sync' => DB::table('sync_logs')
                ->where('user_id', $userId)
                ->where('status', 'success')
                ->max('sync_completed'),
        ];
        
        return response()->json([
            'success' => true,
            'data' => $status
        ]);
    }

    /**
     * Get sync history
     */
    public function getSyncHistory(Request $request)
    {
        $history = SyncLog::where('user_id', $request->user()->id)
            ->orderBy('created_at', 'desc')
            ->limit(50)
            ->get();
        
        return response()->json([
            'success' => true,
            'data' => $history
        ]);
    }

    /**
     * Get companies
     */
    public function getCompanies(Request $request)
    {
        $companies = Company::where('user_id', $request->user()->id)
            ->orderBy('name')
            ->get();
        
        return response()->json([
            'success' => true,
            'data' => $companies
        ]);
    }

    /**
     * Get ledgers
     */
    public function getLedgers(Request $request)
    {
        $ledgers = Ledger::where('user_id', $request->user()->id)
            ->orderBy('name')
            ->paginate(100);
        
        return response()->json([
            'success' => true,
            'data' => $ledgers
        ]);
    }

    /**
     * Get stock items
     */
    public function getStockItems(Request $request)
    {
        $stockItems = StockItem::where('user_id', $request->user()->id)
            ->orderBy('name')
            ->paginate(100);
        
        return response()->json([
            'success' => true,
            'data' => $stockItems
        ]);
    }

    /**
     * Get vouchers
     */
    public function getVouchers(Request $request)
    {
        $vouchers = Voucher::where('user_id', $request->user()->id)
            ->orderBy('date', 'desc')
            ->paginate(100);
        
        return response()->json([
            'success' => true,
            'data' => $vouchers
        ]);
    }

    /**
     * Create sync log entry
     */
    private function createSyncLog($syncType)
    {
        return SyncLog::create([
            'user_id' => auth()->id(),
            'sync_type' => $syncType,
            'status' => 'in_progress',
            'sync_started' => now(),
        ]);
    }

    /**
     * Complete sync log
     */
    private function completeSyncLog($syncLog, $inserted, $updated, $total)
    {
        $syncLog->update([
            'records_inserted' => $inserted,
            'records_updated' => $updated,
            'records_total' => $total,
            'status' => 'success',
            'sync_completed' => now(),
        ]);
    }

    /**
     * Fail sync log
     */
    private function failSyncLog($syncLog, $errorMessage)
    {
        $syncLog->update([
            'status' => 'failed',
            'error_message' => $errorMessage,
            'sync_completed' => now(),
        ]);
    }
}
