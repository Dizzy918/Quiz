import { createContext, useCallback, useContext, useEffect, useState } from 'react'

import { api } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Restores the session on a page refresh and primes the CSRF cookie.
  useEffect(() => {
    let cancelled = false

    async function restore() {
      try {
        await api.csrf()
        const me = await api.me()
        if (!cancelled) setUser(me)
      } catch {
        if (!cancelled) setUser(null)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    restore()
    return () => {
      cancelled = true
    }
  }, [])

  const register = useCallback(async (payload) => {
    await api.register(payload)
    const me = await api.login({
      username: payload.username,
      password: payload.password,
    })
    setUser(me)
    return me
  }, [])

  const login = useCallback(async (payload) => {
    const me = await api.login(payload)
    setUser(me)
    return me
  }, [])

  const logout = useCallback(async () => {
    await api.logout()
    setUser(null)
  }, [])

  const updateProfile = useCallback(async (payload) => {
    const me = await api.updateProfile(payload)
    setUser(me)
    return me
  }, [])

  return (
    <AuthContext.Provider
      value={{ user, loading, register, login, logout, updateProfile }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === null) {
    throw new Error('useAuth must be used inside an AuthProvider')
  }
  return context
}
