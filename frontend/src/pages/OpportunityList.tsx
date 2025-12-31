/**
 * Opportunity List - Sales Pipeline Management
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface Opportunity {
  id: number;
  name: string;
  description?: string;
  stage: string;
  probability: number;
  amount: number;
  expected_close_date?: string;
  score: number;
  customer_id?: number;
  lead_id?: number;
  assigned_to_id: number;
  created_at: string;
}

export default function OpportunityList() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'table' | 'pipeline'>('pipeline');

  useEffect(() => {
    loadOpportunities();
  }, []);

  const loadOpportunities = async () => {
    try {
      setLoading(true);
      const data = await api.get('/opportunities');
      setOpportunities(data);
    } catch (error) {
      console.error('Failed to load opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStageBadge = (stage: string) => {
    const colors: Record<string, string> = {
      prospecting: 'bg-blue-100 text-blue-800',
      qualification: 'bg-yellow-100 text-yellow-800',
      proposal: 'bg-purple-100 text-purple-800',
      negotiation: 'bg-orange-100 text-orange-800',
      closed_won: 'bg-green-100 text-green-800',
      closed_lost: 'bg-red-100 text-red-800',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[stage]}`}>
        {stage.replace('_', ' ')}
      </span>
    );
  };

  const groupByStage = () => {
    const stages = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost'];
    return stages.map(stage => ({
      stage,
      opportunities: opportunities.filter(opp => opp.stage === stage),
      totalValue: opportunities
        .filter(opp => opp.stage === stage)
        .reduce((sum, opp) => sum + opp.amount, 0),
    }));
  };

  if (loading) return <div className="p-8">Loading...</div>;

  const stageGroups = groupByStage();
  const totalPipelineValue = opportunities
    .filter(o => !['closed_won', 'closed_lost'].includes(o.stage))
    .reduce((sum, o) => sum + o.amount, 0);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold">Sales Pipeline</h1>
            <p className="text-gray-600 mt-1">
              Total Pipeline Value: <span className="font-semibold text-blue-600">
                ${totalPipelineValue.toLocaleString()}
              </span>
            </p>
          </div>
          <div className="flex space-x-3">
            <div className="flex border border-gray-300 rounded-md overflow-hidden">
              <button
                onClick={() => setViewMode('pipeline')}
                className={`px-4 py-2 text-sm font-medium ${
                  viewMode === 'pipeline'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Pipeline View
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`px-4 py-2 text-sm font-medium border-l ${
                  viewMode === 'table'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Table View
              </button>
            </div>
            <Link
              to="/opportunities/new"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              + New Opportunity
            </Link>
          </div>
        </div>
      </div>

      {/* Pipeline View */}
      {viewMode === 'pipeline' && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {stageGroups.map(({ stage, opportunities: stageOpps, totalValue }) => (
            <div key={stage} className="bg-gray-50 rounded-lg p-4">
              <div className="mb-3">
                <h3 className="font-semibold text-sm text-gray-700 capitalize mb-1">
                  {stage.replace('_', ' ')}
                </h3>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>{stageOpps.length} deals</span>
                  <span>${(totalValue / 1000).toFixed(0)}K</span>
                </div>
              </div>

              <div className="space-y-2">
                {stageOpps.map((opp) => (
                  <Link
                    key={opp.id}
                    to={`/opportunities/${opp.id}`}
                    className="block bg-white rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow border border-gray-200"
                  >
                    <h4 className="font-medium text-sm text-gray-900 mb-1 truncate">
                      {opp.name}
                    </h4>
                    <div className="text-xs text-gray-600 mb-2">
                      ${opp.amount.toLocaleString()}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        {opp.probability}% prob
                      </span>
                      <div className="w-16 bg-gray-200 rounded-full h-1.5">
                        <div
                          className="bg-blue-600 h-1.5 rounded-full"
                          style={{ width: `${opp.probability}%` }}
                        />
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Table View */}
      {viewMode === 'table' && (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Opportunity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Stage
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Amount
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Probability
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Expected Close
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {opportunities.map((opp) => (
                <tr key={opp.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{opp.name}</div>
                    {opp.description && (
                      <div className="text-sm text-gray-500 truncate max-w-xs">
                        {opp.description}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStageBadge(opp.stage)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right font-medium text-gray-900">
                    ${opp.amount.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center justify-center space-x-2">
                      <span className="text-sm text-gray-600">{opp.probability}%</span>
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${opp.probability}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {opp.expected_close_date
                      ? new Date(opp.expected_close_date).toLocaleDateString()
                      : '—'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-3">
                    <Link
                      to={`/opportunities/${opp.id}`}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      View
                    </Link>
                    <Link
                      to={`/opportunities/${opp.id}/edit`}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      Edit
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
