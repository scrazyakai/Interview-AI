<template>
  <section class="px-4 py-16 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="text-center">
        <h2 class="text-3xl font-bold text-[#1e1e1e] sm:text-4xl">
          为什么选择
          <span class="text-[#f5b61b]">面多多</span>
        </h2>
      </div>

      <div class="mt-10 grid gap-5 lg:grid-cols-2">
        <article
          v-for="item in whyTopCards"
          :key="item.title"
          class="rounded-2xl border border-[#f0ead8] bg-[#fffdf6] p-6 shadow-sm transition hover:shadow-md"
        >
          <h3 class="text-2xl font-semibold text-[#2a2a2a]">{{ item.title }}</h3>
          <p class="mt-2 text-sm leading-6 text-[#6d6d6d]">{{ item.desc }}</p>
          <div class="mt-5 h-24 rounded-xl bg-[linear-gradient(135deg,#fff5db,#f9f4e8)]"></div>
        </article>
      </div>

      <div class="mt-5 grid gap-5 md:grid-cols-3">
        <article
          v-for="item in whyBottomCards"
          :key="item.title"
          class="rounded-2xl border border-[#f1ecdf] bg-[#fffef9] p-5 shadow-sm transition hover:shadow-md"
        >
          <h3 class="text-xl font-semibold text-[#2a2a2a]">{{ item.title }}</h3>
          <p class="mt-2 text-sm leading-6 text-[#737373]">{{ item.desc }}</p>
          <div class="mt-4 h-16 rounded-lg bg-[linear-gradient(135deg,#fff8e8,#f8f6ef)]"></div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { whyBottomCards, whyTopCards } from '../../mock/homeData'
</script>
