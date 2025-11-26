'use client';

interface DebugInfoProps {
  data: any;
  label?: string;
}

export function DebugInfo({ data, label = 'Debug' }: DebugInfoProps) {
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="mt-4 rounded-lg bg-gray-100 p-4 text-xs">
      <p className="font-semibold mb-2">{label}:</p>
      <pre className="overflow-auto max-h-40">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}

