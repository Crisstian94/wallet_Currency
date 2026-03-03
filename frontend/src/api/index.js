import axios from 'axios';

const api = axios.create({
    baseURL: 'http://192.168.100.110:8889', // Adjust the base URL as needed
    headers: {
        'Content-Type': 'application/json',
    },
});
export default api;