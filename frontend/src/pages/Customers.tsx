import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { customersApi, Customer } from '../services/api';
import { Users, Plus, Search, Edit, Trash2, X, AlertCircle } from 'lucide-react';

const Customers: React.FC = () => {
  const { hasPermission } = useAuth();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    address: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
    notes: '',
  });

  const fetchCustomers = useCallback(async () => {
    try {
      const data = await customersApi.getAll({ search: searchTerm || undefined });
      setCustomers(data);
    } catch (err) {
      console.error('Failed to fetch customers:', err);
    } finally {
      setIsLoading(false);
    }
  }, [searchTerm]);

  useEffect(() => {
    fetchCustomers();
  }, [fetchCustomers]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      if (editingCustomer) {
        await customersApi.update(editingCustomer.id, formData);
      } else {
        await customersApi.create(formData);
      }
      setShowModal(false);
      setEditingCustomer(null);
      resetForm();
      fetchCustomers();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to save customer');
    }
  };

  const handleEdit = (customer: Customer) => {
    setEditingCustomer(customer);
    setFormData({
      name: customer.name,
      email: customer.email,
      phone: customer.phone || '',
      company: customer.company || '',
      address: customer.address || '',
      city: customer.city || '',
      state: customer.state || '',
      postal_code: customer.postal_code || '',
      country: customer.country || '',
      notes: customer.notes || '',
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this customer?')) return;

    try {
      await customersApi.delete(id);
      fetchCustomers();
    } catch (error) {
      console.error('Failed to delete customer:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      phone: '',
      company: '',
      address: '',
      city: '',
      state: '',
      postal_code: '',
      country: '',
      notes: '',
    });
    setError('');
  };

  const openNewModal = () => {
    setEditingCustomer(null);
    resetForm();
    setShowModal(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Users className="w-7 h-7 mr-3 text-primary-600" />
            Customers
          </h1>
          <p className="text-gray-500 mt-1">Manage your customer relationships</p>
        </div>
        {hasPermission('customers:write') && (
          <button onClick={openNewModal} className="btn-primary flex items-center">
            <Plus className="w-5 h-5 mr-2" />
            Add Customer
          </button>
        )}
      </div>

      <div className="card">
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search customers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>

        {customers.length === 0 ? (
          <div className="text-center py-12">
            <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No customers found</p>
            {hasPermission('customers:write') && (
              <button onClick={openNewModal} className="btn-primary mt-4">
                Add Your First Customer
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-primary-50">
                  <th className="table-header rounded-tl-lg">Name</th>
                  <th className="table-header">Email</th>
                  <th className="table-header">Phone</th>
                  <th className="table-header">Company</th>
                  <th className="table-header rounded-tr-lg text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((customer) => (
                  <tr key={customer.id} className="hover:bg-gray-50">
                    <td className="table-cell font-medium text-gray-900">{customer.name}</td>
                    <td className="table-cell text-gray-600">{customer.email}</td>
                    <td className="table-cell text-gray-600">{customer.phone || '-'}</td>
                    <td className="table-cell text-gray-600">{customer.company || '-'}</td>
                    <td className="table-cell text-right">
                      <div className="flex items-center justify-end space-x-2">
                        {hasPermission('customers:write') && (
                          <button
                            onClick={() => handleEdit(customer)}
                            className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                        )}
                        {hasPermission('customers:delete') && (
                          <button
                            onClick={() => handleDelete(customer.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">
                {editingCustomer ? 'Edit Customer' : 'Add New Customer'}
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center text-red-700">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  <span className="text-sm">{error}</span>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Name *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="input"
                    required
                  />
                </div>
                <div>
                  <label className="label">Email *</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="input"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Phone</label>
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">Company</label>
                  <input
                    type="text"
                    value={formData.company}
                    onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                    className="input"
                  />
                </div>
              </div>

              <div>
                <label className="label">Address</label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  className="input"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">City</label>
                  <input
                    type="text"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">State</label>
                  <input
                    type="text"
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                    className="input"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Postal Code</label>
                  <input
                    type="text"
                    value={formData.postal_code}
                    onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">Country</label>
                  <input
                    type="text"
                    value={formData.country}
                    onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                    className="input"
                  />
                </div>
              </div>

              <div>
                <label className="label">Notes</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="input"
                  rows={3}
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingCustomer ? 'Update Customer' : 'Add Customer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Customers;
