<template>
  <div class="iv-root">
    <!-- ===== Specialized Interview Header ===== -->
    <header class="iv-header">
      <div class="iv-header-left">
        <button class="iv-exit-btn" type="button" @click="goHome">
          <svg viewBox="0 0 24 24" fill="none" style="width:18px;height:18px;flex-shrink:0;">
            <path d="M18 6 6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          退出
        </button>
        <div class="iv-header-divider"></div>
        <div class="iv-status-pill" :class="statusPillClass">
          <span class="iv-status-dot"></span>
          <span class="iv-status-text">{{ connectionStatusText }}</span>
        </div>
      </div>
      <div class="iv-header-right">
        <div class="iv-mode-pill">
          <svg viewBox="0 0 24 24" fill="none" style="width:16px;height:16px;flex-shrink:0;">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
            <path d="M12 7v5l3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>{{ modeLabel }} · {{ experienceLevelLabel }}</span>
        </div>
      </div>
    </header>

    <!-- ===== Main Arena ===== -->
    <main class="iv-main">
      <!-- Feedback / Error Banner -->
      <div v-if="errorMessage" class="iv-banner iv-banner--error">
        <svg viewBox="0 0 24 24" fill="none" style="width:18px;height:18px;flex-shrink:0;">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
          <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <span>{{ errorMessage }}</span>
      </div>
      <div v-else-if="assistantSpeaking" class="iv-banner iv-banner--info">
        <svg viewBox="0 0 24 24" fill="currentColor" style="width:18px;height:18px;flex-shrink:0;">
          <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
        </svg>
        <span><strong>实时反馈：</strong>AI 面试官正在作答，请稍候...</span>
      </div>

      <!-- 12-col grid -->
      <div class="iv-grid">
        <!-- ===== Left: AI Video Panel (7/12) ===== -->
        <section class="iv-video-panel">
          <!-- Dark video backdrop -->
          <div class="iv-video-bg">
            <img :src="interviewerImage" alt="AI Interviewer" class="iv-interviewer-img" />
            <div class="iv-video-gradient"></div>
          </div>

          <!-- AI Status Overlay (top-left) -->
          <div class="iv-ai-overlay">
            <div class="iv-ai-status-pill">
              <span class="iv-pulse-dot" :class="pulseDotClass"></span>
              <span class="iv-ai-status-label">{{ aiStatusLabel }}</span>
            </div>
            <!-- Voice bars (shown while assistant or user is speaking) -->
            <div v-if="assistantSpeaking || userSpeaking" class="iv-voice-bars">
              <div class="iv-voice-bar" style="height:8px;"></div>
              <div class="iv-voice-bar" style="height:16px;"></div>
              <div class="iv-voice-bar" style="height:12px;"></div>
              <div class="iv-voice-bar" style="height:20px;"></div>
              <div class="iv-voice-bar" style="height:10px;"></div>
            </div>
          </div>

          <!-- Candidate PiP (bottom-right) -->
          <div class="iv-pip">
            <video v-if="cameraOn" ref="videoRef" autoplay playsinline muted class="iv-pip-video"></video>
            <img v-else :src="userAvatar" alt="Candidate Preview" class="iv-pip-image" />
            <div class="iv-pip-label">您（候选人）</div>
          </div>

          <!-- Video Controls (bottom-center) -->
          <div class="iv-video-controls">
            <button class="iv-ctrl-btn" type="button" @click="toggleCamera" :title="cameraBtnTitle">
              <svg v-if="cameraOn" viewBox="0 0 24 24" fill="currentColor" style="width:22px;height:22px;">
                <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="currentColor" style="width:22px;height:22px;">
                <path d="M21 6.5l-4 4V7c0-.55-.45-1-1-1H9.82L21 17.18V6.5zM3.27 2L2 3.27 4.73 6H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.21 0 .39-.08.54-.18L19.73 21 21 19.73 3.27 2z"/>
              </svg>
              <span>摄像头</span>
            </button>

            <button
              class="iv-ctrl-btn iv-ctrl-btn--primary"
              type="button"
              :disabled="isConnecting"
              @click="toggleMicrophone"
              :title="micBtnTitle"
            >
              <svg v-if="microphoneOn" viewBox="0 0 24 24" fill="currentColor" style="width:26px;height:26px;">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15c-.08-.49-.49-.85-.98-.85-.61 0-1.09.54-1 1.14.49 3 2.89 5.35 5.91 5.78V20c0 .55.45 1 1 1s1-.45 1-1v-2.08c3.02-.43 5.42-2.78 5.91-5.78.1-.6-.39-1.14-1-1.14z"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="currentColor" style="width:26px;height:26px;">
                <path d="M19 11h-1.7c0 .74-.16 1.43-.43 2.05l1.23 1.23c.56-.98.9-2.09.9-3.28zm-4.02.17c0-.06.02-.11.02-.17V5c0-1.66-1.34-3-3-3S9 3.34 9 5v.18l5.98 5.99zM4.27 3L3 4.27l6.01 6.01V11c0 1.66 1.34 3 3 3 .23 0 .44-.03.65-.08l1.66 1.66c-.71.33-1.5.52-2.31.52-2.76 0-5.3-2.1-5.3-5.1H5c0 3.41 2.72 6.23 6 6.72V20c0 .55.45 1 1 1s1-.45 1-1v-2.28c.91-.13 1.77-.45 2.54-.9L19.73 21 21 19.73 4.27 3z"/>
              </svg>
              <span>{{ micBtnLabel }}</span>
            </button>

            <button class="iv-ctrl-btn" type="button" @click="endInterview" :disabled="endBtnDisabled" title="结束面试">
              <svg viewBox="0 0 24 24" fill="currentColor" style="width:22px;height:22px;">
                <path d="M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08c-.18-.17-.29-.42-.29-.7 0-.28.11-.53.29-.71C3.34 8.78 7.46 7 12 7s8.66 1.78 11.71 4.67c.18.18.29.43.29.71 0 .28-.11.53-.29.71l-2.48 2.48c-.18.18-.43.29-.71.29-.27 0-.52-.1-.7-.28-.79-.73-1.68-1.36-2.66-1.85-.33-.16-.56-.51-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/>
              </svg>
              <span>结束</span>
            </button>
          </div>
        </section>

        <!-- ===== Right: Chat + Controls (5/12) ===== -->
        <div class="iv-right">
          <!-- Chat History -->
          <section class="iv-chat glass-panel">
            <div class="iv-chat-head">
              <h3 class="iv-chat-title">实时转录</h3>
              <span class="iv-live-badge">{{ liveBadgeLabel }}</span>
            </div>
            <div ref="messageListRef" class="iv-messages">
              <div
                v-for="message in messages"
                :key="message.id"
                class="iv-msg-row"
                :class="msgRowClass(message.role)"
              >
                <div class="iv-msg-icon" :class="msgIconClass(message.role)">
                  <svg v-if="message.role === 'ai'" viewBox="0 0 24 24" fill="currentColor" style="width:16px;height:16px;">
                    <path d="M20 9V7c0-1.1-.9-2-2-2h-3c0-1.66-1.34-3-3-3S9 3.34 9 5H6c-1.1 0-2 .9-2 2v2c-1.66 0-3 1.34-3 3s1.34 3 3 3v4c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-4c1.66 0 3-1.34 3-3s-1.34-3-3-3zm-2 10H6V7h12v12zm-9-6c-.83 0-1.5-.67-1.5-1.5S8.17 10 9 10s1.5.67 1.5 1.5S9.83 13 9 13zm6 0c-.83 0-1.5-.67-1.5-1.5S14.17 10 15 10s1.5.67 1.5 1.5S15.83 13 15 13zm-3 2h-2v-1h2v1zm2 0h-2v-1h2v1z"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="currentColor" style="width:16px;height:16px;">
                    <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
                  </svg>
                </div>
                <div class="iv-msg-bubble" :class="msgBubbleClass(message.role)">
                  <p class="iv-msg-text">{{ message.text }}</p>
                </div>
              </div>
            </div>
          </section>

          <!-- Input Controls -->
          <section class="iv-controls glass-panel">
            <div class="iv-input-row">
              <!-- Big Mic Button -->
              <div class="iv-mic-wrap">
                <div class="iv-mic-glow" :class="micGlowClass"></div>
                <button
                  :class="['iv-mic-btn', micBtnClass]"
                  type="button"
                  :disabled="isConnecting"
                  @click="toggleMicrophone"
                >
                  <svg v-if="microphoneOn" viewBox="0 0 24 24" fill="currentColor" style="width:28px;height:28px;">
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15c-.08-.49-.49-.85-.98-.85-.61 0-1.09.54-1 1.14.49 3 2.89 5.35 5.91 5.78V20c0 .55.45 1 1 1s1-.45 1-1v-2.08c3.02-.43 5.42-2.78 5.91-5.78.1-.6-.39-1.14-1-1.14z"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="currentColor" style="width:28px;height:28px;">
                    <path d="M19 11h-1.7c0 .74-.16 1.43-.43 2.05l1.23 1.23c.56-.98.9-2.09.9-3.28zm-4.02.17c0-.06.02-.11.02-.17V5c0-1.66-1.34-3-3-3S9 3.34 9 5v.18l5.98 5.99zM4.27 3L3 4.27l6.01 6.01V11c0 1.66 1.34 3 3 3 .23 0 .44-.03.65-.08l1.66 1.66c-.71.33-1.5.52-2.31.52-2.76 0-5.3-2.1-5.3-5.1H5c0 3.41 2.72 6.23 6 6.72V20c0 .55.45 1 1 1s1-.45 1-1v-2.28c.91-.13 1.77-.45 2.54-.9L19.73 21 21 19.73 4.27 3z"/>
                  </svg>
                </button>
              </div>

              <!-- Text Input -->
              <div class="iv-text-wrap">
                <input
                  v-model="inputValue"
                  class="iv-text-input"
                  type="text"
                  placeholder="输入您的回答..."
                  :disabled="!isRealtimeReady"
                  @keydown.enter.prevent="sendMessage"
                />
                <button class="iv-send-btn" type="button" :disabled="!isRealtimeReady" @click="sendMessage">
                  <svg viewBox="0 0 24 24" fill="currentColor" style="width:20px;height:20px;">
                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Footer bar -->
            <div class="iv-footer-bar">
              <div class="iv-footer-info">
                <span class="iv-footer-label">{{ interviewSetup?.job_title ?? '模拟面试' }}</span>
                <div class="iv-footer-divider"></div>
                <span class="iv-footer-label">{{ modeLabel }}</span>
              </div>
              <button
                class="iv-end-btn"
                type="button"
                :disabled="endBtnDisabled"
                @click="endInterview"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" style="width:18px;height:18px;">
                  <path d="M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08c-.18-.17-.29-.42-.29-.7 0-.28.11-.53.29-.71C3.34 8.78 7.46 7 12 7s8.66 1.78 11.71 4.67c.18.18.29.43.29.71 0 .28-.11.53-.29.71l-2.48 2.48c-.18.18-.43.29-.71.29-.27 0-.52-.1-.7-.28-.79-.73-1.68-1.36-2.66-1.85-.33-.16-.56-.51-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/>
                </svg>
                结束面试
              </button>
            </div>
          </section>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import interviewerImageAsset from '../assets/Interviewer.png'
