/// Financial statement hierarchies for Balance Sheet and Income Statement
/// Defines tree structures for hierarchical visualization

enum NodeCategory {
  asset,
  currentAsset,
  nonCurrentAsset,
  liability,
  currentLiability,
  longTermLiability,
  equity,
  revenue,
  expense,
  profit,
}

enum NodeType {
  root,
  parent,
  leaf,
  calculated,
}

enum CalculationType {
  none,
  sum,          // Sum of children
  subtract,     // A - B
  custom,       // Custom formula
}

class FinancialNode {
  const FinancialNode({
    required this.id,
    required this.displayName,
    this.metricName,
    this.alternativeNames = const [],
    required this.category,
    required this.type,
    this.calculationType = CalculationType.none,
    this.childMetricNames = const [],
    this.children = const [],
  });

  final String id;
  final String displayName;
  final String? metricName; // null for calculated nodes
  final List<String> alternativeNames; // Alternative metric names in data
  final NodeCategory category;
  final NodeType type;
  final CalculationType calculationType;
  final List<String> childMetricNames; // For rollup calculations
  final List<FinancialNode> children;

  /// Get all possible metric names for this node
  List<String> get allMetricNames {
    if (metricName == null) return [];
    return [metricName!, ...alternativeNames];
  }
}

/// Balance Sheet Hierarchy
class BalanceSheetHierarchy {
  static final List<FinancialNode> roots = [
    // Assets Root
    FinancialNode(
      id: 'total_assets',
      displayName: 'Total Assets',
      metricName: 'Total Assets',
      alternativeNames: ['TotalAssets', 'Total Assets'],
      category: NodeCategory.asset,
      type: NodeType.root,
      calculationType: CalculationType.sum,
      childMetricNames: [],
      children: [
        // Current Assets
        FinancialNode(
          id: 'current_assets',
          displayName: 'Current Assets',
          metricName: 'Current Assets',
          alternativeNames: ['Total Current Assets', 'CurrentAssets'],
          category: NodeCategory.currentAsset,
          type: NodeType.parent,
          calculationType: CalculationType.sum,
          childMetricNames: [],
          children: [
            FinancialNode(
              id: 'cash',
              displayName: 'Cash and Cash Equivalents',
              metricName: 'Cash And Cash Equivalents',
              alternativeNames: [
                'Cash and Cash Equivalents',
                'Cash',
                'Cash, Cash Equivalents and Short Term Investments',
                'Cash Cash Equivalents And Short Term Investments',
                'Cash Equivalents',
                'Cash Financial',
              ],
              category: NodeCategory.currentAsset,
              type: NodeType.leaf,
            ),
            FinancialNode(
              id: 'receivables',
              displayName: 'Accounts Receivable',
              metricName: 'Accounts Receivable',
              alternativeNames: [
                'Receivables',
                'Accounts Receivable, Net',
                'AccountsReceivable',
                'Gross Accounts Receivable',
              ],
              category: NodeCategory.currentAsset,
              type: NodeType.leaf,
            ),
            FinancialNode(
              id: 'inventory',
              displayName: 'Inventory',
              metricName: 'Inventory',
              alternativeNames: ['Inventories', 'Total Inventory'],
              category: NodeCategory.currentAsset,
              type: NodeType.leaf,
            ),
            FinancialNode(
              id: 'other_current_assets',
              displayName: 'Other Current Assets',
              metricName: 'Other Current Assets',
              alternativeNames: [
                'OtherCurrentAssets',
                'Prepaid Expenses and Other Current Assets',
                'Prepaid Assets',
              ],
              category: NodeCategory.currentAsset,
              type: NodeType.leaf,
            ),
          ],
        ),
        // Non-Current Assets
        FinancialNode(
          id: 'non_current_assets',
          displayName: 'Non-Current Assets',
          metricName: null, // Calculated
          category: NodeCategory.nonCurrentAsset,
          type: NodeType.parent,
          calculationType: CalculationType.sum,
          childMetricNames: [],
          children: [
            FinancialNode(
              id: 'ppe',
              displayName: 'Property, Plant and Equipment',
              metricName: 'Net PPE',
              alternativeNames: [
                'Property, Plant and Equipment',
                'Net Property, Plant and Equipment',
                'PP&E',
                'Net Property Plant And Equipment',
                'Gross PPE',
                'Properties',
              ],
              category: NodeCategory.nonCurrentAsset,
              type: NodeType.leaf,
            ),
            FinancialNode(
              id: 'intangibles',
              displayName: 'Intangible Assets',
              metricName: 'Other Intangible Assets',
              alternativeNames: ['Intangible Assets', 'IntangibleAssets', 'Net Intangible Assets'],
              category: NodeCategory.nonCurrentAsset,
              type: NodeType.leaf,
            ),
            FinancialNode(
              id: 'goodwill',
              displayName: 'Goodwill',
              metricName: 'Goodwill',
              alternativeNames: ['Goodwill And Other Intangible Assets'],
              category: NodeCategory.nonCurrentAsset,
              type: NodeType.leaf,
            ),
            FinancialNode(
              id: 'long_term_investments',
              displayName: 'Long-Term Investments',
              metricName: 'Investments And Advances',
              alternativeNames: [
                'Long-Term Investments',
                'Long Term Investments',
                'LongTermInvestments',
                'Long Term Equity Investment',
              ],
              category: NodeCategory.nonCurrentAsset,
              type: NodeType.leaf,
            ),
          ],
        ),
      ],
    ),
    // Liabilities Root
    FinancialNode(
      id: 'total_liabilities',
      displayName: 'Total Liabilities',
      metricName: 'Total Liabilities Net Minority Interest',
      alternativeNames: [
        'Total Liabilities',
        'TotalLiabilities',
        'Total Liab',
      ],
      category: NodeCategory.liability,
      type: NodeType.root,
      calculationType: CalculationType.sum,
      childMetricNames: [],
      children: [
        // Current Liabilities
        FinancialNode(
          id: 'current_liabilities',
          displayName: 'Current Liabilities',
          metricName: 'Current Liabilities',
          alternativeNames: ['Total Current Liabilities', 'CurrentLiabilities'],
          category: NodeCategory.currentLiability,
          type: NodeType.parent,
          calculationType: CalculationType.sum,
          childMetricNames: [],
          children: [
            FinancialNode(
              id: 'accounts_payable',
              displayName: 'Accounts Payable',
              metricName: 'Accounts Payable',
              alternativeNames: ['AccountsPayable', 'Payables', 'Payables And Accrued Expenses'],
              category: NodeCategory.currentLiability,
              type: NodeType.leaf,
            ),
            FinancialNode(
              id: 'short_term_debt',
              displayName: 'Short-Term Debt',
              metricName: 'Current Debt',
              alternativeNames: [
                'Short Term Debt',
                'Short-Term Borrowings',
                'Current Portion of Long-Term Debt',
                'Current Debt And Capital Lease Obligation',
                'Commercial Paper',
              ],
              category: NodeCategory.currentLiability,
              type: NodeType.leaf,
            ),
            FinancialNode(
              id: 'accrued_expenses',
              displayName: 'Accrued Expenses',
              metricName: 'Current Accrued Expenses',
              alternativeNames: [
                'Accrued Expenses',
                'AccruedExpenses',
                'Accrued Liabilities',
              ],
              category: NodeCategory.currentLiability,
              type: NodeType.leaf,
            ),
            FinancialNode(
              id: 'other_current_liabilities',
              displayName: 'Other Current Liabilities',
              metricName: 'Other Current Liabilities',
              alternativeNames: ['OtherCurrentLiabilities'],
              category: NodeCategory.currentLiability,
              type: NodeType.leaf,
            ),
          ],
        ),
        // Long-Term Liabilities
        FinancialNode(
          id: 'long_term_liabilities',
          displayName: 'Long-Term Liabilities',
          metricName: null, // Calculated
          category: NodeCategory.longTermLiability,
          type: NodeType.parent,
          calculationType: CalculationType.sum,
          childMetricNames: [],
          children: [
            FinancialNode(
              id: 'long_term_debt',
              displayName: 'Long-Term Debt',
              metricName: 'Long Term Debt',
              alternativeNames: [
                'Long-Term Borrowings',
                'LongTermDebt',
                'Long Term Debt And Capital Lease Obligation',
              ],
              category: NodeCategory.longTermLiability,
              type: NodeType.leaf,
            ),
            FinancialNode(
              id: 'deferred_tax',
              displayName: 'Deferred Tax Liabilities',
              metricName: 'Non Current Deferred Taxes Liabilities',
              alternativeNames: [
                'Deferred Tax Liabilities',
                'DeferredTaxLiabilities',
                'Deferred Income Tax',
              ],
              category: NodeCategory.longTermLiability,
              type: NodeType.leaf,
            ),
            FinancialNode(
              id: 'other_long_term_liabilities',
              displayName: 'Other Long-Term Liabilities',
              metricName: 'Other Non Current Liabilities',
              alternativeNames: [
                'Other Long-Term Liabilities',
                'OtherLongTermLiabilities',
                'Total Non Current Liabilities Net Minority Interest',
              ],
              category: NodeCategory.longTermLiability,
              type: NodeType.leaf,
            ),
          ],
        ),
      ],
    ),
    // Equity Root
    FinancialNode(
      id: 'shareholders_equity',
      displayName: 'Shareholder Equity',
      metricName: 'Stockholders Equity',
      alternativeNames: [
        'Total Stockholder Equity',
        'Total Stockholders Equity',
        'Shareholder Equity',
        'Total Equity',
        'Stockholders\' Equity',
        'Common Stock Equity',
        'Total Equity Gross Minority Interest',
      ],
      category: NodeCategory.equity,
      type: NodeType.root,
      calculationType: CalculationType.sum,
      childMetricNames: [],
      children: [
        FinancialNode(
          id: 'common_stock',
          displayName: 'Common Stock',
          metricName: 'Common Stock',
          alternativeNames: [
            'CommonStock',
            'Common Stock and Additional Paid in Capital',
          ],
          category: NodeCategory.equity,
          type: NodeType.leaf,
        ),
        FinancialNode(
          id: 'retained_earnings',
          displayName: 'Retained Earnings',
          metricName: 'Retained Earnings',
          alternativeNames: ['RetainedEarnings', 'Accumulated Deficit'],
          category: NodeCategory.equity,
          type: NodeType.leaf,
        ),
        FinancialNode(
          id: 'treasury_stock',
          displayName: 'Treasury Stock',
          metricName: 'Treasury Stock',
          alternativeNames: ['TreasuryStock', 'Treasury Shares'],
          category: NodeCategory.equity,
          type: NodeType.leaf,
        ),
        FinancialNode(
          id: 'other_equity',
          displayName: 'Other Equity Items',
          metricName: 'Other Equity Interest',
          alternativeNames: [
            'Accumulated Other Comprehensive Income',
            'OtherEquity',
          ],
          category: NodeCategory.equity,
          type: NodeType.leaf,
        ),
      ],
    ),
  ];
}

