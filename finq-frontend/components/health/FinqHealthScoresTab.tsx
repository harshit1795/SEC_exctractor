'use client';

import { useState } from 'react';
import { useFinqHealthScores } from '@/lib/hooks/useHealthScores';
import { useTickerData } from '@/lib/hooks/useTickerData';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { humanFormat, formatPercent } from '@/lib/utils';
import { getTickerLogoUrl } from '@/lib/utils';

const CATEGORIES = [
  'Technology',
  'Manufacturing',
  'Public Sector',
  'Finance',
  'Other',
];

export function FinqHealthScoresTab() {
  const [selectedCategory, setSelectedCategory] = useState<string>('Technology');
  const { data, isLoading, error } = useFinqHealthScores(selectedCategory || undefined, 10);

  if (isLoading) {
    return <Loading message="Calculating health scores..." />;
  }

  if (error) {
    return <ErrorDisplay error={error} message="Failed to load health scores" />;
  }

  const scores = data?.scores || [];

  return (
    <div className="space-y-6">
      <Card>
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">FinQ Suggestions</h3>
          <p className="text-sm text-gray-600 mb-4">
            Health Score Formula: <code className="bg-gray-100 px-2 py-1 rounded">(Growth_score + NetMargin_score + FCFMargin_score + (1 - DebtEquity_score)) / 4</code>
          </p>
          
          <details className="mb-4">
            <summary className="cursor-pointer text-sm text-blue-600 hover:text-blue-800">
              How are individual metrics scored?
            </summary>
            <div className="mt-2 p-4 bg-gray-50 rounded-lg text-sm text-gray-700">
              <p className="mb-2">
                Each metric (Growth, Net Margin, FCF Margin, Debt to Equity) is converted into a score between 0 and 1 
                using percentile ranking. A higher percentile rank indicates a better score.
              </p>
              <ul className="list-disc list-inside space-y-1">
                <li><strong>Growth_score, NetMargin_score, FCFMargin_score:</strong> These are directly the percentile ranks of the respective metrics. 
                  For example, a company with a Growth_score of 0.9 means its revenue growth is better than 90% of other companies.</li>
                <li><strong>DebtEquity_score:</strong> This is calculated as <code>1 - percentile_rank(Debt to Equity)</code>. This is because a lower Debt to Equity ratio is generally better, 
                  so we invert the percentile rank to ensure a higher score indicates better financial health.</li>
              </ul>
              <p className="mt-2">
                The final Health Score is the average of these individual metric scores.
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
            <p>No sufficient data to compute health scores for this category yet.</p>
          </div>
        ) : (
          <div>
            <h4 className="text-md font-semibold mb-4">Top Stocks in {selectedCategory}</h4>
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
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Growth
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Net Margin
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      FCF Margin
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Debt/Equity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Insight
                    </th>
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
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {score.growth !== null && score.growth !== undefined
                          ? formatPercent(score.growth * 100)
                          : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {score.netMargin !== null && score.netMargin !== undefined
                          ? formatPercent(score.netMargin * 100)
                          : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {score.fcfMargin !== null && score.fcfMargin !== undefined
                          ? formatPercent(score.fcfMargin * 100)
                          : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {score.debtEquity !== null && score.debtEquity !== undefined
                          ? score.debtEquity.toFixed(2)
                          : 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {score.insight || 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}

