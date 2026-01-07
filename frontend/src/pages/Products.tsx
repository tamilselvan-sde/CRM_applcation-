import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { productsApi, Product } from '../services/api';
import { Package, Plus, Search, Edit, Trash2, X, AlertCircle } from 'lucide-react';

const Products: React.FC = () => {
  const { hasPermission } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    sku: '',
    price: '',
    unit: 'unit',
    is_service: false,
    is_active: true,
  });

  const fetchProducts = useCallback(async () => {
    try {
      const data = await productsApi.getAll({ search: searchTerm || undefined });
      setProducts(data);
    } catch (err) {
      console.error('Failed to fetch products:', err);
    } finally {
      setIsLoading(false);
    }
  }, [searchTerm]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const productData = {
      ...formData,
      price: parseFloat(formData.price),
      sku: formData.sku || undefined,
    };

    try {
      if (editingProduct) {
        await productsApi.update(editingProduct.id, productData);
      } else {
        await productsApi.create(productData);
      }
      setShowModal(false);
      setEditingProduct(null);
      resetForm();
      fetchProducts();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to save product');
    }
  };

  const handleEdit = (product: Product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name,
      description: product.description || '',
      sku: product.sku || '',
      price: product.price.toString(),
      unit: product.unit,
      is_service: product.is_service,
      is_active: product.is_active,
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this product?')) return;

    try {
      await productsApi.delete(id);
      fetchProducts();
    } catch (error) {
      console.error('Failed to delete product:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      sku: '',
      price: '',
      unit: 'unit',
      is_service: false,
      is_active: true,
    });
    setError('');
  };

  const openNewModal = () => {
    setEditingProduct(null);
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
            <Package className="w-7 h-7 mr-3 text-primary-600" />
            Products & Services
          </h1>
          <p className="text-gray-500 mt-1">Manage your product catalog</p>
        </div>
        {hasPermission('products:write') && (
          <button onClick={openNewModal} className="btn-primary flex items-center">
            <Plus className="w-5 h-5 mr-2" />
            Add Product
          </button>
        )}
      </div>

      <div className="card">
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>

        {products.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No products found</p>
            {hasPermission('products:write') && (
              <button onClick={openNewModal} className="btn-primary mt-4">
                Add Your First Product
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-primary-50">
                  <th className="table-header rounded-tl-lg">Name</th>
                  <th className="table-header">SKU</th>
                  <th className="table-header">Type</th>
                  <th className="table-header">Price</th>
                  <th className="table-header">Status</th>
                  <th className="table-header rounded-tr-lg text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {products.map((product) => (
                  <tr key={product.id} className="hover:bg-gray-50">
                    <td className="table-cell">
                      <div>
                        <p className="font-medium text-gray-900">{product.name}</p>
                        {product.description && (
                          <p className="text-sm text-gray-500 truncate max-w-xs">
                            {product.description}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="table-cell text-gray-600">{product.sku || '-'}</td>
                    <td className="table-cell">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          product.is_service
                            ? 'bg-purple-100 text-purple-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {product.is_service ? 'Service' : 'Product'}
                      </span>
                    </td>
                    <td className="table-cell font-medium text-gray-900">
                      ${Number(product.price).toFixed(2)} / {product.unit}
                    </td>
                    <td className="table-cell">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          product.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {product.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="table-cell text-right">
                      <div className="flex items-center justify-end space-x-2">
                        {hasPermission('products:write') && (
                          <button
                            onClick={() => handleEdit(product)}
                            className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                        )}
                        {hasPermission('products:delete') && (
                          <button
                            onClick={() => handleDelete(product.id)}
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
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">
                {editingProduct ? 'Edit Product' : 'Add New Product'}
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
                <label className="label">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="input"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">SKU</label>
                  <input
                    type="text"
                    value={formData.sku}
                    onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">Price *</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    className="input"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="label">Unit</label>
                <input
                  type="text"
                  value={formData.unit}
                  onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                  className="input"
                  placeholder="e.g., unit, hour, piece"
                />
              </div>

              <div className="flex items-center space-x-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_service}
                    onChange={(e) => setFormData({ ...formData, is_service: e.target.checked })}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">This is a service</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
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
                  {editingProduct ? 'Update Product' : 'Add Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Products;
