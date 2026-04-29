<template>
  <div class="rounded-[32px] border border-white/60 bg-white/70 p-4 shadow-[0_18px_50px_rgba(79,56,36,0.08)] backdrop-blur">
    <div class="flex flex-wrap items-center gap-3 sm:gap-4">
      <div v-for="step in steps" :key="step.id" class="flex items-center gap-3">
        <div class="flex items-center gap-3 rounded-full px-1.5 py-1" :class="step.id <= current ? 'bg-[#fff4e8]' : 'bg-stone-100/80'">
          <div
            class="flex h-9 w-9 items-center justify-center rounded-full text-sm font-semibold transition"
            :class="step.id <= current ? 'bg-[linear-gradient(135deg,#1f1710,#c56b35)] text-white shadow-[0_10px_20px_rgba(197,107,53,0.24)]' : 'bg-white text-stone-400'"
          >
            {{ step.id }}
          </div>
          <p class="pr-3 text-sm font-medium" :class="step.id <= current ? 'text-stone-950' : 'text-stone-500'">
            {{ step.label }}
          </p>
        </div>
        <div v-if="step.id < steps.length" class="hidden h-px w-10 bg-stone-200 sm:block"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    current?: number
  }>(),
  {
    current: 1,
  },
)

const steps = [
  { id: 1, label: '配置面试' },
  { id: 2, label: '开始面试' },
]
</script>
