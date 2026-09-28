import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'

import { ApiError } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import Flourish from '../components/Flourish'
import FormField from '../components/FormField'

export default function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [errors, setErrors] = useState({})
  const [generalError, setGeneralError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  if (user) {
    return <Navigate to="/profile" replace />
  }

  function handleChange(event) {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setErrors({})
    setGeneralError(null)
    setSubmitting(true)

    try {
      await login(form)
      navigate('/profile', { replace: true })
    } catch (error) {
      if (error instanceof ApiError) {
        setErrors(error.errors)
        setGeneralError(error.generalMessage)
      } else {
        setGeneralError('Няма връзка със сървъра.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  const fieldError = (name) => {
    const value = errors[name]
    return Array.isArray(value) ? value[0] : value
  }

  return (
    <section className="card">
      <h1>При портата</h1>
      <p className="tagline">Назови се и стражата ще те пусне.</p>
      <Flourish />

      {generalError ? (
        <p className="form-error" role="alert">
          {generalError}
        </p>
      ) : null}

      <form onSubmit={handleSubmit} noValidate>
        <FormField id="username" label="Потребителско име" error={fieldError('username')}>
          <input
            id="username"
            name="username"
            value={form.username}
            onChange={handleChange}
            autoComplete="username"
            required
          />
        </FormField>

        <FormField id="password" label="Парола" error={fieldError('password')}>
          <input
            id="password"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            autoComplete="current-password"
            required
          />
        </FormField>

        <button type="submit" disabled={submitting}>
          {submitting ? 'Отваряне…' : 'Влез'}
        </button>
      </form>

      <p className="switch">
        Още не си посветен? <Link to="/register">Положи клетва</Link>
      </p>
    </section>
  )
}
