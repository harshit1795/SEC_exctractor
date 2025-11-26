'use client';

import { useState } from 'react';
import { useUpdateTickerData, useUpdateLatestData } from '@/lib/hooks/useDataPipeline';

interface DataUpdateButtonProps {
  ticker?: string;
  onUpdateComplete?: () => void;
}

export function DataUpdateButton({ ticker, onUpdateComplete }: DataUpdateButtonProps) {
  const [message, setMessage] = useState<string | null>(null);
  const updateTicker = useUpdateTickerData();
  const updateLatest = useUpdateLatestData();

  const isUpdating = updateTicker.isPending || updateLatest.isPending;

  const handleUpdate = async () => {
    setMessage(null);

    try {
      if (ticker) {
        // Update single ticker
        const result = await updateTicker.mutateAsync({
          ticker,
          forceRefresh: false,
        });
        setMessage(
          result?.success
            ? `✅ Updated ${ticker}: ${result.new_records} new records`
            : `❌ Failed: ${result?.message || 'Unknown error'}`
        );
      } else {
        // Update all tickers
        const result = await updateLatest.mutateAsync(undefined);
        setMessage(
          `✅ Batch update: ${result?.updated || 0} updated, ${result?.failed || 0} failed`
        );
      }

      // Refresh data after update
      if (onUpdateComplete) {
        setTimeout(() => {
          onUpdateComplete();
        }, 1000);
      }
    } catch (error: any) {
      setMessage(`❌ Error: ${error.message || 'Update failed'}`);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handleUpdate}
        disabled={isUpdating}
        className="rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {isUpdating ? (
          <>
            <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent mr-2"></span>
            Updating...
          </>
        ) : (
          <>🔄 Update Data</>
        )}
      </button>
      {message && (
        <span className="text-sm text-gray-600">{message}</span>
      )}
    </div>
  );
}

