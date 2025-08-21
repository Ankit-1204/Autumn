import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function useAuth() { return useContext(AuthContext) }
export function AuthProvider({ children }) {
const [token, setToken] = useState(() => localStorage.getItem('token'))
const [loading, setLoading] = useState(true)
const [user, setUser] = useState(null)

useEffect(() => {
    const validateToken = async () => {
      const storedToken = localStorage.getItem('token')
      if (storedToken) {
        try {
          // You can add a token validation endpoint here
          // For now, we'll just check if the token exists
          setToken(storedToken)
        } catch (error) {
          console.error('Token validation failed:', error)
          localStorage.removeItem('token')
          setToken(null)
        }
      }
      setLoading(false)
    }

    validateToken()
  }, [])

useEffect(() => {
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
      setUser(null)
    }
  }, [token])

  const login = (newToken) => {
    setToken(newToken)
  }

  const logout = () => {
    setToken(null)
    setUser(null)
  }


  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}