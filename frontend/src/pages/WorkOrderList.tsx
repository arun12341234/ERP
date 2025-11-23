/**
 * Work Order List page - Manufacturing work orders
 */
import { useState, useEffect } from 'react';
import { api } from '../lib/api';

interface WorkOrder {
  id: number;
  wo_number: string;
  product_id: number;
  quantity_planned: number;
  quantity_produced: number;
  quantity_scrapped: number;
  scheduled_start: string | null;
  scheduled_end: string | null;
  priority: number;
  status: string;
  created_at: string;
}

export default function WorkOrderList() {
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');

  useEffect(() => {
    loadWorkOrders();
  }, [statusFilter]);

  const loadWorkOrders = async () => {
    try {
      setLoading(true);
      const url = statusFilter ? `/work-orders?status=${statusFilter}` : '/work-orders';
      const data = await api.get(url);
      setWorkOrders(data);
    } catch (error) {
      console.error('Failed to load work orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRelease = async (id: number) => {
    try {
      await api.post(`/work-orders/${id}/release`);
      loadWorkOrders();
    } catch (error) {
      console.error('Failed to release work order:', error);
    }
  };

  const handleStart = async (id: number) => {
    try {
      await api.post(`/work-orders/${id}/start`);
      loadWorkOrders();
    } catch (error) {
      console.error('Failed to start work order:', error);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-800',
      released: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      on_hold: 'bg-orange-100 text-orange-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getPriorityColor = (priority: number) => {
    if (priority >= 8) return 'text-red-600 font-bold';
    if (priority >= 5) return 'text-orange-600 font-medium';
    return 'text-gray-600';
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Work Orders</h1>
        <div className="flex gap-4">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="released">Released</option>
            <option value="in_progress">In Progress</option>
            <option value="on_hold">On Hold</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">WO Number</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Planned</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Produced</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Scrapped</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Progress</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {workOrders.map((wo) => {
              const progress = wo.quantity_planned > 0
                ? Math.round((wo.quantity_produced / wo.quantity_planned) * 100)
                : 0;

              return (
                <tr key={wo.id}>
                  <td className="px-6 py-4 whitespace-nowrap font-mono text-sm font-medium">
                    {wo.wo_number}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-center ${getPriorityColor(wo.priority)}`}>
                    {wo.priority}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-gray-600">
                    {wo.quantity_planned}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-gray-600">
                    {wo.quantity_produced}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-gray-600">
                    {wo.quantity_scrapped}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                    <div className="text-xs text-center text-gray-600 mt-1">{progress}%</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(wo.status)}`}>
                      {wo.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center text-sm">
                    {wo.status === 'draft' && (
                      <button
                        onClick={() => handleRelease(wo.id)}
                        className="text-blue-600 hover:text-blue-900 mr-2"
                      >
                        Release
                      </button>
                    )}
                    {wo.status === 'released' && (
                      <button
                        onClick={() => handleStart(wo.id)}
                        className="text-green-600 hover:text-green-900"
                      >
                        Start
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {workOrders.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No work orders found
        </div>
      )}
    </div>
  );
}
