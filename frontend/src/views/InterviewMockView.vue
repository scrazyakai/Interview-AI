<template>
  <div class="mainContainer">
    <div class="chatSection">
      <div class="messageList">
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
          placeholder="输入你的回答..."
          @keydown.enter.prevent="sendMessage"
        />
        <button class="sendButton" type="button" @click="sendMessage">发送</button>
      </div>
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
      </div>

      <div class="userCard">
        <div class="cardHeader cardHeaderBetween">
          <span>候选人</span>

          <div class="cardActions">
            <button class="cameraButton" type="button" @click="toggleMicrophone">
              {{ microphoneOn ? '关闭麦克风' : '开启麦克风' }}
            </button>
            <button class="cameraButton" type="button" @click="toggleCamera">
              {{ cameraOn ? '关闭摄像头' : '开启摄像头' }}
            </button>
          </div>
        </div>

        <div v-if="!cameraOn" class="avatarStage">
          <div class="avatarCircle">
            <img :src="userAvatar" alt="user avatar" class="cardAvatarImage" />
          </div>
        </div>

        <video v-else ref="videoRef" autoplay playsinline muted class="mediaFrame"></video>

        <p class="cameraHint">
          {{
            cameraOn
              ? '摄像头已开启，正在显示本地实时画面。'
              : microphoneOn
                ? '麦克风已开启，摄像头未开启时仍显示默认头像。'
                : '当前显示默认头像，可按需开启麦克风或摄像头。'
          }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'

type ChatMessage = {
  id: number
  role: 'ai' | 'user'
  name: string
  text: string
}

const interviewerImage = ref(
  'https://akainews.oss-cn-beijing.aliyuncs.com/AI-Interview/interviewer.jpg',
)

const userAvatar = ref(
  "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 520 320'><defs><linearGradient id='bg' x1='0' y1='0' x2='1' y2='1'><stop offset='0%' stop-color='%23edf2f7'/><stop offset='100%' stop-color='%23d9e2ec'/></linearGradient></defs><rect width='520' height='320' rx='28' fill='url(%23bg)'/><circle cx='260' cy='118' r='54' fill='%23ffffff'/><path d='M198 252c12-52 46-82 62-82s50 30 62 82' fill='%23ffffff'/><circle cx='260' cy='118' r='24' fill='%23cbd5e1'/><text x='42' y='286' font-size='28' font-family='Segoe UI, Arial' fill='%23475569'>Candidate Preview</text></svg>",
)

const cameraOn = ref(false)
const microphoneOn = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
const messages = ref<ChatMessage[]>([
  {
    id: 1,
    role: 'ai',
    name: 'AI 面试官',
    text: '欢迎参加前端开发岗位模拟面试。我们先从自我介绍开始，请用 2 到 3 分钟概述你的背景。',
  },
  {
    id: 2,
    role: 'user',
    name: '我',
    text: '好的，我会先介绍最近两年的工作经历，再展开一个最有代表性的项目。',
  },
  {
    id: 3,
    role: 'ai',
    name: 'AI 面试官',
    text: '接下来我会重点追问项目中的技术难点、性能优化方案，以及你在团队中的具体职责。',
  },
])
const inputValue = ref('')

let cameraStream: MediaStream | null = null
let microphoneStream: MediaStream | null = null

async function startCamera() {
  if (cameraOn.value) return

  const stream = await navigator.mediaDevices.getUserMedia({
    video: true,
    audio: false,
  })

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

async function startMicrophone() {
  if (microphoneOn.value) return

  const stream = await navigator.mediaDevices.getUserMedia({
    audio: true,
    video: false,
  })

  microphoneStream = stream
  microphoneOn.value = true
}

function stopMicrophone() {
  if (microphoneStream) {
    microphoneStream.getTracks().forEach((track) => track.stop())
    microphoneStream = null
  }

  microphoneOn.value = false
}

watch(videoRef, async (element) => {
  if (!element || !cameraStream) return
  element.srcObject = cameraStream
  await element.play().catch(() => undefined)
})

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
  } catch {
    stopMicrophone()
  }
}

function sendMessage() {
  const text = inputValue.value.trim()
  if (!text) return

  messages.value.push({
    id: Date.now(),
    role: 'user',
    name: '我',
    text,
  })

  inputValue.value = ''
}

onBeforeUnmount(() => {
  stopCamera()
  stopMicrophone()
})
</script>

<style scoped>
.mainContainer {
  display: flex;
  gap: 24px;
  min-height: 100vh;
  width: min(1440px, calc(100% - 48px));
  margin: 24px auto;
  padding: 24px;
  background: #f3f5f7;
}

.chatSection {
  position: relative;
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  min-width: 0;
  padding: 24px 24px 108px;
  border: 1px solid #e5e7eb;
  border-radius: 24px;
  background: #ffffff;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
}

.messageList {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  gap: 18px;
  overflow-y: auto;
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
  border: 1px solid #e5e7eb;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
}

.messageBubble {
  max-width: min(720px, 72%);
  padding: 14px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  background: #f8fafc;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
}

.messageRowUser .messageBubble {
  background: #eef2ff;
  border-color: #dbe4ff;
}

.messageName {
  margin: 0 0 6px;
  color: #334155;
  font-size: 13px;
  font-weight: 700;
}

.messageText {
  margin: 0;
  color: #0f172a;
  font-size: 15px;
  line-height: 1.75;
}

.inputBar {
  position: absolute;
  right: 24px;
  bottom: 24px;
  left: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  background: #ffffff;
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.08);
}

.messageInput {
  flex: 1 1 auto;
  border: 0;
  background: transparent;
  color: #0f172a;
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
  min-width: 84px;
  padding: 10px 18px;
  background: #111827;
  color: #ffffff;
  font-size: 14px;
  font-weight: 700;
}

.sidePanel {
  display: flex;
  width: 292px;
  flex: none;
  flex-direction: column;
  gap: 18px;
}

.interviewerCard,
.userCard {
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  background: #ffffff;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
}

.cardHeader {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  color: #0f172a;
  font-size: 14px;
  font-weight: 700;
}

.cardHeaderBetween {
  justify-content: space-between;
  gap: 12px;
}

.cardActions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.cameraButton {
  padding: 8px 12px;
  background: #f8fafc;
  color: #111827;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid #e5e7eb;
}

.mediaFrame {
  display: block;
  width: 100%;
  height: 160px;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  object-fit: cover;
  background: #f8fafc;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
}

.avatarStage {
  display: grid;
  width: 100%;
  height: 160px;
  place-items: center;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  background: linear-gradient(180deg, #f8fafc, #f1f5f9);
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
}

.avatarCircle {
  display: grid;
  width: 108px;
  height: 108px;
  place-items: center;
  overflow: hidden;
  border: 4px solid #ffffff;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
}

.cardAvatarImage {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cameraHint {
  margin: 10px 0 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.6;
}

@media (max-width: 980px) {
  .mainContainer {
    flex-direction: column;
  }

  .sidePanel {
    width: 100%;
    flex-direction: row;
  }

  .interviewerCard,
  .userCard {
    flex: 1 1 0;
  }
}

@media (max-width: 720px) {
  .mainContainer {
    width: calc(100% - 24px);
    margin: 12px auto;
    padding: 16px;
  }

  .chatSection {
    padding: 16px 16px 96px;
  }

  .inputBar {
    right: 16px;
    bottom: 16px;
    left: 16px;
  }

  .sidePanel {
    flex-direction: column;
  }

  .messageBubble {
    max-width: 100%;
  }

  .cardHeaderBetween {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
