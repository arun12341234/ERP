/**
 * API client with automatic token injection.
 * Wraps axios for easy authentication and error handling.
 */
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

const axiosInstance = axios.create({
  baseURL: `${API_URL}${API_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: inject auth token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle common errors
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/**
 * Simple API wrapper with common methods.
 */
export const api = {
  async get(url: string, params?: any) {
    const response = await axiosInstance.get(url, { params });
    return response.data;
  },

  async post(url: string, data?: any) {
    const response = await axiosInstance.post(url, data);
    return response.data;
  },

  async put(url: string, data?: any) {
    const response = await axiosInstance.put(url, data);
    return response.data;
  },

  async delete(url: string) {
    const response = await axiosInstance.delete(url);
    return response.data;
  },

  /**
   * Login helper that stores token.
   */
  async login(email: string, password: string) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await axiosInstance.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    const { access_token } = response.data;
    localStorage.setItem('token', access_token);

    // Fetch user profile
    const user = await this.get('/users/me');
    localStorage.setItem('user', JSON.stringify(user));

    return user;
  },

  /**
   * Register helper.
   */
  async register(email: string, password: string, fullName?: string) {
    const response = await axiosInstance.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  },

  /**
   * Logout helper.
   */
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
};
