import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { customersApi, productsApi, invoicesApi, Invoice } from '../services/api';
import { Users, Package, FileText, DollarSign, TrendingUp, Clock, Plus } from 'lucide-react';

const Dashboard: React.FC = () => {
  const { user, hasPermission } = useAuth();
  const [stats, setStats] = useState({
    customers: 0,
    products: 0,
    invoices: 0,
    totalRevenue: 0,
  });
  const [recentInvoices, setRecentInvoices] = useState<Invoice[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [customers, products, invoices] = await Promise.all([
          hasPermission('customers:read') ? customersApi.getAll() : Promise.resolve([]),
          hasPermission('products:read') ? productsApi.getAll() : Promise.resolve([]),
          hasPermission('invoices:read') ? invoicesApi.getAll() : Promise.resolve([]),
        ]);

        const totalRevenue = invoices
          .filter((inv: Invoice) => inv.status === 'paid')
          .reduce((sum: number, inv: Invoice) => sum + Number(inv.total), 0);

        setStats({
          customers: customers.length,
          products: products.length,
          invoices: invoices.length,
          totalRevenue,
        });

        setRecentInvoices(invoices.slice(0, 5));
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [hasPermission]);

  const statCards = [
    {
      title: 'Total Customers',
      value: stats.customers,
      icon: Users,
      color: 'bg-blue-500',
      link: '/customers',
      permission: 'customers:read',
    },
    {
      title: 'Products & Services',
      value: stats.products,
      icon: Package,
      color: 'bg-green-500',
      link: '/products',
      permission: 'products:read',
    },
    {
      title: 'Total Invoices',
      value: stats.invoices,
      icon: FileText,
      color: 'bg-purple-500',
      link: '/invoices',
      permission: 'invoices:read',
    },
    {
      title: 'Total Revenue',
      value: `$${stats.totalRevenue.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      icon: DollarSign,
      color: 'bg-yellow-500',
      link: '/invoices',
      permission: 'invoices:read',
    },
  ];

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
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Welcome back, {user?.first_name || user?.username}!</p>
        </div>
        {hasPermission('invoices:write') && (
          <Link to="/invoices/new" className="btn-primary flex items-center">
            <Plus className="w-5 h-5 mr-2" />
            New Invoice
          </Link>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards
          .filter((card) => hasPermission(card.permission))
          .map((card) => {
            const Icon = card.icon;
            return (
              <Link
                key={card.title}
                to={card.link}
                className="card hover:shadow-md transition-shadow duration-200"
              >
                <div className="flex items-center">
                  <div className={`${card.color} p-3 rounded-lg`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-500">{card.title}</p>
                    <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                  </div>
                </div>
              </Link>
            );
          })}
      </div>

      {hasPermission('invoices:read') && recentInvoices.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <Clock className="w-5 h-5 mr-2 text-primary-600" />
              Recent Invoices
            </h2>
            <Link to="/invoices" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View All
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Invoice</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Customer</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Status</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-600">Amount</th>
                </tr>
              </thead>
              <tbody>
                {recentInvoices.map((invoice) => (
                  <tr key={invoice.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <Link
                        to={`/invoices/${invoice.id}`}
                        className="text-primary-600 hover:text-primary-700 font-medium"
                      >
                        {invoice.invoice_number}
                      </Link>
                    </td>
                    <td className="py-3 px-4 text-gray-600">{invoice.customer_name || 'N/A'}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full capitalize ${getStatusColor(
                          invoice.status
                        )}`}
                      >
                        {invoice.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-medium text-gray-900">
                      ${Number(invoice.total).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center mb-4">
            <TrendingUp className="w-5 h-5 mr-2 text-primary-600" />
            Quick Actions
          </h2>
          <div className="grid grid-cols-2 gap-4">
            {hasPermission('customers:write') && (
              <Link
                to="/customers"
                className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
              >
                <Users className="w-8 h-8 text-primary-600 mb-2" />
                <p className="font-medium text-gray-900">Add Customer</p>
                <p className="text-sm text-gray-500">Create a new customer</p>
              </Link>
            )}
            {hasPermission('products:write') && (
              <Link
                to="/products"
                className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
              >
                <Package className="w-8 h-8 text-primary-600 mb-2" />
                <p className="font-medium text-gray-900">Add Product</p>
                <p className="text-sm text-gray-500">Create a new product</p>
              </Link>
            )}
            {hasPermission('invoices:write') && (
              <Link
                to="/invoices/new"
                className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
              >
                <FileText className="w-8 h-8 text-primary-600 mb-2" />
                <p className="font-medium text-gray-900">Create Invoice</p>
                <p className="text-sm text-gray-500">Generate a new invoice</p>
              </Link>
            )}
            {hasPermission('invoices:read') && (
              <Link
                to="/invoices"
                className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
              >
                <DollarSign className="w-8 h-8 text-primary-600 mb-2" />
                <p className="font-medium text-gray-900">View Invoices</p>
                <p className="text-sm text-gray-500">Manage all invoices</p>
              </Link>
            )}
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Role</h2>
          <div className="p-4 bg-primary-50 rounded-lg">
            <p className="text-lg font-semibold text-primary-700 capitalize">{user?.role}</p>
            <p className="text-sm text-primary-600 mt-1">
              {user?.role === 'admin' && 'Full system access - manage users, customers, products, and invoices'}
              {user?.role === 'manager' && 'Manage customers, products, and invoices'}
              {user?.role === 'staff' && 'Create invoices and view data'}
              {user?.role === 'viewer' && 'Read-only access to view data and download invoices'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
