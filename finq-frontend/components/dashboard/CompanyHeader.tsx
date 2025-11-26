'use client';

import Image from 'next/image';
import { useTickerData } from '@/lib/hooks/useTickerData';
import { getTickerLogoUrl } from '@/lib/utils';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';

interface CompanyHeaderProps {
  ticker: string;
}

export function CompanyHeader({ ticker }: CompanyHeaderProps) {
  const { data, isLoading, error } = useTickerData(ticker, '1y');

  if (isLoading) {
    return (
      <div className="sticky top-0 z-10 rounded-lg bg-white p-4 shadow-md">
        <Loading message="Loading company info..." size="sm" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="sticky top-0 z-10 rounded-lg bg-white p-4 shadow-md">
        <ErrorDisplay error={error} message="Failed to load company information" />
      </div>
    );
  }

  const info = data?.data?.info || {};
  const companyName = info.longName || info.shortName || ticker;
  const sector = info.sector || 'N/A';
  const industry = info.industry || 'N/A';
  const logoUrl = getTickerLogoUrl(ticker);

  return (
    <div className="sticky top-0 z-10 rounded-lg bg-white p-4 shadow-md mb-6">
      <div className="flex items-center gap-4">
        {logoUrl && (
          <div className="flex-shrink-0">
            <Image
              src={logoUrl}
              alt={`${ticker} logo`}
              width={80}
              height={80}
              className="rounded-lg"
              onError={(e) => {
                e.currentTarget.style.display = 'none';
              }}
            />
          </div>
        )}
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-gray-900">
            {ticker} – {companyName}
          </h2>
          <p className="mt-1 text-sm text-gray-600">
            Sector: {sector} • Industry: {industry}
          </p>
        </div>
      </div>
    </div>
  );
}

