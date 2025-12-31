/**
 * Customer Detail Page - View customer information and related data
 */
import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api } from '../lib/api';

interface Customer {
  id: number;
  name: string;
  email: string;
  phone?: string;
  company_name?: string;
  customer_type: string;
  status: string;
  credit_limit: number;
  current_balance: number;
  billing_address?: string;
  shipping_address?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export default function CustomerDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCustomer();
  }, [id]);

  const loadCustomer = async () => {
    try {
      const data = await api.get(`/customers/${id}`);
      setCustomer(data);
    } catch (error) {
      console.error('Failed to load customer:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      suspended: 'bg-red-100 text-red-800',
    };

    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors[status]}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const getTypeBadge = (type: string) => {
    const colors: Record<string, string> = {
      individual: 'bg-blue-100 text-blue-800',
      business: 'bg-purple-100 text-purple-800',
      enterprise: 'bg-indigo-100 text-indigo-800',
    };

    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors[type]}`}>
        {type.charAt(0).toUpperCase() + type.slice(1)}
      </span>
    );
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (!customer) return <div className="p-8">Customer not found</div>;

  const creditUsage = (customer.current_balance / customer.credit_limit) * 100;
  const creditAvailable = customer.credit_limit - customer.current_balance;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <div className="flex items-center space-x-3">
            <Link
              to="/customers"
              className="text-gray-500 hover:text-gray-700"
            >
              ← Back to Customers
            </Link>
          </div>
          <h1 className="text-3xl font-bold mt-2">{customer.name}</h1>
          <p className="text-gray-600 mt-1">{customer.email}</p>
        </div>
        <div className="flex space-x-3">
          <Link
            to={`/customers/${customer.id}/edit`}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Edit Customer
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info Card */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Customer Information</h2>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <div className="mt-1">{getStatusBadge(customer.status)}</div>
              </div>
              <div>
                <p className="text-sm text-gray-500">Type</p>
                <div className="mt-1">{getTypeBadge(customer.customer_type)}</div>
              </div>
              <div>
                <p className="text-sm text-gray-500">Phone</p>
                <p className="mt-1 font-medium">{customer.phone || '—'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Company</p>
                <p className="mt-1 font-medium">{customer.company_name || '—'}</p>
              </div>
            </div>

            {customer.billing_address && (
              <div className="mt-4">
                <p className="text-sm text-gray-500">Billing Address</p>
                <p className="mt-1 text-gray-700 whitespace-pre-line">{customer.billing_address}</p>
              </div>
            )}

            {customer.shipping_address && (
              <div className="mt-4">
                <p className="text-sm text-gray-500">Shipping Address</p>
                <p className="mt-1 text-gray-700 whitespace-pre-line">{customer.shipping_address}</p>
              </div>
            )}

            {customer.notes && (
              <div className="mt-4">
                <p className="text-sm text-gray-500">Notes</p>
                <p className="mt-1 text-gray-700 whitespace-pre-line">{customer.notes}</p>
              </div>
            )}
          </div>

          {/* Placeholder for future related data */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
            <p className="text-gray-500 text-center py-8">
              Sales orders, quotes, and support tickets will appear here
            </p>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Credit Info Card */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Credit Information</h3>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500">Credit Limit</span>
                  <span className="font-medium">${customer.credit_limit.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500">Current Balance</span>
                  <span className={`font-medium ${customer.current_balance > customer.credit_limit ? 'text-red-600' : ''}`}>
                    ${customer.current_balance.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-500">Available Credit</span>
                  <span className={`font-medium ${creditAvailable < 0 ? 'text-red-600' : 'text-green-600'}`}>
                    ${creditAvailable.toLocaleString()}
                  </span>
                </div>

                {/* Credit Usage Bar */}
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Credit Usage</span>
                    <span>{creditUsage.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        creditUsage > 100 ? 'bg-red-600' :
                        creditUsage > 80 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(creditUsage, 100)}%` }}
                    />
                  </div>
                </div>
              </div>

              {creditUsage > 90 && (
                <div className={`p-3 rounded-md ${
                  creditUsage > 100 ? 'bg-red-50 border border-red-200' : 'bg-yellow-50 border border-yellow-200'
                }`}>
                  <p className={`text-sm ${
                    creditUsage > 100 ? 'text-red-800' : 'text-yellow-800'
                  }`}>
                    {creditUsage > 100 ? '⚠️ Credit limit exceeded!' : '⚠️ Approaching credit limit'}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Account Details */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Account Details</h3>
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-gray-500">Customer ID</p>
                <p className="font-medium mt-1">#{customer.id}</p>
              </div>
              <div>
                <p className="text-gray-500">Created</p>
                <p className="font-medium mt-1">
                  {new Date(customer.created_at).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-gray-500">Last Updated</p>
                <p className="font-medium mt-1">
                  {new Date(customer.updated_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
