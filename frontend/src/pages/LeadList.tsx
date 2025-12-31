/**
 * Lead List page - CRM lead management
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface Lead {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  company: string;
  status: string;
  score: number;
  source: string;
  created_at: string;
}

export default function LeadList() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    loadLeads();
  }, [statusFilter]);

  const loadLeads = async () => {
    try {
      setLoading(true);
      const url = statusFilter ? `/leads?status=${statusFilter}` : '/leads';
      const data = await api.get(url);
      setLeads(data);
    } catch (error) {
      console.error('Failed to load leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQualify = async (id: number, score: number) => {
    try {
      await api.post(`/leads/${id}/qualify?score=${score}`);
      loadLeads();
    } catch (error) {
      alert('Failed to qualify lead');
    }
  };

  const handleConvert = async (id: number) => {
    if (!confirm('Convert this qualified lead to a customer?')) return;

    try {
      await api.post(`/leads/${id}/convert`);
      loadLeads();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to convert lead');
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      new: 'bg-blue-100 text-blue-800',
      contacted: 'bg-yellow-100 text-yellow-800',
      qualified: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      converted: 'bg-purple-100 text-purple-800',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Leads</h1>
        <div className="flex space-x-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="new">New</option>
            <option value="contacted">Contacted</option>
            <option value="qualified">Qualified</option>
            <option value="rejected">Rejected</option>
            <option value="converted">Converted</option>
          </select>
          <Link
            to="/leads/new"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            + New Lead
          </Link>
        </div>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {leads.map((lead) => (
              <tr key={lead.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="font-medium text-gray-900">
                    {lead.first_name} {lead.last_name}
                  </div>
                  <div className="text-sm text-gray-500">{lead.source}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                  {lead.company || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                  {lead.email}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(lead.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{lead.score}/100</div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${lead.score}%` }}
                    />
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  <Link
                    to={`/leads/${lead.id}/edit`}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Edit
                  </Link>
                  {lead.status === 'new' && (
                    <button
                      onClick={() => handleQualify(lead.id, 75)}
                      className="text-green-600 hover:text-green-900"
                    >
                      Qualify
                    </button>
                  )}
                  {lead.status === 'qualified' && (
                    <button
                      onClick={() => handleConvert(lead.id)}
                      className="text-purple-600 hover:text-purple-900"
                    >
                      Convert
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
