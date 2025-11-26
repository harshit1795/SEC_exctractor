'use client';

import { useFundamentals } from '@/lib/hooks/useTickerData';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { useMemo, useEffect } from 'react';

interface CategoryFilterProps {
  ticker: string;
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
}

export function CategoryFilter({
  ticker,
  selectedCategory,
  onCategoryChange,
}: CategoryFilterProps) {
  const { data, isLoading, error } = useFundamentals(ticker);

  const categories = useMemo(() => {
    // Handle different response formats
    const dataArray = data?.data?.data || data?.data || [];
    
    if (!dataArray || !Array.isArray(dataArray)) return [];
    
    const uniqueCategories = new Set<string>();
    dataArray.forEach((item: any) => {
      const category = item.Category || item.category;
      if (category) {
        uniqueCategories.add(category);
      }
    });
    
    return Array.from(uniqueCategories).sort();
  }, [data]);

  // Set default category if none selected - MUST be before any early returns
  useEffect(() => {
    if (!selectedCategory && categories.length > 0) {
      const defaultCategory = categories[0];
      onCategoryChange(defaultCategory);
    }
  }, [categories, selectedCategory, onCategoryChange]);

  if (isLoading) {
    return <Loading message="Loading categories..." size="sm" />;
  }

  if (error) {
    return <ErrorDisplay error={error} message="Failed to load categories" />;
  }

  if (categories.length === 0) {
    return (
      <div className="text-sm text-gray-500">No categories available</div>
    );
  }

  return (
    <div>
      <label
        htmlFor="category-select"
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        Metric Category
      </label>
      <select
        id="category-select"
        value={selectedCategory || categories[0] || ''}
        onChange={(e) => onCategoryChange(e.target.value)}
        className="w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
      >
        {categories.map((category) => (
          <option key={category} value={category}>
            {category}
          </option>
        ))}
      </select>
    </div>
  );
}

