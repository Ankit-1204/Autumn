import React, { useState } from 'react'
import { useNavigate , Link} from 'react-router-dom'
import api from '../api/axios'
import { useAuth } from '../contexts/AuthContext'


export default function Login() {
const [email, setEmail] = useState('')
const [password, setPassword] = useState('')
const [loading, setLoading] = useState(false)
const auth = useAuth()
const navigate = useNavigate()


async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    try {
        const res = await api.post('/auth/login', { email, password })
        const token = res.data.access_token
        if (!token) throw new Error('No token returned')
        auth.login(token)
        navigate('/dashboard')
    } catch (err) {
        console.error(err)
        alert(err.response?.data?.detail || 'Login failed')
    } finally { setLoading(false) }
}


return (
<div className="min-h-screen flex items-center justify-center bg-gray-50">
<form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow w-96">
<h2 className="text-xl font-semibold mb-4">Login</h2>
<input className="w-full p-2 mb-3 border rounded" placeholder="Email" value={email} onChange={(e)=>setEmail(e.target.value)} />
<input className="w-full p-2 mb-3 border rounded" placeholder="Password" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} />
<button disabled={loading} className="w-full py-2 bg-blue-600 text-white rounded">{loading? 'Signing in...' : 'Sign in'}</button>
<p className="text-sm text-gray-500 mt-3">No account? <Link to="/signup" className="text-green-600">Sign up</Link></p>
</form>
</div>
)
}