import intervieweeImageAsset from '../assets/Interviewee.png'
import {
  loadAuthSession,
  loadInterviewSetup,
  getInterviewWebSocketUrl,
} from '../utils/auth'

type ChatMessage = {
  id: number
  role: 'ai' | 'user'
  name: string
  text: string
}

type ServerEvent =
  | { type: 'ready'; sessionId: string }
  | { type: 'assistant_text'; text: string }
  | { type: 'assistant_done' }
  | { type: 'user_text_delta'; text: string }
  | { type: 'user_text'; text: string }
  | { type: 'user_speaking' }
  | { type: 'user_done' }
  | { type: 'error'; detail: string }

const router = useRouter()
const interviewSetup = loadInterviewSetup()
const interviewerImage = ref(interviewerImageAsset)
const userAvatar = ref(intervieweeImageAsset)

const messages = ref<ChatMessage[]>([
  {
    id: 1,
    role: 'ai',
    name: '系统',
    text: '面试配置已就绪。点击"开启麦克风"后开始实时模拟面试。',
  },
])

const inputValue = ref('')
const videoRef = ref<HTMLVideoElement | null>(null)
const messageListRef = ref<HTMLDivElement | null>(null)
const cameraOn = ref(false)
const microphoneOn = ref(false)
const assistantSpeaking = ref(false)
const userSpeaking = ref(false)
const connectionState = ref<'idle' | 'connecting' | 'connected' | 'error'>('idle')
const errorMessage = ref('')

