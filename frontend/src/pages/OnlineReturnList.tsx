/**
 * Online Return List page - E-commerce returns booking
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface OnlineReturn {
  id: number;
  return_number: string;
  order_id: number;
  customer_id: number;
  return_reason: string;
  return_type: string;
  quantity: number;
  refund_amount: number;
  refund_method?: string;
  status: string;
  requested_at: string;
  approved_at?: string;
  refunded_at?: string;
  created_at: string;
}

export default function OnlineReturnList() {
  const [returns, setReturns] = useState<OnlineReturn[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReturns();
  }, []);

  const loadReturns = async () => {
    try {
      setLoading(true);
      const data = await api.get('/commerce/returns');
      setReturns(data);
    } catch (error) {
      console.error('Failed to load online returns:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      requested: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      picked_up: 'bg-blue-100 text-blue-800',
      refunded: 'bg-green-100 text-green-800',
      completed: 'bg-gray-100 text-gray-800',
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
        <h1 className="text-3xl font-bold">Online Returns</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Return #</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Quantity</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Refund Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {returns.map((returnItem) => (
              <tr key={returnItem.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="font-mono text-sm font-medium text-gray-900">{returnItem.return_number}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  #{returnItem.order_id}
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900 truncate max-w-xs">{returnItem.return_reason}</div>
                  <div className="text-xs text-gray-500 capitalize">{returnItem.return_type.replace('_', ' ')}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-gray-600">
                  {returnItem.quantity}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <div className="font-medium text-gray-900">${returnItem.refund_amount.toLocaleString()}</div>
                  {returnItem.refund_method && (
                    <div className="text-xs text-gray-500 capitalize">{returnItem.refund_method}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(returnItem.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/commerce/returns/${returnItem.id}`} className="text-blue-600 hover:text-blue-900">
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
