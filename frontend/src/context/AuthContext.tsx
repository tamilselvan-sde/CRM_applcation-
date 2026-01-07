import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi, User, Role } from '../services/api';

interface AuthContextType {
  user: User | null;
  roles: Role[];
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
  hasRole: (roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [roles, setRoles] = useState<Role[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const userData = await authApi.getMe();
          setUser(userData);
          const rolesData = await authApi.getRoles();
          setRoles(rolesData);
        } catch {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = async (token: string) => {
    localStorage.setItem('token', token);
    const userData = await authApi.getMe();
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    const rolesData = await authApi.getRoles();
    setRoles(rolesData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setRoles([]);
  };

  const getUserPermissions = (): string[] => {
    if (!user) return [];
    const userRole = roles.find(r => r.name === user.role);
    return userRole?.permissions || [];
  };

  const hasPermission = (permission: string): boolean => {
    const permissions = getUserPermissions();
    if (permissions.includes('all')) return true;
    return permissions.includes(permission);
  };

  const hasRole = (allowedRoles: string[]): boolean => {
    if (!user) return false;
    return allowedRoles.includes(user.role);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        roles,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        hasPermission,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