const modeLabelMap: Record<string, string> = {
  technical: '技术面',
  behavioral: '行为面',
  mixed: '综合面',
}
const experienceLevelLabelMap: Record<string, string> = {
  intern: '应届生',
  junior: '初级',
  mid: '中级',
  senior: '高级',
}

const modeLabel = computed(() => modeLabelMap[interviewSetup?.mode ?? ''] ?? interviewSetup?.mode ?? '-')
const experienceLevelLabel = computed(
  () => experienceLevelLabelMap[interviewSetup?.experience_level ?? ''] ?? interviewSetup?.experience_level ?? '-',
)
const interviewSummary = computed(() => {
  if (!interviewSetup) return '请先创建面试。'
  return `${interviewSetup.job_title} / ${experienceLevelLabel.value} / ${modeLabel.value}`
})

const isConnecting = computed(() => connectionState.value === 'connecting')
const isRealtimeReady = computed(() => connectionState.value === 'connected')
const connectionStatusText = computed(() => {
  if (connectionState.value === 'connecting') return '连接中'
  if (connectionState.value === 'connected') return '实时通话已连接'
  if (connectionState.value === 'error') return '连接失败'
  return '未连接'
})
const connectionStatusClass = computed(() => {
  if (connectionState.value === 'connected') return 'statusConnected'
  if (connectionState.value === 'connecting') return 'statusConnecting'
  if (connectionState.value === 'error') return 'statusError'
  return 'statusIdle'
})

