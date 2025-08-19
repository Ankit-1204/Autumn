import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function useAuth() { return useContext(AuthContext) }
export function AuthProvider({ children }) {
const [token, setToken] = useState(() => localStorage.getItem('token'))


useEffect(() => {
if (token) localStorage.setItem('token', token)
else localStorage.removeItem('token')
}, [token])


const login = (tkn) => setToken(tkn)
const logout = () => setToken(null)


return (
<AuthContext.Provider value={{ token, login, logout }}>
{children}
</AuthContext.Provider>
)
}