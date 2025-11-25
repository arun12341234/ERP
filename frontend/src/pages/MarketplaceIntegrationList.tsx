/**
 * Marketplace Integration List page - Multi-marketplace sync management
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface MarketplaceIntegration {
  id: number;
  integration_name: string;
  marketplace_name: string;
  marketplace_type: string;
  api_endpoint?: string;
  sync_frequency_minutes: number;
  last_sync_at?: string;
  next_sync_at?: string;
  sync_status: string;
  is_active: boolean;
  total_products_synced: number;
  failed_sync_count: number;
  created_at: string;
}

export default function MarketplaceIntegrationList() {
  const [integrations, setIntegrations] = useState<MarketplaceIntegration[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      setLoading(true);
      const data = await api.get('/commerce/marketplace');
      setIntegrations(data);
    } catch (error) {
      console.error('Failed to load marketplace integrations:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSyncStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      success: 'bg-green-100 text-green-800',
      in_progress: 'bg-blue-100 text-blue-800',
      failed: 'bg-red-100 text-red-800',
      pending: 'bg-yellow-100 text-yellow-800',
      never_synced: 'bg-gray-100 text-gray-800',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status.replace('_', ' ')}
      </span>
    );
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Marketplace Integrations</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Integration</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Marketplace</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Products Synced</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sync Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Sync</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Active</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {integrations.map((integration) => (
              <tr key={integration.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="font-medium text-gray-900">{integration.integration_name}</div>
                  <div className="text-xs text-gray-500">Sync every {integration.sync_frequency_minutes} min</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{integration.marketplace_name}</div>
                  <div className="text-xs text-gray-500 capitalize">{integration.marketplace_type}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <div className="font-medium text-gray-900">{integration.total_products_synced.toLocaleString()}</div>
                  {integration.failed_sync_count > 0 && (
                    <div className="text-xs text-red-600">{integration.failed_sync_count} failures</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getSyncStatusBadge(integration.sync_status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {integration.last_sync_at ? (
                    <div>
                      <div className="text-sm text-gray-600">{new Date(integration.last_sync_at).toLocaleString()}</div>
                      {integration.next_sync_at && (
                        <div className="text-xs text-gray-500">Next: {new Date(integration.next_sync_at).toLocaleString()}</div>
                      )}
                    </div>
                  ) : (
                    <span className="text-sm text-gray-400">Never synced</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${integration.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {integration.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/commerce/marketplace/${integration.id}`} className="text-blue-600 hover:text-blue-900">
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
