'use client';

import { useState, useEffect } from 'react';
import { AuthGuard } from '@/components/shared/AuthGuard';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card } from '@/components/shared/Card';
import { useAuth } from '@/lib/hooks/useAuth';
import { useMetricPreferences } from '@/lib/hooks/useMetricPreferences';
import { api } from '@/lib/api';

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
  
  // API Keys state
  const [apiKeys, setApiKeys] = useState({
    gemini: '',
    fred: '',
  });
  const [apiKeysStatus, setApiKeysStatus] = useState<any>(null);
  const [showGeminiKey, setShowGeminiKey] = useState(false);
  const [showFredKey, setShowFredKey] = useState(false);
  const [loadingKeys, setLoadingKeys] = useState(false);
  const [savingKey, setSavingKey] = useState<string | null>(null);
  const [validatingKey, setValidatingKey] = useState<string | null>(null);
  const [keyMessage, setKeyMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);

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
  
  // Load API keys status
  useEffect(() => {
    if (user?.uid) {
      loadAPIKeysStatus();
    }
  }, [user]);
  
  const loadAPIKeysStatus = async () => {
    if (!user?.uid) return;
    
    setLoadingKeys(true);
    try {
      const response = await api.getAPIKeysStatus(user.uid);
      setApiKeysStatus(response.data);
    } catch (error) {
      console.error('Failed to load API keys status:', error);
    } finally {
      setLoadingKeys(false);
    }
  };
  
  const handleSaveAPIKey = async (keyType: 'gemini' | 'fred') => {
    if (!user?.uid) return;
    
    const apiKey = keyType === 'gemini' ? apiKeys.gemini : apiKeys.fred;
    if (!apiKey.trim()) {
      setKeyMessage({ type: 'error', text: 'Please enter an API key' });
      return;
    }
    
    setSavingKey(keyType);
    setKeyMessage(null);
    
    try {
      const response = await api.setAPIKey(user.uid, keyType, apiKey);
      setKeyMessage({ 
        type: 'success', 
        text: `${keyType === 'gemini' ? 'Gemini' : 'FRED'} API key saved successfully! Consider validating it.` 
      });
      
      // Clear the input field
      setApiKeys(prev => ({ ...prev, [keyType]: '' }));
      
      // Reload status
      await loadAPIKeysStatus();
      
      // Clear message after 5 seconds
      setTimeout(() => setKeyMessage(null), 5000);
    } catch (error: any) {
      setKeyMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to save API key' 
      });
    } finally {
      setSavingKey(null);
    }
  };
  
  const handleValidateAPIKey = async (keyType: 'gemini' | 'fred') => {
    if (!user?.uid) return;
    
    setValidatingKey(keyType);
    setKeyMessage(null);
    
    try {
      const response = await api.validateAPIKey(user.uid, keyType);
      
      if (response.data.is_valid) {
        setKeyMessage({ 
          type: 'success', 
          text: `${keyType === 'gemini' ? 'Gemini' : 'FRED'} API key is valid! ✓` 
        });
      } else {
        setKeyMessage({ 
          type: 'error', 
          text: `${keyType === 'gemini' ? 'Gemini' : 'FRED'} API key validation failed: ${response.data.error_message}` 
        });
      }
      
      // Reload status
      await loadAPIKeysStatus();
      
      // Clear message after 8 seconds
      setTimeout(() => setKeyMessage(null), 8000);
    } catch (error: any) {
      setKeyMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to validate API key' 
      });
    } finally {
      setValidatingKey(null);
    }
  };
  
  const handleDeleteAPIKey = async (keyType: 'gemini' | 'fred') => {
    if (!user?.uid) return;
    
    if (!confirm(`Are you sure you want to delete your ${keyType === 'gemini' ? 'Gemini' : 'FRED'} API key?`)) {
      return;
    }
    
    setKeyMessage(null);
    
    try {
      await api.deleteAPIKey(user.uid, keyType);
      setKeyMessage({ 
        type: 'success', 
        text: `${keyType === 'gemini' ? 'Gemini' : 'FRED'} API key deleted successfully` 
      });
      
      // Reload status
      await loadAPIKeysStatus();
      
      // Clear message after 5 seconds
      setTimeout(() => setKeyMessage(null), 5000);
    } catch (error: any) {
      setKeyMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to delete API key' 
      });
    }
  };

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

          {/* API Keys (BYOK) */}
          <Card>
            <h2 className="text-xl font-semibold mb-4">API Keys (Bring Your Own Key)</h2>
            <p className="text-sm text-gray-600 mb-4">
              Add your own API keys to use AI features. Your keys are encrypted and stored securely.
              If you don't provide your own key, the application will use the default key (if available).
            </p>
            
            {keyMessage && (
              <div className={`mb-4 p-3 rounded-md ${keyMessage.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'}`}>
                {keyMessage.text}
              </div>
            )}
            
            {loadingKeys ? (
              <div className="text-center py-4">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-sm text-gray-600">Loading API keys status...</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Gemini API Key */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-gray-900">Google Gemini API Key</h3>
                      <p className="text-xs text-gray-500 mt-1">Used for AI chat and financial analysis</p>
                    </div>
                    {apiKeysStatus?.has_gemini_key && (
                      <div className="flex items-center space-x-2">
                        {apiKeysStatus.gemini_key_is_valid === true && (
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">✓ Valid</span>
                        )}
                        {apiKeysStatus.gemini_key_is_valid === false && (
                          <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">✗ Invalid</span>
                        )}
                        {apiKeysStatus.gemini_key_is_valid === null && (
                          <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">Not validated</span>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {apiKeysStatus?.has_gemini_key ? (
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2 text-sm text-gray-700">
                        <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>API key is set</span>
                      </div>
                      {apiKeysStatus.gemini_key_last_validated && (
                        <p className="text-xs text-gray-500">
                          Last validated: {new Date(apiKeysStatus.gemini_key_last_validated).toLocaleString()}
                        </p>
                      )}
                      <div className="flex space-x-2 mt-3">
                        <button
                          onClick={() => handleValidateAPIKey('gemini')}
                          disabled={validatingKey === 'gemini'}
                          className="px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {validatingKey === 'gemini' ? 'Validating...' : 'Validate Key'}
                        </button>
                        <button
                          onClick={() => handleDeleteAPIKey('gemini')}
                          className="px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100"
                        >
                          Delete Key
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className="relative">
                        <input
                          type={showGeminiKey ? 'text' : 'password'}
                          value={apiKeys.gemini}
                          onChange={(e) => setApiKeys(prev => ({ ...prev, gemini: e.target.value }))}
                          placeholder="Enter your Gemini API key"
                          className="w-full rounded-md border border-gray-300 px-3 py-2 pr-10 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                        />
                        <button
                          type="button"
                          onClick={() => setShowGeminiKey(!showGeminiKey)}
                          className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                        >
                          {showGeminiKey ? '🙈' : '👁️'}
                        </button>
                      </div>
                      <button
                        onClick={() => handleSaveAPIKey('gemini')}
                        disabled={savingKey === 'gemini' || !apiKeys.gemini.trim()}
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {savingKey === 'gemini' ? 'Saving...' : 'Save Gemini Key'}
                      </button>
                      <p className="text-xs text-gray-500 mt-2">
                        Get your API key from <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google AI Studio</a>
                      </p>
                    </div>
                  )}
                </div>
                
                {/* FRED API Key */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-gray-900">FRED API Key</h3>
                      <p className="text-xs text-gray-500 mt-1">Used for economic data (Federal Reserve)</p>
                    </div>
                    {apiKeysStatus?.has_fred_key && (
                      <div className="flex items-center space-x-2">
                        {apiKeysStatus.fred_key_is_valid === true && (
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">✓ Valid</span>
                        )}
                        {apiKeysStatus.fred_key_is_valid === false && (
                          <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">✗ Invalid</span>
                        )}
                        {apiKeysStatus.fred_key_is_valid === null && (
                          <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">Not validated</span>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {apiKeysStatus?.has_fred_key ? (
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2 text-sm text-gray-700">
                        <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>API key is set</span>
                      </div>
                      {apiKeysStatus.fred_key_last_validated && (
                        <p className="text-xs text-gray-500">
                          Last validated: {new Date(apiKeysStatus.fred_key_last_validated).toLocaleString()}
                        </p>
                      )}
                      <div className="flex space-x-2 mt-3">
                        <button
                          onClick={() => handleValidateAPIKey('fred')}
                          disabled={validatingKey === 'fred'}
                          className="px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {validatingKey === 'fred' ? 'Validating...' : 'Validate Key'}
                        </button>
                        <button
                          onClick={() => handleDeleteAPIKey('fred')}
                          className="px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100"
                        >
                          Delete Key
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className="relative">
                        <input
                          type={showFredKey ? 'text' : 'password'}
                          value={apiKeys.fred}
                          onChange={(e) => setApiKeys(prev => ({ ...prev, fred: e.target.value }))}
                          placeholder="Enter your FRED API key"
                          className="w-full rounded-md border border-gray-300 px-3 py-2 pr-10 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                        />
                        <button
                          type="button"
                          onClick={() => setShowFredKey(!showFredKey)}
                          className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                        >
                          {showFredKey ? '🙈' : '👁️'}
                        </button>
                      </div>
                      <button
                        onClick={() => handleSaveAPIKey('fred')}
                        disabled={savingKey === 'fred' || !apiKeys.fred.trim()}
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {savingKey === 'fred' ? 'Saving...' : 'Save FRED Key'}
                      </button>
                      <p className="text-xs text-gray-500 mt-2">
                        Get your API key from <a href="https://fred.stlouisfed.org/docs/api/api_key.html" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">FRED</a>
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
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
