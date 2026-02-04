'use client';

import { useState, useEffect } from 'react';
import { AuthGuard } from '@/components/shared/AuthGuard';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card } from '@/components/shared/Card';
import { useAuth } from '@/lib/hooks/useAuth';
import { useMetricPreferences } from '@/lib/hooks/useMetricPreferences';

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const { clearAll } = useMetricPreferences();
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    feed: true,
  });
  const [preferences, setPreferences] = useState({
    theme: 'light',
    defaultTicker: '',
    defaultCategory: '',
  });

  // Load preferences from localStorage
  useEffect(() => {
    const savedNotifications = localStorage.getItem('notificationPreferences');
    const savedPreferences = localStorage.getItem('userPreferences');
    
    if (savedNotifications) {
      try {
        setNotifications(JSON.parse(savedNotifications));
      } catch (e) {
        console.error('Failed to parse notification preferences:', e);
      }
    }
    
    if (savedPreferences) {
      try {
        setPreferences(JSON.parse(savedPreferences));
      } catch (e) {
        console.error('Failed to parse user preferences:', e);
      }
    }
  }, []);

  const handleNotificationChange = (key: string, value: boolean) => {
    const updated = { ...notifications, [key]: value };
    setNotifications(updated);
    localStorage.setItem('notificationPreferences', JSON.stringify(updated));
  };

  const handlePreferenceChange = (key: string, value: string) => {
    const updated = { ...preferences, [key]: value };
    setPreferences(updated);
    localStorage.setItem('userPreferences', JSON.stringify(updated));
  };

  const handleClearMetricPreferences = () => {
    if (confirm('Are you sure you want to clear all saved metric preferences? This cannot be undone.')) {
      clearAll();
      alert('All metric preferences have been cleared.');
    }
  };

  const handleExportData = () => {
    // Export user preferences and settings
    const exportData = {
      notifications,
      preferences,
      exportedAt: new Date().toISOString(),
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `finq-settings-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <AuthGuard>
      <MainLayout>
        <h1 className="mb-6 text-3xl font-bold text-gray-900">Settings</h1>

        <div className="space-y-6">
          {/* Account Settings */}
          <Card>
            <h2 className="text-xl font-semibold mb-4">Account</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <p className="text-gray-900">{user?.email || 'N/A'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Display Name
                </label>
                <p className="text-gray-900">{user?.displayName || 'Not set'}</p>
              </div>
              <div>
                <button
                  onClick={logout}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </Card>

          {/* Notification Preferences */}
          <Card>
            <h2 className="text-xl font-semibold mb-4">Notifications</h2>
            <div className="space-y-4">
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={notifications.email}
                  onChange={(e) => handleNotificationChange('email', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Email notifications</span>
              </label>
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={notifications.push}
                  onChange={(e) => handleNotificationChange('push', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Push notifications</span>
              </label>
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={notifications.feed}
                  onChange={(e) => handleNotificationChange('feed', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Feed updates</span>
              </label>
            </div>
          </Card>

          {/* User Preferences */}
          <Card>
            <h2 className="text-xl font-semibold mb-4">Preferences</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Theme
                </label>
                <select
                  value={preferences.theme}
                  onChange={(e) => handlePreferenceChange('theme', e.target.value)}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="auto">Auto</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Default Ticker
                </label>
                <input
                  type="text"
                  value={preferences.defaultTicker}
                  onChange={(e) => handlePreferenceChange('defaultTicker', e.target.value.toUpperCase())}
                  placeholder="e.g., AAPL"
                  className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Default Category
                </label>
                <select
                  value={preferences.defaultCategory}
                  onChange={(e) => handlePreferenceChange('defaultCategory', e.target.value)}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                >
                  <option value="">None</option>
                  <option value="Technology">Technology</option>
                  <option value="Manufacturing">Manufacturing</option>
                  <option value="Finance">Finance</option>
                  <option value="Public Sector">Public Sector</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Data Management */}
          <Card>
            <h2 className="text-xl font-semibold mb-4">Data Management</h2>
            <div className="space-y-4">
              <div>
                <button
                  onClick={handleClearMetricPreferences}
                  className="px-4 py-2 text-sm font-medium text-white bg-orange-600 rounded-md hover:bg-orange-700"
                >
                  Clear Metric Preferences
                </button>
                <p className="mt-2 text-sm text-gray-600">
                  Clear all saved metric selections for dashboard tabs
                </p>
              </div>
              <div>
                <button
                  onClick={handleExportData}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                >
                  Export Settings
                </button>
                <p className="mt-2 text-sm text-gray-600">
                  Download your settings and preferences as a JSON file
                </p>
              </div>
            </div>
          </Card>
        </div>
      </MainLayout>
    </AuthGuard>
  );
}
