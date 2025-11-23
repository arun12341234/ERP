/**
 * Machine List page - Production machines
 */
import { useState, useEffect } from 'react';
import { api } from '../lib/api';

interface Machine {
  id: number;
  machine_code: string;
  name: string;
  machine_type: string;
  status: string;
  is_active: boolean;
  department: string;
  location: string;
  hourly_capacity: number;
  next_maintenance_date: string | null;
}

export default function MachineList() {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMachines();
  }, []);

  const loadMachines = async () => {
    try {
      setLoading(true);
      const data = await api.get('/machines');
      setMachines(data);
    } catch (error) {
      console.error('Failed to load machines:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      available: 'bg-green-100 text-green-800',
      in_use: 'bg-blue-100 text-blue-800',
      maintenance: 'bg-yellow-100 text-yellow-800',
      breakdown: 'bg-red-100 text-red-800',
      retired: 'bg-gray-100 text-gray-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Machines</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Capacity/hr</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Next Maint.</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {machines.map((machine) => (
              <tr key={machine.id}>
                <td className="px-6 py-4 whitespace-nowrap font-mono text-sm font-medium">
                  {machine.machine_code}
                </td>
                <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                  {machine.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                  {machine.machine_type || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                  {machine.department || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                  {machine.location || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-gray-600">
                  {machine.hourly_capacity}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(machine.status)}`}>
                    {machine.status.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {machine.next_maintenance_date
                    ? new Date(machine.next_maintenance_date).toLocaleDateString()
                    : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {machines.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No machines found
        </div>
      )}
    </div>
  );
}
