import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import NavBar from './components/NavBar'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import WorkFlowView from './pages/WorkFlowView'


function ProtectedRoute({ children }) {
    const { token, loading } = useAuth()
    if (loading) {
      return <div className="loading">Loading...</div>
    }
    if (!token) {
      return <Navigate to="/login" replace />
    }
    return children
  }

  function AppRoutes() {
    return (
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/workflows/:id" element={<ProtectedRoute><WorkFlowView /></ProtectedRoute>} />
        <Route path="*" element={<div className="container p-4">Page not found</div>} />
      </Routes>
    )
  }

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <NavBar />
          <main>
            <AppRoutes />
          </main>
        </div>
      </Router>
    </AuthProvider>
  )
}