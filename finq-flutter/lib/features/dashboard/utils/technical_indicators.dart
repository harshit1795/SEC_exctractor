import 'dart:math';

import '../price_chart.dart';

class TechnicalIndicators {
  static List<double?> calculateSMA(List<PricePoint> points, int period) {
    if (points.isEmpty) return [];
    
    final sma = List<double?>.filled(points.length, null);
    if (points.length < period) return sma;

    for (int i = 0; i <= points.length - period; i++) {
        double sum = 0;
        for (int j = 0; j < period; j++) {
            sum += points[i + j].close; // Assuming points are sorted ascending by date?
            // Actually price_chart.dart returns sorted by date ASCENDING (oldest to newest).
            // Let's verify sort order in price_chart.dart.
            // "points.sort((a, b) => a.date.compareTo(b.date));" -> Ascending.
            // So index 0 is oldest.
            // moving average should be calculated ending at index i.
        }
    }
    
    // Efficient SMA:
    double sum = 0;
    for (int i=0; i<points.length; i++) {
        sum += points[i].close;
        if (i >= period) {
            sum -= points[i - period].close;
            sma[i] = sum / period;
        } else if (i == period - 1) {
            sma[i] = sum / period;
        }
    }
    return sma;
  }

  static List<double?> calculateEMA(List<PricePoint> points, int period) {
    if (points.isEmpty) return [];
    final ema = List<double?>.filled(points.length, null);
    if (points.length < period) return ema;

    final k = 2 / (period + 1);
    
    // Initial SMA
    double sum = 0;
    for (int i = 0; i < period; i++) {
      sum += points[i].close;
    }
    ema[period - 1] = sum / period;

    for (int i = period; i < points.length; i++) {
      ema[i] = (points[i].close * k) + (ema[i - 1]! * (1 - k));
    }
    return ema;
  }

  static RsiResult calculateRSI(List<PricePoint> points, {int period = 14}) {
    if (points.isEmpty || points.length <= period) {
        return RsiResult(values: List.filled(points.length, null));
    }

    final rsi = List<double?>.filled(points.length, null);
    
    double avgGain = 0;
    double avgLoss = 0;

    // First period
    for (int i = 1; i <= period; i++) {
      final change = points[i].close - points[i - 1].close;
      if (change > 0) avgGain += change;
      else avgLoss += change.abs();
    }
    
    avgGain /= period;
    avgLoss /= period;
    
    rsi[period] = 100 - (100 / (1 + (avgGain / (avgLoss == 0 ? 1 : avgLoss))));

    for (int i = period + 1; i < points.length; i++) {
        final change = points[i].close - points[i - 1].close;
        final gain = change > 0 ? change : 0.0;
        final loss = change < 0 ? change.abs() : 0.0;
        
        avgGain = ((avgGain * (period - 1)) + gain) / period;
        avgLoss = ((avgLoss * (period - 1)) + loss) / period;
        
        final rs = avgGain / (avgLoss == 0 ? 1 : avgLoss);
        rsi[i] = 100 - (100 / (1 + rs));
    }

    return RsiResult(values: rsi);
  }

  static MacdResult calculateMACD(List<PricePoint> points, {
    int fastPeriod = 12,
    int slowPeriod = 26,
    int signalPeriod = 9,
  }) {
    final fastEma = calculateEMA(points, fastPeriod);
    final slowEma = calculateEMA(points, slowPeriod);
    
    final macdLine = List<double?>.filled(points.length, null);
    final signalLine = List<double?>.filled(points.length, null);
    final histogram = List<double?>.filled(points.length, null);

    // Calculate MACD Line
    for (int i = 0; i < points.length; i++) {
        if (fastEma[i] != null && slowEma[i] != null) {
            macdLine[i] = fastEma[i]! - slowEma[i]!;
        }
    }

    // Calculate Signal Line (EMA of MACD Line)
    // We need to extract non-null MACD values to calculate their EMA properly, 
    // keeping indices aligned is tricky. 
    // Simplified: Start calculating Signal Line after we have enough MACD line data.
    
    // Find first valid MACD index
    int firstValidMacd = -1;
    for (int i=0; i < points.length; i++) {
        if (macdLine[i] != null) {
            firstValidMacd = i;
            break;
        }
    }

    if (firstValidMacd != -1 && (points.length - firstValidMacd) >= signalPeriod) {
        // Calculate initial SMA for Signal
        double sum = 0;
        for (int i = 0; i < signalPeriod; i++) {
            sum += macdLine[firstValidMacd + i]!;
        }
        signalLine[firstValidMacd + signalPeriod - 1] = sum / signalPeriod;
        
        // Calculate EMA for Signal
        final k = 2 / (signalPeriod + 1);
        for (int i = firstValidMacd + signalPeriod; i < points.length; i++) {
            signalLine[i] = (macdLine[i]! * k) + (signalLine[i - 1]! * (1 - k));
        }
    }

    // Calculate Histogram
    for (int i = 0; i < points.length; i++) {
        if (macdLine[i] != null && signalLine[i] != null) {
            histogram[i] = macdLine[i]! - signalLine[i]!;
        }
    }

    return MacdResult(
        macd: macdLine,
        signal: signalLine,
        histogram: histogram,
    );
  }

  static BollingerResult calculateBollingerBands(List<PricePoint> points, {
      int period = 20, 
      double stdDevMultiplier = 2.0
  }) {
    if (points.isEmpty) return BollingerResult(upper: [], middle: [], lower: []);
    
    final middle = calculateSMA(points, period);
    final upper = List<double?>.filled(points.length, null);
    final lower = List<double?>.filled(points.length, null);

    for (int i = period - 1; i < points.length; i++) {
        if (middle[i] == null) continue;

        double sumSqDiff = 0;
        for (int j = 0; j < period; j++) {
            final diff = points[i - j].close - middle[i]!;
            sumSqDiff += diff * diff;
        }
        final variance = sumSqDiff / period;
        final stdDev = sqrt(variance);
        
        upper[i] = middle[i]! + (stdDev * stdDevMultiplier);
        lower[i] = middle[i]! - (stdDev * stdDevMultiplier);
    }
    
    return BollingerResult(upper: upper, middle: middle, lower: lower);
  }
}

class RsiResult {
    final List<double?> values;
    RsiResult({required this.values});
}

class MacdResult {
    final List<double?> macd;
    final List<double?> signal;
    final List<double?> histogram;
    
    MacdResult({required this.macd, required this.signal, required this.histogram});
}

class BollingerResult {
    final List<double?> upper;
    final List<double?> middle;
    final List<double?> lower;

    BollingerResult({required this.upper, required this.middle, required this.lower});
}
