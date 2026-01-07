import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { invoicesApi, Invoice } from '../services/api';
import { FileText, Download, ArrowLeft, Trash2 } from 'lucide-react';
import { format } from 'date-fns';

const InvoiceDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { hasPermission } = useAuth();
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchInvoice = async () => {
      if (!id) return;
      try {
        const data = await invoicesApi.getById(parseInt(id));
        setInvoice(data);
      } catch (error) {
        console.error('Failed to fetch invoice:', error);
        navigate('/invoices');
      } finally {
        setIsLoading(false);
      }
    };
    fetchInvoice();
  }, [id, navigate]);

  const handleDownloadPdf = async () => {
    if (!invoice) return;
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

  const handleDelete = async () => {
    if (!invoice) return;
    if (!confirm('Are you sure you want to delete this invoice?')) return;

    try {
      await invoicesApi.delete(invoice.id);
      navigate('/invoices');
    } catch (error) {
      console.error('Failed to delete invoice:', error);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!invoice) return;
    try {
      const updated = await invoicesApi.update(invoice.id, { status: newStatus as Invoice['status'] });
      setInvoice(updated);
    } catch (error) {
      console.error('Failed to update status:', error);
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

  if (!invoice) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Invoice not found</p>
        <Link to="/invoices" className="btn-primary mt-4 inline-flex items-center">
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Invoices
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
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
              Invoice {invoice.invoice_number}
            </h1>
            <p className="text-gray-500 mt-1">
              Created on {format(new Date(invoice.created_at), 'MMMM dd, yyyy')}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleDownloadPdf}
            className="btn-primary flex items-center"
          >
            <Download className="w-5 h-5 mr-2" />
            Download PDF
          </button>
          {hasPermission('invoices:delete') && (
            <button
              onClick={handleDelete}
              className="btn-danger flex items-center"
            >
              <Trash2 className="w-5 h-5 mr-2" />
              Delete
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Invoice Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Invoice Number</p>
                <p className="font-medium text-gray-900">{invoice.invoice_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <div className="flex items-center space-x-2">
                  <span
                    className={`inline-flex px-2 py-1 text-xs font-medium rounded-full capitalize ${getStatusColor(
                      invoice.status
                    )}`}
                  >
                    {invoice.status}
                  </span>
                  {hasPermission('invoices:write') && (
                    <select
                      value={invoice.status}
                      onChange={(e) => handleStatusChange(e.target.value)}
                      className="text-sm border border-gray-300 rounded px-2 py-1"
                    >
                      <option value="draft">Draft</option>
                      <option value="pending">Pending</option>
                      <option value="paid">Paid</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  )}
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-500">Issue Date</p>
                <p className="font-medium text-gray-900">
                  {format(new Date(invoice.issue_date), 'MMMM dd, yyyy')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Due Date</p>
                <p className="font-medium text-gray-900">
                  {invoice.due_date
                    ? format(new Date(invoice.due_date), 'MMMM dd, yyyy')
                    : 'Not set'}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Customer Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Name</p>
                <p className="font-medium text-gray-900">{invoice.customer_name || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="font-medium text-gray-900">{invoice.customer_email || 'N/A'}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Line Items</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-primary-50">
                    <th className="table-header rounded-tl-lg">Description</th>
                    <th className="table-header text-right">Qty</th>
                    <th className="table-header text-right">Unit Price</th>
                    <th className="table-header text-right rounded-tr-lg">Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {invoice.items.map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="table-cell">
                        <p className="font-medium text-gray-900">
                          {item.product_name || item.description || 'Item'}
                        </p>
                        {item.description && item.product_name && (
                          <p className="text-sm text-gray-500">{item.description}</p>
                        )}
                      </td>
                      <td className="table-cell text-right text-gray-600">
                        {Number(item.quantity)}
                      </td>
                      <td className="table-cell text-right text-gray-600">
                        ${Number(item.unit_price).toFixed(2)}
                      </td>
                      <td className="table-cell text-right font-medium text-gray-900">
                        ${Number(item.subtotal).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {invoice.notes && (
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Notes</h2>
              <p className="text-gray-600 whitespace-pre-wrap">{invoice.notes}</p>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="card bg-primary-50">
            <h2 className="text-lg font-semibold text-primary-900 mb-4">Summary</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-primary-700">Subtotal</span>
                <span className="font-medium text-primary-900">
                  ${Number(invoice.subtotal).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-primary-700">Tax ({Number(invoice.tax_rate)}%)</span>
                <span className="font-medium text-primary-900">
                  ${Number(invoice.tax_amount).toFixed(2)}
                </span>
              </div>
              <div className="border-t border-primary-200 pt-3">
                <div className="flex justify-between">
                  <span className="text-lg font-semibold text-primary-900">Total</span>
                  <span className="text-lg font-bold text-primary-900">
                    ${Number(invoice.total).toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions</h2>
            <div className="space-y-3">
              <button
                onClick={handleDownloadPdf}
                className="w-full btn-primary flex items-center justify-center"
              >
                <Download className="w-5 h-5 mr-2" />
                Download PDF
              </button>
              {hasPermission('invoices:write') && invoice.status === 'draft' && (
                <button
                  onClick={() => handleStatusChange('pending')}
                  className="w-full btn-secondary flex items-center justify-center"
                >
                  Send Invoice
                </button>
              )}
              {hasPermission('invoices:write') && invoice.status === 'pending' && (
                <button
                  onClick={() => handleStatusChange('paid')}
                  className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center"
                >
                  Mark as Paid
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvoiceDetail;