let cameraStream: MediaStream | null = null
let microphoneStream: MediaStream | null = null
let websocket: WebSocket | null = null
let inputAudioContext: AudioContext | null = null
let outputAudioContext: AudioContext | null = null
let processorNode: ScriptProcessorNode | null = null
let processorSourceNode: MediaStreamAudioSourceNode | null = null
let processorMuteNode: GainNode | null = null
let nextPlaybackTime = 0
let activeAssistantMessageId: number | null = null
let activeUserTranscriptMessageId: number | null = null
let isIntentionalSocketClose = false
let pendingPcmBytes = new Uint8Array(0)

function appendMessage(role: ChatMessage['role'], text: string) {
  messages.value.push({
    id: Date.now() + Math.floor(Math.random() * 1000),
    role,
    name: role === 'ai' ? 'AI 面试官' : '我',
    text,
  })
}

function appendAssistantChunk(text: string) {
  if (!text) return
  if (activeAssistantMessageId == null) {
    const id = Date.now() + Math.floor(Math.random() * 1000)
    activeAssistantMessageId = id
    messages.value.push({ id, role: 'ai', name: 'AI 面试官', text })
    return
  }

  const target = messages.value.find((message) => message.id === activeAssistantMessageId)
  if (target) target.text += text
}

function upsertUserTranscriptDraft(text: string) {
  if (!text) return

  if (activeUserTranscriptMessageId == null) {
    const id = Date.now() + Math.floor(Math.random() * 1000)
    activeUserTranscriptMessageId = id
    messages.value.push({ id, role: 'user', name: '我', text })
    return
  }

  const target = messages.value.find((message) => message.id === activeUserTranscriptMessageId)
  if (target) {
    target.text = text
  } else {
    activeUserTranscriptMessageId = null
    upsertUserTranscriptDraft(text)
  }
}

function finalizeUserTranscript(text?: string) {
  const finalText = text?.trim()
  const target =
    activeUserTranscriptMessageId == null
      ? null
      : messages.value.find((message) => message.id === activeUserTranscriptMessageId)

  if (target) {
    if (finalText) {
      target.text = finalText
    } else if (!target.text.trim()) {
      messages.value = messages.value.filter((message) => message.id !== activeUserTranscriptMessageId)
    }
  } else if (finalText) {
    appendMessage('user', finalText)
  }

  activeUserTranscriptMessageId = null
}

function markAssistantDone() {
  activeAssistantMessageId = null
  assistantSpeaking.value = false
}

async function startCamera() {
  if (cameraOn.value) return
  const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
  cameraStream = stream
  cameraOn.value = true
  await nextTick()
  if (videoRef.value) {
    videoRef.value.srcObject = stream
    await videoRef.value.play().catch(() => undefined)
  }
}

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop())
    cameraStream = null
  }
  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
  cameraOn.value = false
}

function createRealtimeSocket() {
  const authSession = loadAuthSession()
  const sessionUuid = interviewSetup?.session_uuid?.trim()

  if (!authSession?.access_token || !sessionUuid) {
    throw new Error('缺少登录态或面试会话信息，请重新创建面试。')
  }

  const socket = new WebSocket(getInterviewWebSocketUrl(authSession.access_token, sessionUuid))
  socket.binaryType = 'arraybuffer'
  isIntentionalSocketClose = false

  socket.onopen = () => {
    connectionState.value = 'connecting'
    errorMessage.value = ''
  }

  socket.onmessage = async (event) => {
    if (typeof event.data === 'string') {
      const payload = JSON.parse(event.data) as ServerEvent

      if (payload.type === 'ready') {
        connectionState.value = 'connected'
        appendMessage('ai', `面试已开始，当前配置：${interviewSummary.value}。请先做一个简短的自我介绍。`)
        return
      }
      if (payload.type === 'assistant_text') {
        assistantSpeaking.value = true
        appendAssistantChunk(payload.text)
        return
      }
      if (payload.type === 'assistant_done') {
        markAssistantDone()
        return
      }
      if (payload.type === 'user_text_delta') {
        upsertUserTranscriptDraft(payload.text)
        return
      }
      if (payload.type === 'user_text') {
        finalizeUserTranscript(payload.text)
        return
      }
      if (payload.type === 'user_speaking') {
        userSpeaking.value = true
        return
      }
      if (payload.type === 'user_done') {
        userSpeaking.value = false
        finalizeUserTranscript()
        return
      }
      if (payload.type === 'error') {
        connectionState.value = 'error'
        errorMessage.value = payload.detail
      }
      return
    }

    if (event.data instanceof ArrayBuffer) {
      await playAudioChunk(event.data)
    }
  }

  socket.onerror = () => {
    connectionState.value = 'error'
    errorMessage.value = '实时连接失败，请确认后端服务和语音配置可用。'
  }

  socket.onclose = () => {
    const shouldResetToIdle = isIntentionalSocketClose
    microphoneOn.value = false
    userSpeaking.value = false
    assistantSpeaking.value = false
    activeAssistantMessageId = null
    activeUserTranscriptMessageId = null

    if (shouldResetToIdle) {
      connectionState.value = 'idle'
      errorMessage.value = ''
      return
    }

    connectionState.value = 'error'
    if (!errorMessage.value) {
      errorMessage.value = '实时连接已断开，请检查后端日志。'
    }
  }

  websocket = socket
}

