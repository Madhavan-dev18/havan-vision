import axios from 'axios';

// FIXED: Uses Vite environment variable for production, falls back to localhost for dev
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';

const api = axios.create({
    baseURL: API_URL,
    withCredentials: true, // MUST BE TRUE TO SEND HTTPONLY COOKIES
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // Note: Token cleanup should now be handled by the server clearing the secure cookies
            // We just clear the user session from local state to trigger the UI redirect
            localStorage.removeItem('user');
            window.dispatchEvent(new Event('auth_change'));
        }
        return Promise.reject(error);
    }
);

export default api;