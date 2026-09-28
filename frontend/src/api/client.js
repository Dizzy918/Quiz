const API_BASE = '/api'

function readCookie(name) {
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`))
  return match ? decodeURIComponent(match[2]) : null
}

export class ApiError extends Error {
  constructor(status, errors) {
    super('Request failed')
    this.status = status
    this.errors = errors
  }

  /** First message for a field, or the generic one when the field is clean. */
  messageFor(field) {
    const value = this.errors?.[field]
    return Array.isArray(value) ? value[0] : value
  }

  /** Error not tied to a single field, or null when the fields say it all. */
  get generalMessage() {
    const explicit = this.messageFor('non_field_errors') ?? this.messageFor('detail')
    if (explicit) {
      return explicit
    }
    return Object.keys(this.errors ?? {}).length > 0
      ? null
      : 'Нещо се обърка. Опитайте отново.'
  }
}

async function request(path, { method = 'GET', body } = {}) {
  const headers = {}
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }
  if (method !== 'GET' && method !== 'HEAD') {
    const token = readCookie('csrftoken')
    if (token) {
      headers['X-CSRFToken'] = token
    }
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    credentials: 'same-origin',
    body: body === undefined ? undefined : JSON.stringify(body),
  })

  if (response.status === 204) {
    return null
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new ApiError(response.status, data?.errors ?? {})
  }

  return data
}

export const api = {
  csrf: () => request('/auth/csrf/'),
  register: (payload) => request('/auth/register/', { method: 'POST', body: payload }),
  login: (payload) => request('/auth/login/', { method: 'POST', body: payload }),
  logout: () => request('/auth/logout/', { method: 'POST' }),
  me: () => request('/auth/me/'),
  updateProfile: (payload) => request('/auth/me/', { method: 'PATCH', body: payload }),
}
