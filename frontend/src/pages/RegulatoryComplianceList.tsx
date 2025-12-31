/**
 * Regulatory Compliance List page - Compliance monitoring and reporting
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface RegulatoryCompliance {
  id: number;
  compliance_id: string;
  regulation_name: string;
  regulation_type: string;
  authority: string;
  jurisdiction: string;
  compliance_status: string;
  last_audit_date?: string;
  next_audit_date?: string;
  responsible_person_id?: number;
  required_documents?: string;
  certification_expiry?: string;
  created_at: string;
}

export default function RegulatoryComplianceList() {
  const [compliances, setCompliances] = useState<RegulatoryCompliance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCompliances();
  }, []);

  const loadCompliances = async () => {
    try {
      setLoading(true);
      const data = await api.get('/governance/compliance');
      setCompliances(data);
    } catch (error) {
      console.error('Failed to load compliance records:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      compliant: 'bg-green-100 text-green-800',
      non_compliant: 'bg-red-100 text-red-800',
      under_review: 'bg-yellow-100 text-yellow-800',
      pending_audit: 'bg-blue-100 text-blue-800',
      exempt: 'bg-gray-100 text-gray-800',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status.replace('_', ' ')}
      </span>
    );
  };

  const isExpiringSoon = (expiryDate?: string) => {
    if (!expiryDate) return false;
    const daysUntilExpiry = Math.ceil((new Date(expiryDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry <= 30 && daysUntilExpiry >= 0;
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Regulatory Compliance</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Regulation</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Authority</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Next Audit</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cert. Expiry</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {compliances.map((compliance) => (
              <tr key={compliance.id} className={isExpiringSoon(compliance.certification_expiry) ? 'bg-yellow-50' : ''}>
                <td className="px-6 py-4">
                  <div className="font-medium text-gray-900">{compliance.regulation_name}</div>
                  <div className="text-xs text-gray-500">{compliance.compliance_id}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap capitalize text-sm text-gray-600">
                  {compliance.regulation_type}
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900">{compliance.authority}</div>
                  <div className="text-xs text-gray-500">{compliance.jurisdiction}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(compliance.compliance_status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {compliance.next_audit_date ? new Date(compliance.next_audit_date).toLocaleDateString() : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {compliance.certification_expiry ? (
                    <div className="flex items-center">
                      <span className={isExpiringSoon(compliance.certification_expiry) ? 'text-red-600 font-medium' : 'text-gray-600'}>
                        {new Date(compliance.certification_expiry).toLocaleDateString()}
                      </span>
                      {isExpiringSoon(compliance.certification_expiry) && (
                        <span className="ml-2 text-red-600" title="Expiring Soon">⚠️</span>
                      )}
                    </div>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/governance/compliance/${compliance.id}`} className="text-blue-600 hover:text-blue-900">
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
