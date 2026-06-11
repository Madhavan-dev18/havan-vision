import axios from 'axios';

// FIXED: Uses Vite environment variable for production, falls back to localhost for dev
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            window.dispatchEvent(new Event('auth_change'));
        }
        return Promise.reject(error);
    }
);

export default api;