/**
 * Warehouse Slot List page - Warehouse slotting optimization
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface WarehouseSlot {
  id: number;
  slot_code: string;
  warehouse_id?: number;
  zone: string;
  aisle: string;
  rack: string;
  level: number;
  position: string;
  slot_type: string;
  capacity_m3: number;
  max_weight_kg: number;
  current_occupancy_percent: number;
  temperature_controlled: boolean;
  product_id?: number;
  quantity_stored?: number;
  status: string;
  last_accessed_at?: string;
  created_at: string;
}

export default function WarehouseSlotList() {
  const [slots, setSlots] = useState<WarehouseSlot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSlots();
  }, []);

  const loadSlots = async () => {
    try {
      setLoading(true);
      const data = await api.get('/logistics/warehouse-slots');
      setSlots(data);
    } catch (error) {
      console.error('Failed to load warehouse slots:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      available: 'bg-green-100 text-green-800',
      occupied: 'bg-blue-100 text-blue-800',
      reserved: 'bg-yellow-100 text-yellow-800',
      maintenance: 'bg-red-100 text-red-800',
      blocked: 'bg-gray-100 text-gray-800',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };

  const getOccupancyColor = (occupancy: number) => {
    if (occupancy >= 90) return 'text-red-600';
    if (occupancy >= 70) return 'text-yellow-600';
    if (occupancy >= 40) return 'text-blue-600';
    return 'text-green-600';
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Warehouse Slotting</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Slot Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Capacity (m³)</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Occupancy</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {slots.map((slot) => (
              <tr key={slot.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <span className="font-mono text-sm font-medium text-gray-900">{slot.slot_code}</span>
                    {slot.temperature_controlled && (
                      <span className="ml-2 text-blue-600" title="Temperature Controlled">❄️</span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{slot.zone} / {slot.aisle}</div>
                  <div className="text-xs text-gray-500">Rack {slot.rack}, L{slot.level}, Pos {slot.position}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap capitalize text-gray-600">
                  {slot.slot_type.replace('_', ' ')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-gray-600">
                  {slot.capacity_m3.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <span className={`font-medium ${getOccupancyColor(slot.current_occupancy_percent)}`}>
                    {slot.current_occupancy_percent.toFixed(0)}%
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(slot.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/logistics/warehouse-slots/${slot.id}`} className="text-blue-600 hover:text-blue-900">
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
