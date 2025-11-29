'use client';

import { useState } from 'react';
import { useUpdateTickerData, useUpdateLatestData, useDataStatus } from '@/lib/hooks/useDataPipeline';

interface DataUpdateButtonProps {
  ticker?: string;
  onUpdateComplete?: () => void;
  showUpdateAll?: boolean;
}

export function DataUpdateButton({ ticker, onUpdateComplete, showUpdateAll = false }: DataUpdateButtonProps) {
  const [message, setMessage] = useState<string | null>(null);
  const [updateType, setUpdateType] = useState<'single' | 'all' | null>(null);
  const updateTicker = useUpdateTickerData();
  const updateLatest = useUpdateLatestData();
  const { data: dataStatus } = useDataStatus(ticker);

  const isUpdating = updateTicker.isPending || updateLatest.isPending;

  const handleUpdateSingle = async () => {
    if (!ticker) return;
    
    setMessage(null);
    setUpdateType('single');

    try {
      const result = await updateTicker.mutateAsync({
        ticker,
        forceRefresh: false,
      });
      setMessage(
        result?.success
          ? `✅ Updated ${ticker}: ${result.new_records || 0} new records, ${result.total_records || 0} total`
          : `❌ Failed: ${result?.message || 'Unknown error'}`
      );

      if (onUpdateComplete) {
        setTimeout(() => {
          onUpdateComplete();
        }, 1000);
      }
    } catch (error: any) {
      setMessage(`❌ Error: ${error?.response?.data?.detail || error.message || 'Update failed'}`);
    } finally {
      setUpdateType(null);
    }
  };

  const handleUpdateAll = async () => {
    setMessage(null);
    setUpdateType('all');

    try {
      const result = await updateLatest.mutateAsync(undefined);
      const updated = result?.updated || 0;
      const failed = result?.failed || 0;
      const total = result?.total_tickers || 0;
      
      if (failed === 0) {
        setMessage(`✅ Successfully updated all ${updated} tickers`);
      } else {
        setMessage(`⚠️ Updated ${updated}/${total} tickers (${failed} failed)`);
      }

      if (onUpdateComplete) {
        setTimeout(() => {
          onUpdateComplete();
        }, 2000);
      }
    } catch (error: any) {
      setMessage(`❌ Error: ${error?.response?.data?.detail || error.message || 'Update failed'}`);
    } finally {
      setUpdateType(null);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 flex-wrap">
        {ticker && (
          <button
            onClick={handleUpdateSingle}
            disabled={isUpdating}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
            title={`Update data for ${ticker} only`}
          >
            {isUpdating && updateType === 'single' ? (
              <>
                <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
                Updating {ticker}...
              </>
            ) : (
              <>🔄 Update {ticker}</>
            )}
          </button>
        )}
        
        {showUpdateAll && (
          <button
            onClick={handleUpdateAll}
            disabled={isUpdating}
            className="rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
            title="Update all tickers in the fundamentals database"
          >
            {isUpdating && updateType === 'all' ? (
              <>
                <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
                Updating All Data...
              </>
            ) : (
              <>📊 Update All Data</>
            )}
          </button>
        )}
      </div>
      
      {message && (
        <div className={`text-sm p-2 rounded ${
          message.startsWith('✅') 
            ? 'bg-green-50 text-green-800' 
            : message.startsWith('⚠️')
            ? 'bg-yellow-50 text-yellow-800'
            : 'bg-red-50 text-red-800'
        }`}>
          {message}
        </div>
      )}
      
      {dataStatus?.latest_period && (
        <p className="text-xs text-gray-500">
          Latest data period: <span className="font-medium">{dataStatus.latest_period}</span>
          {dataStatus.total_records && (
            <> • {dataStatus.total_records.toLocaleString()} records</>
          )}
        </p>
      )}
    </div>
  );
}

