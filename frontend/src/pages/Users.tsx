import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { authApi, User, Role } from '../services/api';
import { Settings, Edit, Trash2, X, AlertCircle, Shield } from 'lucide-react';

const Users: React.FC = () => {
  const { user: currentUser, hasRole } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    role: '',
    is_active: true,
  });

  const fetchData = async () => {
    try {
      const [usersData, rolesData] = await Promise.all([
        authApi.getUsers(),
        authApi.getRoles(),
      ]);
      setUsers(usersData);
      setRoles(rolesData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (hasRole(['admin'])) {
      fetchData();
    } else {
      setIsLoading(false);
    }
  }, [hasRole]);

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setFormData({
      role: user.role,
      is_active: user.is_active,
    });
    setShowModal(true);
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!editingUser) return;

    try {
      await authApi.updateUser(editingUser._id, formData);
      setShowModal(false);
      setEditingUser(null);
      fetchData();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to update user');
    }
  };

  const handleDelete = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user?')) return;

    try {
      await authApi.deleteUser(userId);
      fetchData();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      alert(error.response?.data?.detail || 'Failed to delete user');
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'bg-red-100 text-red-800';
      case 'manager':
        return 'bg-purple-100 text-purple-800';
      case 'staff':
        return 'bg-blue-100 text-blue-800';
      case 'viewer':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (!hasRole(['admin'])) {
    return (
      <div className="text-center py-12">
        <Shield className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500">You don't have permission to access this page</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <Settings className="w-7 h-7 mr-3 text-primary-600" />
          User Management
        </h1>
        <p className="text-gray-500 mt-1">Manage user accounts and roles</p>
      </div>

      <div className="card">
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Available Roles</h2>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {roles.map((role) => (
              <div
                key={role._id}
                className="p-4 border border-gray-200 rounded-lg"
              >
                <span
                  className={`inline-flex px-2 py-1 text-xs font-medium rounded-full capitalize ${getRoleColor(
                    role.name
                  )}`}
                >
                  {role.name}
                </span>
                <p className="text-sm text-gray-600 mt-2">{role.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">All Users</h2>
        {users.length === 0 ? (
          <div className="text-center py-12">
            <Settings className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No users found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-primary-50">
                  <th className="table-header rounded-tl-lg">Username</th>
                  <th className="table-header">Email</th>
                  <th className="table-header">Name</th>
                  <th className="table-header">Role</th>
                  <th className="table-header">Status</th>
                  <th className="table-header rounded-tr-lg text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user._id} className="hover:bg-gray-50">
                    <td className="table-cell font-medium text-gray-900">
                      {user.username}
                      {user._id === currentUser?._id && (
                        <span className="ml-2 text-xs text-primary-600">(You)</span>
                      )}
                    </td>
                    <td className="table-cell text-gray-600">{user.email}</td>
                    <td className="table-cell text-gray-600">
                      {user.first_name || user.last_name
                        ? `${user.first_name || ''} ${user.last_name || ''}`.trim()
                        : '-'}
                    </td>
                    <td className="table-cell">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full capitalize ${getRoleColor(
                          user.role
                        )}`}
                      >
                        {user.role}
                      </span>
                    </td>
                    <td className="table-cell">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          user.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="table-cell text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handleEdit(user)}
                          className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg"
                          title="Edit"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        {user._id !== currentUser?._id && (
                          <button
                            onClick={() => handleDelete(user._id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                            title="Delete"
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

      {showModal && editingUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Edit User</h2>
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

              <div>
                <p className="text-sm text-gray-500">Username</p>
                <p className="font-medium text-gray-900">{editingUser.username}</p>
              </div>

              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="font-medium text-gray-900">{editingUser.email}</p>
              </div>

              <div>
                <label className="label">Role</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="input"
                >
                  {roles.map((role) => (
                    <option key={role._id} value={role.name}>
                      {role.name} - {role.description}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) =>
                      setFormData({ ...formData, is_active: e.target.checked })
                    }
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Active</span>
                </label>
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
                  Update User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Users;
