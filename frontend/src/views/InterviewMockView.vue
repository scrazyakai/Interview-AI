<template>
  <div class="interview-deck">
    <div class="interview-deck__glow interview-deck__glow--left"></div>
    <div class="interview-deck__glow interview-deck__glow--right"></div>

    <div class="interview-deck__shell">
      <div class="mainContainer mainContainer--compact">
        <section class="chatSection">
          <div class="chatSection__header">
            <div>
              <p class="sectionLabel">Live Transcript</p>
              <h2 class="sectionTitle">实时对话</h2>
            </div>
            <div class="chatSection__pulse" :class="isRealtimeReady ? 'chatSection__pulse--on' : 'chatSection__pulse--off'">
              <span class="chatSection__pulseDot"></span>
              {{ isRealtimeReady ? '实时链路已建立' : '等待连接开始' }}
            </div>
          </div>

          <div ref="messageListRef" class="messageList">
            <div
              v-for="message in messages"
              :key="message.id"
              class="messageRow"
              :class="message.role === 'user' ? 'messageRowUser' : 'messageRowAi'"
            >
              <img
                v-if="message.role === 'ai'"
                :src="interviewerImage"
                alt="AI interviewer avatar"
                class="messageAvatar"
              />

              <div class="messageBubble">
                <p class="messageName">{{ message.name }}</p>
                <p class="messageText">{{ message.text }}</p>
              </div>
            </div>
          </div>

          <div class="inputBarWrap">
            <div class="inputBar">
              <input
                v-model="inputValue"
                class="messageInput"
                type="text"
                placeholder="也可以直接输入文字提问..."
                :disabled="!isRealtimeReady"
                @keydown.enter.prevent="sendMessage"
              />
              <button class="sendButton" type="button" :disabled="!isRealtimeReady" @click="sendMessage">
                发送
              </button>
            </div>
            <p v-if="errorMessage" class="errorBanner">{{ errorMessage }}</p>
          </div>
        </section>

        <aside class="sidePanel">
          <section class="controlCard controlCard--dark">
            <div class="cardHeader">
              <span>AI 面试官</span>
              <span class="miniBadge">Voice Coach</span>
            </div>

            <div class="avatarStage avatarStage--dark">
              <div class="avatarCircle avatarCircle--lg">
                <img :src="interviewerImage" alt="interviewer" class="cardAvatarImage" />
              </div>
            </div>

            <p class="cardHint cardHintLight">
              开启麦克风后，浏览器会持续把 16k PCM 音频发送到后端，再由后端转给实时面试服务。
            </p>
          </section>

          <section class="controlCard">
            <div class="cardHeader">
              <span>候选人控制台</span>
              <span class="miniBadge miniBadgeWarm">Device</span>
            </div>

            <div v-if="!cameraOn" class="avatarStage">
              <div class="avatarCircle avatarCircle--lg">
                <img :src="userAvatar" alt="user avatar" class="cardAvatarImage" />
              </div>
            </div>

            <video v-else ref="videoRef" autoplay playsinline muted class="mediaFrame"></video>

            <div class="actionGrid">
              <button class="cameraButton cameraButtonPrimary" type="button" :disabled="isConnecting" @click="toggleMicrophone">
                {{ microphoneOn ? '关闭麦克风' : isConnecting ? '连接中...' : '开启麦克风' }}
              </button>
              <button class="cameraButton" type="button" @click="toggleCamera">
                {{ cameraOn ? '关闭摄像头' : '开启摄像头' }}
              </button>
              <button
                class="cameraButton cameraButtonDanger actionGrid__full"
                type="button"
                :disabled="!microphoneOn && connectionState !== 'connecting'"
                @click="endInterview"
              >
                结束面试
              </button>
            </div>

            <p class="cameraHint">
              {{
                microphoneOn
                  ? '实时语音已连接，可以直接开口回答问题，AI 会返回文本和语音。'
                  : '点击“开启麦克风”后开始本次模拟面试，摄像头仅用于本地预览。'
              }}
            </p>
          </section>

          <section class="controlCard">
            <div class="cardHeader">
              <span>本次面试配置</span>
              <span class="miniBadge miniBadgeSoft">Session</span>
            </div>
            <ul class="infoList">
              <li><strong>岗位：</strong>{{ interviewSetup?.job_title ?? '-' }}</li>
              <li><strong>经验：</strong>{{ experienceLevelLabel }}</li>
              <li><strong>模式：</strong>{{ modeLabel }}</li>
            </ul>
            <p class="cardHint">{{ interviewSetup?.job_description ?? '暂无岗位描述。' }}</p>
          </section>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

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
const interviewerImage = ref('https://akainews.oss-cn-beijing.aliyuncs.com/AI-Interview/interviewer.jpg')
const userAvatar = ref(
  "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 520 320'><defs><linearGradient id='bg' x1='0' y1='0' x2='1' y2='1'><stop offset='0%' stop-color='%23edf2f7'/><stop offset='100%' stop-color='%23d9e2ec'/></linearGradient></defs><rect width='520' height='320' rx='28' fill='url(%23bg)'/><circle cx='260' cy='118' r='54' fill='%23ffffff'/><path d='M198 252c12-52 46-82 62-82s50 30 62 82' fill='%23ffffff'/><circle cx='260' cy='118' r='24' fill='%23cbd5e1'/><text x='42' y='286' font-size='28' font-family='Segoe UI, Arial' fill='%23475569'>Candidate Preview</text></svg>",
)