/// Income Statement Hierarchy
class IncomeStatementHierarchy {
  static final FinancialNode root = FinancialNode(
    id: 'income_statement',
    displayName: 'Income Statement',
    metricName: null,
    category: NodeCategory.revenue,
    type: NodeType.root,
    children: [
      // Revenue
      FinancialNode(
        id: 'total_revenue',
        displayName: 'Total Revenue',
        metricName: 'Total Revenue',
        alternativeNames: ['Revenue', 'Net Revenue', 'Sales', 'Total Revenue (ttm)', 'Operating Revenue'],
        category: NodeCategory.revenue,
        type: NodeType.parent,
        children: [
          FinancialNode(
            id: 'revenue',
            displayName: 'Revenue',
            metricName: 'Operating Revenue',
            alternativeNames: ['Revenue', 'Net Sales', 'Total Revenue'],
            category: NodeCategory.revenue,
            type: NodeType.leaf,
          ),
        ],
      ),
      // Cost of Revenue
      FinancialNode(
        id: 'cost_of_revenue',
        displayName: 'Cost of Revenue',
        metricName: 'Cost Of Revenue',
        alternativeNames: [
          'Cost of Revenue',
          'Cost of Goods Sold',
          'COGS',
          'Cost of Sales',
          'Cost Of Revenue (ttm)',
          'Reconciled Cost Of Revenue',
        ],
        category: NodeCategory.expense,
        type: NodeType.parent,
        children: [
          FinancialNode(
            id: 'cogs',
            displayName: 'Cost of Goods Sold',
            metricName: 'Cost Of Revenue',
            alternativeNames: ['Cost of Goods Sold', 'COGS'],
            category: NodeCategory.expense,
            type: NodeType.leaf,
          ),
        ],
      ),
      // Gross Profit
      FinancialNode(
        id: 'gross_profit',
        displayName: 'Gross Profit',
        metricName: 'Gross Profit',
        alternativeNames: ['Gross Income', 'Gross Profit (ttm)'],
        category: NodeCategory.profit,
        type: NodeType.calculated,
        calculationType: CalculationType.subtract,
        childMetricNames: ['Total Revenue', 'Cost of Revenue'],
      ),
      // Operating Expenses
      FinancialNode(
        id: 'operating_expenses',
        displayName: 'Operating Expenses',
        metricName: 'Operating Expense',
        alternativeNames: ['Total Operating Expenses', 'OPEX'],
        category: NodeCategory.expense,
        type: NodeType.parent,
        calculationType: CalculationType.sum,
        childMetricNames: [],
        children: [
          FinancialNode(
            id: 'sga',
            displayName: 'Selling, General and Administrative',
            metricName: 'Selling General And Administration',
            alternativeNames: ['Selling General and Administrative', 'SG&A', 'SGA', 'Selling General And Administrative', 'General And Administrative Expense'],
            category: NodeCategory.expense,
            type: NodeType.leaf,
          ),
          FinancialNode(
            id: 'rnd',
            displayName: 'Research and Development',
            metricName: 'Research And Development',
            alternativeNames: ['Research and Development', 'R&D'],
            category: NodeCategory.expense,
            type: NodeType.leaf,
          ),
          FinancialNode(
            id: 'depreciation',
            displayName: 'Depreciation and Amortization',
            metricName: 'Depreciation And Amortization In Income Statement',
            alternativeNames: [
              'Depreciation and Amortization',
              'Depreciation',
              'Amortization',
              'Depreciation Amortization Depletion',
              'Depreciation Amortization Depletion Income Statement',
              'Reconciled Depreciation',
            ],
            category: NodeCategory.expense,
            type: NodeType.leaf,
          ),
        ],
      ),
      // Operating Income
      FinancialNode(
        id: 'operating_income',
        displayName: 'Operating Income',
        metricName: 'Operating Income',
        alternativeNames: [
          'EBIT',
          'Operating Profit',
          'Operating Income (ttm)',
          'Earnings Before Interest and Taxes',
        ],
        category: NodeCategory.profit,
        type: NodeType.calculated,
        calculationType: CalculationType.subtract,
        childMetricNames: ['Gross Profit', 'Operating Expenses'],
      ),
      // Other Income/Expenses
      FinancialNode(
        id: 'other_items',
        displayName: 'Other Income/Expenses',
        metricName: null,
        category: NodeCategory.expense,
        type: NodeType.parent,
        calculationType: CalculationType.sum,
        childMetricNames: [],
        children: [
          FinancialNode(
            id: 'interest_expense',
            displayName: 'Interest Expense',
            metricName: 'Interest Expense',
            alternativeNames: ['Net Interest Expense', 'InterestExpense'],
            category: NodeCategory.expense,
            type: NodeType.leaf,
          ),
          FinancialNode(
            id: 'interest_income',
            displayName: 'Interest Income',
            metricName: 'Interest Income',
            alternativeNames: ['InterestIncome'],
            category: NodeCategory.revenue,
            type: NodeType.leaf,
          ),
          FinancialNode(
            id: 'other_income',
            displayName: 'Other Income/Expense',
            metricName: 'Other Income Expense',
            alternativeNames: [
              'Other Income (Expense)',
              'OtherIncomeExpense',
              'Non Operating Income Net Other',
            ],
            category: NodeCategory.revenue,
            type: NodeType.leaf,
          ),
        ],
      ),
      // Income Before Tax
      FinancialNode(
        id: 'income_before_tax',
        displayName: 'Income Before Tax',
        metricName: 'Pretax Income',
        alternativeNames: [
          'Income Before Tax',
          'Earnings Before Tax',
          'Pretax Income (ttm)',
        ],
        category: NodeCategory.profit,
        type: NodeType.calculated,
        calculationType: CalculationType.custom,
      ),
      // Tax Expense
      FinancialNode(
        id: 'tax_expense',
        displayName: 'Tax Expense',
        metricName: 'Tax Provision',
        alternativeNames: [
          'Income Tax Expense',
          'Tax Expense',
          'TaxExpense',
          'Tax Provision (ttm)',
        ],
        category: NodeCategory.expense,
        type: NodeType.leaf,
      ),
      // Net Income
      FinancialNode(
        id: 'net_income',
        displayName: 'Net Income',
        metricName: 'Net Income Common Stockholders',
        alternativeNames: [
          'Net Income',
          'Net Income To Common',
          'Net Income (ttm)',
          'Net Income From Continuing Operations',
          'Net Income Continuous Operations',
          'Net Income From Continuing Operation Net Minority Interest',
          'Net Income Including Noncontrolling Interests',
          'Diluted NI Availto Com Stockholders',
        ],
        category: NodeCategory.profit,
        type: NodeType.leaf,
        calculationType: CalculationType.none,
        childMetricNames: [],
      ),
    ],
  );
}
