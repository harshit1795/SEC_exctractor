'use client';

import { useState, useMemo, useRef, useEffect } from 'react';

interface MultiSelectProps {
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
  placeholder?: string;
  label?: string;
  maxHeight?: string;
}

export function MultiSelect({
  options,
  selected,
  onChange,
  placeholder = 'Search and select...',
  label,
  maxHeight = '300px',
}: MultiSelectProps) {
  const [searchText, setSearchText] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const filteredOptions = useMemo(() => {
    if (!searchText.trim()) {
      return options;
    }
    const searchLower = searchText.toLowerCase();
    return options.filter((option) =>
      option.toLowerCase().includes(searchLower)
    );
  }, [options, searchText]);

  const handleToggle = (option: string) => {
    if (selected.includes(option)) {
      onChange(selected.filter((item) => item !== option));
    } else {
      onChange([...selected, option]);
    }
  };

  const handleSelectAll = () => {
    if (selected.length === filteredOptions.length) {
      onChange([]);
    } else {
      onChange([...filteredOptions]);
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div ref={containerRef} className="relative">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-left shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-700">
              {selected.length === 0
                ? placeholder
                : `${selected.length} metric${selected.length !== 1 ? 's' : ''} selected`}
            </span>
            <svg
              className={`h-5 w-5 text-gray-400 transition-transform ${
                isOpen ? 'rotate-180' : ''
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </div>
        </button>

        {isOpen && (
          <div
            className="absolute z-50 mt-1 w-full rounded-md border border-gray-300 bg-white shadow-lg"
            style={{ maxHeight }}
          >
            <div className="p-2 border-b border-gray-200">
              <input
                type="text"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                placeholder="Search metrics..."
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                onClick={(e) => e.stopPropagation()}
              />
            </div>
            <div className="p-2 border-b border-gray-200">
              <button
                type="button"
                onClick={handleSelectAll}
                className="text-xs text-blue-600 hover:text-blue-700"
              >
                {selected.length === filteredOptions.length
                  ? 'Deselect All'
                  : 'Select All'}
              </button>
              <span className="text-xs text-gray-500 ml-2">
                ({filteredOptions.length} available)
              </span>
            </div>
            <div className="overflow-y-auto" style={{ maxHeight: '250px' }}>
              {filteredOptions.length === 0 ? (
                <div className="p-3 text-sm text-gray-500 text-center">
                  No metrics found
                </div>
              ) : (
                filteredOptions.map((option) => {
                  const isSelected = selected.includes(option);
                  return (
                    <label
                      key={option}
                      className="flex items-center px-3 py-2 hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleToggle(option)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        onClick={(e) => e.stopPropagation()}
                      />
                      <span className="ml-3 text-sm text-gray-700">
                        {option}
                      </span>
                    </label>
                  );
                })
              )}
            </div>
          </div>
        )}
      </div>

      {/* Selected items chips */}
      {selected.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-2">
          {selected.map((item) => (
            <span
              key={item}
              className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800"
            >
              {item}
              <button
                type="button"
                onClick={() => handleToggle(item)}
                className="text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

