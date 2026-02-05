/// Comprehensive Financial Metric Descriptions
/// CPA-style explanations for Income Statement, Balance Sheet, and Cash Flow metrics
/// Based on GAAP (Generally Accepted Accounting Principles)

class MetricDescriptions {
  static const Map<String, String> descriptions = {
    // ==================== INCOME STATEMENT METRICS ====================
    
    // Revenue Metrics
    'Total Revenue': 'From an accounting perspective, this is the "top line" on the Income Statement representing all sales recognized under accrual accounting principles (GAAP). Revenue is recorded when earned, not when cash is received, following the revenue recognition principle. A CPA would explain that this includes all operating revenue from core business activities. Consistent growth typically indicates strong market demand and business expansion.',
    'Revenue': 'The total sales recognized under accrual accounting principles. Revenue is recorded when the company has fulfilled its performance obligations, regardless of when payment is received. This follows GAAP revenue recognition standards (ASC 606). Accountants use this as the foundation for all profitability calculations.',
    'Net Revenue': 'Total revenue after accounting for returns, allowances, and discounts. This is the "net" sales figure that appears on the Income Statement. A CPA would note that net revenue is more accurate than gross revenue for analysis, as it reflects actual sales after customer returns and price adjustments.',
    'Sales': 'Revenue from selling products or services. In accounting terms, this represents the primary revenue stream and is recorded when ownership transfers to the customer, following the revenue recognition principle.',
    
    // Cost of Goods Sold / Cost of Revenue
    'Cost of Goods Sold': 'Also called COGS or Cost of Revenue, this represents the direct costs of producing goods or services sold. Under accounting principles, this includes materials, direct labor, and manufacturing overhead. A CPA would explain that COGS is matched to revenue in the same period (matching principle) and appears on the Income Statement. Lower COGS relative to revenue indicates better production efficiency.',
    'Cost of Revenue': 'The direct costs associated with generating revenue, including production costs, service delivery costs, and cost of sales. This follows the matching principle - costs are recognized in the same period as related revenue. Accountants use this to calculate gross profit.',
    'COGS': 'Cost of Goods Sold - the direct expenses of producing products sold. This includes raw materials, direct labor, and manufacturing overhead allocated to products. A CPA would note that COGS appears on the Income Statement and is subtracted from revenue to calculate gross profit.',
    
    // Gross Profit
    'Gross Profit': 'Revenue minus Cost of Goods Sold. This is the first level of profit on the Income Statement and shows profitability before operating expenses. From an accounting perspective, gross profit must be sufficient to cover operating expenses, interest, and taxes. A CPA would explain that negative gross profit means the company is selling below production cost, which is unsustainable.',
    'Gross Income': 'Same as Gross Profit - the profit remaining after direct production costs. This accounting metric indicates pricing power and production efficiency before considering operating expenses.',
    
    // Operating Expenses
    'Operating Expenses': "Also called OPEX, these are costs incurred in running day-to-day business operations (excluding COGS). Under GAAP, these include salaries, rent, utilities, marketing, R&D, and depreciation. A CPA would note that operating expenses are period costs, meaning they're expensed in the period incurred, not matched to specific revenue.",
    'Selling, General and Administrative': 'SG&A expenses include costs for selling products (sales commissions, advertising) and general administration (salaries, office rent, utilities). These are operating expenses that appear on the Income Statement. Accountants track SG&A as a percentage of revenue to assess cost control efficiency.',
    'Research and Development': 'R&D expenses represent costs for developing new products, services, or processes. Under accounting rules, R&D is typically expensed immediately (not capitalized) unless it meets specific criteria. A CPA would note that high R&D spending may indicate innovation focus but reduces current profitability.',
    'Depreciation': "The systematic allocation of the cost of tangible assets (like equipment, buildings) over their useful lives. This is a non-cash expense that reduces reported income but doesn't involve actual cash outflow. Accountants use depreciation to match asset costs with the periods that benefit from asset use (matching principle).",
    'Amortization': "Similar to depreciation but for intangible assets (patents, trademarks, goodwill). This non-cash expense allocates the cost of intangible assets over their useful lives. A CPA would explain that amortization reduces reported earnings but doesn't affect cash flow.",
    'Depreciation and Amortization': "The combined non-cash expenses for both tangible and intangible assets. These accounting adjustments reduce reported income but don't represent actual cash outflows. Analysts often add these back to net income to assess cash-generating ability.",
    
    // Operating Income
    'Operating Income': 'Also called EBIT (Earnings Before Interest and Taxes), this is profit from core business operations. Calculated as Gross Profit minus Operating Expenses. A CPA would explain that this isolates operating performance from financing decisions (interest) and tax strategies, making it useful for comparing companies with different capital structures.',
    'EBIT': 'Earnings Before Interest and Taxes - operating income that excludes financing and tax effects. This accounting metric shows pure business profitability. CPAs use EBIT to compare companies with different debt levels and tax situations, as it focuses solely on operational efficiency.',
    'Operating Profit': 'Same as Operating Income - the profit from core business activities before interest and taxes. This appears on the Income Statement and indicates how profitable the business model itself is, independent of financing structure.',
    
    // EBITDA
    'EBITDA': "Earnings Before Interest, Taxes, Depreciation, and Amortization. This non-GAAP measure approximates operating cash flow by removing non-cash expenses and financing/tax effects. A CPA would note that EBITDA helps assess cash-generating ability, but it can be misleading if capital expenditures (which aren't included) are high, as it doesn't account for necessary asset replacements.",
    
    // Interest and Other Income/Expenses
    'Interest Expense': 'The cost of borrowing money, including interest on loans, bonds, and credit lines. This appears on the Income Statement and represents the financing cost of debt. A CPA would explain that high interest expense relative to operating income indicates heavy debt burden and financial risk.',
    'Interest Income': 'Revenue earned from investments, cash deposits, or loans made to others. This is non-operating income that appears on the Income Statement. Accountants separate this from operating income to distinguish core business performance from investment returns.',
    'Other Income': "Revenue from non-core business activities, such as gains on asset sales, investment income, or foreign exchange gains. A CPA would note that this is separated from operating income because it's not part of regular business operations and may not be sustainable.",
    'Other Expenses': "Costs from non-core activities, such as losses on asset sales, restructuring charges, or impairment losses. These are separated from operating expenses because they're typically one-time or non-recurring items.",
    
    // Income Before Tax
    'Income Before Tax': 'Also called Pre-Tax Income or Earnings Before Tax (EBT), this is profit before income tax expense. Calculated as Operating Income plus Other Income minus Other Expenses and Interest Expense. A CPA would use this to assess profitability before tax effects, which can vary significantly based on tax strategies and jurisdictions.',
    'Pre-Tax Income': 'Profit before income taxes are deducted. This accounting metric shows earnings before tax effects and is useful for comparing companies in different tax jurisdictions or with different tax strategies.',
    'Earnings Before Tax': 'Same as Income Before Tax - the profit figure before income tax expense is applied. This appears on the Income Statement and is the basis for calculating income tax expense.',
    
    // Income Tax
    'Income Tax Expense': "The tax obligation based on taxable income, calculated using applicable tax rates. Under accounting rules, this includes current tax expense (taxes payable) and deferred tax expense (future tax obligations). A CPA would explain that the effective tax rate (tax expense / pre-tax income) shows the company's tax burden.",
    'Provision for Income Taxes': 'The estimated income tax expense for the period, including both current and deferred taxes. This accounting provision follows the matching principle - taxes are recognized in the same period as the related income.',
    
    // Net Income
    'Net Income': 'The "bottom line" - final profit after ALL expenses, taxes, interest, and accounting adjustments. This represents earnings available to shareholders and is the basis for calculating EPS. A CPA would emphasize that positive net income indicates profitability, while negative (net loss) indicates the company is losing money. This is crucial for dividend capacity and shareholder returns.',
    'Net Earnings': 'Same as Net Income - the final profit figure on the Income Statement. This is the most comprehensive measure of profitability and is used to calculate return on equity and earnings per share.',
    'Net Profit': 'The final profit after all deductions. This accounting metric shows what remains for shareholders after all obligations are met.',
    
    // Earnings Per Share
    'EPS': 'Earnings Per Share - Net Income divided by weighted average shares outstanding. This is a key accounting metric required by GAAP to be reported on the Income Statement. A CPA would explain that EPS shows how much profit each share represents, making it easier to compare companies of different sizes. Higher EPS generally indicates better profitability per share.',
    'Diluted EPS': 'EPS calculated assuming all potentially dilutive securities (stock options, convertible bonds, warrants) are converted to shares. This is the more conservative accounting measure required by GAAP. A CPA would note that diluted EPS shows the "worst case" earnings per share if all conversion rights were exercised, providing investors with a more realistic picture.',
    'Basic EPS': 'Earnings Per Share using only currently outstanding shares, without assuming conversion of dilutive securities. This is simpler than diluted EPS but may overstate earnings per share if the company has many stock options or convertible securities.',
    
    // ==================== BALANCE SHEET METRICS ====================
    
    // Current Assets
    'Current Assets': 'Assets expected to be converted to cash or used within one year, per accounting definitions. This includes cash, accounts receivable, inventory, and short-term investments. Accountants classify these separately to assess short-term liquidity. A CPA would note that current assets are crucial for meeting short-term obligations and are used in liquidity ratios like the current ratio.',
    'Cash and Cash Equivalents': 'The most liquid assets, including physical cash, bank deposits, and short-term investments that can be converted to cash within 90 days (like Treasury bills). This appears first on the Balance Sheet. A CPA would explain that adequate cash is essential for operations, but excessive cash may indicate inefficient capital allocation.',
    'Cash': 'Physical currency and demand deposits. This is the most liquid asset and appears on the Balance Sheet. Accountants track cash levels to ensure the company can meet immediate obligations and take advantage of opportunities.',
    'Accounts Receivable': "Money owed to the company by customers who purchased on credit. Under accrual accounting, this is recorded when revenue is earned, even if cash hasn't been received. A CPA would note that high receivables relative to revenue may indicate collection problems, while low receivables suggest efficient collection or cash sales.",
    'Inventory': 'Goods held for sale in the ordinary course of business. Under accounting rules, inventory is valued at the lower of cost or market value. A CPA would explain that inventory represents tied-up capital - too much inventory indicates poor sales or overproduction, while too little may mean lost sales opportunities.',
    'Prepaid Expenses': 'Payments made for future benefits, such as insurance premiums or rent paid in advance. These are current assets because they provide value within one year. Accountants record these as assets and expense them over time (matching principle).',
    'Short-Term Investments': 'Investments that can be converted to cash within one year, such as marketable securities or certificates of deposit. These are classified as current assets and are typically valued at fair market value under accounting rules.',
    
    // Non-Current Assets
    'Total Assets': 'Everything the company owns that has economic value, following the accounting equation: Assets = Liabilities + Equity. Assets are recorded at historical cost (or fair value for certain items) per GAAP. A CPA would explain that assets are resources used to generate revenue. Total assets include both current assets (convertible within a year) and non-current assets (long-term).',
    'Property, Plant and Equipment': 'Also called PP&E or Fixed Assets, these are long-term tangible assets used in operations, such as buildings, machinery, and vehicles. Under accounting rules, these are recorded at cost and depreciated over their useful lives. A CPA would note that PP&E represents significant capital investment and is essential for operations.',
    'PP&E': 'Property, Plant and Equipment - long-term tangible assets used in business operations. These are depreciated over time, with the cost allocated to expense periods that benefit from asset use. Accountants track PP&E to assess capital intensity and asset utilization.',
    'Fixed Assets': "Long-term tangible assets that aren't easily converted to cash, such as buildings, equipment, and land. These are depreciated (except land) and represent the company's productive capacity. A CPA would explain that high fixed assets relative to revenue may indicate capital-intensive operations.",
    'Intangible Assets': 'Non-physical assets with value, such as patents, trademarks, copyrights, and goodwill. Under accounting rules, purchased intangibles are recorded at cost and amortized over their useful lives. A CPA would note that intangible assets can be significant for technology and brand-focused companies.',
    'Goodwill': 'The excess of purchase price over the fair value of net assets acquired in a business combination. This intangible asset represents brand value, customer relationships, and other unidentifiable assets. Under GAAP, goodwill is not amortized but is tested annually for impairment. A CPA would explain that goodwill only appears after acquisitions.',
    'Long-Term Investments': 'Investments in other companies, bonds, or assets held for more than one year. These are classified as non-current assets and may be valued at cost, equity method, or fair value depending on the investment type and accounting standards.',
    
    // Current Liabilities
    'Current Liabilities': 'Debts and obligations due within one year, including accounts payable, short-term loans, accrued expenses, and current portion of long-term debt. Accountants classify these separately to assess short-term liquidity risk. A CPA would note that current liabilities must be covered by current assets - if not, the company may face cash flow problems.',
    'Accounts Payable': 'Money the company owes to suppliers for goods or services purchased on credit. This represents short-term trade credit and appears on the Balance Sheet. A CPA would explain that accounts payable is essentially free short-term financing, but excessive payables may indicate cash flow problems or strained supplier relationships.',
    'Short-Term Debt': 'Loans and borrowings that must be repaid within one year, including bank loans, lines of credit, and the current portion of long-term debt. This is a current liability that requires cash payment. Accountants track this to assess short-term financing needs and liquidity.',
    'Accrued Expenses': 'Expenses that have been incurred but not yet paid, such as wages payable, interest payable, or taxes payable. Under the accrual basis of accounting, these are recorded when incurred, not when paid. A CPA would note that accrued expenses represent obligations that will require cash payment.',
    'Current Portion of Long-Term Debt': 'The portion of long-term debt that must be repaid within the next year. This is reclassified from long-term to current liabilities as the due date approaches. Accountants do this to accurately reflect short-term obligations.',
    
    // Long-Term Liabilities
    'Total Liabilities': "All obligations the company owes to creditors, suppliers, and other parties. In accounting terms, liabilities represent claims against the company's assets and are recorded when incurred, following the matching principle. A CPA would explain that liabilities must be paid using assets, so high liabilities relative to assets can indicate financial risk and reduced financial flexibility.",
    'Long-Term Debt': "Borrowings that don't need to be repaid within one year, such as bonds, mortgages, and long-term loans. This is a non-current liability that represents long-term financing. A CPA would note that long-term debt provides leverage but increases financial risk and requires interest payments that reduce profitability.",
    'Bonds Payable': 'Long-term debt securities issued to investors, representing money borrowed that must be repaid with interest. These are recorded at face value (or present value if issued at a discount/premium). Accountants track bonds to assess long-term financing and debt service requirements.',
    'Deferred Tax Liabilities': 'Future tax obligations that will be paid in later periods, arising from temporary differences between accounting income and taxable income. Under GAAP, these are recognized when income is reported for accounting but taxed later. A CPA would explain that deferred taxes represent future cash outflows.',
    'Total Liabilities Net Minority Interest': "All company debts excluding minority ownership interests in subsidiaries. This accounting adjustment removes liabilities related to subsidiaries that aren't fully owned. A CPA would use this to assess the parent company's true debt burden, excluding obligations from partially-owned entities.",
    
    // Equity
    'Shareholder Equity': "Also called 'Book Value' or 'Net Worth,' this is Assets minus Liabilities. From an accounting perspective, this represents the owners' residual claim on company assets after all debts are paid. A CPA would explain that positive equity means assets exceed liabilities - negative equity (deficit) indicates the company owes more than it owns, which is a serious red flag.",
    'Total Stockholder Equity': "The accounting value of shareholders' ownership interest, including paid-in capital (money invested), retained earnings (profits kept in the business), and treasury stock (repurchased shares). A CPA would note that this is the residual interest - what remains after liabilities are subtracted from assets. It's the foundation for calculating return on equity.",
    'Retained Earnings': 'Cumulative profits kept in the business rather than paid as dividends. This is calculated as beginning retained earnings plus net income minus dividends. A CPA would explain that growing retained earnings indicate the company is reinvesting profits for growth, while declining retained earnings may indicate losses or high dividend payouts.',
    'Paid-In Capital': 'Also called Contributed Capital, this is money invested by shareholders in exchange for stock. This includes both the par value of stock and additional paid-in capital (amounts above par value). Accountants track this to show how much shareholders have invested versus what the company has earned.',
    'Common Stock': "The par or stated value of common shares issued. This is a component of shareholders' equity representing the legal capital of the corporation. A CPA would note that common stock gives shareholders voting rights and residual claim on assets after all obligations are met.",
    'Treasury Stock': "Company stock that has been repurchased from shareholders. This reduces shareholders' equity and is recorded at cost. A CPA would explain that treasury stock represents shares available for reissuance or retirement, and reduces the number of outstanding shares (which can increase EPS).",
    
    // Working Capital
    'Working Capital': 'Current Assets minus Current Liabilities. This accounting metric measures short-term financial health and liquidity. A CPA would explain that positive working capital means the company can pay its short-term bills - negative working capital indicates potential cash flow problems. Accountants monitor this closely as it affects day-to-day operations and short-term solvency.',
    'Net Working Capital': "Same as Working Capital - the difference between current assets and current liabilities. This shows the company's ability to fund operations and meet short-term obligations without additional financing.",
    
    // Debt Metrics
    'Total Debt': 'All borrowed money the company must repay, including both short-term and long-term debt. From an accounting perspective, debt is a liability that must be serviced with interest payments. A CPA would note that debt provides leverage (amplifies returns) but increases financial risk - too much debt relative to equity can make a company vulnerable to economic downturns and interest rate changes.',
    'Net Debt': "Total Debt minus Cash and Cash Equivalents. This accounting adjustment shows the company's true debt burden after accounting for available cash. A CPA would explain that net debt is more meaningful than gross debt because cash can be used to pay down debt. Negative net debt means the company has more cash than debt, which is very strong financially and indicates excellent liquidity.",
    
    // ==================== CASH FLOW STATEMENT METRICS ====================
    
    // Operating Activities
    'Operating Cash Flow': 'Cash generated from core business operations, calculated using the indirect method (starting with net income and adjusting for non-cash items like depreciation) or direct method. This is the most important line on the Cash Flow Statement. A CPA would emphasize that positive operating cash flow is essential - it shows the business can generate cash from operations, not just from borrowing or selling assets. This is often considered more reliable than net income for assessing financial health.',
    'Cash from Operations': 'Same as Operating Cash Flow - cash generated from day-to-day business activities. This includes cash received from customers minus cash paid to suppliers, employees, and for operating expenses. Accountants use this to assess whether the business model generates cash.',
    'Net Cash from Operating Activities': 'The net cash inflow or outflow from operating activities on the Statement of Cash Flows. This shows if operations are generating or consuming cash. A CPA would note that consistently negative operating cash flow is a major red flag, even if the company reports profits.',
    
    // Investing Activities
    'Cash from Investing Activities': 'Cash flows related to buying or selling long-term assets, such as property, equipment, or investments. Negative cash flow here typically indicates capital expenditures (investments in growth), while positive indicates asset sales. A CPA would explain that capital expenditures are necessary for maintaining and growing the business.',
    'Capital Expenditures': 'Also called CAPEX, these are cash outflows for purchasing or improving long-term assets like property, plant, and equipment. This appears as a negative figure in investing activities. A CPA would note that adequate CAPEX is necessary to maintain operations and support growth, but excessive CAPEX relative to cash flow can strain finances.',
    'CAPEX': 'Capital Expenditures - money spent on long-term assets. Under accounting rules, these are capitalized (recorded as assets) rather than expensed immediately. A CPA would explain that CAPEX is an investment in future operations and is crucial for maintaining competitive position.',
    
    // Financing Activities
    'Cash from Financing Activities': 'Cash flows from borrowing, repaying debt, issuing stock, repurchasing stock, or paying dividends. Positive cash flow indicates raising capital, while negative indicates returning capital to investors or creditors. A CPA would note that this shows how the company finances its operations and growth.',
    'Dividends Paid': 'Cash distributions to shareholders, appearing as a negative figure in financing activities. This represents return of capital to owners. A CPA would explain that dividends reduce retained earnings and cash, but can signal financial strength and shareholder-friendly management.',
    'Stock Repurchases': "Cash used to buy back company stock from shareholders, appearing as a negative in financing activities. This reduces shareholders' equity and outstanding shares. A CPA would note that repurchases can increase EPS by reducing share count and signal management believes the stock is undervalued.",
    
    // Free Cash Flow
    'Free Cash Flow': "Operating Cash Flow minus Capital Expenditures. This accounting metric shows cash available after maintaining the business. A CPA would explain that free cash flow is what's left for dividends, debt repayment, acquisitions, or growth investments. It's a key indicator of financial flexibility, value creation, and the company's ability to return capital to shareholders without jeopardizing operations.",
    'FCF': "Free Cash Flow - the cash available after capital expenditures. This is a critical metric for assessing financial health and valuation. Accountants and analysts use FCF to evaluate a company's ability to fund growth, pay dividends, and reduce debt without external financing.",
    
    // Net Cash Flow
    'Net Cash Flow': 'The sum of cash flows from operating, investing, and financing activities. This shows the net change in cash and cash equivalents during the period. A CPA would note that this reconciles the beginning and ending cash balances on the Balance Sheet.',
    'Change in Cash': 'The net increase or decrease in cash and cash equivalents during the period, calculated from all cash flow activities. This accounting metric explains how the cash balance changed from the beginning to the end of the period.',
    
    // ==================== FINANCIAL RATIOS ====================
    
    // Profitability Ratios
    'Gross Margin': 'Gross Profit divided by Revenue, expressed as a percentage. This accounting ratio shows how much profit is made on each dollar of sales before operating expenses. CPAs use this to compare pricing strategies and production efficiency across companies. Higher margins typically indicate better pricing power, lower production costs, or superior product differentiation.',
    'Operating Margin': "Operating Income divided by Revenue, shown as a percentage. This accounting ratio measures operational efficiency - how much profit is generated from each dollar of sales after operating expenses. A CPA would explain that this shows management's ability to control costs and run the business efficiently, excluding financing and tax considerations. It's useful for comparing companies within the same industry.",
    'Net Margin': "Net Income divided by Revenue, shown as a percentage. This is the final profitability ratio on the Income Statement. Accountants use this to assess overall profitability after ALL expenses. A CPA would note that net margin shows what percentage of sales becomes profit for shareholders - it's the most comprehensive profitability measure and indicates the company's ability to convert sales into earnings.",
    'Profit Margin': 'Same as Net Margin - the percentage of revenue that becomes profit. This is a key indicator of overall business profitability and efficiency.',
    
    // Return Ratios
    'ROE': "Return on Equity - Net Income divided by Average Shareholder Equity, expressed as a percentage. This accounting ratio measures how efficiently the company uses shareholders' invested capital to generate profits. A CPA would explain that higher ROE indicates better use of equity capital. It's a key metric for assessing management effectiveness, comparing companies within industries, and evaluating investment returns. However, very high ROE can also indicate excessive leverage.",
    'ROA': "Return on Assets - Net Income divided by Average Total Assets, expressed as a percentage. This accounting efficiency ratio shows how well the company uses its assets to generate profits. A CPA would note that ROA helps assess asset utilization - companies that generate more profit per dollar of assets are more efficient. It's useful for comparing companies with different capital structures, as it's not affected by financing decisions.",
    'Return on Investment': 'ROI - a measure of the efficiency of an investment. Calculated as (Gain from Investment - Cost of Investment) / Cost of Investment. A CPA would use this to assess the profitability of capital investments and compare different investment opportunities.',
    'Return on Capital Employed': 'ROCE - Operating Income divided by Capital Employed (Total Assets minus Current Liabilities). This accounting ratio measures how efficiently the company uses its capital to generate operating profits. A CPA would explain that this is useful for comparing companies with different financing structures.',
    
    // Liquidity Ratios
    'Current Ratio': 'Current Assets divided by Current Liabilities. This accounting liquidity ratio measures short-term financial health and ability to pay short-term bills. A CPA would note that a ratio above 1.0 means current assets exceed current liabilities, indicating the company can pay short-term obligations. However, too high a ratio (above 2-3) might indicate inefficient use of assets or poor working capital management. Industry standards vary.',
    'Quick Ratio': 'Also called Acid-Test Ratio - (Current Assets - Inventory) divided by Current Liabilities. This is a more conservative liquidity measure than the current ratio because it excludes inventory, which may not be easily converted to cash. A CPA would explain that a quick ratio above 1.0 indicates strong short-term liquidity without relying on inventory sales.',
    'Cash Ratio': "Cash and Cash Equivalents divided by Current Liabilities. This is the most conservative liquidity ratio, showing the company's ability to pay short-term obligations using only cash. A CPA would note that this ratio shows immediate liquidity but doesn't account for other current assets that can be converted to cash.",
    
    // Leverage Ratios
    'Debt To Equity Ratio': 'Total Debt divided by Shareholder Equity. This accounting ratio measures financial leverage and risk. A CPA would explain that a ratio above 1.0 means the company has more debt than equity, which increases financial risk but can also amplify returns (leverage). Industry standards vary significantly - utilities often have higher ratios (2-3) than technology companies (0.5-1.0). Too much debt can make a company vulnerable during economic downturns and increase bankruptcy risk.',
    'Debt Ratio': 'Total Debt divided by Total Assets, expressed as a percentage. This accounting ratio shows what percentage of assets is financed by debt. A CPA would note that a higher ratio indicates greater reliance on debt financing and higher financial risk.',
    'Equity Ratio': 'Shareholder Equity divided by Total Assets, expressed as a percentage. This shows what percentage of assets is financed by equity. A CPA would explain that a higher equity ratio indicates a more conservative capital structure with less financial risk.',
    'Times Interest Earned': "Also called Interest Coverage Ratio - Operating Income divided by Interest Expense. This accounting ratio measures the company's ability to pay interest on debt. A CPA would note that a ratio above 2-3 typically indicates the company can comfortably service its debt, while below 1.0 means operating income doesn't cover interest payments, which is a serious concern.",
    
    // Efficiency Ratios
    'Asset Turnover': 'Revenue divided by Average Total Assets. This accounting ratio measures how efficiently the company uses assets to generate sales. A CPA would explain that higher turnover indicates better asset utilization. This is useful for comparing companies in asset-intensive industries.',
    'Inventory Turnover': 'Cost of Goods Sold divided by Average Inventory. This accounting ratio shows how many times inventory is sold and replaced during a period. A CPA would note that higher turnover indicates efficient inventory management and strong sales, while low turnover may indicate overstocking or slow-moving inventory.',
    'Receivables Turnover': 'Revenue divided by Average Accounts Receivable. This accounting ratio measures how quickly the company collects payments from customers. A CPA would explain that higher turnover indicates efficient collection, while low turnover may indicate collection problems or lenient credit terms.',
    'Days Sales Outstanding': 'DSO - Average Accounts Receivable divided by (Revenue / 365). This accounting metric shows the average number of days it takes to collect payment from customers. A CPA would note that lower DSO is better, as it means faster cash collection. Industry standards vary based on payment terms.',
    
    // Valuation Ratios
    'PE Ratio': 'Price-to-Earnings Ratio - Stock price divided by earnings per share. This valuation metric compares market price to accounting earnings. A CPA would explain that a lower P/E ratio may indicate better value, but it varies by industry and growth expectations. It shows how much investors are willing to pay for each dollar of earnings. High P/E ratios may indicate growth expectations, while low P/E ratios may indicate value or concerns.',
    'P/E Ratio': 'Same as PE Ratio - a valuation metric comparing stock price to earnings per share. This helps assess whether a stock is overvalued or undervalued relative to earnings.',
    'Price to Book Ratio': 'Stock price divided by book value per share. This valuation ratio compares market value to accounting (book) value. A CPA would note that a ratio below 1.0 means the stock trades below book value, which may indicate undervaluation, though it could also reflect poor asset quality or future concerns.',
    'P/B Ratio': 'Price-to-Book Ratio - compares market price to book value per share. This helps assess whether the stock is trading above or below its accounting value.',
    'EV/EBITDA': 'Enterprise Value to EBITDA - a valuation ratio used by accountants and analysts. Enterprise Value includes both equity and debt, making it useful for comparing companies with different capital structures. A CPA would explain that this ratio shows how many years of EBITDA it would take to pay for the entire company - lower ratios may indicate better value, but must be considered in context of growth and industry norms.',
    'Market Cap': "Market Capitalization - Current stock price multiplied by total shares outstanding. This represents the total market value of the company's equity. A CPA would note that market cap reflects investor sentiment and future expectations, while book value (from financial statements) reflects historical accounting values. The difference indicates market premium or discount to accounting value.",
    
    // Per Share Metrics
    'Book Value Per Share': "Shareholder Equity divided by number of shares outstanding. This accounting metric shows the theoretical value of each share based on financial statements. A CPA would note that when market price is below book value per share, the stock may be undervalued, though this doesn't account for intangible assets or future growth potential that aren't fully reflected in accounting values.",
    'Tangible Book Value Per Share': 'Book value per share excluding intangible assets and goodwill. This shows the per-share value of tangible assets only. A CPA would use this for companies with significant intangible assets to assess the value of physical assets.',
    
    // Other Common Metrics
    'Book Value': "The accounting value of the company from the Balance Sheet (Assets minus Liabilities). This represents the historical cost basis, not market value. A CPA would explain that book value is what shareholders would theoretically receive if the company were liquidated at accounting values. It's the foundation for calculating book value per share and comparing to market value.",
    'Tangible Book Value': 'Book value excluding intangible assets and goodwill. This shows the value of physical, tangible assets only. A CPA would use this to assess the value of hard assets, especially for companies with significant goodwill or intangible assets.',
    'Enterprise Value': 'Market capitalization plus total debt minus cash. This valuation metric represents the total value of the company, including both equity and debt. A CPA would explain that EV is useful for comparing companies with different capital structures and is often used in acquisition analysis.',
  };

