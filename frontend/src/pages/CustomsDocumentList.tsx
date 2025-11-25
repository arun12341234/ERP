/**
 * Customs Document List page - Import/Export documentation
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface CustomsDocument {
  id: number;
  document_number: string;
  document_type: string;
  shipment_id?: number;
  country_of_origin: string;
  country_of_destination: string;
  customs_value: number;
  currency: string;
  hs_code?: string;
  duty_amount?: number;
  tax_amount?: number;
  status: string;
  submitted_date?: string;
  cleared_date?: string;
  created_at: string;
}

export default function CustomsDocumentList() {
  const [documents, setDocuments] = useState<CustomsDocument[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const data = await api.get('/logistics/customs');
      setDocuments(data);
    } catch (error) {
      console.error('Failed to load customs documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-800',
      submitted: 'bg-blue-100 text-blue-800',
      under_review: 'bg-yellow-100 text-yellow-800',
      cleared: 'bg-green-100 text-green-800',
      held: 'bg-red-100 text-red-800',
      rejected: 'bg-red-100 text-red-800',
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
        <h1 className="text-3xl font-bold">Customs Documents</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Document #</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Route</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Customs Value</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cleared Date</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {documents.map((doc) => (
              <tr key={doc.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="font-mono text-sm font-medium text-gray-900">{doc.document_number}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap capitalize text-gray-600">
                  {doc.document_type.replace('_', ' ')}
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900">{doc.country_of_origin}</div>
                  <div className="text-sm text-gray-500">→ {doc.country_of_destination}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <div className="font-medium text-gray-900">{doc.currency} {doc.customs_value.toLocaleString()}</div>
                  {(doc.duty_amount || doc.tax_amount) && (
                    <div className="text-xs text-gray-500">
                      Duties & Taxes: {doc.currency} {((doc.duty_amount || 0) + (doc.tax_amount || 0)).toLocaleString()}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(doc.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                  {doc.cleared_date ? new Date(doc.cleared_date).toLocaleDateString() : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/logistics/customs/${doc.id}`} className="text-blue-600 hover:text-blue-900">
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
