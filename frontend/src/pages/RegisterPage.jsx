import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'

import { ApiError } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import Flourish from '../components/Flourish'
import FormField from '../components/FormField'

const EMPTY = {
  username: '',
  email: '',
  nickname: '',
  password: '',
  password_confirm: '',
}

export default function RegisterPage() {
  const { user, register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState(EMPTY)
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
      await register(form)
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
      <h1>Посвещение</h1>
      <p className="tagline">Впиши името си в списъка на рицарите.</p>
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

        <FormField id="email" label="Имейл" error={fieldError('email')}>
          <input
            id="email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            autoComplete="email"
            required
          />
        </FormField>

        <FormField id="nickname" label="Прякор" error={fieldError('nickname')}>
          <input
            id="nickname"
            name="nickname"
            value={form.nickname}
            onChange={handleChange}
            maxLength={30}
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
            autoComplete="new-password"
            required
          />
        </FormField>

        <FormField
          id="password_confirm"
          label="Повторете паролата"
          error={fieldError('password_confirm')}
        >
          <input
            id="password_confirm"
            name="password_confirm"
            type="password"
            value={form.password_confirm}
            onChange={handleChange}
            autoComplete="new-password"
            required
          />
        </FormField>

        <button type="submit" disabled={submitting}>
          {submitting ? 'Вписване…' : 'Положи клетва'}
        </button>
      </form>

      <p className="switch">
        Вече си посветен? <Link to="/login">Към портата</Link>
      </p>
    </section>
  )
}
