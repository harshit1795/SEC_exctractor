/**
 * Technical Analysis Indicators
 */

export interface PriceData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

/**
 * Calculate Simple Moving Average
 */
export function calculateSMA(data: number[], period: number): number[] {
  const sma: number[] = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      sma.push(NaN);
    } else {
      const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
      sma.push(sum / period);
    }
  }
  return sma;
}

/**
 * Calculate Exponential Moving Average
 */
export function calculateEMA(data: number[], period: number): number[] {
  const ema: number[] = [];
  const multiplier = 2 / (period + 1);
  
  for (let i = 0; i < data.length; i++) {
    if (i === 0) {
      ema.push(data[i]);
    } else if (i < period - 1) {
      // Use SMA for initial values
      const sum = data.slice(0, i + 1).reduce((a, b) => a + b, 0);
      ema.push(sum / (i + 1));
    } else {
      ema.push((data[i] - ema[i - 1]) * multiplier + ema[i - 1]);
    }
  }
  return ema;
}

/**
 * Calculate RSI (Relative Strength Index)
 */
export function calculateRSI(prices: number[], period: number = 14): number[] {
  const rsi: number[] = [];
  const gains: number[] = [];
  const losses: number[] = [];

  for (let i = 1; i < prices.length; i++) {
    const change = prices[i] - prices[i - 1];
    gains.push(change > 0 ? change : 0);
    losses.push(change < 0 ? Math.abs(change) : 0);
  }

  for (let i = 0; i < prices.length; i++) {
    if (i < period) {
      rsi.push(NaN);
    } else {
      const avgGain = gains.slice(i - period, i).reduce((a, b) => a + b, 0) / period;
      const avgLoss = losses.slice(i - period, i).reduce((a, b) => a + b, 0) / period;
      
      if (avgLoss === 0) {
        rsi.push(100);
      } else {
        const rs = avgGain / avgLoss;
        rsi.push(100 - (100 / (1 + rs)));
      }
    }
  }

  return rsi;
}

/**
 * Calculate MACD (Moving Average Convergence Divergence)
 */
export function calculateMACD(
  prices: number[],
  fastPeriod: number = 12,
  slowPeriod: number = 26,
  signalPeriod: number = 9
): { macd: number[]; signal: number[]; histogram: number[] } {
  const fastEMA = calculateEMA(prices, fastPeriod);
  const slowEMA = calculateEMA(prices, slowPeriod);
  
  const macd = fastEMA.map((fast, i) => {
    const slow = slowEMA[i];
    if (isNaN(fast) || isNaN(slow)) return NaN;
    return fast - slow;
  });
  
  // Calculate signal line from MACD values (filter out NaN for EMA calculation)
  const macdValues = macd.filter((v) => !isNaN(v));
  const signalEMA = calculateEMA(macdValues, signalPeriod);
  
  // Pad signal array to match macd length
  const paddedSignal: number[] = [];
  let signalIndex = 0;
  for (let i = 0; i < macd.length; i++) {
    if (isNaN(macd[i])) {
      paddedSignal.push(NaN);
    } else {
      if (signalIndex < signalEMA.length) {
        paddedSignal.push(signalEMA[signalIndex]);
        signalIndex++;
      } else {
        paddedSignal.push(NaN);
      }
    }
  }
  
  const histogram = macd.map((m, i) => {
    const s = paddedSignal[i];
    if (isNaN(m) || isNaN(s)) return NaN;
    return m - s;
  });
  
  return { macd, signal: paddedSignal, histogram };
}

/**
 * Calculate Bollinger Bands
 */
export function calculateBollingerBands(
  prices: number[],
  period: number = 20,
  stdDev: number = 2
): { upper: number[]; middle: number[]; lower: number[] } {
  const sma = calculateSMA(prices, period);
  const upper: number[] = [];
  const lower: number[] = [];

  for (let i = 0; i < prices.length; i++) {
    if (i < period - 1) {
      upper.push(NaN);
      lower.push(NaN);
    } else {
      const slice = prices.slice(i - period + 1, i + 1);
      const mean = sma[i];
      const variance = slice.reduce((sum, price) => sum + Math.pow(price - mean, 2), 0) / period;
      const standardDeviation = Math.sqrt(variance);
      
      upper.push(mean + stdDev * standardDeviation);
      lower.push(mean - stdDev * standardDeviation);
    }
  }

  return { upper, middle: sma, lower };
}

/**
 * Add technical indicators to price data
 */
export function addTechnicalIndicators(data: PriceData[]): (PriceData & {
  rsi?: number;
  macd?: number;
  macdSignal?: number;
  macdHistogram?: number;
  bbUpper?: number;
  bbMiddle?: number;
  bbLower?: number;
})[] {
  const closes = data.map((d) => d.close);
  
  const rsi = calculateRSI(closes, 14);
  const { macd, signal, histogram } = calculateMACD(closes, 12, 26, 9);
  const { upper, middle, lower } = calculateBollingerBands(closes, 20, 2);

  return data.map((item, index) => ({
    ...item,
    rsi: rsi[index] || undefined,
    macd: macd[index] || undefined,
    macdSignal: signal[index] || undefined,
    macdHistogram: histogram[index] || undefined,
    bbUpper: upper[index] || undefined,
    bbMiddle: middle[index] || undefined,
    bbLower: lower[index] || undefined,
  }));
}

