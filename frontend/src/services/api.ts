import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  role?: string;
}

export interface User {
  _id: string;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Role {
  _id: string;
  name: string;
  description?: string;
  permissions: string[];
}

export interface Customer {
  id: number;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: number;
  name: string;
  description?: string;
  sku?: string;
  price: number;
  unit: string;
  is_service: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface InvoiceItem {
  id?: number;
  product_id: number;
  description?: string;
  quantity: number;
  unit_price: number;
  subtotal?: number;
  product_name?: string;
}

export interface Invoice {
  id: number;
  invoice_number: string;
  customer_id: number;
  customer_name?: string;
  customer_email?: string;
  status: 'draft' | 'pending' | 'paid' | 'cancelled';
  issue_date: string;
  due_date?: string;
  subtotal: number;
  tax_rate: number;
  tax_amount: number;
  total: number;
  notes?: string;
  pdf_path?: string;
  created_at: string;
  updated_at: string;
  items: InvoiceItem[];
}

export const authApi = {
  login: async (credentials: LoginCredentials) => {
    const response = await api.post<{ access_token: string; token_type: string }>('/auth/login', credentials);
    return response.data;
  },
  register: async (data: RegisterData) => {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },
  getMe: async () => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
  getRoles: async () => {
    const response = await api.get<Role[]>('/auth/roles');
    return response.data;
  },
  getUsers: async () => {
    const response = await api.get<User[]>('/auth/users');
    return response.data;
  },
  updateUser: async (userId: string, data: Partial<User>) => {
    const response = await api.put<User>(`/auth/users/${userId}`, data);
    return response.data;
  },
  deleteUser: async (userId: string) => {
    await api.delete(`/auth/users/${userId}`);
  },
};

export const customersApi = {
  getAll: async (params?: { skip?: number; limit?: number; search?: string }) => {
    const response = await api.get<Customer[]>('/customers', { params });
    return response.data;
  },
  getById: async (id: number) => {
    const response = await api.get<Customer>(`/customers/${id}`);
    return response.data;
  },
  create: async (data: Omit<Customer, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await api.post<Customer>('/customers', data);
    return response.data;
  },
  update: async (id: number, data: Partial<Customer>) => {
    const response = await api.put<Customer>(`/customers/${id}`, data);
    return response.data;
  },
  delete: async (id: number) => {
    await api.delete(`/customers/${id}`);
  },
};

export const productsApi = {
  getAll: async (params?: { skip?: number; limit?: number; search?: string; is_service?: boolean; is_active?: boolean }) => {
    const response = await api.get<Product[]>('/products', { params });
    return response.data;
  },
  getById: async (id: number) => {
    const response = await api.get<Product>(`/products/${id}`);
    return response.data;
  },
  create: async (data: Omit<Product, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await api.post<Product>('/products', data);
    return response.data;
  },
  update: async (id: number, data: Partial<Product>) => {
    const response = await api.put<Product>(`/products/${id}`, data);
    return response.data;
  },
  delete: async (id: number) => {
    await api.delete(`/products/${id}`);
  },
};

export const invoicesApi = {
  getAll: async (params?: { skip?: number; limit?: number; status?: string; customer_id?: number }) => {
    const response = await api.get<Invoice[]>('/invoices', { params });
    return response.data;
  },
  getById: async (id: number) => {
    const response = await api.get<Invoice>(`/invoices/${id}`);
    return response.data;
  },
  create: async (data: { customer_id: number; status?: string; due_date?: string; tax_rate?: number; notes?: string; items: InvoiceItem[] }) => {
    const response = await api.post<Invoice>('/invoices', data);
    return response.data;
  },
  update: async (id: number, data: Partial<Invoice>) => {
    const response = await api.put<Invoice>(`/invoices/${id}`, data);
    return response.data;
  },
  delete: async (id: number) => {
    await api.delete(`/invoices/${id}`);
  },
  downloadPdf: async (id: number) => {
    const response = await api.get(`/invoices/${id}/pdf`, { responseType: 'blob' });
    return response.data;
  },
};

export default api;