async function ensureOutputAudioContext() {
  if (!outputAudioContext) {
    outputAudioContext = new AudioContext({ sampleRate: 24000 })
  }
  if (outputAudioContext.state === 'suspended') {
    await outputAudioContext.resume()
  }
}

function convertFloat32ToInt16(buffer: Float32Array) {
  const pcm = new Int16Array(buffer.length)
  for (let index = 0; index < buffer.length; index += 1) {
    const sample = Math.max(-1, Math.min(1, buffer[index] ?? 0))
    pcm[index] = sample < 0 ? sample * 0x8000 : sample * 0x7fff
  }
  return pcm
}

function decodeInt16PcmChunk(chunk: ArrayBuffer) {
  const view = new DataView(chunk)
  const samples = new Float32Array(chunk.byteLength / 2)
  for (let index = 0; index < samples.length; index += 1) {
    samples[index] = view.getInt16(index * 2, true) / 32768.0
  }
  return samples
}

function appendPcmChunkToQueue(chunk: ArrayBuffer) {
  const incoming = new Uint8Array(chunk)
  const merged = new Uint8Array(pendingPcmBytes.length + incoming.length)
  merged.set(pendingPcmBytes, 0)
  merged.set(incoming, pendingPcmBytes.length)
  pendingPcmBytes = merged

  while (pendingPcmBytes.length >= 3200) {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) return
    const frame = pendingPcmBytes.slice(0, 3200)
    pendingPcmBytes = pendingPcmBytes.slice(3200)
    websocket.send(frame.buffer)
  }
}

async function playAudioChunk(chunk: ArrayBuffer) {
  await ensureOutputAudioContext()
  if (!outputAudioContext) return

  const samples = decodeInt16PcmChunk(chunk)
  const audioBuffer = outputAudioContext.createBuffer(1, samples.length, 24000)
  audioBuffer.copyToChannel(samples, 0)
  const source = outputAudioContext.createBufferSource()
  source.buffer = audioBuffer
  source.connect(outputAudioContext.destination)
  const now = outputAudioContext.currentTime
  const startAt = Math.max(now, nextPlaybackTime)
  source.start(startAt)
  nextPlaybackTime = startAt + audioBuffer.duration
}

async function setupMicrophoneProcessing(stream: MediaStream) {
  inputAudioContext = new AudioContext({ sampleRate: 16000 })
  await inputAudioContext.resume()
  processorSourceNode = inputAudioContext.createMediaStreamSource(stream)
  processorNode = inputAudioContext.createScriptProcessor(4096, 1, 1)
  processorMuteNode = inputAudioContext.createGain()
  processorMuteNode.gain.value = 0

  processorNode.onaudioprocess = (event) => {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) return
    const inputData = event.inputBuffer.getChannelData(0)
    const pcm16 = convertFloat32ToInt16(inputData)
    appendPcmChunkToQueue(pcm16.buffer.slice(0))
  }

  processorSourceNode.connect(processorNode)
  processorNode.connect(processorMuteNode)
  processorMuteNode.connect(inputAudioContext.destination)
}

async function startMicrophone() {
  if (microphoneOn.value) return
  connectionState.value = 'connecting'
  errorMessage.value = ''
  nextPlaybackTime = 0
  pendingPcmBytes = new Uint8Array(0)

  const stream = await navigator.mediaDevices.getUserMedia({
    audio: { channelCount: 1, noiseSuppression: true, echoCancellation: true },
    video: false,
  })

  microphoneStream = stream
  await ensureOutputAudioContext()
  createRealtimeSocket()
  await setupMicrophoneProcessing(stream)
  microphoneOn.value = true
}

function cleanupRealtimeResources() {
  if (processorNode) {
    processorNode.disconnect()
    processorNode.onaudioprocess = null
    processorNode = null
  }
  if (processorSourceNode) {
    processorSourceNode.disconnect()
    processorSourceNode = null
  }
  if (processorMuteNode) {
    processorMuteNode.disconnect()
    processorMuteNode = null
  }
  if (inputAudioContext) {
    void inputAudioContext.close().catch(() => undefined)
    inputAudioContext = null
  }
  if (microphoneStream) {
    microphoneStream.getTracks().forEach((track) => track.stop())
    microphoneStream = null
  }
  if (websocket) {
    if (pendingPcmBytes.length > 0 && websocket.readyState === WebSocket.OPEN) {
      const padding = new Uint8Array(3200)
      padding.set(pendingPcmBytes.slice(0, Math.min(pendingPcmBytes.length, 3200)))
      websocket.send(padding.buffer)
    }
    pendingPcmBytes = new Uint8Array(0)
    if (websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify({ type: 'stop' }))
    }
    isIntentionalSocketClose = true
    websocket.close()
    websocket = null
  }
}

