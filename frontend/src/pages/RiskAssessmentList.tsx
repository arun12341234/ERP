/**
 * Risk Assessment List page - Enterprise risk management
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface RiskAssessment {
  id: number;
  risk_id: string;
  risk_title: string;
  risk_category: string;
  risk_level: string;
  probability: number;
  impact: number;
  risk_score: number;
  status: string;
  owner_id: number;
  identified_date: string;
  mitigation_plan?: string;
  created_at: string;
}

export default function RiskAssessmentList() {
  const [risks, setRisks] = useState<RiskAssessment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRisks();
  }, []);

  const loadRisks = async () => {
    try {
      setLoading(true);
      const data = await api.get('/governance/risks');
      setRisks(data);
    } catch (error) {
      console.error('Failed to load risk assessments:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelBadge = (level: string) => {
    const colors: Record<string, string> = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[level] || 'bg-gray-100 text-gray-800'}`}>
        {level}
      </span>
    );
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      identified: 'bg-yellow-100 text-yellow-800',
      analyzing: 'bg-blue-100 text-blue-800',
      mitigating: 'bg-purple-100 text-purple-800',
      monitoring: 'bg-indigo-100 text-indigo-800',
      closed: 'bg-green-100 text-green-800',
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
        <h1 className="text-3xl font-bold">Risk Assessments</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Risk Score</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Level</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {risks.map((risk) => (
              <tr key={risk.id}>
                <td className="px-6 py-4">
                  <div className="font-medium text-gray-900">{risk.risk_title}</div>
                  <div className="text-xs text-gray-500">{risk.risk_id}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap capitalize text-sm text-gray-600">
                  {risk.risk_category}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <div className="font-bold text-lg text-gray-900">{risk.risk_score}</div>
                  <div className="text-xs text-gray-500">P:{risk.probability} × I:{risk.impact}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getRiskLevelBadge(risk.risk_level)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(risk.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/governance/risks/${risk.id}`} className="text-blue-600 hover:text-blue-900">
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
