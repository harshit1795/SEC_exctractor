/**
 * Tab descriptions for dashboard tabs
 * Provides summaries of what each tab does and what users can accomplish
 */

export const TAB_DESCRIPTIONS: Record<string, string> = {
  'trend': 'Analyze financial metrics over time with interactive charts. Select multiple metrics from Income Statement, Balance Sheet, or Cash Flow to visualize trends. Switch between line and bar charts, and view data across different time periods. Perfect for identifying patterns, growth trajectories, and comparing metrics side-by-side.',
  
  'snapshot': 'View current period financial data with period-over-period comparisons. See the latest values for selected metrics and calculate quarter-over-quarter (QoQ) or year-over-year (YoY) changes. Color-coded indicators show positive or negative changes, making it easy to spot improvements or concerns in financial performance.',
  
  'earnings': 'Track earnings performance and expectations. View historical EPS trends comparing reported vs. estimated earnings, see surprise percentages, and get details on the last quarter\'s results and upcoming earnings dates. Essential for understanding how the company is performing relative to analyst expectations.',
  
  'price': 'Interactive stock price charts with technical analysis. View price movements as line or candlestick charts, apply technical indicators (RSI, MACD, Bollinger Bands), filter by date range, and see key performance indicators. Analyze daily, weekly, or monthly aggregations to understand price trends and volatility.',
  
  'disclosures': 'Access and read SEC filings directly. Browse 10-K and 10-Q filings, navigate through key sections like Business Overview, Risk Factors, and Management Discussion & Analysis. Copy sections to clipboard for further analysis. Stay informed about company disclosures and regulatory filings.',
  
  'macro': 'Explore macroeconomic indicators from the Federal Reserve Economic Data (FRED). Select from GDP, unemployment, inflation, interest rates, and more. Visualize economic trends with customizable date ranges, aggregation options, and chart types. Understand how broader economic conditions may impact your investments.',
  
  'finq360': 'Comprehensive 360-degree analysis combining multiple data sources. Integrate company fundamentals, earnings data, and macroeconomic indicators in a single view. Create multi-dimensional visualizations to see how company performance relates to economic conditions. Perfect for holistic financial analysis.',
  
  'bot': 'AI-powered financial assistant powered by Google Gemini. Ask questions about financial data, company analysis, market insights, or get explanations of financial metrics. Select data sources (fundamentals, SEC filings, economic data) to provide context. Maintain chat history across sessions and create new conversations for different analysis topics.',
};

/**
 * Get description for a tab
 */
export function getTabDescription(tabId: string): string {
  return TAB_DESCRIPTIONS[tabId] || 'Explore financial data and analysis tools in this tab.';
}