function stopMicrophone() {
  cleanupRealtimeResources()
  microphoneOn.value = false
  connectionState.value = 'idle'
  assistantSpeaking.value = false
  userSpeaking.value = false
  activeAssistantMessageId = null
  activeUserTranscriptMessageId = null
}

function endInterview() {
  if (!microphoneOn.value && connectionState.value !== 'connecting') return
  stopMicrophone()
  appendMessage('ai', '本次面试已结束，实时连接已断开。')
}

async function toggleCamera() {
  if (cameraOn.value) {
    stopCamera()
    return
  }
  try {
    await startCamera()
  } catch {
    stopCamera()
  }
}

async function toggleMicrophone() {
  if (microphoneOn.value) {
    stopMicrophone()
    return
  }
  try {
    await startMicrophone()
  } catch (error) {
    stopMicrophone()
    connectionState.value = 'error'
    errorMessage.value = error instanceof Error ? error.message : '开启麦克风失败。'
  }
}

function sendMessage() {
  const text = inputValue.value.trim()
  if (!text || !websocket || websocket.readyState !== WebSocket.OPEN) return
  appendMessage('user', text)
  websocket.send(JSON.stringify({ type: 'text', content: text }))
  inputValue.value = ''
}

watch(videoRef, async (element) => {
  if (!element || !cameraStream) return
  element.srcObject = cameraStream
  await element.play().catch(() => undefined)
})

watch(
  messages,
  async () => {
    await nextTick()
    const list = messageListRef.value
    if (!list) return
    list.scrollTop = list.scrollHeight
  },
  { deep: true },
)

onBeforeUnmount(() => {
  stopCamera()
  stopMicrophone()
  if (outputAudioContext) {
    void outputAudioContext.close().catch(() => undefined)
    outputAudioContext = null
  }
})

// ── Template helpers (extracted to avoid single-quotes inside HTML attributes) ──

function goHome() {
  router.push('/')
}

const statusPillClass = computed(() => 'iv-status-pill--' + connectionState.value)

const pulseDotClass = computed(() => ({
  'iv-pulse-dot--active': isRealtimeReady.value || isConnecting.value,
}))

const aiStatusLabel = computed(() => {
  if (isRealtimeReady.value) return 'AI 面试官正在倾听'
  if (isConnecting.value) return '连接中...'
  return '等待开始'
})

const cameraBtnTitle = computed(() => (cameraOn.value ? '关闭摄像头' : '开启摄像头'))

const micBtnTitle = computed(() => (microphoneOn.value ? '关闭麦克风' : '开启麦克风'))

const micBtnLabel = computed(() => {
  if (microphoneOn.value) return '关闭麦克风'
  if (isConnecting.value) return '连接中...'
  return '开启麦克风'
})

const endBtnDisabled = computed(() => !microphoneOn.value && connectionState.value !== 'connecting')

const liveBadgeLabel = computed(() => (isRealtimeReady.value ? '实时' : '等待中'))

function msgRowClass(role: string) {
  return role === 'user' ? 'iv-msg-row--user' : 'iv-msg-row--ai'
}

function msgIconClass(role: string) {
  return role === 'user' ? 'iv-msg-icon--user' : 'iv-msg-icon--ai'
}

function msgBubbleClass(role: string) {
  return role === 'user' ? 'iv-msg-bubble--user' : 'iv-msg-bubble--ai'
}

const micGlowClass = computed(() => ({ 'iv-mic-glow--active': microphoneOn.value }))

const micBtnClass = computed(() => ({ 'iv-mic-btn--active': microphoneOn.value }))
</script>

<style scoped>
/* ============================================================
   IV — Interview Mock View · Glassmorphism Design System
   Primary: #00236f  Secondary: #006c49  Surface: #f8f9ff
   ============================================================ */

/* ---------- Root ---------- */
.iv-root {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  height: 100vh;
  overflow: hidden;
  background: #f8f9ff;
  font-family: 'Inter', sans-serif;
  color: #0b1c30;
}

