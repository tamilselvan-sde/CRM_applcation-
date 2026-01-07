import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  Users,
  Package,
  FileText,
  Settings,
  LogOut,
  Menu,
  X,
  ChevronDown,
  User,
} from 'lucide-react';

const Layout: React.FC = () => {
  const { user, logout, hasRole, hasPermission } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard, permission: null },
    { path: '/customers', label: 'Customers', icon: Users, permission: 'customers:read' },
    { path: '/products', label: 'Products', icon: Package, permission: 'products:read' },
    { path: '/invoices', label: 'Invoices', icon: FileText, permission: 'invoices:read' },
    { path: '/users', label: 'Users', icon: Settings, permission: null, roles: ['admin'] },
  ];

  const filteredNavItems = navItems.filter(item => {
    if (item.roles && !hasRole(item.roles)) return false;
    if (item.permission && !hasPermission(item.permission)) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between h-16 px-6 bg-primary-600">
          <Link to="/" className="text-xl font-bold text-white">
            CRM App
          </Link>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-white hover:text-primary-200"
          >
            <X size={24} />
          </button>
        </div>
        <nav className="mt-6 px-4">
          {filteredNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center px-4 py-3 mb-2 rounded-lg transition-colors duration-200 ${
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Icon size={20} className="mr-3" />
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-40 bg-white shadow-sm">
          <div className="flex items-center justify-between h-16 px-4 lg:px-8">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-gray-600 hover:text-gray-900"
            >
              <Menu size={24} />
            </button>
            <div className="flex-1" />
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center space-x-3 text-gray-700 hover:text-gray-900"
              >
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <User size={18} className="text-primary-600" />
                </div>
                <span className="hidden md:block font-medium">{user?.username}</span>
                <span className="hidden md:block text-sm text-gray-500 capitalize">({user?.role})</span>
                <ChevronDown size={16} />
              </button>
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 py-1">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900">{user?.email}</p>
                    <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <LogOut size={16} className="mr-2" />
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="p-4 lg:p-8">
          <Outlet />
        </main>
      </div>

      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default Layout;
