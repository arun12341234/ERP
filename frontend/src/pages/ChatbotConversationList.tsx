/**
 * Chatbot Conversation List page - AI chatbot interaction tracking
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface ChatbotConversation {
  id: number;
  conversation_id: string;
  customer_id?: number;
  session_id: string;
  channel: string;
  status: string;
  message_count: number;
  first_message?: string;
  last_message?: string;
  sentiment?: string;
  resolution_status?: string;
  handled_by_bot: boolean;
  escalated_to_human: boolean;
  started_at: string;
  ended_at?: string;
  created_at: string;
}

export default function ChatbotConversationList() {
  const [conversations, setConversations] = useState<ChatbotConversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const data = await api.get('/commerce/chatbot');
      setConversations(data);
    } catch (error) {
      console.error('Failed to load chatbot conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      waiting: 'bg-yellow-100 text-yellow-800',
      resolved: 'bg-blue-100 text-blue-800',
      closed: 'bg-gray-100 text-gray-800',
      escalated: 'bg-red-100 text-red-800',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };

  const getSentimentIcon = (sentiment?: string) => {
    if (!sentiment) return null;
    const icons: Record<string, string> = {
      positive: '😊',
      neutral: '😐',
      negative: '😞',
    };
    return icons[sentiment] || null;
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Chatbot Conversations</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Conversation ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Channel</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Messages</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Handling</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Started</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {conversations.map((conv) => (
              <tr key={conv.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="font-mono text-xs font-medium text-gray-900">{conv.conversation_id}</div>
                  {conv.first_message && (
                    <div className="text-xs text-gray-500 truncate max-w-xs">{conv.first_message}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap capitalize text-sm text-gray-600">
                  {conv.channel}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-gray-900">{conv.message_count}</span>
                    {conv.sentiment && (
                      <span className="ml-2 text-lg">{getSentimentIcon(conv.sentiment)}</span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(conv.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {conv.escalated_to_human ? (
                    <span className="text-xs text-red-600">👤 Human</span>
                  ) : conv.handled_by_bot ? (
                    <span className="text-xs text-blue-600">🤖 Bot</span>
                  ) : (
                    <span className="text-xs text-gray-400">-</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {new Date(conv.started_at).toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/commerce/chatbot/${conv.id}`} className="text-blue-600 hover:text-blue-900">
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