const messages = ref<ChatMessage[]>([
  {
    id: 1,
    role: 'ai',
    name: '系统',
    text: '面试配置已就绪。点击“开启麦克风”后开始实时模拟面试。',
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

function decodeFloat32PcmChunk(chunk: ArrayBuffer) {
  const view = new DataView(chunk)
  const samples = new Float32Array(chunk.byteLength / 4)
  for (let index = 0; index < samples.length; index += 1) {
    samples[index] = view.getFloat32(index * 4, true)
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

  const samples = decodeFloat32PcmChunk(chunk)
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
</script>

<style scoped>
.interview-deck {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background: linear-gradient(180deg, #f6efe6 0%, #efe6da 46%, #f4f6f8 100%);
}

.interview-deck__glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(80px);
  opacity: 0.7;
}

.interview-deck__glow--left {
  top: 90px;
  left: -60px;
  width: 280px;
  height: 280px;
  background: rgba(234, 148, 86, 0.22);
}

.interview-deck__glow--right {
  top: 140px;
  right: -80px;
  width: 320px;
  height: 320px;
  background: rgba(46, 90, 137, 0.12);
}

.interview-deck__shell {
  position: relative;
  z-index: 1;
  width: min(1480px, calc(100% - 32px));
  margin: 0 auto;
  padding: 24px 0 32px;
}

.interview-hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin: 22px auto 0;
  padding: 28px 30px;
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 34px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 26px 80px rgba(79, 56, 36, 0.12);
  backdrop-filter: blur(18px);
}

.mainContainer {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) 360px;
  gap: 22px;
  margin-top: 22px;
}

.chatSection {
  display: flex;
  min-height: 78vh;
  flex-direction: column;
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 34px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 26px 80px rgba(79, 56, 36, 0.12);
  backdrop-filter: blur(18px);
}

.chatSection__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 0;
}

.chatSection__pulse {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.chatSection__pulse--on {
  background: #ecfdf3;
  color: #166534;
}

.chatSection__pulse--off {
  background: #f3f4f6;
  color: #667085;
}

.chatSection__pulseDot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.sectionLabel,
.panelEyebrow {
  margin: 0 0 8px;
  color: #9f4f22;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.sectionTitle,
.panelTitle {
  margin: 0;
  color: #1f1710;
  font-size: clamp(2rem, 3.2vw, 3rem);
  line-height: 1.04;
  letter-spacing: -0.05em;
}

.panelSummary {
  margin: 10px 0 0;
  color: #6f6256;
  font-size: 15px;
  line-height: 1.8;
}

.statusGroup {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.statusGroupHero {
  justify-content: flex-end;
}

.statusBadge {
  padding: 9px 13px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.statusConnected,
.statusActive {
  background: #dcfce7;
  color: #166534;
}

.statusConnecting {
  background: #fef3c7;
  color: #92400e;
}

.statusIdle {
  background: #eceff3;
  color: #5b6572;
}

.statusError {
  background: #fee2e2;
  color: #b91c1c;
}

.messageList {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  gap: 18px;
  overflow-y: auto;
  margin: 18px 18px 0;
  padding: 6px 10px 18px;
}

.messageRow {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.messageRowAi {
  justify-content: flex-start;
}

.messageRowUser {
  justify-content: flex-end;
}

.messageAvatar {
  width: 42px;
  height: 42px;
  flex: none;
  border: 2px solid rgba(255, 255, 255, 0.88);
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 10px 22px rgba(79, 56, 36, 0.14);
}

.messageBubble {
  max-width: min(760px, 74%);
  padding: 16px 18px;
  border: 1px solid rgba(189, 173, 156, 0.4);
  border-radius: 22px;
  background: rgba(255, 251, 247, 0.96);
  box-shadow: 0 16px 30px rgba(79, 56, 36, 0.06);
}

.messageRowUser .messageBubble {
  border-color: rgba(219, 180, 145, 0.52);
  background: linear-gradient(180deg, #fff2e6, #fde8d7);
}

.messageName {
  margin: 0 0 6px;
  color: #7a6858;
  font-size: 13px;
  font-weight: 700;
}

.messageText {
  margin: 0;
  color: #1f1710;
  font-size: 15px;
  line-height: 1.78;
  white-space: pre-wrap;
}

.inputBarWrap {
  padding: 0 18px 18px;
}

.inputBar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border: 1px solid rgba(210, 193, 176, 0.52);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.messageInput {
  flex: 1 1 auto;
  border: 0;
  background: transparent;
  color: #1f1710;
  font-size: 15px;
  outline: none;
}

.sendButton,
.cameraButton {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  cursor: pointer;
}

.sendButton {
  min-width: 88px;
  padding: 10px 18px;
  border: 0;
  background: linear-gradient(135deg, #1f1710, #9f4f22 62%, #d98952);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  box-shadow: 0 14px 28px rgba(159, 79, 34, 0.22);
}

.sendButton:disabled,
.cameraButton:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.errorBanner {
  margin: 10px 4px 0;
  padding: 10px 12px;
  border-radius: 14px;
  background: #fee2e2;
  color: #991b1b;
  font-size: 13px;
}

.sidePanel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.controlCard {
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 24px 70px rgba(79, 56, 36, 0.12);
  backdrop-filter: blur(18px);
}

.controlCard--dark {
  border-color: rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(31, 23, 16, 0.97), rgba(60, 40, 27, 0.94));
}

.cardHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
  color: #1f1710;
  font-size: 14px;
  font-weight: 700;
}

.controlCard--dark .cardHeader {
  color: #fff7f0;
}

.miniBadge {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  color: #ffd8bc;
  font-size: 11px;
  font-weight: 700;
}

.miniBadgeWarm {
  background: #fff2e6;
  color: #9f4f22;
}

.miniBadgeSoft {
  background: #f3f4f6;
  color: #667085;
}

.avatarStage {
  display: grid;
  width: 100%;
  height: 188px;
  place-items: center;
  border: 1px solid rgba(210, 193, 176, 0.45);
  border-radius: 24px;
  background: radial-gradient(circle at top, rgba(241, 181, 128, 0.18), transparent 40%), linear-gradient(180deg, #fffaf5, #f3ede5);
}

.avatarStage--dark {
  border-color: rgba(255, 255, 255, 0.1);
  background: radial-gradient(circle at top, rgba(245, 155, 90, 0.18), transparent 34%), linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
}

.avatarCircle {
  display: grid;
  place-items: center;
  overflow: hidden;
  border-radius: 50%;
  background: #ffffff;
}

.avatarCircle--lg {
  width: 116px;
  height: 116px;
  border: 4px solid rgba(255, 255, 255, 0.92);
  box-shadow: 0 14px 28px rgba(79, 56, 36, 0.18);
}

.cardAvatarImage {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mediaFrame {
  display: block;
  width: 100%;
  height: 188px;
  border: 1px solid rgba(210, 193, 176, 0.45);
  border-radius: 24px;
  object-fit: cover;
  background: #f8fafc;
}

.actionGrid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.actionGrid__full {
  grid-column: 1 / -1;
}

.cameraButton {
  min-height: 42px;
  padding: 10px 12px;
  border: 1px solid rgba(203, 182, 161, 0.52);
  background: #fffaf5;
  color: #1f1710;
  font-size: 12px;
  font-weight: 700;
}

.cameraButtonPrimary {
  border: 0;
  background: linear-gradient(135deg, #1f1710, #9f4f22 62%, #d98952);
  color: #fff;
  box-shadow: 0 14px 28px rgba(159, 79, 34, 0.22);
}

.cameraButtonDanger {
  border-color: rgba(185, 28, 28, 0.14);
  background: #fff1f2;
  color: #b91c1c;
}

.infoList {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
  color: #4c4137;
  font-size: 14px;
}

.cardHint,
.cameraHint {
  margin: 14px 0 0;
  color: #6f6256;
  font-size: 13px;
  line-height: 1.75;
}

.cardHintLight {
  color: rgba(255, 241, 230, 0.8);
}

@media (max-width: 1120px) {
  .mainContainer {
    grid-template-columns: 1fr;
  }

  .sidePanel {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    display: grid;
  }
}

@media (max-width: 820px) {
  .interview-deck__shell {
    width: calc(100% - 20px);
    padding-top: 18px;
  }

  .interview-hero,
  .chatSection,
  .controlCard {
    border-radius: 26px;
  }

  .interview-hero,
  .chatSection__header {
    flex-direction: column;
  }

  .statusGroupHero {
    justify-content: flex-start;
  }

  .sidePanel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .chatSection {
    min-height: 70vh;
  }

  .messageBubble {
    max-width: 100%;
  }

  .inputBar {
    flex-direction: column;
    align-items: stretch;
  }

  .actionGrid {
    grid-template-columns: 1fr;
  }
}
</style>






