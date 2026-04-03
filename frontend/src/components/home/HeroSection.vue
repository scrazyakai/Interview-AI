<template>
  <section class="px-4 pb-16 pt-12 sm:px-6 lg:px-8 lg:pb-20">
    <div class="mx-auto max-w-7xl">
      <div class="mx-auto max-w-4xl text-center">
        <h1 class="text-4xl font-bold tracking-tight text-[#212121] sm:text-5xl lg:text-6xl">
          面一次，强一次，
          <span class="text-[#f5b61b]">直通 offer!</span>
        </h1>

        <div class="mt-7 flex flex-col justify-center gap-3 sm:flex-row">
          <select
            v-model="selectedJobTitle"
            class="h-11 rounded-xl border border-[#e8e8e8] bg-white px-4 text-sm text-[#585858] shadow-sm outline-none transition hover:border-[#f5b61b]"
          >
            <option v-for="option in jobTitleOptions" :key="option" :value="option">
              {{ option }}
            </option>
          </select>
          <select
            v-model="selectedExperienceLevel"
            class="h-11 rounded-xl border border-[#e8e8e8] bg-white px-4 text-sm text-[#585858] shadow-sm outline-none transition hover:border-[#f5b61b]"
          >
            <option v-for="option in experienceLevelOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
          <button
            type="button"
            class="h-11 rounded-xl bg-[#f5b61b] px-7 text-sm font-semibold text-white shadow-[0_8px_24px_rgba(245,182,27,0.35)] transition hover:-translate-y-0.5 hover:bg-[#e5a300]"
            @click="handleStart"
          >
            开始面试
          </button>
        </div>

        <div class="mt-5 flex flex-wrap items-center justify-center gap-2">
          <button
            v-for="tag in directionTags"
            :key="tag"
            class="rounded-full border border-[#ebebeb] bg-white px-4 py-1.5 text-xs text-[#616161] transition hover:border-[#f5b61b] hover:text-[#c88f0f]"
          >
            {{ tag }}
          </button>
        </div>
      </div>

      <div class="mt-10 grid gap-5 lg:grid-cols-[1.7fr_1fr]">
        <div class="rounded-2xl border border-[#ececec] bg-white p-4 shadow-sm sm:p-5">
          <div class="mb-4 flex items-center gap-2 text-xs text-[#6b6b6b]">
            <span class="h-2 w-2 rounded-full bg-[#f5b61b]"></span>
            沉浸式模拟面试 · Java 后端方向
          </div>

          <div class="space-y-3">
            <article
              v-for="(item, idx) in chatMessages"
              :key="`${item.role}-${idx}`"
              :class="[
                'max-w-[92%] rounded-2xl px-4 py-3 text-sm leading-6 transition',
                item.role === '面试官'
                  ? 'mr-auto bg-[#f6f6f6] text-[#424242]'
                  : 'ml-auto border border-[#f7e0a0] bg-[#fff8e8] text-[#3f3f3f]',
              ]"
            >
              <p class="mb-1 text-xs font-semibold text-[#7b7b7b]">{{ item.role }}</p>
              <p>{{ item.content }}</p>
            </article>
          </div>

          <div class="mt-4 rounded-xl border border-[#efefef] bg-[#fafafa] px-4 py-3 text-sm text-[#9a9a9a]">
            AI 正在思考中...
          </div>
        </div>

        <div class="grid gap-4">
          <div class="overflow-hidden rounded-2xl border border-[#ececec] bg-white shadow-sm">
            <div class="h-40 bg-[linear-gradient(135deg,#fff5dc,#f8f8f8)]"></div>
            <div class="flex items-center justify-between border-t border-[#f0f0f0] px-4 py-3 text-sm">
              <span class="font-medium text-[#3a3a3a]">候选人画面</span>
              <span class="rounded-full bg-[#eef8ec] px-2 py-0.5 text-xs text-[#2f8f2f]">在线</span>
            </div>
          </div>

          <div class="overflow-hidden rounded-2xl border border-[#ececec] bg-white shadow-sm">
            <div class="h-40 bg-[linear-gradient(135deg,#fff7e6,#f6f6f6)]"></div>
            <div class="flex items-center justify-between border-t border-[#f0f0f0] px-4 py-3 text-sm">
              <span class="font-medium text-[#3a3a3a]">AI 面试官</span>
              <span class="rounded-full bg-[#fff3d4] px-2 py-0.5 text-xs text-[#b67b00]">追问中</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import { experienceLevelOptions, jobTitleOptions, type ExperienceLevelValue } from '../../constants/interviewOptions'
import { chatMessages, directionTags } from '../../mock/homeData'

const emit = defineEmits<{
  start: [payload: { jobTitle: string; experienceLevel: ExperienceLevelValue }]
}>()

const defaultJobTitle = jobTitleOptions[0] ?? '前端'
const defaultExperienceLevel = (experienceLevelOptions[0]?.value ?? 'intern') as ExperienceLevelValue

const selectedJobTitle = ref<string>(defaultJobTitle)
const selectedExperienceLevel = ref<ExperienceLevelValue>(defaultExperienceLevel)

function handleStart() {
  emit('start', {
    jobTitle: selectedJobTitle.value,
    experienceLevel: selectedExperienceLevel.value,
  })
}
</script>
