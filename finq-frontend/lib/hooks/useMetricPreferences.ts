'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from './useAuth';

// Structure: { [ticker: string]: { [category: string]: string[] } }
// Example: { "AAPL": { "IncomeStatement": ["Revenue", "Net Income"], "BalanceSheet": ["Assets"] } }
interface MetricPreferences {
  [ticker: string]: {
    [category: string]: string[];
  };
}

const STORAGE_KEY = 'finq_metric_preferences';

export function useMetricPreferences() {
  const { user } = useAuth();
  const storageKey = user ? `${STORAGE_KEY}_${user.uid}` : STORAGE_KEY;
  
  const [preferences, setPreferences] = useState<MetricPreferences>(() => {
    if (typeof window === 'undefined') return {};
    
    try {
      const saved = localStorage.getItem(storageKey);
      if (!saved) return {};
      
      const parsed = JSON.parse(saved);
      
      // Migration: If old format (category -> metrics), convert to new format
      // Check if it's old format (has category keys directly, not ticker keys)
      const isOldFormat = parsed && typeof parsed === 'object' && 
        Object.keys(parsed).some(key => {
          const value = parsed[key];
          return Array.isArray(value) || (typeof value === 'object' && !Array.isArray(value) && Object.keys(value).some(k => Array.isArray(value[k])));
        });
      
      if (isOldFormat && !Object.keys(parsed).some(key => parsed[key] && typeof parsed[key] === 'object' && !Array.isArray(parsed[key]))) {
        // Old format detected - migrate to new format
        // We'll migrate to a default ticker or user can re-save
        console.log('Migrating old preferences format to new ticker-based format');
        return {};
      }
      
      return parsed;
    } catch {
      return {};
    }
  });

  // Save preferences to localStorage whenever they change
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    try {
      localStorage.setItem(storageKey, JSON.stringify(preferences));
    } catch (error) {
      console.error('Failed to save metric preferences:', error);
    }
  }, [preferences, storageKey]);

  const getMetricsForCategory = useCallback(
    (ticker: string, category: string): string[] => {
      if (!ticker || !category) return [];
      return preferences[ticker.toUpperCase()]?.[category] || [];
    },
    [preferences]
  );

  const setMetricsForCategory = useCallback(
    (ticker: string, category: string, metrics: string[]) => {
      if (!ticker || !category) return;
      
      setPreferences((prev) => {
        const tickerKey = ticker.toUpperCase();
        return {
          ...prev,
          [tickerKey]: {
            ...(prev[tickerKey] || {}),
            [category]: metrics,
          },
        };
      });
    },
    []
  );

  const clearCategory = useCallback((ticker: string, category: string) => {
    if (!ticker || !category) return;
    
    setPreferences((prev) => {
      const tickerKey = ticker.toUpperCase();
      const updated = { ...prev };
      if (updated[tickerKey]) {
        updated[tickerKey] = { ...updated[tickerKey] };
        delete updated[tickerKey][category];
        // Remove ticker entry if no categories left
        if (Object.keys(updated[tickerKey]).length === 0) {
          delete updated[tickerKey];
        }
      }
      return updated;
    });
  }, []);

  const clearAll = useCallback(() => {
    setPreferences({});
  }, []);

  const clearTicker = useCallback((ticker: string) => {
    if (!ticker) return;
    
    setPreferences((prev) => {
      const updated = { ...prev };
      delete updated[ticker.toUpperCase()];
      return updated;
    });
  }, []);

  const hasPreferencesForCategory = useCallback(
    (ticker: string, category: string): boolean => {
      if (!ticker || !category) return false;
      const tickerPrefs = preferences[ticker.toUpperCase()];
      return tickerPrefs?.[category]?.length > 0 || false;
    },
    [preferences]
  );

  return {
    getMetricsForCategory,
    setMetricsForCategory,
    clearCategory,
    clearTicker,
    clearAll,
    hasPreferencesForCategory,
    preferences,
  };
}

