import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import NavBar from './components/NavBar'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import WorkFlowView from './pages/WorkFlowView'


function ProtectedRoute({ children }) {
    const token = useAuth()
    if (!token) return <Navigate to="/login" replace />
    return children
}


export default function App() {
return (
<AuthProvider>
<Router>
<NavBar />
<Routes>
<Route path="/" element={<div className="p-6">Welcome — <Link to="/dashboard" className="text-blue-600">Dashboard</Link></div>} />
<Route path="/signup" element={<Signup />} />
<Route path="/login" element={<Login />} />
<Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
<Route path="/workflows/:id" element={<ProtectedRoute><WorkFlowView /></ProtectedRoute>} />
<Route path="*" element={<div className="p-6">Not found</div>} />
</Routes>
</Router>
</AuthProvider>
)
}