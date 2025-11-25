/**
 * Carrier Performance List page - Carrier performance review
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface CarrierPerformance {
  id: number;
  carrier_id: number;
  carrier_name: string;
  evaluation_period_start: string;
  evaluation_period_end: string;
  total_shipments: number;
  on_time_deliveries: number;
  late_deliveries: number;
  damaged_shipments: number;
  lost_shipments: number;
  on_time_rate: number;
  damage_rate: number;
  average_transit_time_days: number;
  cost_per_shipment: number;
  customer_satisfaction_score: number;
  overall_rating: number;
  status: string;
  created_at: string;
}

export default function CarrierPerformanceList() {
  const [performances, setPerformances] = useState<CarrierPerformance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPerformances();
  }, []);

  const loadPerformances = async () => {
    try {
      setLoading(true);
      const data = await api.get('/logistics/carrier-performance');
      setPerformances(data);
    } catch (error) {
      console.error('Failed to load carrier performance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (rating: number) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <span key={i} className={i <= rating ? 'text-yellow-400' : 'text-gray-300'}>
          ★
        </span>
      );
    }
    return <div className="flex">{stars}</div>;
  };

  const getPerformanceColor = (rate: number) => {
    if (rate >= 95) return 'text-green-600';
    if (rate >= 85) return 'text-yellow-600';
    if (rate >= 75) return 'text-orange-600';
    return 'text-red-600';
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Carrier Performance</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Carrier</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Shipments</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">On-Time Rate</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Damage Rate</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Rating</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {performances.map((perf) => (
              <tr key={perf.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="font-medium text-gray-900">{perf.carrier_name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {new Date(perf.evaluation_period_start).toLocaleDateString()} - {new Date(perf.evaluation_period_end).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-gray-600">
                  {perf.total_shipments}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <span className={`font-medium ${getPerformanceColor(perf.on_time_rate)}`}>
                    {perf.on_time_rate.toFixed(1)}%
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <span className={`font-medium ${perf.damage_rate > 5 ? 'text-red-600' : 'text-green-600'}`}>
                    {perf.damage_rate.toFixed(1)}%
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {renderStars(perf.overall_rating)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/logistics/carrier-performance/${perf.id}`} className="text-blue-600 hover:text-blue-900">
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