  /// Get a description for a metric, with fallback options
  /// Includes accounting context and CPA-style explanations
  static String getDescription(String metricName) {
    // Try exact match first
    if (descriptions.containsKey(metricName)) {
      return descriptions[metricName]!;
    }
    
    // Try case-insensitive match
    final lowerName = metricName.toLowerCase();
    for (final entry in descriptions.entries) {
      if (entry.key.toLowerCase() == lowerName) {
        return entry.value;
      }
    }
    
    // Try partial matches for common patterns with accounting context
    if (lowerName.contains('revenue') || lowerName.contains('sales')) {
      return 'From an accounting perspective, revenue represents all sales recognized under accrual accounting principles (GAAP). Revenue is recorded when earned, not necessarily when cash is received, following the revenue recognition principle (ASC 606). This is the "top line" of the Income Statement and shows the company\'s ability to generate sales from its business operations. A CPA would note that consistent revenue growth typically indicates strong market demand and business expansion.';
    }
    if (lowerName.contains('income') || lowerName.contains('profit') || lowerName.contains('earnings')) {
      return 'In accounting terms, this represents profit after expenses are deducted from revenue. The Income Statement shows different levels of profit: Gross Profit (after cost of goods), Operating Income (after operating expenses), and Net Income (after all expenses, interest, and taxes). A CPA would explain that positive income indicates profitability, while negative indicates losses. Income is calculated using accrual accounting, meaning it\'s recognized when earned, not when cash is received.';
    }
    if (lowerName.contains('margin')) {
      return 'An accounting ratio showing profitability as a percentage of revenue. Margins are calculated at different levels: Gross Margin (gross profit/revenue), Operating Margin (operating income/revenue), and Net Margin (net income/revenue). Higher margins indicate better pricing power, cost control, or operational efficiency. CPAs use margins to compare companies, assess profitability trends, and evaluate management effectiveness in controlling costs relative to revenue generation.';
    }
    if (lowerName.contains('ratio')) {
      return 'A financial ratio compares two accounting values to assess performance, efficiency, or financial health. Common ratios include profitability ratios (margins, ROE, ROA), liquidity ratios (current ratio, quick ratio), and leverage ratios (debt-to-equity). Accountants use ratios to normalize for company size and make meaningful comparisons across companies and time periods. Ratios help identify trends, strengths, and weaknesses in financial performance.';
    }
    if (lowerName.contains('assets')) {
      return 'In accounting, assets are resources owned by the company that have economic value and are expected to provide future benefits. Assets are recorded on the Balance Sheet at historical cost (or fair value for certain items) per GAAP. They include current assets (cash, inventory, receivables - convertible within a year) and non-current assets (property, equipment, investments - long-term). Assets are used to generate revenue and are the foundation of the accounting equation: Assets = Liabilities + Equity.';
    }
    if (lowerName.contains('liabilit') || lowerName.contains('debt') || lowerName.contains('payable')) {
      return 'From an accounting perspective, liabilities are obligations the company owes to creditors, suppliers, or other parties. These are recorded when incurred, following the matching principle. Liabilities represent claims against the company\'s assets and must be paid using cash or other assets. They include current liabilities (due within a year) and long-term liabilities (due after a year). A CPA would explain that high liabilities relative to assets can indicate financial risk and reduced financial flexibility. Debt provides leverage but increases financial risk.';
    }
    if (lowerName.contains('equity') || lowerName.contains('stockholder') || lowerName.contains('book value')) {
      return 'In accounting terms, equity (or Shareholder Equity) represents the owners\' residual interest in the company, calculated as Assets minus Liabilities. This is also called "Book Value" or "Net Worth." It includes paid-in capital (investments), retained earnings (profits kept in the business), and treasury stock (repurchased shares). A CPA would explain that positive equity means assets exceed liabilities - negative equity (deficit) is a red flag indicating the company owes more than it owns. Equity is the foundation for calculating return on equity.';
    }
    if (lowerName.contains('cash flow') || lowerName.contains('cashflow')) {
      return 'Cash flow tracks the actual movement of cash, which differs from accounting profit. The Statement of Cash Flows categorizes cash flows into Operating (business activities), Investing (asset transactions), and Financing (borrowing/equity). A CPA would emphasize that positive operating cash flow is critical - it shows the business generates cash from operations, not just from borrowing or asset sales. Cash flow is often more important than reported profit for assessing financial health, as profit can be manipulated through accounting choices, but cash flow reflects actual cash generation.';
    }
    if (lowerName.contains('eps') || lowerName.contains('earnings per share')) {
      return 'Earnings Per Share (EPS) is a key accounting metric calculated as Net Income divided by weighted average shares outstanding. It shows how much profit each share represents, making it easier to compare companies of different sizes. GAAP requires reporting both Basic EPS and Diluted EPS (assuming all convertible securities are converted). A CPA would explain that higher EPS generally indicates better profitability per share. EPS is used in valuation ratios like P/E ratio and is a key metric for investors assessing earnings relative to share price.';
    }
    if (lowerName.contains('return') || lowerName.contains('roe') || lowerName.contains('roa')) {
      return 'Return ratios measure how efficiently the company uses capital or assets to generate profits. Return on Equity (ROE) shows efficiency of using shareholder capital, while Return on Assets (ROA) shows efficiency of using total assets. These accounting ratios help assess management effectiveness and compare companies within industries. Higher returns typically indicate better capital utilization. A CPA would note that ROE can be influenced by leverage (debt), while ROA is not, making ROA useful for comparing companies with different capital structures.';
    }
    if (lowerName.contains('depreciation') || lowerName.contains('amortization')) {
      return 'Depreciation (for tangible assets) and Amortization (for intangible assets) are accounting methods to allocate the cost of long-term assets over their useful lives. These are non-cash expenses that reduce reported income but don\'t involve actual cash outflows. Accountants use these to match asset costs with the periods that benefit from asset use (matching principle). A CPA would explain that these expenses reduce taxable income and reported earnings, but don\'t affect cash flow, which is why EBITDA (earnings before these items) is often used to approximate cash-generating ability.';
    }
    if (lowerName.contains('cost') || lowerName.contains('cogs') || lowerName.contains('expense')) {
      return 'In accounting, costs and expenses represent the consumption of resources to generate revenue. Costs are matched to revenue in the same period (matching principle). Cost of Goods Sold (COGS) represents direct production costs, while operating expenses represent costs of running the business. A CPA would explain that expenses reduce net income and appear on the Income Statement. Effective cost control relative to revenue is crucial for profitability.';
    }
    if (lowerName.contains('turnover') || lowerName.contains('days')) {
      return 'Turnover ratios measure how efficiently the company uses assets or manages working capital. Examples include inventory turnover (how quickly inventory is sold), receivables turnover (how quickly customers pay), and asset turnover (how efficiently assets generate sales). Days ratios (like Days Sales Outstanding) show the average time for processes. A CPA would explain that higher turnover typically indicates better efficiency, though industry norms vary significantly.';
    }
    
    // Default fallback with accounting context
    return 'This is a financial metric used in accounting and financial analysis to assess company performance, financial position, or cash flows. Financial metrics are derived from the three main financial statements: Income Statement (profitability), Balance Sheet (financial position), and Statement of Cash Flows (liquidity). Accountants use these metrics to evaluate financial health, compare companies, assess management performance, and identify trends. Metrics follow Generally Accepted Accounting Principles (GAAP) and provide standardized ways to analyze financial information.';
  }
}
