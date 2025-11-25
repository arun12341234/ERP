/**
 * Cold Chain Monitoring List page - Temperature-sensitive shipment monitoring
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface ColdChainMonitoring {
  id: number;
  monitoring_id: string;
  shipment_id?: number;
  product_name: string;
  temperature_celsius: number;
  humidity_percent: number;
  temperature_min: number;
  temperature_max: number;
  location: string;
  sensor_id: string;
  temperature_status: string;
  alert_triggered: boolean;
  alert_message?: string;
  recorded_at: string;
  created_at: string;
}

export default function ColdChainMonitoringList() {
  const [monitoring, setMonitoring] = useState<ColdChainMonitoring[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMonitoring();
  }, []);

  const loadMonitoring = async () => {
    try {
      setLoading(true);
      const data = await api.get('/logistics/cold-chain');
      setMonitoring(data);
    } catch (error) {
      console.error('Failed to load cold chain monitoring data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTemperatureStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      normal: 'bg-green-100 text-green-800',
      warning: 'bg-yellow-100 text-yellow-800',
      critical: 'bg-red-100 text-red-800',
      below_range: 'bg-blue-100 text-blue-800',
      above_range: 'bg-orange-100 text-orange-800',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status.replace('_', ' ')}
      </span>
    );
  };

  const getTemperatureColor = (temp: number, min: number, max: number) => {
    if (temp < min) return 'text-blue-600';
    if (temp > max) return 'text-red-600';
    if (temp >= max - 2 || temp <= min + 2) return 'text-yellow-600';
    return 'text-green-600';
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Cold Chain Monitoring</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Monitoring ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Temperature</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Humidity</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Recorded</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {monitoring.map((record) => (
              <tr key={record.id} className={record.alert_triggered ? 'bg-red-50' : ''}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <span className="font-mono text-xs font-medium text-gray-900">{record.monitoring_id}</span>
                    {record.alert_triggered && (
                      <span className="ml-2 text-red-600" title="Alert">🚨</span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900">{record.product_name}</div>
                  <div className="text-xs text-gray-500">Sensor: {record.sensor_id}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-600">{record.location}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <div className={`font-medium ${getTemperatureColor(record.temperature_celsius, record.temperature_min, record.temperature_max)}`}>
                    {record.temperature_celsius.toFixed(1)}°C
                  </div>
                  <div className="text-xs text-gray-500">
                    Range: {record.temperature_min}°C - {record.temperature_max}°C
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-gray-600">
                  {record.humidity_percent.toFixed(1)}%
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getTemperatureStatusBadge(record.temperature_status)}
                  {record.alert_message && (
                    <div className="text-xs text-red-600 mt-1">{record.alert_message}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {new Date(record.recorded_at).toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/logistics/cold-chain/${record.id}`} className="text-blue-600 hover:text-blue-900">
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
