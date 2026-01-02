'use client';

import { useState, useEffect } from 'react';
import { IAPUser } from '@/lib/utils/iapAuth';

interface UserProfileProps {
  compact?: boolean;
  showRawData?: boolean;
}

export function UserProfile({ compact = false, showRawData = false }: UserProfileProps) {
  const [user, setUser] = useState<IAPUser | null>(null);
  const [headers, setHeaders] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUser();
  }, []);

  const fetchUser = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/auth/user');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch user: ${response.status}`);
      }

      const data = await response.json();
      setUser(data.user);
      setHeaders(data.headers);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch user:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2">
        <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-blue-600"></div>
        <span className="text-sm text-gray-600">Loading user...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-sm text-red-600">
        ⚠️ {error}
      </div>
    );
  }

  if (!user) {
    return (
      <div className="text-sm text-gray-600">
        No user information available
      </div>
    );
  }

  // Compact view (for header/navbar)
  if (compact) {
    return (
      <div className="flex items-center gap-3">
        {user.picture && (
          <img
            src={user.picture}
            alt={user.name || user.email}
            className="w-8 h-8 rounded-full"
          />
        )}
        <div className="flex flex-col">
          <span className="text-sm font-medium text-gray-900">
            {user.name || user.email}
          </span>
          <span className="text-xs text-gray-500">
            {user.authMethod === 'iap' ? '🔐 IAP' : '🔧 Dev Mode'}
          </span>
        </div>
      </div>
    );
  }

  // Full view (for dashboard/settings)
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">User Information</h3>
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium ${
            user.authMethod === 'iap'
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}
        >
          {user.authMethod === 'iap' ? '🔐 IAP Authenticated' : '🔧 Development Mode'}
        </span>
      </div>

      <div className="space-y-4">
        {/* User Avatar */}
        {user.picture && (
          <div className="flex justify-center">
            <img
              src={user.picture}
              alt={user.name || user.email}
              className="w-20 h-20 rounded-full border-2 border-gray-200"
            />
          </div>
        )}

        {/* User Details */}
        <div className="space-y-3">
          {user.name && (
            <div>
              <label className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </label>
              <p className="mt-1 text-sm text-gray-900">{user.name}</p>
            </div>
          )}

          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wider">
              Email
            </label>
            <p className="mt-1 text-sm text-gray-900">{user.email}</p>
          </div>

          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wider">
              User ID
            </label>
            <p className="mt-1 text-sm font-mono text-gray-900 bg-gray-50 px-2 py-1 rounded">
              {user.userId}
            </p>
          </div>

          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wider">
              Authentication Method
            </label>
            <p className="mt-1 text-sm text-gray-900">{user.authMethod}</p>
          </div>
        </div>

        {/* IAP Headers Debug */}
        {showRawData && Object.keys(headers).length > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-900 mb-3">IAP Headers</h4>
            <div className="bg-gray-50 rounded p-3 text-xs font-mono overflow-x-auto">
              <pre>{JSON.stringify(headers, null, 2)}</pre>
            </div>
          </div>
        )}

        {/* Raw IAP Data */}
        {showRawData && user.raw && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-900 mb-3">JWT Payload</h4>
            <div className="bg-gray-50 rounded p-3 text-xs font-mono overflow-x-auto">
              <pre>{JSON.stringify(user.raw, null, 2)}</pre>
            </div>
          </div>
        )}

        {/* Refresh Button */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <button
            onClick={fetchUser}
            className="w-full px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            🔄 Refresh User Info
          </button>
        </div>
      </div>
    </div>
  );
}

