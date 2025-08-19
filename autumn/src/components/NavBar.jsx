import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'


export default function NavBar() {
const auth = useAuth()
const navigate = useNavigate()


const handleLogout = () => {
auth.logout()
navigate('/login')
}


return (
<nav className="bg-white shadow p-3 flex items-center justify-between">
<div className="flex items-center gap-4">
<Link to="/" className="font-bold text-lg">Workflow Platform</Link>
{auth.token && <Link to="/dashboard" className="text-sm text-gray-600">Dashboard</Link>}
</div>
<div>
{auth.token ? (
<button onClick={handleLogout} className="px-3 py-1 bg-red-500 text-white rounded">Logout</button>
) : (
<div className="space-x-2">
<Link to="/login" className="px-3 py-1 border rounded text-sm">Login</Link>
<Link to="/signup" className="px-3 py-1 bg-blue-500 text-white rounded text-sm">Sign up</Link>
</div>
)}
</div>
</nav>
)
}