<template>
  <section class="px-4 py-16 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="text-center">
        <h2 class="text-3xl font-bold text-[#1f1f1f] sm:text-4xl">
          全方位锻炼你的
          <span class="text-[#f5b61b]">面试竞争力</span>
        </h2>
        <p class="mt-4 text-sm text-[#7a7a7a]">选择合适的面试模式，突破短板，放大长板。</p>
      </div>

      <div class="mt-10 grid gap-6 lg:grid-cols-3">
        <article
          v-for="card in featureCards"
          :key="card.title"
          class="rounded-2xl border border-[#ececec] bg-white p-6 shadow-[0_12px_26px_rgba(15,23,42,0.06)] transition hover:-translate-y-1 hover:shadow-[0_18px_34px_rgba(15,23,42,0.09)]"
        >
          <div class="inline-flex h-11 w-11 items-center justify-center rounded-full bg-[#fff2cf] text-lg text-[#c88f0f]">
            {{ card.icon }}
          </div>

          <h3 class="mt-5 text-2xl font-semibold text-[#222]">{{ card.title }}</h3>
          <p class="mt-3 text-sm leading-6 text-[#666]">{{ card.description }}</p>

          <ul class="mt-5 space-y-2 text-sm text-[#555]">
            <li v-for="point in card.points" :key="point" class="flex items-center gap-2">
              <span class="h-1.5 w-1.5 rounded-full bg-[#f5b61b]"></span>
              {{ point }}
            </li>
          </ul>

          <div class="mt-5 flex flex-wrap gap-2">
            <span
              v-for="tag in card.tags"
              :key="tag"
              class="rounded-full bg-[#f6f6f6] px-3 py-1 text-xs text-[#707070]"
            >
              {{ tag }}
            </span>
          </div>

          <button
            type="button"
            class="mt-7 h-11 w-full rounded-xl bg-[#f5b61b] text-sm font-semibold text-white transition hover:bg-[#e5a300]"
          >
            {{ card.button }}
          </button>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { featureCards } from '../../mock/homeData'
</script>
