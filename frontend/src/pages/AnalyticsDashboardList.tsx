/**
 * Analytics Dashboard List page - Business analytics and KPI tracking
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface AnalyticsDashboard {
  id: number;
  dashboard_id: string;
  dashboard_name: string;
  dashboard_type: string;
  department: string;
  owner_id: number;
  is_public: boolean;
  refresh_frequency_minutes: number;
  last_refreshed_at?: string;
  created_at: string;
}

export default function AnalyticsDashboardList() {
  const [dashboards, setDashboards] = useState<AnalyticsDashboard[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboards();
  }, []);

  const loadDashboards = async () => {
    try {
      setLoading(true);
      const data = await api.get('/governance/analytics');
      setDashboards(data);
    } catch (error) {
      console.error('Failed to load analytics dashboards:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Analytics Dashboards</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dashboard</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Visibility</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Refreshed</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {dashboards.map((dashboard) => (
              <tr key={dashboard.id}>
                <td className="px-6 py-4">
                  <div className="font-medium text-gray-900">{dashboard.dashboard_name}</div>
                  <div className="text-xs text-gray-500">{dashboard.dashboard_id}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap capitalize text-sm text-gray-600">
                  {dashboard.dashboard_type}
                </td>
                <td className="px-6 py-4 whitespace-nowrap capitalize text-sm text-gray-600">
                  {dashboard.department}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${dashboard.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {dashboard.is_public ? 'Public' : 'Private'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {dashboard.last_refreshed_at ? new Date(dashboard.last_refreshed_at).toLocaleString() : 'Never'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/governance/analytics/${dashboard.id}`} className="text-blue-600 hover:text-blue-900">
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
