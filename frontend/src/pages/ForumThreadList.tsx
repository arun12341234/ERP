/**
 * Forum Thread List page - Community discussion forum
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface ForumThread {
  id: number;
  thread_id: string;
  title: string;
  content: string;
  category: string;
  author_id: number;
  author_name?: string;
  status: string;
  is_pinned: boolean;
  is_locked: boolean;
  view_count: number;
  reply_count: number;
  last_reply_at?: string;
  created_at: string;
  updated_at: string;
}

export default function ForumThreadList() {
  const [threads, setThreads] = useState<ForumThread[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadThreads();
  }, []);

  const loadThreads = async () => {
    try {
      setLoading(true);
      const data = await api.get('/commerce/forum');
      setThreads(data);
    } catch (error) {
      console.error('Failed to load forum threads:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800',
      archived: 'bg-blue-100 text-blue-800',
      flagged: 'bg-red-100 text-red-800',
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
        <h1 className="text-3xl font-bold">Community Forum</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Thread</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Author</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Replies</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Views</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Activity</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {threads.map((thread) => (
              <tr key={thread.id} className={thread.is_pinned ? 'bg-yellow-50' : ''}>
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    {thread.is_pinned && <span className="mr-2 text-yellow-600" title="Pinned">📌</span>}
                    {thread.is_locked && <span className="mr-2 text-red-600" title="Locked">🔒</span>}
                    <div>
                      <div className="font-medium text-gray-900">{thread.title}</div>
                      <div className="text-xs text-gray-500 truncate max-w-xs">{thread.content}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap capitalize text-sm text-gray-600">
                  {thread.category}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {thread.author_name || `User #${thread.author_id}`}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                  {thread.reply_count}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-600">
                  {thread.view_count}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(thread.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {thread.last_reply_at ? new Date(thread.last_reply_at).toLocaleString() : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/commerce/forum/${thread.id}`} className="text-blue-600 hover:text-blue-900">
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
