/**
 * Shipment Tracking List page - Real-time shipment tracking
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface ShipmentTracking {
  id: number;
  shipment_id: number;
  tracking_number: string;
  location: string;
  status: string;
  event_type: string;
  event_description?: string;
  latitude?: number;
  longitude?: number;
  timestamp: string;
  created_at: string;
}

export default function ShipmentTrackingList() {
  const [trackings, setTrackings] = useState<ShipmentTracking[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrackings();
  }, []);

  const loadTrackings = async () => {
    try {
      setLoading(true);
      const data = await api.get('/logistics/tracking');
      setTrackings(data);
    } catch (error) {
      console.error('Failed to load tracking data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      picked_up: 'bg-blue-100 text-blue-800',
      in_transit: 'bg-purple-100 text-purple-800',
      out_for_delivery: 'bg-yellow-100 text-yellow-800',
      delivered: 'bg-green-100 text-green-800',
      delayed: 'bg-red-100 text-red-800',
      exception: 'bg-red-100 text-red-800',
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
        <h1 className="text-3xl font-bold">Shipment Tracking</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tracking #</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Event</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {trackings.map((tracking) => (
              <tr key={tracking.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="font-mono text-sm font-medium text-gray-900">{tracking.tracking_number}</span>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900">{tracking.location}</div>
                  {tracking.latitude && tracking.longitude && (
                    <div className="text-xs text-gray-500">
                      {tracking.latitude.toFixed(4)}, {tracking.longitude.toFixed(4)}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4">
                  <div className="font-medium text-gray-900 capitalize">{tracking.event_type.replace('_', ' ')}</div>
                  {tracking.event_description && (
                    <div className="text-sm text-gray-500 truncate max-w-xs">{tracking.event_description}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(tracking.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                  {new Date(tracking.timestamp).toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/logistics/tracking/${tracking.id}`} className="text-blue-600 hover:text-blue-900">
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
