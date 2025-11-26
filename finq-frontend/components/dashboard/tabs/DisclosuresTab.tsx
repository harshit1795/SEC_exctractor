'use client';

import { useState } from 'react';
import { useSec10K, useSec10Q, useSecFilings } from '@/lib/hooks/useSecData';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';

interface DisclosuresTabProps {
  ticker: string;
}

type ReportType = '10-K' | '10-Q';

interface SectionOption {
  label: string;
  key: string;
}

const SECTION_OPTIONS_10K: SectionOption[] = [
  { label: "Business Overview (Item 1)", key: "business" },
  { label: "Risk Factors (Item 1A)", key: "risk" },
  { label: "Management's Discussion & Analysis (Item 7)", key: "mda" },
];

const SECTION_OPTIONS_10Q: SectionOption[] = [
  { label: "Risk Factors (Part II, Item 1A)", key: "risk" },
  { label: "Management's Discussion & Analysis (Part I, Item 2)", key: "mda" },
];

export function DisclosuresTab({ ticker }: DisclosuresTabProps) {
  const [reportType, setReportType] = useState<ReportType>('10-K');
  const [selectedSection, setSelectedSection] = useState<string>('');

  // Fetch filing metadata
  const { data: filingsData, isLoading: isLoadingFilings, error: filingsError } = useSecFilings(ticker);

  // Fetch sections based on report type - only fetch if we have filing info
  const filingInfoForType = filingsData?.filings?.[reportType.toLowerCase()] || 
                             filingsData?.filings?.[reportType] ||
                             null;
  const shouldFetchSections = !!filingInfoForType;
  
  const { data: sec10KData, isLoading: isLoading10K, error: error10K } = useSec10K(
    ticker,
    reportType === '10-K' && shouldFetchSections ? ['business', 'risk', 'mda'] : []
  );

  const { data: sec10QData, isLoading: isLoading10Q, error: error10Q } = useSec10Q(
    ticker,
    reportType === '10-Q' && shouldFetchSections ? ['risk', 'mda'] : []
  );

  const isLoading = isLoadingFilings || (reportType === '10-K' && shouldFetchSections ? isLoading10K : false) || (reportType === '10-Q' && shouldFetchSections ? isLoading10Q : false);
  // Only show error if it's from filings, not from sections (sections might fail if no filing exists)
  const error = filingsError;
  const sectionsData = reportType === '10-K' ? sec10KData : sec10QData;
  const sectionOptions = reportType === '10-K' ? SECTION_OPTIONS_10K : SECTION_OPTIONS_10Q;

  // Set default section when report type or options change
  if (sectionOptions.length > 0 && (!selectedSection || !sectionOptions.find(opt => opt.key === selectedSection))) {
    setSelectedSection(sectionOptions[0].key);
  }

  // Get filing info from metadata - backend returns { filings: { "10-k": {...}, "10-q": {...} } }
  const filingInfo = filingsData?.filings?.[reportType.toLowerCase()] || 
                     filingsData?.filings?.[reportType] ||
                     null;

  if (isLoading) {
    return <Loading message="Loading SEC filings..." />;
  }

  if (error) {
    // Check if it's a 404 or other error
    const errorMessage = error instanceof Error ? error.message : String(error);
    const is404 = errorMessage.includes('404') || errorMessage.includes('Not Found');
    
    return (
      <Card>
        <div className="text-center py-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Unable to Load SEC Filings</h3>
          <p className="text-gray-600 mb-4">
            {is404 
              ? "The SEC filing endpoint returned a 404 error. Please restart the backend server to apply the latest changes."
              : "Failed to load SEC filings. This may occur if:"}
          </p>
          {!is404 && (
            <ul className="text-sm text-gray-500 text-left max-w-md mx-auto space-y-1 mb-4">
              <li>• The CIK mapping file is not available</li>
              <li>• The SEC API is temporarily unavailable</li>
              <li>• The backend server needs to be restarted</li>
            </ul>
          )}
          <p className="text-sm text-gray-500 mt-4">
            Error: {errorMessage}
          </p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">🏛️ Company Disclosures</h2>
        <p className="text-gray-600 mb-6">
          View key sections from the latest 10-K and 10-Q filings for {ticker}.
        </p>

        {/* Report Type Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Select Report Type
          </label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="10-K"
                checked={reportType === '10-K'}
                onChange={(e) => {
                  setReportType(e.target.value as ReportType);
                  setSelectedSection(''); // Reset section selection
                }}
                className="mr-2"
              />
              <span className="text-sm font-medium">10-K</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="10-Q"
                checked={reportType === '10-Q'}
                onChange={(e) => {
                  setReportType(e.target.value as ReportType);
                  setSelectedSection(''); // Reset section selection
                }}
                className="mr-2"
              />
              <span className="text-sm font-medium">10-Q</span>
            </label>
          </div>
        </div>

        {/* Filing Information */}
        {filingInfo && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-blue-900 mb-1">
                  Latest {reportType} filed on: {filingInfo.filingDate || filingInfo.filing_date || 'N/A'}
                </p>
                {filingInfo.doc_url && (
                  <a
                    href={filingInfo.doc_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-800 underline mt-1 inline-block"
                  >
                    View on SEC.gov →
                  </a>
                )}
                {filingInfo.accessionNumber && (
                  <p className="text-xs text-gray-600 mt-1">
                    Accession Number: {filingInfo.accessionNumber}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
        
        {/* Debug info - remove in production */}
        {process.env.NODE_ENV === 'development' && filingsData && (
          <div className="mb-4 p-2 bg-gray-100 rounded text-xs">
            <p>Debug: filingsData keys: {Object.keys(filingsData.filings || {}).join(', ')}</p>
            <p>Debug: reportType: {reportType}, looking for: {reportType.toLowerCase()}</p>
            <p>Debug: filingInfo: {filingInfo ? JSON.stringify(filingInfo).substring(0, 100) : 'null'}</p>
          </div>
        )}

        {/* Section Selection */}
        {sectionOptions.length > 0 && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Section to Display
            </label>
            <select
              value={selectedSection}
              onChange={(e) => setSelectedSection(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
            >
              {sectionOptions.map((option) => (
                <option key={option.key} value={option.key}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        )}
      </Card>

      {/* Section Content */}
      {sectionsData && selectedSection && (
        <Card>
          <div className="mb-4">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {sectionOptions.find((opt) => opt.key === selectedSection)?.label || 'Section Content'}
            </h3>
            {filingInfo && (
              <p className="text-sm text-gray-500 mb-4">
                From {reportType} filed on {filingInfo.filingDate}
              </p>
            )}
          </div>

          <div className="prose max-w-none">
            {(() => {
              // Map section key to backend section name
              const sectionName = sectionOptions.find(opt => opt.key === selectedSection)?.label || '';
              const sectionContent = sectionsData.sections?.[sectionName] || 
                                     sectionsData.sections?.[selectedSection] ||
                                     Object.values(sectionsData.sections || {})[0];
              
              return sectionContent ? (
                <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
                  <div className="whitespace-pre-wrap text-sm text-gray-700 leading-relaxed max-h-[600px] overflow-y-auto">
                    {sectionContent}
                  </div>
                </div>
              ) : (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-yellow-800">
                  Section content not found or empty. This may occur if the filing structure is different than expected.
                </p>
              </div>
              );
            })()}
          </div>

          {/* Copy to Clipboard Button */}
          {(() => {
            const sectionName = sectionOptions.find(opt => opt.key === selectedSection)?.label || '';
            const sectionContent = sectionsData.sections?.[sectionName] || 
                                   sectionsData.sections?.[selectedSection] ||
                                   Object.values(sectionsData.sections || {})[0];
            return sectionContent && (
            <div className="mt-4">
              <button
                onClick={() => {
                  const sectionName = sectionOptions.find(opt => opt.key === selectedSection)?.label || '';
                  const sectionContent = sectionsData.sections?.[sectionName] || 
                                         sectionsData.sections?.[selectedSection] ||
                                         Object.values(sectionsData.sections || {})[0];
                  if (sectionContent) {
                    navigator.clipboard.writeText(sectionContent);
                    // You could add a toast notification here
                  }
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                📋 Copy Section to Clipboard
              </button>
            </div>
            );
          })()}
        </Card>
      )}

      {/* No Data Message */}
      {!filingInfo && !isLoading && !error && (
        <Card>
          <div className="text-center py-8">
            <p className="text-gray-600 mb-2">
              No {reportType} filings found for {ticker}.
            </p>
            <p className="text-sm text-gray-500 mb-4">
              This may occur if:
            </p>
            <ul className="text-sm text-gray-500 text-left max-w-md mx-auto space-y-1">
              <li>• The company hasn't filed recently</li>
              <li>• The ticker is not recognized by the SEC</li>
              <li>• The CIK mapping file is not available</li>
              <li>• The SEC API is temporarily unavailable</li>
            </ul>
            <p className="text-sm text-gray-500 mt-4">
              Please try again later or contact support if the issue persists.
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}

