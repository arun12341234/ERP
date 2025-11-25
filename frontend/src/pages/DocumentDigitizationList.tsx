/**
 * Document Digitization List page - Document OCR and digitization
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface DocumentDigitization {
  id: number;
  document_id: string;
  document_name: string;
  document_type: string;
  file_path: string;
  file_size_mb: number;
  page_count: number;
  processing_status: string;
  ocr_confidence?: number;
  extracted_text?: string;
  uploaded_at: string;
  processing_started_at?: string;
  processing_completed_at?: string;
  created_at: string;
}

export default function DocumentDigitizationList() {
  const [documents, setDocuments] = useState<DocumentDigitization[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const data = await api.get('/governance/documents');
      setDocuments(data);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
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
        <h1 className="text-3xl font-bold">Document Digitization</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Document</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Pages</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Size</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Confidence</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {documents.map((doc) => (
              <tr key={doc.id}>
                <td className="px-6 py-4">
                  <div className="font-medium text-gray-900">{doc.document_name}</div>
                  <div className="text-xs text-gray-500">{doc.document_id}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap capitalize text-sm text-gray-600">
                  {doc.document_type}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-600">
                  {doc.page_count}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-600">
                  {doc.file_size_mb.toFixed(2)} MB
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  {doc.ocr_confidence ? (
                    <span className={`font-medium ${doc.ocr_confidence >= 90 ? 'text-green-600' : doc.ocr_confidence >= 70 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {doc.ocr_confidence.toFixed(0)}%
                    </span>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(doc.processing_status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/governance/documents/${doc.id}`} className="text-blue-600 hover:text-blue-900">
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
