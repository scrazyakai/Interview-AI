export type TokenResponse = {
  access_token: string
  token_type: string
  username: string
}

export type InterviewSetupPayload = {
  job_title: string
  job_description: string
  experience_level: string
  mode: string
  resume_text: string
  session_uuid: string
}

export const API_BASE_URL = 'http://127.0.0.1:8000/api'
export const AUTH_STORAGE_KEY = 'interview-ai-auth'
export const INTERVIEW_SETUP_STORAGE_KEY = 'interview-ai-setup'

export function getInterviewWebSocketUrl(token: string, sessionUuid: string) {
  const apiUrl = new URL(API_BASE_URL)
  apiUrl.protocol = apiUrl.protocol === 'https:' ? 'wss:' : 'ws:'
  apiUrl.pathname = '/api/interview/ws'
  apiUrl.searchParams.set('token', token)
  apiUrl.searchParams.set('session_uuid', sessionUuid)
  apiUrl.hash = ''
  return apiUrl.toString()
}

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

export function loadInterviewSetup(): InterviewSetupPayload | null {
  const raw = localStorage.getItem(INTERVIEW_SETUP_STORAGE_KEY)
  if (!raw) return null

  try {
    return JSON.parse(raw) as InterviewSetupPayload
  } catch {
    localStorage.removeItem(INTERVIEW_SETUP_STORAGE_KEY)
    return null
  }
}

export function saveInterviewSetup(payload: InterviewSetupPayload) {
  localStorage.setItem(INTERVIEW_SETUP_STORAGE_KEY, JSON.stringify(payload))
}

export function clearInterviewSetup() {
  localStorage.removeItem(INTERVIEW_SETUP_STORAGE_KEY)
}
