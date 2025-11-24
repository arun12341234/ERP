import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface Alert {
  id: number;
  alert_id: string;
  alert_type: string;
  severity: string;
  title: string;
  message: string;
  source_system: string | null;
  source_component: string | null;
  status: string;
  assigned_to_id: number | null;
  acknowledged_at: string | null;
  resolved_at: string | null;
  is_escalated: number;
  escalation_level: number;
  occurrence_count: number;
  first_occurred_at: string;
  last_occurred_at: string;
  priority: number;
  created_at: string;
}

const AlertList: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    fetchAlerts();
  }, [severityFilter, statusFilter]);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      let url = `${apiUrl}/api/v1/governance/alerts`;

      const params = new URLSearchParams();
      if (severityFilter !== 'all') params.append('severity', severityFilter);
      if (statusFilter !== 'all') params.append('status', statusFilter);

      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch alerts');
      }
      const data = await response.json();
      setAlerts(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      info: 'bg-blue-100 text-blue-800',
      warning: 'bg-yellow-100 text-yellow-800',
      error: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800',
    };
    return colors[severity] || 'bg-gray-100 text-gray-800';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      new: 'bg-purple-100 text-purple-800',
      acknowledged: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      resolved: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'info':
        return 'ℹ';
      case 'warning':
        return '⚠';
      case 'error':
        return '⚠';
      case 'critical':
        return '⚠';
      default:
        return '';
    }
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const handleAcknowledge = async (alertId: string) => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/governance/alerts/${alertId}/acknowledge`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to acknowledge alert');
      }

      fetchAlerts();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to acknowledge alert');
    }
  };

  const handleResolve = async (alertId: string) => {
    const notes = prompt('Enter resolution notes:');
    if (!notes) return;

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/governance/alerts/${alertId}/resolve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ resolution_notes: notes }),
      });

      if (!response.ok) {
        throw new Error('Failed to resolve alert');
      }

      fetchAlerts();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to resolve alert');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">Loading alerts...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alert Management</h1>
          <p className="mt-2 text-sm text-gray-700">
            Monitor and respond to system alerts
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Link
            to="/governance/alerts/new"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Create Alert
          </Link>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="mb-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="severity-filter" className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Severity
              </label>
              <select
                id="severity-filter"
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              >
                <option value="all">All Severities</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div>
              <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Status
              </label>
              <select
                id="status-filter"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              >
                <option value="all">All Statuses</option>
                <option value="new">New</option>
                <option value="acknowledged">Acknowledged</option>
                <option value="in_progress">In Progress</option>
                <option value="resolved">Resolved</option>
                <option value="closed">Closed</option>
              </select>
            </div>
          </div>

          <div className="space-y-4">
            {alerts.length === 0 ? (
              <div className="text-center py-8 text-sm text-gray-500">
                No alerts found
              </div>
            ) : (
              alerts.map((alert) => (
                <div key={alert.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getSeverityColor(alert.severity)}`}>
                          {getSeverityIcon(alert.severity)} {alert.severity.toUpperCase()}
                        </span>
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(alert.status)}`}>
                          {alert.status.toUpperCase()}
                        </span>
                        <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                          {alert.alert_type.toUpperCase()}
                        </span>
                        {alert.is_escalated === 1 && (
                          <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                            ESCALATED L{alert.escalation_level}
                          </span>
                        )}
                        {alert.occurrence_count > 1 && (
                          <span className="text-xs text-gray-500">
                            ({alert.occurrence_count} occurrences)
                          </span>
                        )}
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 mb-1">{alert.title}</h3>
                      <p className="text-sm text-gray-600 mb-2">{alert.message}</p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        {alert.source_system && (
                          <span>System: {alert.source_system}</span>
                        )}
                        {alert.source_component && (
                          <span>Component: {alert.source_component}</span>
                        )}
                        <span>Priority: {alert.priority}</span>
                        <span>First: {formatDateTime(alert.first_occurred_at)}</span>
                      </div>
                    </div>
                    <div className="ml-4 flex flex-col space-y-2">
                      {alert.status === 'new' && (
                        <button
                          onClick={() => handleAcknowledge(alert.alert_id)}
                          className="px-3 py-1 text-xs font-medium text-blue-600 hover:text-blue-800 border border-blue-300 rounded hover:bg-blue-50"
                        >
                          Acknowledge
                        </button>
                      )}
                      {(alert.status === 'acknowledged' || alert.status === 'in_progress') && (
                        <button
                          onClick={() => handleResolve(alert.alert_id)}
                          className="px-3 py-1 text-xs font-medium text-green-600 hover:text-green-800 border border-green-300 rounded hover:bg-green-50"
                        >
                          Resolve
                        </button>
                      )}
                      <Link
                        to={`/governance/alerts/${alert.id}`}
                        className="px-3 py-1 text-xs font-medium text-indigo-600 hover:text-indigo-800 border border-indigo-300 rounded hover:bg-indigo-50 text-center"
                      >
                        View Details
                      </Link>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertList;
