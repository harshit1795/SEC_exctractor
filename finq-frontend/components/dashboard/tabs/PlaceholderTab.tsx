'use client';

import { Card } from '@/components/shared/Card';

interface PlaceholderTabProps {
  title: string;
  description?: string;
}

export function PlaceholderTab({ title, description }: PlaceholderTabProps) {
  return (
    <Card>
      <div className="text-center py-12">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
        {description && (
          <p className="text-gray-600 mb-4">{description}</p>
        )}
        <p className="text-sm text-gray-500">
          This tab is coming soon. Content will be implemented next.
        </p>
      </div>
    </Card>
  );
}

