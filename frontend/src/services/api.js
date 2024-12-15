// src/services/api.js
import axios from 'axios';

const instance = axios.create({
    baseURL: 'http://localhost:6009/api', // Ensure this matches your backend server URL
    headers: {
        'Content-Type': 'application/json',
    },
});

export default instance;
