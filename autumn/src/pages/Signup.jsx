import React, { useState } from 'react'
import { useNavigate,Link } from 'react-router-dom'
import api from '../api/axios'


export default function Signup() {
const [email, setEmail] = useState('')
const [password, setPassword] = useState('')
const [loading, setLoading] = useState(false)
const navigate = useNavigate()


async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    try {
        await api.post('/auth/signup', { email, password })
        navigate('/login')
    } catch (err) {
        console.error(err)
        alert(err.response?.data?.detail || 'Signup failed')
    } finally { setLoading(false) }
    }


return (
<div className="min-h-screen flex items-center justify-center bg-gray-50">
<form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow w-96">
<h2 className="text-xl font-semibold mb-4">Create account</h2>
<input className="w-full p-2 mb-3 border rounded" placeholder="Email" value={email} onChange={(e)=>setEmail(e.target.value)} />
<input className="w-full p-2 mb-3 border rounded" placeholder="Password" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} />
<button disabled={loading} className="w-full py-2 bg-green-600 text-white rounded">{loading? 'Creating...' : 'Sign up'}</button>
<p className="text-sm text-gray-500 mt-3">Already have an account? <Link to="/login" className="text-blue-500">Login</Link></p>
</form>
</div>
)
}