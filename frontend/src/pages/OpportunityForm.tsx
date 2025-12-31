/**
 * Opportunity Form - Create/Edit Sales Opportunity
 */
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { api } from '../lib/api';

const opportunitySchema = z.object({
  name: z.string().min(1, 'Opportunity name is required'),
  description: z.string().optional(),
  amount: z.number().min(0, 'Amount must be positive'),
  stage: z.string(),
  probability: z.number().min(0).max(100, 'Probability must be between 0 and 100'),
  expected_close_date: z.string().optional(),
  customer_id: z.number().optional(),
  lead_id: z.number().optional(),
  assigned_to_id: z.number(),
});

type OpportunityForm = z.infer<typeof opportunitySchema>;

interface Customer {
  id: number;
  name: string;
  company_name?: string;
}

interface Lead {
  id: number;
  first_name: string;
  last_name: string;
  company?: string;
}

interface User {
  id: number;
  full_name: string;
  email: string;
}

export default function OpportunityFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [selectedStage, setSelectedStage] = useState('prospecting');

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
    setValue,
  } = useForm<OpportunityForm>({
    resolver: zodResolver(opportunitySchema),
    defaultValues: {
      stage: 'prospecting',
      probability: 10,
      amount: 0,
      assigned_to_id: 0,
    },
  });

  const stage = watch('stage');

  useEffect(() => {
    loadFormData();
    if (id) {
      loadOpportunity();
    }
  }, [id]);

  // Auto-update probability based on stage
  useEffect(() => {
    const stageProbabilities: Record<string, number> = {
      prospecting: 10,
      qualification: 25,
      proposal: 50,
      negotiation: 75,
      closed_won: 100,
      closed_lost: 0,
    };
    if (stageProbabilities[stage] !== undefined) {
      setValue('probability', stageProbabilities[stage]);
      setSelectedStage(stage);
    }
  }, [stage, setValue]);

  const loadFormData = async () => {
    try {
      const [customersData, leadsData, usersData] = await Promise.all([
        api.get('/customers'),
        api.get('/leads'),
        api.get('/users'),
      ]);
      setCustomers(customersData);
      setLeads(leadsData.filter((l: any) => l.status === 'qualified'));
      setUsers(usersData);

      // Set default assigned_to_id to current user if creating new
      if (!id && usersData.length > 0) {
        setValue('assigned_to_id', usersData[0].id);
      }
    } catch (error) {
      console.error('Failed to load form data:', error);
    }
  };

  const loadOpportunity = async () => {
    try {
      const opportunity = await api.get(`/opportunities/${id}`);
      reset(opportunity);
      setSelectedStage(opportunity.stage);
    } catch (error) {
      setError('Failed to load opportunity');
    }
  };

  const onSubmit = async (data: OpportunityForm) => {
    setLoading(true);
    setError('');

    try {
      if (id) {
        await api.put(`/opportunities/${id}`, data);
      } else {
        await api.post('/opportunities', data);
      }
      navigate('/opportunities');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save opportunity');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">
          {id ? 'Edit Opportunity' : 'New Opportunity'}
        </h1>
        <p className="mt-2 text-gray-600">
          {id ? 'Update opportunity details' : 'Create a new sales opportunity'}
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="bg-white shadow rounded-lg p-6 space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Opportunity Name *
          </label>
          <input
            {...register('name')}
            placeholder="e.g., Enterprise Software License"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <textarea
            {...register('description')}
            rows={3}
            placeholder="Describe the opportunity..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Customer
            </label>
            <select
              {...register('customer_id', { valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Customer (Optional)</option>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name} {customer.company_name ? `(${customer.company_name})` : ''}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lead
            </label>
            <select
              {...register('lead_id', { valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Lead (Optional)</option>
              {leads.map((lead) => (
                <option key={lead.id} value={lead.id}>
                  {lead.first_name} {lead.last_name} {lead.company ? `(${lead.company})` : ''}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-500">Only qualified leads shown</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Amount ($) *
            </label>
            <input
              {...register('amount', { valueAsNumber: true })}
              type="number"
              step="0.01"
              placeholder="0.00"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.amount && (
              <p className="mt-1 text-sm text-red-600">{errors.amount.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Expected Close Date
            </label>
            <input
              {...register('expected_close_date')}
              type="date"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sales Stage *
            </label>
            <select
              {...register('stage')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="prospecting">Prospecting</option>
              <option value="qualification">Qualification</option>
              <option value="proposal">Proposal</option>
              <option value="negotiation">Negotiation</option>
              <option value="closed_won">Closed Won</option>
              <option value="closed_lost">Closed Lost</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Probability (%) *
            </label>
            <input
              {...register('probability', { valueAsNumber: true })}
              type="number"
              min="0"
              max="100"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${watch('probability') || 0}%` }}
              />
            </div>
            {errors.probability && (
              <p className="mt-1 text-sm text-red-600">{errors.probability.message}</p>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Assigned To *
          </label>
          <select
            {...register('assigned_to_id', { valueAsNumber: true })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select User</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.full_name} ({user.email})
              </option>
            ))}
          </select>
          {errors.assigned_to_id && (
            <p className="mt-1 text-sm text-red-600">{errors.assigned_to_id.message}</p>
          )}
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={() => navigate('/opportunities')}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Saving...' : id ? 'Update Opportunity' : 'Create Opportunity'}
          </button>
        </div>
      </form>
    </div>
  );
}
