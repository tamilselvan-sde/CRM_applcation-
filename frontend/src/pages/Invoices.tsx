import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { invoicesApi, Invoice } from '../services/api';
import { FileText, Plus, Eye, Download, Trash2 } from 'lucide-react';
import { format } from 'date-fns';

const Invoices: React.FC = () => {
  const { hasPermission } = useAuth();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  const fetchInvoices = useCallback(async () => {
    try {
      const params: { status?: string } = {};
      if (statusFilter) params.status = statusFilter;
      const data = await invoicesApi.getAll(params);
      setInvoices(data);
    } catch (err) {
      console.error('Failed to fetch invoices:', err);
    } finally {
      setIsLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    fetchInvoices();
  }, [fetchInvoices]);

  const handleDownloadPdf = async (invoice: Invoice) => {
    try {
      const blob = await invoicesApi.downloadPdf(invoice.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `invoice_${invoice.invoice_number}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download PDF:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this invoice?')) return;

    try {
      await invoicesApi.delete(id);
      fetchInvoices();
    } catch (error) {
      console.error('Failed to delete invoice:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <FileText className="w-7 h-7 mr-3 text-primary-600" />
            Invoices
          </h1>
          <p className="text-gray-500 mt-1">Manage and track your invoices</p>
        </div>
        {hasPermission('invoices:write') && (
          <Link to="/invoices/new" className="btn-primary flex items-center">
            <Plus className="w-5 h-5 mr-2" />
            Create Invoice
          </Link>
        )}
      </div>

      <div className="card">
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input max-w-xs"
          >
            <option value="">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="pending">Pending</option>
            <option value="paid">Paid</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>

        {invoices.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No invoices found</p>
            {hasPermission('invoices:write') && (
              <Link to="/invoices/new" className="btn-primary mt-4 inline-flex items-center">
                <Plus className="w-5 h-5 mr-2" />
                Create Your First Invoice
              </Link>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-primary-50">
                  <th className="table-header rounded-tl-lg">Invoice #</th>
                  <th className="table-header">Customer</th>
                  <th className="table-header">Issue Date</th>
                  <th className="table-header">Due Date</th>
                  <th className="table-header">Status</th>
                  <th className="table-header">Total</th>
                  <th className="table-header rounded-tr-lg text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="table-cell">
                      <Link
                        to={`/invoices/${invoice.id}`}
                        className="text-primary-600 hover:text-primary-700 font-medium"
                      >
                        {invoice.invoice_number}
                      </Link>
                    </td>
                    <td className="table-cell text-gray-600">
                      {invoice.customer_name || 'N/A'}
                    </td>
                    <td className="table-cell text-gray-600">
                      {format(new Date(invoice.issue_date), 'MMM dd, yyyy')}
                    </td>
                    <td className="table-cell text-gray-600">
                      {invoice.due_date
                        ? format(new Date(invoice.due_date), 'MMM dd, yyyy')
                        : '-'}
                    </td>
                    <td className="table-cell">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full capitalize ${getStatusColor(
                          invoice.status
                        )}`}
                      >
                        {invoice.status}
                      </span>
                    </td>
                    <td className="table-cell font-medium text-gray-900">
                      ${Number(invoice.total).toLocaleString('en-US', {
                        minimumFractionDigits: 2,
                      })}
                    </td>
                    <td className="table-cell text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <Link
                          to={`/invoices/${invoice.id}`}
                          className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg"
                          title="View"
                        >
                          <Eye className="w-4 h-4" />
                        </Link>
                        <button
                          onClick={() => handleDownloadPdf(invoice)}
                          className="p-2 text-green-600 hover:bg-green-50 rounded-lg"
                          title="Download PDF"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        {hasPermission('invoices:delete') && (
                          <button
                            onClick={() => handleDelete(invoice.id)}
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
    </div>
  );
};

export default Invoices;
