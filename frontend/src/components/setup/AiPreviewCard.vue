<template>
  <aside class="rounded-[32px] border border-white/60 bg-[linear-gradient(180deg,rgba(35,25,18,0.96),rgba(62,42,28,0.94))] p-6 text-stone-100 shadow-[0_28px_80px_rgba(31,21,15,0.28)]">
    <p class="text-[11px] font-semibold uppercase tracking-[0.3em] text-stone-400">AI Preview</p>
    <h3 class="mt-4 text-2xl font-semibold tracking-[-0.03em] text-white">你的面试即将被这样构建</h3>

    <div class="mt-6 space-y-3">
      <article v-for="item in highlights" :key="item" class="rounded-[22px] border border-white/10 bg-white/5 px-4 py-4">
        <div class="flex items-start gap-3">
          <span class="mt-1 inline-flex h-6 w-6 items-center justify-center rounded-full bg-[#f7a460]/20 text-xs font-semibold text-[#ffd5b7]">AI</span>
          <p class="text-sm leading-7 text-stone-200">{{ item }}</p>
        </div>
      </article>
    </div>

    <div class="mt-6 rounded-[24px] border border-[#f7a460]/20 bg-[#f7a460]/10 p-4">
      <p class="text-[11px] font-semibold uppercase tracking-[0.22em] text-[#ffd5b7]">Coach Tip</p>
      <p class="mt-3 text-sm leading-7 text-stone-100">{{ averageTip }}</p>
    </div>
  </aside>
</template>

<script setup lang="ts">
defineProps<{
  highlights: string[]
  averageTip: string
}>()
</script>
