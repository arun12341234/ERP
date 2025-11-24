import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface DashboardStats {
  total_shipments: number;
  in_transit: number;
  delivered_today: number;
  pending_returns: number;
  active_alerts: number;
}

const LogisticsDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    total_shipments: 0,
    in_transit: 0,
    delivered_today: 0,
    pending_returns: 0,
    active_alerts: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

      // Fetch various statistics
      const shipmentsResponse = await fetch(`${apiUrl}/api/v1/logistics/shipments`);
      const shipments = await shipmentsResponse.json();

      const inTransit = shipments.filter((s: any) => s.status === 'in_transit' || s.status === 'out_for_delivery').length;
      const deliveredToday = shipments.filter((s: any) => {
        const today = new Date().toDateString();
        return s.actual_delivery_date && new Date(s.actual_delivery_date).toDateString() === today;
      }).length;

      const returnsResponse = await fetch(`${apiUrl}/api/v1/logistics/return-requests?status=submitted`);
      const returns = await returnsResponse.json();

      const alertsResponse = await fetch(`${apiUrl}/api/v1/logistics/cold-chain/alerts`);
      const alerts = await alertsResponse.json();

      setStats({
        total_shipments: shipments.length,
        in_transit: inTransit,
        delivered_today: deliveredToday,
        pending_returns: returns.length,
        active_alerts: alerts.length,
      });
    } catch (err) {
      console.error('Failed to fetch dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total Shipments',
      value: stats.total_shipments,
      icon: '📦',
      color: 'bg-blue-500',
      link: '/logistics/shipments',
    },
    {
      title: 'In Transit',
      value: stats.in_transit,
      icon: '🚚',
      color: 'bg-purple-500',
      link: '/logistics/shipments?status=in_transit',
    },
    {
      title: 'Delivered Today',
      value: stats.delivered_today,
      icon: '✅',
      color: 'bg-green-500',
      link: '/logistics/shipments?status=delivered',
    },
    {
      title: 'Pending Returns',
      value: stats.pending_returns,
      icon: '🔄',
      color: 'bg-orange-500',
      link: '/logistics/returns',
    },
    {
      title: 'Active Alerts',
      value: stats.active_alerts,
      icon: '⚠️',
      color: 'bg-red-500',
      link: '/logistics/cold-chain/alerts',
    },
  ];

  const quickActions = [
    {
      title: 'Create Logistics Request',
      description: 'Initiate a new shipment request',
      icon: '📋',
      link: '/logistics/requests/new',
      color: 'bg-indigo-100 text-indigo-600',
    },
    {
      title: 'Track Shipment',
      description: 'Real-time tracking and monitoring',
      icon: '🗺️',
      link: '/logistics/tracking',
      color: 'bg-blue-100 text-blue-600',
    },
    {
      title: 'Manage Returns',
      description: 'Process return requests',
      icon: '↩️',
      link: '/logistics/returns',
      color: 'bg-orange-100 text-orange-600',
    },
    {
      title: 'Customs Documents',
      description: 'Import/Export documentation',
      icon: '📄',
      link: '/logistics/customs',
      color: 'bg-purple-100 text-purple-600',
    },
    {
      title: 'Carrier Performance',
      description: 'Review carrier metrics',
      icon: '📊',
      link: '/logistics/carrier-performance',
      color: 'bg-green-100 text-green-600',
    },
    {
      title: 'Warehouse Slotting',
      description: 'Manage warehouse slots',
      icon: '🏭',
      link: '/logistics/warehouse-slots',
      color: 'bg-yellow-100 text-yellow-600',
    },
  ];

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Supply Chain & Logistics</h1>
        <p className="mt-2 text-sm text-gray-700">
          Comprehensive logistics management and tracking
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        {statCards.map((card) => (
          <Link
            key={card.title}
            to={card.link}
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">{card.icon}</span>
              <div className={`${card.color} rounded-full w-3 h-3`}></div>
            </div>
            <div className="text-3xl font-bold text-gray-900">{card.value}</div>
            <div className="text-sm text-gray-600 mt-1">{card.title}</div>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickActions.map((action) => (
            <Link
              key={action.title}
              to={action.link}
              className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
            >
              <div className={`${action.color} inline-flex items-center justify-center w-12 h-12 rounded-lg text-2xl mb-4`}>
                {action.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{action.title}</h3>
              <p className="text-sm text-gray-600">{action.description}</p>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Logistics Modules</h2>
        </div>
        <div className="px-6 py-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">📦 Process 76: Logistics Request</h3>
              <p className="text-sm text-gray-600 mb-2">Create and manage shipment requests</p>
              <Link to="/logistics/requests" className="text-indigo-600 hover:text-indigo-800 text-sm">
                View Requests →
              </Link>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">📊 Process 77: Loading Plan</h3>
              <p className="text-sm text-gray-600 mb-2">Optimize loading and capacity utilization</p>
              <Link to="/logistics/loading-plans" className="text-indigo-600 hover:text-indigo-800 text-sm">
                View Plans →
              </Link>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">🚚 Process 78: Shipment Dispatch</h3>
              <p className="text-sm text-gray-600 mb-2">Dispatch and manage shipments</p>
              <Link to="/logistics/shipments" className="text-indigo-600 hover:text-indigo-800 text-sm">
                View Shipments →
              </Link>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">🗺️ Process 79: Real-Time Tracking</h3>
              <p className="text-sm text-gray-600 mb-2">Track shipments with GPS updates</p>
              <Link to="/logistics/tracking" className="text-indigo-600 hover:text-indigo-800 text-sm">
                Track Shipments →
              </Link>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">✅ Process 80: Delivery Confirmation</h3>
              <p className="text-sm text-gray-600 mb-2">Record proof of delivery</p>
              <Link to="/logistics/delivery-confirmations" className="text-indigo-600 hover:text-indigo-800 text-sm">
                View Confirmations →
              </Link>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">💰 Process 81: Freight Invoice</h3>
              <p className="text-sm text-gray-600 mb-2">Reconcile freight invoices</p>
              <Link to="/logistics/freight-invoices" className="text-indigo-600 hover:text-indigo-800 text-sm">
                View Invoices →
              </Link>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">📈 Process 82: Demand Forecast</h3>
              <p className="text-sm text-gray-600 mb-2">Forecast demand with analytics</p>
              <Link to="/logistics/demand-forecasts" className="text-indigo-600 hover:text-indigo-800 text-sm">
                View Forecasts →
              </Link>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">🛣️ Process 83: Route Optimization</h3>
              <p className="text-sm text-gray-600 mb-2">Optimize delivery routes</p>
              <Link to="/logistics/route-optimizations" className="text-indigo-600 hover:text-indigo-800 text-sm">
                View Routes →
              </Link>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">⭐ Process 84: Carrier Performance</h3>
              <p className="text-sm text-gray-600 mb-2">Review carrier performance metrics</p>
              <Link to="/logistics/carrier-performance" className="text-indigo-600 hover:text-indigo-800 text-sm">
                View Performance →
              </Link>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">🏭 Process 85: Warehouse Slotting</h3>
              <p className="text-sm text-gray-600 mb-2">Manage warehouse slot assignments</p>
              <Link to="/logistics/warehouse-slots" className="text-indigo-600 hover:text-indigo-800 text-sm">
                View Slots →
              </Link>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">📦 Process 86: Packaging Request</h3>
              <p className="text-sm text-gray-600 mb-2">Manage packaging requests</p>
              <Link to="/logistics/packaging-requests" className="text-indigo-600 hover:text-indigo-800 text-sm">
                View Requests →
              </Link>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">↩️ Process 87: Returns & Reverse Logistics</h3>
              <p className="text-sm text-gray-600 mb-2">Handle product returns</p>
              <Link to="/logistics/return-requests" className="text-indigo-600 hover:text-indigo-800 text-sm">
                View Returns →
              </Link>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">📄 Process 88: Customs Documents</h3>
              <p className="text-sm text-gray-600 mb-2">Import/Export documentation</p>
              <Link to="/logistics/customs-documents" className="text-indigo-600 hover:text-indigo-800 text-sm">
                View Documents →
              </Link>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">🔗 Process 89: 3PL Integration</h3>
              <p className="text-sm text-gray-600 mb-2">Integrate with 3PL providers</p>
              <Link to="/logistics/3pl-providers" className="text-indigo-600 hover:text-indigo-800 text-sm">
                View Providers →
              </Link>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">❄️ Process 90: Cold Chain Monitoring</h3>
              <p className="text-sm text-gray-600 mb-2">Monitor temperature-sensitive shipments</p>
              <Link to="/logistics/cold-chain" className="text-indigo-600 hover:text-indigo-800 text-sm">
                View Monitoring →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogisticsDashboard;
