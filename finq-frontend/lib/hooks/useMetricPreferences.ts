'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from './useAuth';

interface MetricPreferences {
  [category: string]: string[]; // category -> selected metrics
}

const STORAGE_KEY = 'finq_metric_preferences';

export function useMetricPreferences() {
  const { user } = useAuth();
  const storageKey = user ? `${STORAGE_KEY}_${user.uid}` : STORAGE_KEY;
  
  const [preferences, setPreferences] = useState<MetricPreferences>(() => {
    if (typeof window === 'undefined') return {};
    
    try {
      const saved = localStorage.getItem(storageKey);
      return saved ? JSON.parse(saved) : {};
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
    (category: string): string[] => {
      return preferences[category] || [];
    },
    [preferences]
  );

  const setMetricsForCategory = useCallback(
    (category: string, metrics: string[]) => {
      setPreferences((prev) => ({
        ...prev,
        [category]: metrics,
      }));
    },
    []
  );

  const clearCategory = useCallback((category: string) => {
    setPreferences((prev) => {
      const updated = { ...prev };
      delete updated[category];
      return updated;
    });
  }, []);

  const clearAll = useCallback(() => {
    setPreferences({});
  }, []);

  const hasPreferencesForCategory = useCallback(
    (category: string): boolean => {
      return category in preferences && (preferences[category]?.length || 0) > 0;
    },
    [preferences]
  );

  return {
    getMetricsForCategory,
    setMetricsForCategory,
    clearCategory,
    clearAll,
    hasPreferencesForCategory,
    preferences,
  };
}

