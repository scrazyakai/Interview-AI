<template>
  <section class="rounded-2xl border border-gray-100 bg-white p-6 shadow-md">
    <form class="space-y-7" @submit.prevent="emit('submit')">
      <div>
        <h3 class="text-base font-semibold text-gray-900">基本信息</h3>
        <div class="mt-4 grid gap-4 sm:grid-cols-2">
          <label class="space-y-2">
            <span class="text-sm text-gray-600">岗位方向</span>
            <select
              :value="jobTitle"
              class="h-11 w-full rounded-xl border border-gray-200 bg-white px-3 text-sm text-gray-700 transition hover:border-yellow-400 focus:border-yellow-400 focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
              :disabled="loading"
              @change="emit('update:jobTitle', ($event.target as HTMLSelectElement).value)"
            >
              <option v-for="option in jobTitleOptions" :key="option" :value="option">{{ option }}</option>
            </select>
          </label>

          <label class="space-y-2">
            <span class="text-sm text-gray-600">经验级别</span>
            <select
              :value="experienceLevel"
              class="h-11 w-full rounded-xl border border-gray-200 bg-white px-3 text-sm text-gray-700 transition hover:border-yellow-400 focus:border-yellow-400 focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
              :disabled="loading"
              @change="emit('update:experienceLevel', ($event.target as HTMLSelectElement).value)"
            >
              <option v-for="option in experienceLevelOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>
        </div>
      </div>

      <div>
        <h3 class="text-base font-semibold text-gray-900">面试设置</h3>
        <div class="mt-4 space-y-4">
          <label class="space-y-2">
            <span class="text-sm text-gray-600">面试模式</span>
            <select
              :value="mode"
              class="h-11 w-full rounded-xl border border-gray-200 bg-white px-3 text-sm text-gray-700 transition hover:border-yellow-400 focus:border-yellow-400 focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
              :disabled="loading"
              @change="emit('update:mode', ($event.target as HTMLSelectElement).value)"
            >
              <option v-for="option in modeOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>

          <div>
            <span class="mb-2 block text-sm text-gray-600">上传简历</span>
            <div
              class="rounded-xl border-2 border-dashed p-5 text-center transition"
              :class="isDragOver ? 'border-yellow-400 bg-yellow-50' : 'border-gray-200 hover:border-yellow-400 hover:bg-yellow-50/40'"
              @dragover.prevent="isDragOver = true"
              @dragleave.prevent="isDragOver = false"
              @drop.prevent="handleDrop"
            >
              <input ref="fileInputRef" class="hidden" type="file" accept="application/pdf,.pdf" :disabled="loading" @change="handleSelect" />
              <button
                type="button"
                class="text-sm text-gray-700"
                :disabled="loading"
                @click="fileInputRef?.click()"
              >
                📄 拖拽 PDF 到这里 或 点击上传
              </button>
              <p class="mt-2 text-xs text-gray-500">{{ resumeFileName || '尚未选择文件' }}</p>
            </div>
          </div>
        </div>
      </div>

      <div>
        <h3 class="text-base font-semibold text-gray-900">补充信息</h3>
        <p class="mt-2 text-sm text-yellow-700">{{ helperTip }}</p>
        <textarea
          :value="jobDescription"
          rows="6"
          maxlength="2000"
          :disabled="loading"
          class="mt-3 w-full rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-700 transition placeholder:text-gray-400 hover:border-yellow-400 focus:border-yellow-400 focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
          placeholder="示例：
- 技术栈：Java / Spring Boot / MySQL
- 岗位：后端开发
- 重点考察：项目经验 + 八股文"
          @input="emit('update:jobDescription', ($event.target as HTMLTextAreaElement).value)"
        ></textarea>
      </div>

      <p v-if="errorMessage" class="rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ errorMessage }}</p>

      <div class="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:items-center sm:justify-between">
        <button
          type="button"
          class="h-11 rounded-xl border border-gray-300 px-5 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
          :disabled="loading"
          @click="emit('back')"
        >
          返回首页
        </button>

        <button
          type="submit"
          class="h-11 rounded-xl bg-yellow-500 px-6 text-sm font-semibold text-white shadow-lg transition hover:bg-yellow-600 disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="disableSubmit || loading"
        >
          {{ loading ? '生成中...' : '🚀 创建面试并开始' }}
        </button>
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  jobTitle: string
  experienceLevel: string
  mode: string
  jobDescription: string
  resumeFileName: string
  helperTip: string
  loading: boolean
  disableSubmit: boolean
  errorMessage: string
  jobTitleOptions: readonly string[]
  experienceLevelOptions: ReadonlyArray<{ label: string; value: string }>
  modeOptions: ReadonlyArray<{ label: string; value: string }>
}>()

const emit = defineEmits<{
  'update:jobTitle': [value: string]
  'update:experienceLevel': [value: string]
  'update:mode': [value: string]
  'update:jobDescription': [value: string]
  'file-selected': [file: File]
  back: []
  submit: []
}>()

const fileInputRef = ref<HTMLInputElement | null>(null)
const isDragOver = ref(false)

function pickFileFromEvent(event: Event): File | null {
  const input = event.target as HTMLInputElement | null
  return input?.files?.[0] ?? null
}

function handleSelect(event: Event) {
  const file = pickFileFromEvent(event)
  if (!file) return
  emit('file-selected', file)
}

function handleDrop(event: DragEvent) {
  isDragOver.value = false
  const file = event.dataTransfer?.files?.[0]
  if (!file) return
  emit('file-selected', file)
}
</script>
