export type TokenResponse = {
  access_token: string
  token_type: string
  username: string
}

export const API_BASE_URL = 'http://127.0.0.1:8000/api'
export const AUTH_STORAGE_KEY = 'interview-ai-auth'

export function loadAuthSession(): TokenResponse | null {
  const raw = localStorage.getItem(AUTH_STORAGE_KEY)
  if (!raw) return null

  try {
    return JSON.parse(raw) as TokenResponse
  } catch {
    localStorage.removeItem(AUTH_STORAGE_KEY)
    return null
  }
}

export function saveAuthSession(session: TokenResponse) {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session))
}

export function clearAuthSession() {
  localStorage.removeItem(AUTH_STORAGE_KEY)
}
