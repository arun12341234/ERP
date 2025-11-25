/**
 * Offer Campaign List page - Promotional campaign management
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';

interface OfferCampaign {
  id: number;
  campaign_code: string;
  campaign_name: string;
  campaign_type: string;
  discount_type: string;
  discount_value: number;
  min_purchase_amount?: number;
  max_discount_amount?: number;
  usage_limit_per_customer?: number;
  total_usage_limit?: number;
  current_usage_count: number;
  start_date: string;
  end_date: string;
  status: string;
  is_active: boolean;
  created_at: string;
}

export default function OfferCampaignList() {
  const [campaigns, setCampaigns] = useState<OfferCampaign[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    try {
      setLoading(true);
      const data = await api.get('/commerce/campaigns');
      setCampaigns(data);
    } catch (error) {
      console.error('Failed to load offer campaigns:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string, isActive: boolean) => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-800',
      active: 'bg-green-100 text-green-800',
      scheduled: 'bg-blue-100 text-blue-800',
      expired: 'bg-red-100 text-red-800',
      paused: 'bg-yellow-100 text-yellow-800',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status} {!isActive && '(Inactive)'}
      </span>
    );
  };

  const isExpired = (endDate: string) => {
    return new Date(endDate) < new Date();
  };

  const isUpcoming = (startDate: string) => {
    return new Date(startDate) > new Date();
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Offer Campaigns</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Campaign</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Discount</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Usage</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {campaigns.map((campaign) => (
              <tr key={campaign.id} className={isExpired(campaign.end_date) ? 'bg-gray-50' : ''}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="font-mono text-sm font-medium text-gray-900">{campaign.campaign_code}</span>
                </td>
                <td className="px-6 py-4">
                  <div className="font-medium text-gray-900">{campaign.campaign_name}</div>
                  <div className="text-xs text-gray-500 capitalize">{campaign.campaign_type.replace('_', ' ')}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {campaign.discount_type === 'percentage' ? `${campaign.discount_value}%` : `$${campaign.discount_value}`}
                  </div>
                  {campaign.min_purchase_amount && (
                    <div className="text-xs text-gray-500">Min: ${campaign.min_purchase_amount}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <div className="text-sm text-gray-900">{campaign.current_usage_count}</div>
                  {campaign.total_usage_limit && (
                    <div className="text-xs text-gray-500">/ {campaign.total_usage_limit}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className={`text-sm ${isUpcoming(campaign.start_date) ? 'text-blue-600' : 'text-gray-600'}`}>
                    {new Date(campaign.start_date).toLocaleDateString()}
                  </div>
                  <div className={`text-sm ${isExpired(campaign.end_date) ? 'text-red-600' : 'text-gray-600'}`}>
                    - {new Date(campaign.end_date).toLocaleDateString()}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(campaign.status, campaign.is_active)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link to={`/commerce/campaigns/${campaign.id}`} className="text-blue-600 hover:text-blue-900">
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
