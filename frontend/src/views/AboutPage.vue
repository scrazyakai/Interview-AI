<template>
  <main class="relative overflow-hidden bg-[#f7f3eb] text-stone-900">
    <div
      class="pointer-events-none absolute inset-x-0 top-0 h-[420px] bg-[radial-gradient(circle_at_top_left,_rgba(214,145,84,0.24),_transparent_42%),radial-gradient(circle_at_top_right,_rgba(111,78,55,0.14),_transparent_38%)]"
    />

    <section class="relative mx-auto max-w-6xl px-4 pb-16 pt-10 sm:px-6 lg:px-8 lg:pt-16">
      <div class="grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
        <div>
          <p
            class="inline-flex rounded-full border border-stone-300/80 bg-white/70 px-4 py-1 text-xs font-semibold uppercase tracking-[0.32em] text-stone-600 backdrop-blur"
          >
            Product Story
          </p>
          <h1 class="mt-6 max-w-4xl font-serif text-4xl leading-tight text-stone-950 sm:text-5xl lg:text-6xl">
            把模拟面试做成一场
            <span class="text-[#9f4f22]">可训练、可复盘、可成长</span>
            的产品体验。
          </h1>
          <p class="mt-6 max-w-2xl text-base leading-8 text-stone-700 sm:text-lg">
            产品介绍页聚焦三个核心目标：帮用户更快进入练习状态、让反馈足够具体、让每一次训练都能沉淀为下一次进步的起点。
          </p>
        </div>

        <div class="rounded-[32px] border border-stone-300/70 bg-white/80 p-6 shadow-[0_24px_80px_rgba(75,54,33,0.12)] backdrop-blur">
          <p class="text-sm font-semibold uppercase tracking-[0.22em] text-stone-500">Core Promise</p>
          <div class="mt-5 space-y-4">
            <article
              v-for="highlight in highlights"
              :key="highlight.title"
              class="rounded-[24px] border border-stone-200 bg-stone-50/80 p-4"
            >
              <p class="text-sm text-stone-500">{{ highlight.kicker }}</p>
              <h2 class="mt-2 text-xl font-semibold text-stone-950">{{ highlight.title }}</h2>
              <p class="mt-2 text-sm leading-7 text-stone-700">{{ highlight.description }}</p>
            </article>
          </div>
        </div>
      </div>
    </section>

    <section class="relative mx-auto max-w-6xl px-4 pb-20 sm:px-6 lg:px-8">
      <div class="grid gap-6 md:grid-cols-3">
        <article
          v-for="pillar in pillars"
          :key="pillar.title"
          class="rounded-[28px] border border-stone-200/80 bg-white/85 p-6 shadow-[0_20px_60px_rgba(88,62,40,0.08)] backdrop-blur"
        >
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-stone-500">{{ pillar.eyebrow }}</p>
          <h3 class="mt-4 text-2xl font-semibold text-stone-950">{{ pillar.title }}</h3>
          <p class="mt-4 text-sm leading-7 text-stone-700">{{ pillar.description }}</p>
        </article>
      </div>

      <div class="mt-8 grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <section class="rounded-[32px] bg-stone-950 p-7 text-stone-100 shadow-[0_26px_80px_rgba(25,20,16,0.28)]">
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-stone-400">Experience Loop</p>
          <div class="mt-6 space-y-5">
            <div v-for="step in journey" :key="step.title" class="rounded-[24px] border border-white/10 bg-white/5 p-5">
              <div class="flex items-center gap-3">
                <span
                  class="inline-flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-sm font-semibold text-white"
                >
                  {{ step.index }}
                </span>
                <h3 class="text-lg font-semibold">{{ step.title }}</h3>
              </div>
              <p class="mt-3 text-sm leading-7 text-stone-300">{{ step.description }}</p>
            </div>
          </div>
        </section>

        <section class="rounded-[32px] border border-stone-300/70 bg-[#efe4d3] p-7">
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-stone-500">Why It Feels Different</p>
          <div class="mt-6 grid gap-4 sm:grid-cols-2">
            <article
              v-for="detail in details"
              :key="detail.title"
              class="rounded-[24px] border border-stone-300/70 bg-white/70 p-5"
            >
              <h3 class="text-lg font-semibold text-stone-950">{{ detail.title }}</h3>
              <p class="mt-3 text-sm leading-7 text-stone-700">{{ detail.description }}</p>
            </article>
          </div>
        </section>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
const highlights = [
  {
    kicker: 'Start Fast',
    title: '用更低门槛开始第一次练习',
    description: '从岗位、经验、模式到简历信息，入口流程尽量短，让用户先进入面试状态，再逐步完善资料。',
  },
  {
    kicker: 'Coach Better',
    title: '把 AI 反馈做成真实陪练',
    description: '不仅输出结果，更强调追问、节奏、表达质量和内容深度，让训练接近真实面试氛围。',
  },
  {
    kicker: 'Grow Continuously',
    title: '让每次训练都能沉淀',
    description: '围绕复盘和可持续练习设计流程，帮助用户形成一条从准备到提升的长期成长曲线。',
  },
] as const

const pillars = [
  {
    eyebrow: '01',
    title: '准备信息结构化',
    description: '岗位方向、经验阶段、简历内容和岗位描述被清晰组织，为后续面试上下文建立更稳定的输入。',
  },
  {
    eyebrow: '02',
    title: '模拟过程更像真实对话',
    description: '产品不是静态问答器，而是更接近面试现场的动态交流空间，帮助用户提前适应压力与节奏。',
  },
  {
    eyebrow: '03',
    title: '复盘结果可直接行动',
    description: '最终不只告诉用户“好或不好”，而是把问题落到表达、内容、结构和准备重点上。',
  },
] as const

const journey = [
  {
    index: '1',
    title: '选择目标岗位与练习模式',
    description: '通过简洁配置建立训练上下文，降低第一次使用门槛。',
  },
  {
    index: '2',
    title: '进入模拟面试并实时应答',
    description: '用户在真实节奏中完成回答，更容易暴露表达和思路上的薄弱点。',
  },
  {
    index: '3',
    title: '获得反馈并继续下一轮优化',
    description: '把每轮练习转化为可执行的改进建议，让产品形成持续训练闭环。',
  },
] as const

const details = [
  {
    title: '统一入口体验',
    description: '首页、模拟面试、产品介绍现在都通过独立路由页面渲染，导航行为更明确，用户心智也更稳定。',
  },
  {
    title: '组件职责更清晰',
    description: 'View 负责页面壳层和路由承接，Page 负责页面内容，后续扩展时不容易互相牵连。',
  },
  {
    title: '更适合继续扩展',
    description: '后面如果继续加入案例、定价、FAQ 或多语言内容，可以直接在产品介绍页内部扩展组件层。',
  },
  {
    title: '导航状态可预测',
    description: '页面高亮直接由路由路径驱动，不需要额外的页面状态同步逻辑。',
  },
] as const
</script>
