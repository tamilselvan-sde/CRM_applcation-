import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { customersApi, productsApi, invoicesApi, Customer, Product, InvoiceItem } from '../services/api';
import { FileText, ArrowLeft, Plus, Trash2, AlertCircle } from 'lucide-react';

const CreateInvoice: React.FC = () => {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    customer_id: '',
    status: 'draft',
    due_date: '',
    tax_rate: '0',
    notes: '',
  });

  const [items, setItems] = useState<InvoiceItem[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [customersData, productsData] = await Promise.all([
          customersApi.getAll(),
          productsApi.getAll({ is_active: true }),
        ]);
        setCustomers(customersData);
        setProducts(productsData);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const addItem = () => {
    setItems([
      ...items,
      {
        product_id: 0,
        description: '',
        quantity: 1,
        unit_price: 0,
      },
    ]);
  };

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: keyof InvoiceItem, value: string | number) => {
    const newItems = [...items];
    if (field === 'product_id') {
      const product = products.find((p) => p.id === Number(value));
      newItems[index] = {
        ...newItems[index],
        product_id: Number(value),
        unit_price: product ? product.price : 0,
        description: product ? product.name : '',
      };
    } else {
      newItems[index] = {
        ...newItems[index],
        [field]: field === 'quantity' || field === 'unit_price' ? Number(value) : value,
      };
    }
    setItems(newItems);
  };

  const calculateSubtotal = () => {
    return items.reduce((sum, item) => sum + item.quantity * item.unit_price, 0);
  };

  const calculateTax = () => {
    return calculateSubtotal() * (parseFloat(formData.tax_rate) / 100);
  };

  const calculateTotal = () => {
    return calculateSubtotal() + calculateTax();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!formData.customer_id) {
      setError('Please select a customer');
      return;
    }

    if (items.length === 0) {
      setError('Please add at least one item');
      return;
    }

    const invalidItems = items.filter((item) => !item.product_id || item.quantity <= 0);
    if (invalidItems.length > 0) {
      setError('Please fill in all item details');
      return;
    }

    setIsSaving(true);

    try {
      const invoiceData = {
        customer_id: parseInt(formData.customer_id),
        status: formData.status as 'draft' | 'pending' | 'paid' | 'cancelled',
        due_date: formData.due_date || undefined,
        tax_rate: parseFloat(formData.tax_rate),
        notes: formData.notes || undefined,
        items: items.map((item) => ({
          product_id: item.product_id,
          description: item.description,
          quantity: item.quantity,
          unit_price: item.unit_price,
        })),
      };

      const invoice = await invoicesApi.create(invoiceData);
      navigate(`/invoices/${invoice.id}`);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to create invoice');
    } finally {
      setIsSaving(false);
    }
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
      <div className="flex items-center">
        <Link
          to="/invoices"
          className="mr-4 p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <FileText className="w-7 h-7 mr-3 text-primary-600" />
            Create Invoice
          </h1>
          <p className="text-gray-500 mt-1">Create a new invoice for your customer</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center text-red-700">
            <AlertCircle className="w-5 h-5 mr-2" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Invoice Details</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="label">Customer *</label>
                  <select
                    value={formData.customer_id}
                    onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                    className="input"
                    required
                  >
                    <option value="">Select a customer</option>
                    {customers.map((customer) => (
                      <option key={customer.id} value={customer.id}>
                        {customer.name} ({customer.email})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="label">Status</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="input"
                  >
                    <option value="draft">Draft</option>
                    <option value="pending">Pending</option>
                    <option value="paid">Paid</option>
                  </select>
                </div>
                <div>
                  <label className="label">Due Date</label>
                  <input
                    type="date"
                    value={formData.due_date}
                    onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">Tax Rate (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={formData.tax_rate}
                    onChange={(e) => setFormData({ ...formData, tax_rate: e.target.value })}
                    className="input"
                  />
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Line Items</h2>
                <button
                  type="button"
                  onClick={addItem}
                  className="btn-secondary flex items-center text-sm"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Item
                </button>
              </div>

              {items.length === 0 ? (
                <div className="text-center py-8 border-2 border-dashed border-gray-200 rounded-lg">
                  <p className="text-gray-500 mb-4">No items added yet</p>
                  <button
                    type="button"
                    onClick={addItem}
                    className="btn-primary inline-flex items-center"
                  >
                    <Plus className="w-5 h-5 mr-2" />
                    Add First Item
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {items.map((item, index) => (
                    <div
                      key={index}
                      className="p-4 border border-gray-200 rounded-lg space-y-4"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-700">Item {index + 1}</span>
                        <button
                          type="button"
                          onClick={() => removeItem(index)}
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="grid grid-cols-4 gap-4">
                        <div className="col-span-2">
                          <label className="label">Product/Service</label>
                          <select
                            value={item.product_id || ''}
                            onChange={(e) => updateItem(index, 'product_id', e.target.value)}
                            className="input"
                            required
                          >
                            <option value="">Select product</option>
                            {products.map((product) => (
                              <option key={product.id} value={product.id}>
                                {product.name} - ${Number(product.price).toFixed(2)}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="label">Quantity</label>
                          <input
                            type="number"
                            min="1"
                            step="1"
                            value={item.quantity}
                            onChange={(e) => updateItem(index, 'quantity', e.target.value)}
                            className="input"
                            required
                          />
                        </div>
                        <div>
                          <label className="label">Unit Price</label>
                          <input
                            type="number"
                            min="0"
                            step="0.01"
                            value={item.unit_price}
                            onChange={(e) => updateItem(index, 'unit_price', e.target.value)}
                            className="input"
                            required
                          />
                        </div>
                      </div>
                      <div>
                        <label className="label">Description (optional)</label>
                        <input
                          type="text"
                          value={item.description || ''}
                          onChange={(e) => updateItem(index, 'description', e.target.value)}
                          className="input"
                          placeholder="Additional description"
                        />
                      </div>
                      <div className="text-right">
                        <span className="text-sm text-gray-500">Subtotal: </span>
                        <span className="font-medium text-gray-900">
                          ${(item.quantity * item.unit_price).toFixed(2)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Notes</h2>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="input"
                rows={4}
                placeholder="Add any notes or payment instructions..."
              />
            </div>
          </div>

          <div className="space-y-6">
            <div className="card bg-primary-50 sticky top-24">
              <h2 className="text-lg font-semibold text-primary-900 mb-4">Summary</h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-primary-700">Subtotal</span>
                  <span className="font-medium text-primary-900">
                    ${calculateSubtotal().toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-primary-700">Tax ({formData.tax_rate}%)</span>
                  <span className="font-medium text-primary-900">
                    ${calculateTax().toFixed(2)}
                  </span>
                </div>
                <div className="border-t border-primary-200 pt-3">
                  <div className="flex justify-between">
                    <span className="text-lg font-semibold text-primary-900">Total</span>
                    <span className="text-lg font-bold text-primary-900">
                      ${calculateTotal().toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-6 space-y-3">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="w-full btn-primary flex items-center justify-center"
                >
                  {isSaving ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    'Create Invoice'
                  )}
                </button>
                <Link
                  to="/invoices"
                  className="w-full btn-secondary flex items-center justify-center"
                >
                  Cancel
                </Link>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default CreateInvoice;
