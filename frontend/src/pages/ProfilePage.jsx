import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { ApiError } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import Flourish from '../components/Flourish'
import FormField from '../components/FormField'
import Shield, { AVATAR_KEYS, SHIELDS } from '../components/Shield'

export default function ProfilePage() {
  const { user, logout, updateProfile } = useAuth()
  const navigate = useNavigate()
  const [nickname, setNickname] = useState(user.profile?.nickname ?? '')
  const [avatarKey, setAvatarKey] = useState(user.profile?.avatar_key ?? AVATAR_KEYS[0])
  const [errors, setErrors] = useState({})
  const [generalError, setGeneralError] = useState(null)
  const [saved, setSaved] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setErrors({})
    setGeneralError(null)
    setSaved(false)
    setSubmitting(true)

    try {
      await updateProfile({ nickname, avatar_key: avatarKey })
      setSaved(true)
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

  async function handleLogout() {
    try {
      await logout()
    } finally {
      navigate('/login', { replace: true })
    }
  }

  const fieldError = (name) => {
    const value = errors[name]
    return Array.isArray(value) ? value[0] : value
  }

  return (
    <section className="card">
      <header className="profile-header">
        <div className="crest">
          <Shield avatarKey={user.profile?.avatar_key} size={62} />
        </div>
        <div>
          <h1>{user.profile?.nickname ?? user.username}</h1>
          <p className="muted">
            {user.username} · {user.email}
          </p>
        </div>
      </header>

      <Flourish />

      {generalError ? (
        <p className="form-error" role="alert">
          {generalError}
        </p>
      ) : null}
      {saved ? (
        <p className="form-success" role="status">
          Гербът е пречертан.
        </p>
      ) : null}

      <form onSubmit={handleSubmit} noValidate>
        <FormField id="nickname" label="Име в битка" error={fieldError('nickname')}>
          <input
            id="nickname"
            name="nickname"
            value={nickname}
            onChange={(event) => setNickname(event.target.value)}
            maxLength={30}
            required
          />
        </FormField>

        <fieldset className="avatars">
          <legend>Герб</legend>
          {SHIELDS.map((shield) => (
            <label
              key={shield.key}
              className={`avatar-option${avatarKey === shield.key ? ' selected' : ''}`}
            >
              <input
                type="radio"
                name="avatar_key"
                value={shield.key}
                checked={avatarKey === shield.key}
                onChange={() => setAvatarKey(shield.key)}
              />
              <Shield avatarKey={shield.key} size={46} />
              {shield.name}
            </label>
          ))}
          {fieldError('avatar_key') ? (
            <p className="field-error" role="alert">
              {fieldError('avatar_key')}
            </p>
          ) : null}
        </fieldset>

        <div className="actions">
          <button type="submit" disabled={submitting}>
            {submitting ? 'Запечатване…' : 'Запечатай'}
          </button>
          <button type="button" className="secondary" onClick={handleLogout}>
            Напусни
          </button>
        </div>
      </form>
    </section>
  )
}
