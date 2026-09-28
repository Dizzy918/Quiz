import { Navigate, Route, Routes } from 'react-router-dom'

import './App.css'
import { useAuth } from './auth/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Shield from './components/Shield'
import LoginPage from './pages/LoginPage'
import ProfilePage from './pages/ProfilePage'
import RegisterPage from './pages/RegisterPage'

export default function App() {
  const { loading } = useAuth()

  return (
    <div className="app">
      <header className="app-header">
        <span className="brand">
          <Shield avatarKey="knight-1" size={26} />
          Quiz Conquest
        </span>
      </header>

      <main>
        {loading ? (
          <p className="status">Разгъване на картата…</p>
        ) : (
          <Routes>
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/profile" replace />} />
          </Routes>
        )}
      </main>
    </div>
  )
}
