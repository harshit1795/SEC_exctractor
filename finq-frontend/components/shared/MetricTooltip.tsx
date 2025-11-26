'use client';

import { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { getMetricDescription } from '@/lib/metricDescriptions';

interface MetricTooltipProps {
  metricName: string;
  className?: string;
}

export function MetricTooltip({ metricName, className = '' }: MetricTooltipProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [position, setPosition] = useState<{ top: number; left: number; placement: 'top' | 'bottom' } | null>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const description = getMetricDescription(metricName);

  useEffect(() => {
    if (isHovered && buttonRef.current) {
      const updatePosition = () => {
        if (!buttonRef.current) return;
        
        const buttonRect = buttonRef.current.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;
        const tooltipWidth = 600;
        const tooltipHeight = 300; // Estimated height
        const spacing = 8;
        
        // Calculate horizontal position (centered on button)
        let left = buttonRect.left + (buttonRect.width / 2) - (tooltipWidth / 2);
        
        // Ensure tooltip stays within viewport
        if (left < 10) {
          left = 10;
        } else if (left + tooltipWidth > viewportWidth - 10) {
          left = viewportWidth - tooltipWidth - 10;
        }
        
        // Calculate vertical position
        const spaceAbove = buttonRect.top;
        const spaceBelow = viewportHeight - buttonRect.bottom;
        const showAbove = spaceAbove >= tooltipHeight + spacing || spaceBelow < spaceAbove;
        
        let top: number;
        let placement: 'top' | 'bottom';
        
        if (showAbove) {
          // Show above button
          top = buttonRect.top - tooltipHeight - spacing;
          placement = 'top';
        } else {
          // Show below button
          top = buttonRect.bottom + spacing;
          placement = 'bottom';
        }
        
        // Ensure tooltip doesn't go off screen vertically
        if (top < 10) {
          top = 10;
        } else if (top + tooltipHeight > viewportHeight - 10) {
          top = viewportHeight - tooltipHeight - 10;
        }
        
        setPosition({ top, left, placement });
      };
      
      updatePosition();
      
      // Update position on scroll/resize
      window.addEventListener('scroll', updatePosition, true);
      window.addEventListener('resize', updatePosition);
      
      return () => {
        window.removeEventListener('scroll', updatePosition, true);
        window.removeEventListener('resize', updatePosition);
      };
    } else {
      setPosition(null);
    }
  }, [isHovered]);

  return (
    <>
      <div className={`relative inline-block ${className}`}>
        <button
          ref={buttonRef}
          type="button"
          className="inline-flex items-center justify-center w-4 h-4 ml-1 text-gray-400 hover:text-blue-600 transition-colors"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
          }}
          aria-label={`Information about ${metricName}`}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="w-4 h-4"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"
            />
          </svg>
        </button>
      </div>

      {isHovered && position && typeof window !== 'undefined' && createPortal(
        <div
          ref={tooltipRef}
          className="fixed z-[9999] w-[600px] max-w-[calc(100vw-2rem)] p-4 text-sm text-gray-700 bg-white border border-gray-200 rounded-lg shadow-xl pointer-events-auto"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          style={{
            top: `${position.top}px`,
            left: `${position.left}px`,
            maxWidth: 'min(600px, calc(100vw - 2rem))',
            wordWrap: 'break-word',
            overflowWrap: 'break-word',
            maxHeight: 'calc(100vh - 2rem)',
            overflowY: 'auto'
          }}
        >
          <div className="font-semibold text-gray-900 mb-2 text-base border-b border-gray-200 pb-2">{metricName}</div>
          <div className="text-gray-600 leading-relaxed whitespace-normal">{description}</div>
        </div>,
        document.body
      )}
    </>
  );
}