/* ---------- Specialized Header ---------- */
.iv-header {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  padding: 0 24px;
  box-sizing: border-box;
  background: rgba(248, 249, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(197, 197, 211, 0.2);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  flex-shrink: 0;
}

.iv-header-left,
.iv-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.iv-exit-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #444651;
  font-size: 14px;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.iv-exit-btn:hover {
  background: rgba(197, 197, 211, 0.2);
  color: #0b1c30;
}

.iv-header-divider {
  width: 1px;
  height: 24px;
  background: rgba(197, 197, 211, 0.35);
}

/* Connection status pill */
.iv-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  border-radius: 999px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  background: rgba(229, 238, 255, 0.7);
  color: #444651;
  border: 1px solid rgba(197, 197, 211, 0.3);
}
.iv-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #757682;
}
.iv-status-pill--connecting .iv-status-dot {
  background: #f59e0b;
  animation: pulse-dot 1.2s ease-in-out infinite;
}
.iv-status-pill--connected .iv-status-dot {
  background: #006c49;
  animation: pulse-dot 1.8s ease-in-out infinite;
}
.iv-status-pill--error .iv-status-dot {
  background: #ba1a1a;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.75); }
}

/* Mode/timer pill (right side) */
.iv-mode-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(30, 58, 138, 0.08);
  color: #00236f;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* ---------- Main ---------- */
.iv-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 24px 16px;
  box-sizing: border-box;
  overflow: hidden;
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
}

/* ---------- Banners ---------- */
.iv-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-radius: 12px;
  font-size: 14px;
  flex-shrink: 0;
}
.iv-banner--error {
  background: rgba(255, 218, 214, 0.5);
  border: 1px solid rgba(186, 26, 26, 0.2);
  color: #93000a;
}
.iv-banner--info {
  background: rgba(108, 248, 187, 0.2);
  border: 1px solid rgba(0, 108, 73, 0.2);
  color: #00714d;
}

/* ---------- 12-col Grid ---------- */
.iv-grid {
  flex: 1;
  display: grid;
  grid-template-columns: 7fr 5fr;
  gap: 24px;
  min-height: 0;
  overflow: hidden;
}

/* ---------- Glass utility ---------- */
.glass-panel {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 10px 30px rgba(30, 58, 138, 0.05);
}

/* ---------- Left: Video Panel ---------- */
.iv-video-panel {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(11, 28, 48, 0.15);
  min-height: 0;
}

.iv-video-bg {
  position: absolute;
  inset: 0;
  background: #0f172a;
}
.iv-interviewer-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.8;
  filter: brightness(0.75);
}
.iv-video-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6) 0%, transparent 50%);
}

/* AI Status overlay (top-left) */
.iv-ai-overlay {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 20;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.iv-ai-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.iv-ai-status-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: #fff;
}
.iv-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}
.iv-pulse-dot--active {
  background: #4edea3;
  animation: pulse-dot 1.5s ease-in-out infinite;
}

/* Voice bars */
.iv-voice-bars {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 24px;
  padding: 0 14px;
}
.iv-voice-bar {
  width: 4px;
  border-radius: 2px;
  background: #4edea3;
  transition: height 0.1s ease-in-out;
  animation: voice-bounce 0.8s ease-in-out infinite alternate;
}
.iv-voice-bar:nth-child(1) { animation-delay: 0s; }
.iv-voice-bar:nth-child(2) { animation-delay: 0.15s; }
.iv-voice-bar:nth-child(3) { animation-delay: 0.3s; }
.iv-voice-bar:nth-child(4) { animation-delay: 0.45s; }
.iv-voice-bar:nth-child(5) { animation-delay: 0.6s; }
@keyframes voice-bounce {
  from { transform: scaleY(0.4); }
  to   { transform: scaleY(1.3); }
}

/* PiP */
.iv-pip {
  position: absolute;
  bottom: 24px;
  right: 24px;
  width: 140px;
  height: 180px;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  z-index: 20;
  background: #1e293b;
}
.iv-pip-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.iv-pip-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.iv-pip-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1e293b;
}
.iv-pip-label {
  position: absolute;
  bottom: 6px;
  left: 8px;
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  font-family: 'JetBrains Mono', monospace;
  background: rgba(0, 0, 0, 0.45);
  padding: 2px 6px;
  border-radius: 4px;
}

