export type TokenResponse = {
  access_token: string
  token_type: string
  username: string
  role: number   // 1=普通用户  2=VIP  3=管理员
}

function decodeJwtRole(token: string): number {
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
    return typeof payload.role === 'number' ? payload.role : 1
  } catch {
    return 1
  }
}

type ApiEnvelope<T> = {
  code?: number
  message?: string
  detail?: string
  data?: T
  items?: T
  list?: T
  results?: T
}

export type InterviewSetupPayload = {
  job_title: string
  job_description: string
  experience_level: string
  mode: string
  resume_text: string
  session_uuid: string
}

export type InterviewSessionCreateResponse = {
  success: boolean
  session_uuid: string
}

export const API_BASE_URL = 'http://127.0.0.1:8000/api'
export const AUTH_STORAGE_KEY = 'interview-ai-auth'
export const INTERVIEW_SETUP_STORAGE_KEY = 'interview-ai-setup'

function extractEnvelopePayload<T>(payload: unknown): T | null {
  if (!payload || typeof payload !== 'object') return null

  const wrapped = payload as ApiEnvelope<T>
  if (wrapped.data !== undefined) return wrapped.data
  if (wrapped.items !== undefined) return wrapped.items
  if (wrapped.list !== undefined) return wrapped.list
  if (wrapped.results !== undefined) return wrapped.results

  return payload as T
}

export function extractApiPayload<T>(payload: unknown): T | null {
  return extractEnvelopePayload<T>(payload)
}

export function getApiErrorMessage(payload: unknown, fallback: string): string {
  if (!payload || typeof payload !== 'object') return fallback

  const wrapped = payload as ApiEnvelope<unknown>
  if (typeof wrapped.detail === 'string' && wrapped.detail.trim()) return wrapped.detail
  if (typeof wrapped.message === 'string' && wrapped.message.trim() && wrapped.message !== 'success') {
    return wrapped.message
  }

  const nested = extractEnvelopePayload<Record<string, unknown>>(payload)
  if (!nested || typeof nested !== 'object') return fallback

  const nestedDetail = nested.detail
  if (typeof nestedDetail === 'string' && nestedDetail.trim()) return nestedDetail

  const nestedMessage = nested.message
  if (typeof nestedMessage === 'string' && nestedMessage.trim() && nestedMessage !== 'success') {
    return nestedMessage
  }

  return fallback
}

function toTokenResponse(payload: unknown): TokenResponse | null {
  const normalized = extractEnvelopePayload<Record<string, unknown>>(payload)
  if (!normalized || typeof normalized !== 'object') return null

  const accessToken = normalized.access_token
  const username = normalized.username
  const tokenType = normalized.token_type

  if (typeof accessToken !== 'string' || !accessToken.trim()) return null
  if (typeof username !== 'string' || !username.trim()) return null

  return {
    access_token: accessToken,
    token_type: typeof tokenType === 'string' && tokenType.trim() ? tokenType : 'bearer',
    username,
    role: decodeJwtRole(accessToken),
  }
}

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
    return toTokenResponse(JSON.parse(raw))
  } catch {
    localStorage.removeItem(AUTH_STORAGE_KEY)
    return null
  }
}

export function saveAuthSession(session: TokenResponse | unknown) {
  const normalized = toTokenResponse(session)
  if (!normalized) {
    throw new Error('登录响应缺少有效的用户信息，请稍后重试。')
  }

  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(normalized))
}

export function clearAuthSession() {
  localStorage.removeItem(AUTH_STORAGE_KEY)
}

export async function createInterviewSession(
  payload: Omit<InterviewSetupPayload, 'session_uuid'>,
): Promise<InterviewSessionCreateResponse> {
  const authSession = loadAuthSession()
  if (!authSession?.access_token) {
    throw new Error('未检测到登录状态，请先登录后再创建面试。')
  }

  const response = await fetch(`${API_BASE_URL}/interview/create-session`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `${authSession.token_type} ${authSession.access_token}`,
    },
    body: JSON.stringify(payload),
  })

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(getApiErrorMessage(data, '创建面试会话失败，请稍后重试。'))
  }

  const sessionPayload = extractApiPayload<InterviewSessionCreateResponse>(data)
  if (!sessionPayload?.session_uuid) {
    throw new Error('创建面试会话失败：服务响应缺少 session_uuid。')
  }

  return sessionPayload
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
