// frontend/src/services/api.js
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:6009/api', // Backend API base URL
    headers: {
        'Content-Type': 'application/json',
    },
});

axios.defaults.baseURL = 'http://127.0.0.1:6009';

// In src/services/api.js or at the top of App.jsx
axios.interceptors.request.use(request => {
    console.log('=== Starting Request ===');
    console.log('Request URL:', request.url);
    console.log('Request Method:', request.method);
    console.log('Request Headers:', request.headers);
    console.log('Request Data:', request.data);
    return request;
});

axios.interceptors.response.use(
    response => {
        console.log('=== Response Received ===');
        console.log('Response Status:', response.status);
        console.log('Response Data:', response.data);
        return response;
    },
    error => {
        console.error('=== Response Error ===');
        console.error('Error Config:', error.config);
        console.error('Error Message:', error.message);
        if (error.response) {
            console.error('Error Response:', error.response);
        }
        return Promise.reject(error);
    }
);

export default api;