/* Video controls */
.iv-video-controls {
  position: absolute;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 30;
  display: flex;
  align-items: center;
  gap: 20px;
}
.iv-ctrl-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  width: 52px;
  height: 52px;
  color: #fff;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
  font-family: 'Inter', sans-serif;
  font-size: 10px;
  font-weight: 600;
  justify-content: center;
}
.iv-ctrl-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}
.iv-ctrl-btn:active { transform: scale(0.92); }
.iv-ctrl-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.iv-ctrl-btn span {
  display: none; /* hide labels in circular button; shown via title attr */
}
.iv-ctrl-btn--primary {
  width: 60px;
  height: 60px;
  background: #006c49;
  border-color: transparent;
  box-shadow: 0 4px 14px rgba(0, 108, 73, 0.4);
}
.iv-ctrl-btn--primary:hover { background: #005236; }

/* ---------- Right column ---------- */
.iv-right {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
  overflow: hidden;
}

/* Chat */
.iv-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-radius: 16px;
  padding: 20px;
  min-height: 0;
  overflow: hidden;
}
.iv-chat-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-shrink: 0;
}
.iv-chat-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #00236f;
  font-family: 'Inter', sans-serif;
}
.iv-live-badge {
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(229, 238, 255, 0.8);
  color: #444651;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

/* Message list */
.iv-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding-right: 4px;
  scrollbar-width: thin;
  scrollbar-color: rgba(197, 197, 211, 0.4) transparent;
}
.iv-messages::-webkit-scrollbar { width: 4px; }
.iv-messages::-webkit-scrollbar-track { background: transparent; }
.iv-messages::-webkit-scrollbar-thumb { background: rgba(197, 197, 211, 0.4); border-radius: 2px; }

.iv-msg-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.iv-msg-row--user { flex-direction: row-reverse; }

.iv-msg-icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.iv-msg-icon--ai {
  background: rgba(30, 58, 138, 0.12);
  color: #00236f;
}
.iv-msg-icon--user {
  background: rgba(108, 248, 187, 0.25);
  color: #006c49;
}

.iv-msg-bubble {
  max-width: 78%;
  padding: 10px 14px;
  border-radius: 14px;
}
.iv-msg-bubble--ai {
  background: rgba(239, 244, 255, 0.9);
  border: 1px solid rgba(197, 197, 211, 0.1);
  border-top-left-radius: 4px;
}
.iv-msg-bubble--user {
  background: #00236f;
  color: #fff;
  border-top-right-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 35, 111, 0.2);
}
.iv-msg-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.55;
  font-family: 'Inter', sans-serif;
}

/* Controls */
.iv-controls {
  flex-shrink: 0;
  border-radius: 16px;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.iv-input-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

/* Mic button */
.iv-mic-wrap {
  position: relative;
  flex-shrink: 0;
}
.iv-mic-glow {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  background: rgba(0, 108, 73, 0.2);
  filter: blur(8px);
  opacity: 0;
  transition: opacity 0.3s;
}
.iv-mic-glow--active { opacity: 1; }
.iv-mic-btn {
  position: relative;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: rgba(220, 235, 255, 0.6);
  color: #00236f;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
}
.iv-mic-btn:hover { background: rgba(197, 197, 211, 0.4); }
.iv-mic-btn:active { transform: scale(0.92); }
.iv-mic-btn--active {
  background: #006c49;
  color: #fff;
  box-shadow: 0 4px 14px rgba(0, 108, 73, 0.35);
}
.iv-mic-btn:disabled { opacity: 0.45; cursor: not-allowed; }

/* Text input */
.iv-text-wrap {
  flex: 1;
  position: relative;
}
.iv-text-input {
  width: 100%;
  height: 52px;
  box-sizing: border-box;
  background: rgba(248, 249, 255, 0.9);
  border: 1px solid rgba(197, 197, 211, 0.5);
  border-radius: 12px;
  padding: 0 48px 0 16px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  color: #0b1c30;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.iv-text-input::placeholder {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: rgba(117, 118, 130, 0.55);
}
.iv-text-input:focus {
  border-color: #00236f;
  box-shadow: 0 0 0 3px rgba(0, 35, 111, 0.08);
}
.iv-text-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.iv-send-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #00236f;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.12s;
}
.iv-send-btn:hover { background: rgba(0, 35, 111, 0.08); }
.iv-send-btn:disabled { opacity: 0.35; cursor: not-allowed; }

/* Footer bar */
.iv-footer-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid rgba(197, 197, 211, 0.2);
}
.iv-footer-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.iv-footer-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: #757682;
  text-transform: uppercase;
}
.iv-footer-divider {
  width: 1px;
  height: 14px;
  background: rgba(197, 197, 211, 0.35);
}

.iv-end-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: 10px;
  border: 1px solid rgba(186, 26, 26, 0.15);
  background: rgba(255, 218, 214, 0.4);
  color: #ba1a1a;
  font-size: 13px;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.iv-end-btn:hover {
  background: #ba1a1a;
  color: #fff;
}
.iv-end-btn:active { transform: scale(0.96); }
.iv-end-btn:disabled { opacity: 0.35; cursor: not-allowed; }

/* ---------- Responsive ---------- */
@media (max-width: 1024px) {
  .iv-grid {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }
  .iv-video-panel {
    min-height: 320px;
    max-height: 420px;
  }
}
@media (max-width: 640px) {
  .iv-main { padding: 12px; gap: 10px; }
  .iv-pip { width: 100px; height: 130px; }
  .iv-input-row { gap: 10px; }
  .iv-msg-bubble { max-width: 90%; }
}

</style>







