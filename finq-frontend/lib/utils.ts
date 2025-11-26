/**
 * Utility functions
 */

/**
 * Format number to human-readable USD (e.g. $3.4B, $120M, $950)
 */
export function humanFormat(num: number | null | undefined): string {
  if (num === null || num === undefined || isNaN(num)) {
    return 'N/A';
  }
  const sign = num < 0 ? '-' : '';
  let absNum = Math.abs(num);
  const units = ['', 'K', 'M', 'B', 'T'];
  
  for (const unit of units) {
    if (absNum < 1000) {
      const formatted = unit ? `${absNum.toFixed(1)}${unit}` : `${absNum.toFixed(0)}`;
      return `${sign}$${formatted}`;
    }
    absNum /= 1000;
  }
  return `${sign}$${absNum.toFixed(1)}P`;
}

/**
 * Format number for axis (returns value and unit)
 */
export function humanFormatForAxis(num: number | null | undefined): { value: number; unit: string } {
  if (num === null || num === undefined || isNaN(num)) {
    return { value: num as any, unit: '' };
  }
  const absNum = Math.abs(num);
  
  if (absNum >= 1_000_000_000) {
    return { value: num / 1_000_000_000, unit: 'B' };
  } else if (absNum >= 1_000_000) {
    return { value: num / 1_000_000, unit: 'M' };
  } else if (absNum >= 1_000) {
    return { value: num / 1_000, unit: 'K' };
  }
  return { value: num, unit: '' };
}

/**
 * Determine the appropriate unit and format for a metric based on its name
 */
export function getMetricUnit(metricName: string): { 
  unit: string; 
  isPercentage: boolean; 
  isRatio: boolean;
  formatFn: (value: number) => string;
} {
  const name = metricName.toLowerCase();
  
  // Percentage metrics
  const percentageKeywords = ['margin', 'ratio', 'rate', 'return', 'yield', 'percent', '%', 'p/e', 'pe ratio', 'ev/ebitda', 'price to', 'p/b', 'pb ratio'];
  const isPercentage = percentageKeywords.some(keyword => name.includes(keyword));
  
  // Ratio metrics (but not percentages)
  const ratioKeywords = ['ratio', 'multiple', 'per share', 'eps', 'book value'];
  const isRatio = ratioKeywords.some(keyword => name.includes(keyword)) && !isPercentage;
  
  if (isPercentage) {
    return {
      unit: '%',
      isPercentage: true,
      isRatio: false,
      formatFn: (value: number) => `${(value * 100).toFixed(2)}%`
    };
  }
  
  // Currency metrics (revenue, income, assets, etc.)
  const currencyKeywords = ['revenue', 'income', 'profit', 'loss', 'assets', 'liabilities', 'equity', 'cash', 'flow', 'debt', 'capital', 'expense', 'cost', 'sales', 'earnings'];
  const isCurrency = currencyKeywords.some(keyword => name.includes(keyword));
  
  if (isCurrency || !isRatio) {
    return {
      unit: '$',
      isPercentage: false,
      isRatio: false,
      formatFn: (value: number) => humanFormat(value)
    };
  }
  
  // Default: just numbers
  return {
    unit: '',
    isPercentage: false,
    isRatio: true,
    formatFn: (value: number) => formatNumber(value)
  };
}

/**
 * Get ticker logo URL from Parqet
 */
export function getTickerLogoUrl(ticker: string): string {
  return `https://assets.parqet.com/logos/symbol/${ticker}?format=png`;
}

/**
 * Format date for display
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

/**
 * Format date for API (YYYY-MM-DD)
 */
export function formatDateForAPI(date: Date): string {
  return date.toISOString().split('T')[0];
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Format percentage
 */
export function formatPercent(num: number | null | undefined, decimals: number = 2): string {
  if (num === null || num === undefined || isNaN(num)) {
    return 'N/A';
  }
  return `${num.toFixed(decimals)}%`;
}

/**
 * Format number with commas
 */
export function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined || isNaN(num)) {
    return 'N/A';
  }
  return num.toLocaleString('en-US');
}

/**
 * Get relative time (e.g., "2 hours ago")
 */
export function getRelativeTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - d.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return 'just now';
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  } else if (diffInSeconds < 604800) {
    const days = Math.floor(diffInSeconds / 86400);
    return `${days} day${days > 1 ? 's' : ''} ago`;
  } else {
    return formatDate(d);
  }
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.slice(0, maxLength - 3) + '...';
}

/**
 * Get color based on value (positive/negative)
 */
export function getValueColor(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return 'text-gray-500';
  }
  if (value > 0) {
    return 'text-green-600';
  } else if (value < 0) {
    return 'text-red-600';
  }
  return 'text-gray-500';
}

