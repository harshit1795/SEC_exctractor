'use client';

import { useState, useMemo, useEffect } from 'react';
import { useCustomHealthScores } from '@/lib/hooks/useHealthScores';
import { useFundamentals } from '@/lib/hooks/useTickerData';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { MultiSelect } from '@/components/shared/MultiSelect';
import { humanFormat } from '@/lib/utils';
import { getTickerLogoUrl } from '@/lib/utils';
import { useAuth } from '@/lib/hooks/useAuth';

const CATEGORIES = [
  'Technology',
  'Manufacturing',
  'Public Sector',
  'Finance',
  'Other',
];

export function CustomHealthScoresTab() {
  const { user } = useAuth();
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('Technology');
  
  // Get available metrics from fundamentals data (use first available ticker as sample)
  const { data: sampleFundamentals } = useFundamentals('AAPL');
  const availableMetrics = useMemo(() => {
    const dataArray = sampleFundamentals?.data?.data || sampleFundamentals?.data || [];
    if (!Array.isArray(dataArray)) return [];
    const metrics = new Set<string>();
    dataArray.forEach((item: any) => {
      const metric = item.Metric || item.metric;
      if (metric) metrics.add(metric);
    });
    return Array.from(metrics).sort();
  }, [sampleFundamentals]);

  // Load saved preferences
  useEffect(() => {
    if (user?.uid) {
      const saved = localStorage.getItem(`health_metrics_${user.uid}`);
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          if (Array.isArray(parsed) && parsed.length > 0) {
            setSelectedMetrics(parsed);
          }
        } catch (e) {
          // Ignore parse errors
        }
      }
    }
  }, [user?.uid]);

  const { data, isLoading, error } = useCustomHealthScores(selectedMetrics, 10);

  const handleSavePreferences = () => {
    if (user?.uid && selectedMetrics.length > 0) {
      localStorage.setItem(`health_metrics_${user.uid}`, JSON.stringify(selectedMetrics));
      alert('Preferences saved!');
    }
  };

  if (isLoading) {
    return <Loading message="Calculating custom health scores..." />;
  }

  if (error) {
    return <ErrorDisplay error={error} message="Failed to load custom health scores" />;
  }

  const scores = data?.scores || [];

  return (
    <div className="space-y-6">
      <Card>
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">Your Selections</h3>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select your preferred metrics for health score calculation:
            </label>
            <MultiSelect
              options={availableMetrics}
              selected={selectedMetrics}
              onChange={setSelectedMetrics}
              placeholder="Search and select metrics..."
            />
          </div>

          <button
            onClick={handleSavePreferences}
            disabled={selectedMetrics.length === 0}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Save Preferences
          </button>
        </div>

        {selectedMetrics.length > 0 && (
          <>
            <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-gray-700 mb-2">
                <strong>Custom Health Score Formula:</strong>{' '}
                <code className="bg-white px-2 py-1 rounded">
                  ({selectedMetrics.map(m => `\`${m}_score\``).join(' + ')}) / {selectedMetrics.length}
                </code>
              </p>
              <details className="mt-2">
                <summary className="cursor-pointer text-sm text-blue-600 hover:text-blue-800">
                  How are individual metrics scored?
                </summary>
                <div className="mt-2 text-sm text-gray-700">
                  <p>
                    Each selected metric is converted into a score between 0 and 1 using percentile ranking. 
                    A higher percentile rank indicates a better score.
                  </p>
                  <p className="mt-2">
                    <strong>Note:</strong> For simplicity, this calculation assumes that a higher value for each selected metric is always better. 
                    If you select metrics where a lower value is preferable (e.g., Debt-to-Equity Ratio), 
                    you may need to manually invert its contribution to the overall score for accurate results.
                  </p>
                </div>
              </details>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Category
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            {scores.length === 0 ? (
              <div className="text-center py-8 text-gray-600">
                <p>No sufficient data to compute health scores for this category and selection.</p>
              </div>
            ) : (
              <div>
                <h4 className="text-md font-semibold mb-4">Top Companies by Custom Health Score</h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Ticker
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Health Score
                        </th>
                        {selectedMetrics.map((metric) => (
                          <th
                            key={metric}
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                          >
                            {metric}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {scores.map((score: any) => (
                        <tr key={score.ticker} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <img
                                src={getTickerLogoUrl(score.ticker)}
                                alt={score.ticker}
                                className="h-8 w-8 rounded-full mr-2"
                                onError={(e) => {
                                  (e.target as HTMLImageElement).style.display = 'none';
                                }}
                              />
                              <span className="text-sm font-medium text-gray-900">{score.ticker}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="flex-1">
                                <div className="w-full bg-gray-200 rounded-full h-2.5">
                                  <div
                                    className={`h-2.5 rounded-full ${
                                      (score.healthScore || 0) >= 0.7
                                        ? 'bg-green-600'
                                        : (score.healthScore || 0) >= 0.5
                                        ? 'bg-yellow-500'
                                        : 'bg-red-600'
                                    }`}
                                    style={{ width: `${((score.healthScore || 0) * 100)}%` }}
                                  />
                                </div>
                                <span className="text-sm text-gray-900 mt-1">
                                  {((score.healthScore || 0) * 100).toFixed(1)}%
                                </span>
                              </div>
                            </div>
                          </td>
                          {selectedMetrics.map((metric) => (
                            <td key={metric} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {score[metric] !== null && score[metric] !== undefined
                                ? humanFormat(score[metric])
                                : 'N/A'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}

        {selectedMetrics.length === 0 && (
          <div className="text-center py-8 text-gray-600">
            <p>Please select metrics above to calculate custom health scores.</p>
          </div>
        )}
      </Card>
    </div>
  );
}

