/**
 * Opportunity Detail - View Sales Opportunity Details
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
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
  updated_at?: string;
}

interface Customer {
  id: number;
  name: string;
  email: string;
  company_name?: string;
}

interface Lead {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  company?: string;
}

interface User {
  id: number;
  full_name: string;
  email: string;
}

export default function OpportunityDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [lead, setLead] = useState<Lead | null>(null);
  const [assignedUser, setAssignedUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOpportunity();
  }, [id]);

  const loadOpportunity = async () => {
    try {
      setLoading(true);
      const data = await api.get(`/opportunities/${id}`);
      setOpportunity(data);

      // Load related data
      if (data.customer_id) {
        const customerData = await api.get(`/customers/${data.customer_id}`);
        setCustomer(customerData);
      }
      if (data.lead_id) {
        const leadData = await api.get(`/leads/${data.lead_id}`);
        setLead(leadData);
      }
      if (data.assigned_to_id) {
        const userData = await api.get(`/users/${data.assigned_to_id}`);
        setAssignedUser(userData);
      }
    } catch (error) {
      console.error('Failed to load opportunity:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this opportunity?')) return;

    try {
      await api.delete(`/opportunities/${id}`);
      navigate('/opportunities');
    } catch (error) {
      alert('Failed to delete opportunity');
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
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors[stage]}`}>
        {stage.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  const getStageProgress = (stage: string) => {
    const stages = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won'];
    const currentIndex = stages.indexOf(stage);
    if (stage === 'closed_lost') return 0;
    return ((currentIndex + 1) / stages.length) * 100;
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (!opportunity) return <div className="p-8">Opportunity not found</div>;

  const stageProgress = getStageProgress(opportunity.stage);
  const daysUntilClose = opportunity.expected_close_date
    ? Math.ceil((new Date(opportunity.expected_close_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
    : null;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <h1 className="text-3xl font-bold">{opportunity.name}</h1>
            {getStageBadge(opportunity.stage)}
          </div>
          <p className="text-gray-600">
            Created {new Date(opportunity.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex space-x-3">
          <Link
            to={`/opportunities/${id}/edit`}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Edit
          </Link>
          <button
            onClick={handleDelete}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Delete
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Opportunity Value */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Deal Value</h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-baseline mb-2">
                  <span className="text-sm text-gray-600">Amount</span>
                  <span className="text-3xl font-bold text-gray-900">
                    ${opportunity.amount.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-baseline">
                  <span className="text-sm text-gray-600">Weighted Value (Probability-adjusted)</span>
                  <span className="text-xl font-semibold text-blue-600">
                    ${((opportunity.amount * opportunity.probability) / 100).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Stage Progress */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Sales Stage Progress</h2>
            <div className="space-y-4">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Current Stage</span>
                <span className="font-medium">{opportunity.stage.replace('_', ' ')}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full ${
                    opportunity.stage === 'closed_won' ? 'bg-green-600' :
                    opportunity.stage === 'closed_lost' ? 'bg-red-600' : 'bg-blue-600'
                  }`}
                  style={{ width: `${stageProgress}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-2">
                <span>Prospecting</span>
                <span>Qualification</span>
                <span>Proposal</span>
                <span>Negotiation</span>
                <span>Won</span>
              </div>
            </div>
          </div>

          {/* Probability */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Win Probability</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-4xl font-bold text-gray-900">{opportunity.probability}%</span>
                <span className="text-sm text-gray-600">Likelihood to close</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className={`h-4 rounded-full ${
                    opportunity.probability >= 75 ? 'bg-green-500' :
                    opportunity.probability >= 50 ? 'bg-yellow-500' :
                    opportunity.probability >= 25 ? 'bg-orange-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${opportunity.probability}%` }}
                />
              </div>
            </div>
          </div>

          {/* Description */}
          {opportunity.description && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-3">Description</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{opportunity.description}</p>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Timeline */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Timeline</h2>
            <div className="space-y-4">
              {opportunity.expected_close_date && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">Expected Close Date</div>
                  <div className="font-medium">
                    {new Date(opportunity.expected_close_date).toLocaleDateString('en-US', {
                      month: 'long',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </div>
                  {daysUntilClose !== null && (
                    <div className={`text-sm mt-1 ${
                      daysUntilClose < 0 ? 'text-red-600' :
                      daysUntilClose <= 7 ? 'text-orange-600' : 'text-gray-600'
                    }`}>
                      {daysUntilClose < 0
                        ? `Overdue by ${Math.abs(daysUntilClose)} days`
                        : daysUntilClose === 0
                        ? 'Due today'
                        : `${daysUntilClose} days remaining`}
                    </div>
                  )}
                </div>
              )}
              <div>
                <div className="text-sm text-gray-600 mb-1">Created</div>
                <div className="font-medium">
                  {new Date(opportunity.created_at).toLocaleDateString('en-US', {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Assigned User */}
          {assignedUser && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">Assigned To</h2>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                  {assignedUser.full_name.charAt(0)}
                </div>
                <div>
                  <div className="font-medium">{assignedUser.full_name}</div>
                  <div className="text-sm text-gray-600">{assignedUser.email}</div>
                </div>
              </div>
            </div>
          )}

          {/* Customer/Lead Info */}
          {(customer || lead) && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4">Related Contact</h2>
              {customer && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">Customer</div>
                  <Link
                    to={`/customers/${customer.id}`}
                    className="font-medium text-blue-600 hover:text-blue-800"
                  >
                    {customer.name}
                  </Link>
                  {customer.company_name && (
                    <div className="text-sm text-gray-600 mt-1">{customer.company_name}</div>
                  )}
                  <div className="text-sm text-gray-600">{customer.email}</div>
                </div>
              )}
              {lead && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">Lead</div>
                  <Link
                    to={`/leads/${lead.id}/edit`}
                    className="font-medium text-blue-600 hover:text-blue-800"
                  >
                    {lead.first_name} {lead.last_name}
                  </Link>
                  {lead.company && (
                    <div className="text-sm text-gray-600 mt-1">{lead.company}</div>
                  )}
                  <div className="text-sm text-gray-600">{lead.email}</div>
                </div>
              )}
            </div>
          )}

          {/* Deal Score */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Deal Score</h2>
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600">{opportunity.score}</div>
              <div className="text-sm text-gray-600 mt-1">out of 100</div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${opportunity.score}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
