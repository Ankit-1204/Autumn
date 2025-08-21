import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
baseURL: API_BASE,
timeout: 10000,
headers: { 'Content-Type': 'application/json' }
})


api.interceptors.request.use((cfg) => {
const token = localStorage.getItem('token')
if (token) cfg.headers.Authorization = `Bearer ${token}`
return cfg
})

export default api