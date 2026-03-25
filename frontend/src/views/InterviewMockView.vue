<template>
  <div class="interviewPage">
    <AppTopbar @logout="logout" />

    <div class="mainContainer">
      <div class="chatSection">
        <div class="chatTopbar">
          <div>
            <p class="panelEyebrow">Realtime Interview</p>
            <h1 class="panelTitle">AI 实时语音面试</h1>
            <p class="panelSummary">{{ interviewSummary }}</p>
          </div>

          <div class="statusGroup">
            <span class="statusBadge" :class="connectionStatusClass">{{ connectionStatusText }}</span>
            <span class="statusBadge" :class="assistantSpeaking ? 'statusActive' : 'statusIdle'">
              {{ assistantSpeaking ? 'AI 回答中' : 'AI 待机' }}
            </span>
            <span class="statusBadge" :class="userSpeaking ? 'statusActive' : 'statusIdle'">
              {{ userSpeaking ? '你正在说话' : '麦克风空闲' }}
            </span>
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

      <div class="sidePanel">
        <div class="interviewerCard">
          <div class="cardHeader">
            <span>AI 面试官</span>
          </div>

          <div class="avatarStage">
            <div class="avatarCircle">
              <img :src="interviewerImage" alt="interviewer" class="cardAvatarImage" />
            </div>
          </div>

          <p class="cardHint">
            开启麦克风后，浏览器会持续把 16k PCM 音频发送到后端，再由后端转给实时面试服务。
          </p>
        </div>

        <div class="userCard">
          <div class="cardHeader">
            <span>候选人</span>
          </div>

          <div v-if="!cameraOn" class="avatarStage">
            <div class="avatarCircle">
              <img :src="userAvatar" alt="user avatar" class="cardAvatarImage" />
            </div>
          </div>

          <video v-else ref="videoRef" autoplay playsinline muted class="mediaFrame"></video>

          <div class="cardActions cardActionsRow">
            <button class="cameraButton" type="button" :disabled="isConnecting" @click="toggleMicrophone">
              {{ microphoneOn ? '关闭麦克风' : isConnecting ? '连接中...' : '开启麦克风' }}
            </button>
            <button
              class="cameraButton cameraButtonDanger"
              type="button"
              :disabled="!microphoneOn && connectionState !== 'connecting'"
              @click="endInterview"
            >
              结束面试
            </button>
            <button class="cameraButton" type="button" @click="toggleCamera">
              {{ cameraOn ? '关闭摄像头' : '开启摄像头' }}
            </button>
          </div>

          <p class="cameraHint">
            {{
              microphoneOn
                ? '实时语音已连接，可以直接开口回答问题，AI 会返回文本和语音。'
                : '点击“开启麦克风”后开始本次模拟面试，摄像头仅用于本地预览。'
            }}
          </p>
        </div>

        <div class="infoCard">
          <div class="cardHeader">
            <span>本次面试配置</span>
          </div>
          <ul class="infoList">
            <li><strong>岗位：</strong>{{ interviewSetup?.job_title ?? '-' }}</li>
            <li><strong>经验：</strong>{{ experienceLevelLabel }}</li>
            <li><strong>模式：</strong>{{ modeLabel }}</li>
          </ul>
          <p class="cardHint">{{ interviewSetup?.job_description ?? '' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import AppTopbar from '../components/AppTopbar.vue'
import {
  clearAuthSession,
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
let isIntentionalSocketClose = false
let pendingPcmBytes = new Uint8Array(0)

function logout() {
  clearAuthSession()
  router.push('/')
}

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
  const socket = new WebSocket(getInterviewWebSocketUrl())
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
      if (payload.type === 'user_speaking') {
        userSpeaking.value = true
        return
      }
      if (payload.type === 'user_done') {
        userSpeaking.value = false
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
.interviewPage {
  min-height: 100vh;
}
.mainContainer {
  display: flex;
  gap: 24px;
  min-height: calc(100vh - 48px);
  width: min(1440px, calc(100% - 48px));
  margin: 24px auto 32px;
  padding: 24px;
  background: radial-gradient(circle at top right, rgba(255, 217, 153, 0.28), transparent 28%), linear-gradient(180deg, #f4f1ea 0%, #eef2f6 100%);
}
.chatSection {
  position: relative;
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  min-width: 0;
  height: 80vh;
  padding: 24px 24px 120px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
}
.chatTopbar {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  margin-bottom: 20px;
}
.panelEyebrow,.fieldLabel,.configTitle { margin: 0 0 6px; color: #92400e; font-size: 12px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
.panelTitle { margin: 0; color: #111827; font-size: 30px; line-height: 1.1; }
.panelSummary { margin: 10px 0 0; color: #64748b; font-size: 14px; }
.statusGroup { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; }
.statusBadge { padding: 8px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.statusConnected,.statusActive { background: #dcfce7; color: #166534; }
.statusConnecting { background: #fef3c7; color: #92400e; }
.statusIdle { background: #e2e8f0; color: #475569; }
.statusError { background: #fee2e2; color: #b91c1c; }
.messageList { display: flex; flex: 1 1 auto; flex-direction: column; gap: 18px; overflow-y: auto; padding-right: 8px; }
.messageRow { display: flex; align-items: flex-start; gap: 12px; }
.messageRowAi { justify-content: flex-start; }
.messageRowUser { justify-content: flex-end; }
.messageAvatar { width: 42px; height: 42px; flex: none; border: 1px solid #e5e7eb; border-radius: 50%; object-fit: cover; box-shadow: 0 8px 18px rgba(15, 23, 42, 0.12); }
.messageBubble { max-width: min(740px, 72%); padding: 14px 16px; border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 20px; background: #f8fafc; }
.messageRowUser .messageBubble { background: #dbeafe; border-color: #bfdbfe; }
.messageName { margin: 0 0 6px; color: #475569; font-size: 13px; font-weight: 700; }
.messageText { margin: 0; color: #0f172a; font-size: 15px; line-height: 1.75; white-space: pre-wrap; }
.inputBar { position: absolute; right: 24px; bottom: 24px; left: 24px; display: flex; align-items: center; gap: 12px; padding: 14px; border: 1px solid rgba(15, 23, 42, 0.08); border-radius: 18px; background: rgba(255, 255, 255, 0.96); }
.messageInput { flex: 1 1 auto; border: 0; background: transparent; color: #0f172a; font-size: 15px; outline: none; }
.sendButton,.cameraButton { display: inline-flex; align-items: center; justify-content: center; border-radius: 999px; cursor: pointer; }
.sendButton { min-width: 84px; padding: 10px 18px; border: 0; background: #111827; color: #fff; font-size: 14px; font-weight: 700; }
.sendButton:disabled,.cameraButton:disabled { cursor: not-allowed; opacity: 0.6; }
.errorBanner { position: absolute; right: 24px; bottom: 90px; left: 24px; margin: 0; padding: 10px 12px; border-radius: 12px; background: #fee2e2; color: #991b1b; font-size: 13px; }
.sidePanel { display: flex; width: 340px; flex: none; flex-direction: column; gap: 18px; }
.infoCard,.interviewerCard,.userCard { padding: 16px; border: 1px solid rgba(15, 23, 42, 0.08); border-radius: 24px; background: rgba(255, 255, 255, 0.9); box-shadow: 0 18px 42px rgba(15, 23, 42, 0.06); }
.cardHeader { display: flex; align-items: center; margin-bottom: 12px; color: #0f172a; font-size: 14px; font-weight: 700; }
.infoList { margin: 0; padding: 0; list-style: none; display: grid; gap: 8px; color: #334155; font-size: 14px; }
.cardActions { display: flex; gap: 8px; }
.cardActionsRow { margin-top: 12px; justify-content: space-between; }
.cameraButton { flex: 1 1 0; min-height: 38px; padding: 8px 10px; border: 1px solid rgba(15, 23, 42, 0.08); background: #f8fafc; color: #111827; font-size: 11px; font-weight: 700; }
.cameraButtonDanger { border-color: rgba(185, 28, 28, 0.16); background: #fff1f2; color: #b91c1c; }
.mediaFrame { display: block; width: 100%; height: 180px; border: 1px solid #e5e7eb; border-radius: 16px; object-fit: cover; background: #f8fafc; }
.avatarStage { display: grid; width: 100%; height: 180px; place-items: center; border: 1px solid rgba(148, 163, 184, 0.16); border-radius: 18px; background: radial-gradient(circle at top, rgba(251, 191, 36, 0.16), transparent 38%), linear-gradient(180deg, #f8fafc, #eef2f7); }
.avatarCircle { display: grid; width: 110px; height: 110px; place-items: center; overflow: hidden; border: 4px solid #ffffff; border-radius: 50%; background: #ffffff; }
.cardAvatarImage { width: 100%; height: 100%; object-fit: cover; }
.cardHint,.cameraHint { margin: 12px 0 0; color: #64748b; font-size: 13px; line-height: 1.6; }
@media (max-width: 980px) { .mainContainer { flex-direction: column; } .chatSection { height: auto; min-height: auto; } .sidePanel { width: 100%; } }
@media (max-width: 720px) { .mainContainer { width: calc(100% - 24px); margin: 12px auto; padding: 16px; } .chatSection { padding: 18px 18px 112px; } .chatTopbar,.cardActionsRow { flex-direction: column; } .statusGroup { justify-content: flex-start; } .inputBar { right: 18px; bottom: 18px; left: 18px; } .messageBubble { max-width: 100%; } }
</style>




