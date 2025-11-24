/**
 * Chart of Accounts List page - GL account master
 */
import { useState, useEffect } from 'react';
import { api } from '../lib/api';

interface Account {
  id: number;
  account_code: string;
  account_name: string;
  account_type: string;
  account_subtype: string | null;
  current_balance: number;
  is_active: boolean;
}

export default function ChartOfAccountsList() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [typeFilter, setTypeFilter] = useState<string>('');

  useEffect(() => {
    loadAccounts();
  }, [typeFilter]);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const url = typeFilter ? `/chart-of-accounts?account_type=${typeFilter}` : '/chart-of-accounts';
      const data = await api.get(url);
      setAccounts(data);
    } catch (error) {
      console.error('Failed to load accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatAmount = (cents: number) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      asset: 'bg-blue-100 text-blue-800',
      liability: 'bg-red-100 text-red-800',
      equity: 'bg-purple-100 text-purple-800',
      revenue: 'bg-green-100 text-green-800',
      expense: 'bg-orange-100 text-orange-800',
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Chart of Accounts</h1>
        <div className="flex gap-4">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="">All Types</option>
            <option value="asset">Asset</option>
            <option value="liability">Liability</option>
            <option value="equity">Equity</option>
            <option value="revenue">Revenue</option>
            <option value="expense">Expense</option>
          </select>
        </div>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Account Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Account Name</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Subtype</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Current Balance</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {accounts.map((account) => (
              <tr key={account.id}>
                <td className="px-6 py-4 whitespace-nowrap font-mono text-sm font-medium">
                  {account.account_code}
                </td>
                <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                  {account.account_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(account.account_type)}`}>
                    {account.account_type}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {account.account_subtype || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right font-medium text-gray-900">
                  {formatAmount(account.current_balance)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className={`px-2 py-1 rounded-full text-xs ${account.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {account.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {accounts.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No accounts found
        </div>
      )}
    </div>
  );
}
