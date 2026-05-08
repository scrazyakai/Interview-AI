<template>
  <div class="min-h-screen" style="background-color: #f8f9ff; color: #0b1c30;">
    <!-- Fixed TopAppBar -->
    <header class="fixed top-0 z-50 w-full h-16 flex justify-between items-center px-6"
            style="background: rgba(248,249,255,0.8); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-bottom: 1px solid rgba(197,197,211,0.2); box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined cursor-pointer" style="color: #00236f; font-size: 24px;">psychology</span>
        <RouterLink to="/" class="font-bold text-xl" style="color: #00236f; text-decoration: none; font-family: 'Inter', sans-serif;">InterviewAI</RouterLink>
      </div>
      <nav class="hidden md:flex items-center gap-6">
        <span class="text-sm cursor-pointer" style="color: #444651; font-family: 'Inter', sans-serif;">功能特性</span>
        <span class="text-sm cursor-pointer" style="color: #444651; font-family: 'Inter', sans-serif;">价格方案</span>
        <span class="text-sm cursor-pointer" style="color: #444651; font-family: 'Inter', sans-serif;">关于我们</span>
      </nav>
      <div class="flex items-center gap-3">
        <RouterLink to="/interview/setup"
          class="hidden md:inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold transition-all"
          style="color: #00236f; border: 1px solid #00236f; background: transparent; text-decoration: none; font-family: 'Inter', sans-serif;">
          登录
        </RouterLink>
        <RouterLink to="/interview/setup"
          class="inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold transition-all"
          style="background-color: #00236f; color: #ffffff; text-decoration: none; font-family: 'Inter', sans-serif;">
          免费开始
        </RouterLink>
      </div>
    </header>

    <main class="pt-16">
      <!-- Hero Section -->
      <section class="max-w-7xl mx-auto px-6 py-20 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <!-- Left: Headline + CTAs + Social Proof -->
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full mb-6"
               style="background-color: #eff4ff; border: 1px solid #c5c5d3;">
            <span class="material-symbols-outlined text-sm" style="color: #006c49; font-size: 16px;">auto_awesome</span>
            <span class="text-xs font-semibold" style="color: #006c49; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05em;">AI-POWERED COACHING</span>
          </div>
          <h1 class="font-bold mb-6" style="font-family: 'Inter', sans-serif; font-size: 48px; line-height: 1.2; letter-spacing: -0.02em; color: #0b1c30;">
            用 AI 掌控<br/>你的下一次面试
          </h1>
          <p class="mb-8 text-lg" style="color: #444651; font-family: 'Inter', sans-serif; line-height: 1.6;">
            通过实时 AI 反馈、个性化题库和深度面试分析，帮助你在技术面试中脱颖而出，斩获心仪 offer。
          </p>
          <div class="flex flex-col sm:flex-row gap-4 mb-10">
            <RouterLink to="/interview/setup"
              class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-lg font-semibold text-base transition-all"
              style="background-color: #006c49; color: #ffffff; text-decoration: none; font-family: 'Inter', sans-serif;">
              <span class="material-symbols-outlined text-xl">play_circle</span>
              免费开始模拟
            </RouterLink>
            <RouterLink to="/interview/setup"
              class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-lg font-semibold text-base transition-all"
              style="background: transparent; color: #00236f; border: 1px solid #00236f; text-decoration: none; font-family: 'Inter', sans-serif;">
              查看演示
              <span class="material-symbols-outlined text-xl">arrow_forward</span>
            </RouterLink>
          </div>
          <!-- Social proof -->
          <div class="flex items-center gap-3">
            <div class="flex -space-x-2">
              <div class="w-8 h-8 rounded-full border-2 border-white flex items-center justify-center text-xs font-bold text-white"
                   style="background-color: #1e3a8a;">L</div>
              <div class="w-8 h-8 rounded-full border-2 border-white flex items-center justify-center text-xs font-bold text-white"
                   style="background-color: #006c49;">Z</div>
              <div class="w-8 h-8 rounded-full border-2 border-white flex items-center justify-center text-xs font-bold text-white"
                   style="background-color: #2724b8;">W</div>
              <div class="w-8 h-8 rounded-full border-2 border-white flex items-center justify-center text-xs font-bold text-white"
                   style="background-color: #4059aa;">A</div>
            </div>
            <div>
              <div class="flex items-center gap-1">
                <span v-for="i in 5" :key="i" class="material-symbols-outlined text-sm" style="color: #006c49; font-size: 16px; font-variation-settings: 'FILL' 1;">star</span>
              </div>
              <p class="text-sm" style="color: #444651; font-family: 'Inter', sans-serif;">
                <span class="font-semibold" style="color: #0b1c30;">50,000+</span> 名求职者已在使用
              </p>
            </div>
          </div>
        </div>

        <!-- Right: Glass Card with Video Preview -->
        <div class="relative">
          <div class="rounded-2xl p-6" style="background: rgba(255,255,255,0.7); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.08);">
            <!-- Mock video -->
            <div class="w-full aspect-video rounded-xl mb-4 relative overflow-hidden flex items-center justify-center"
                 style="background: linear-gradient(135deg, #1e3a8a 0%, #00236f 100%);">
              <span class="material-symbols-outlined text-white opacity-80" style="font-size: 64px;">video_chat</span>
              <!-- Timer pill -->
              <div class="absolute top-3 right-3 px-3 py-1 rounded-full flex items-center gap-1"
                   style="background: rgba(255,255,255,0.15); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.2);">
                <span class="material-symbols-outlined text-white" style="font-size: 16px;">schedule</span>
                <span class="text-white font-semibold text-sm" style="font-family: 'JetBrains Mono', monospace;">04:32</span>
              </div>
            </div>
            <!-- Live feedback -->
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full animate-pulse" style="background-color: #006c49;"></div>
                <span class="text-xs font-semibold" style="color: #006c49; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05em;">LIVE AI FEEDBACK</span>
              </div>
              <span class="text-xs font-bold" style="color: #006c49; font-family: 'JetBrains Mono', monospace;">88%</span>
            </div>
            <div class="w-full rounded-full h-2 overflow-hidden" style="background-color: #e5eeff;">
              <div class="h-full rounded-full" style="width: 88%; background-color: #006c49;"></div>
            </div>
            <p class="text-xs mt-2" style="color: #444651; font-family: 'Inter', sans-serif;">自信度评分 — 表现优异</p>
          </div>
        </div>
      </section>

      <!-- Feature Bento Grid -->
      <section class="max-w-7xl mx-auto px-6 py-16">
        <div class="text-center mb-12">
          <p class="text-xs font-semibold mb-3" style="color: #006c49; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05em;">CORE FEATURES</p>
          <h2 class="font-bold" style="font-family: 'Inter', sans-serif; font-size: 36px; line-height: 1.2; letter-spacing: -0.01em; color: #0b1c30;">
            一站式面试准备平台
          </h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- AI Real-time Feedback (col-span-2) -->
          <div class="md:col-span-2 rounded-2xl p-6" style="background: rgba(255,255,255,0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center" style="background-color: #eff4ff;">
                <span class="material-symbols-outlined" style="color: #00236f; font-size: 20px;">analytics</span>
              </div>
              <div>
                <h3 class="font-semibold text-lg" style="color: #0b1c30; font-family: 'Inter', sans-serif;">实时 AI 反馈</h3>
                <p class="text-sm" style="color: #444651;">面试过程中即时分析你的表现</p>
              </div>
            </div>
            <!-- Mini bar chart -->
            <div class="flex items-end gap-2 h-20 mt-4">
              <div v-for="(bar, i) in barData" :key="i"
                   class="flex-1 rounded-t-md transition-all"
                   :style="{ height: bar.h + '%', backgroundColor: bar.color }"></div>
            </div>
            <div class="flex justify-between mt-2">
              <span v-for="label in ['沟通', '技术', '逻辑', '自信', '表达']" :key="label"
                    class="text-xs" style="color: #444651; font-family: 'JetBrains Mono', monospace;">{{ label }}</span>
            </div>
          </div>

          <!-- Industry Q&A Card -->
          <div class="rounded-2xl p-6 flex flex-col justify-between" style="background-color: #1e3a8a;">
            <div>
              <div class="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style="background: rgba(144,168,255,0.15);">
                <span class="material-symbols-outlined" style="color: #90a8ff; font-size: 20px;">quiz</span>
              </div>
              <h3 class="font-semibold text-lg mb-2" style="color: #ffffff; font-family: 'Inter', sans-serif;">行业真题库</h3>
              <p class="text-sm" style="color: #90a8ff; font-family: 'Inter', sans-serif; line-height: 1.5;">涵盖 FAANG、字节、腾讯等顶级公司历年真实面试题</p>
            </div>
            <div class="flex flex-wrap gap-2 mt-4">
              <span v-for="tag in questionTags" :key="tag"
                    class="px-2 py-1 rounded-full text-xs font-semibold"
                    style="background: rgba(144,168,255,0.15); color: #b6c4ff; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05em;">{{ tag }}</span>
            </div>
          </div>

          <!-- Voice & Text Card -->
          <div class="rounded-2xl p-6" style="background: rgba(255,255,255,0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style="background-color: #6cf8bb;">
              <span class="material-symbols-outlined" style="color: #006c49; font-size: 20px;">mic</span>
            </div>
            <h3 class="font-semibold text-lg mb-2" style="color: #0b1c30; font-family: 'Inter', sans-serif;">语音 & 文字双模式</h3>
            <p class="text-sm" style="color: #444651; font-family: 'Inter', sans-serif; line-height: 1.5;">支持语音作答和文字输入，灵活适配不同练习场景</p>
          </div>

          <!-- AI Tutor (col-span-2) -->
          <div class="md:col-span-2 rounded-2xl p-6 flex flex-col md:flex-row items-center gap-6" style="background: rgba(255,255,255,0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
            <div class="flex-1">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style="background-color: #e1e0ff;">
                <span class="material-symbols-outlined" style="color: #0d0097; font-size: 20px;">psychology</span>
              </div>
              <h3 class="font-semibold text-lg mb-2" style="color: #0b1c30; font-family: 'Inter', sans-serif;">AI 面试教练</h3>
              <p class="text-sm" style="color: #444651; font-family: 'Inter', sans-serif; line-height: 1.5;">
                专属 AI 教练根据你的简历和目标岗位，制定个性化训练计划，追踪成长轨迹
              </p>
            </div>
            <div class="w-full md:w-48 h-32 rounded-xl flex items-center justify-center"
                 style="background: linear-gradient(135deg, #e1e0ff, #dce1ff);">
              <span class="material-symbols-outlined" style="color: #0d0097; font-size: 48px;">smart_toy</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Trust Section -->
      <section class="max-w-7xl mx-auto px-6 py-12">
        <p class="text-center text-sm mb-8" style="color: #444651; font-family: 'Inter', sans-serif;">
          已帮助求职者成功入职
        </p>
        <div class="flex flex-wrap justify-center items-center gap-8 md:gap-16">
          <span v-for="company in companies" :key="company"
                class="text-lg font-bold tracking-wider"
                style="color: #c5c5d3; font-family: 'Inter', sans-serif;">{{ company }}</span>
        </div>
      </section>

      <!-- FAQ Section -->
      <section class="max-w-3xl mx-auto px-6 py-16">
        <h2 class="font-bold text-center mb-12" style="font-family: 'Inter', sans-serif; font-size: 36px; line-height: 1.2; letter-spacing: -0.01em; color: #0b1c30;">
          常见问题
        </h2>
        <div class="space-y-4">
          <details v-for="faq in faqs" :key="faq.q"
                   class="rounded-xl overflow-hidden"
                   style="background: rgba(255,255,255,0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
            <summary class="flex items-center justify-between px-6 py-4 cursor-pointer font-semibold"
                     style="color: #0b1c30; font-family: 'Inter', sans-serif; list-style: none;">
              {{ faq.q }}
              <span class="material-symbols-outlined" style="color: #444651;">expand_more</span>
            </summary>
            <div class="px-6 pb-4 text-sm" style="color: #444651; font-family: 'Inter', sans-serif; line-height: 1.6;">
              {{ faq.a }}
            </div>
          </details>
        </div>
      </section>

      <!-- CTA Banner -->
      <section class="max-w-7xl mx-auto px-6 py-8 mb-16">
        <div class="relative rounded-2xl overflow-hidden px-12 py-16 text-center"
             style="background-color: #1e3a8a;">
          <!-- Blob decorations -->
          <div class="absolute top-0 left-0 w-64 h-64 rounded-full opacity-10"
               style="background: #4059aa; transform: translate(-30%, -30%);"></div>
          <div class="absolute bottom-0 right-0 w-64 h-64 rounded-full opacity-10"
               style="background: #006c49; transform: translate(30%, 30%);"></div>
          <div class="relative z-10">
            <p class="text-xs font-semibold mb-4" style="color: #90a8ff; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05em;">START YOUR JOURNEY</p>
            <h2 class="font-bold mb-4 text-white" style="font-family: 'Inter', sans-serif; font-size: 36px; line-height: 1.2; letter-spacing: -0.01em;">
              今天就开始备战面试
            </h2>
            <p class="mb-8 text-lg" style="color: #90a8ff; font-family: 'Inter', sans-serif; line-height: 1.6;">
              无需信用卡，立即体验 AI 面试教练全部功能
            </p>
            <RouterLink to="/interview/setup"
              class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl font-semibold text-base transition-all"
              style="background-color: #006c49; color: #ffffff; text-decoration: none; font-family: 'Inter', sans-serif;">
              <span class="material-symbols-outlined">rocket_launch</span>
              免费开始使用
            </RouterLink>
          </div>
        </div>
      </section>

      <!-- Footer -->
      <footer class="max-w-7xl mx-auto px-6 pb-16 pt-8" style="border-top: 1px solid #c5c5d3;">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
          <div>
            <div class="flex items-center gap-2 mb-4">
              <span class="material-symbols-outlined" style="color: #00236f; font-size: 20px;">psychology</span>
              <span class="font-bold text-lg" style="color: #00236f; font-family: 'Inter', sans-serif;">InterviewAI</span>
            </div>
            <p class="text-sm" style="color: #444651; font-family: 'Inter', sans-serif; line-height: 1.6;">
              用 AI 的力量，帮助每一位求职者拿到心仪 offer。
            </p>
          </div>
          <div>
            <p class="font-semibold mb-4 text-sm" style="color: #0b1c30; font-family: 'Inter', sans-serif;">产品</p>
            <ul class="space-y-2">
              <li v-for="item in footerProduct" :key="item"
                  class="text-sm cursor-pointer" style="color: #444651; font-family: 'Inter', sans-serif;">{{ item }}</li>
            </ul>
          </div>
          <div>
            <p class="font-semibold mb-4 text-sm" style="color: #0b1c30; font-family: 'Inter', sans-serif;">公司</p>
            <ul class="space-y-2">
              <li v-for="item in footerCompany" :key="item"
                  class="text-sm cursor-pointer" style="color: #444651; font-family: 'Inter', sans-serif;">{{ item }}</li>
            </ul>
          </div>
          <div>
            <p class="font-semibold mb-4 text-sm" style="color: #0b1c30; font-family: 'Inter', sans-serif;">法律</p>
            <ul class="space-y-2">
              <li v-for="item in footerLegal" :key="item"
                  class="text-sm cursor-pointer" style="color: #444651; font-family: 'Inter', sans-serif;">{{ item }}</li>
            </ul>
          </div>
        </div>
        <p class="text-center text-xs" style="color: #757682; font-family: 'Inter', sans-serif;">
          © 2024 InterviewAI. 保留所有权利。
        </p>
      </footer>
    </main>

    <!-- Mobile Bottom Nav -->
    <nav class="md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-2 rounded-t-xl"
         style="background: rgba(248,249,255,0.8); backdrop-filter: blur(12px); border-top: 1px solid rgba(197,197,211,0.2); box-shadow: 0 -10px 30px rgba(30,58,138,0.05);">
      <RouterLink to="/" class="flex flex-col items-center py-1 px-4" style="text-decoration: none; color: #00236f;">
        <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1; font-size: 24px;">home</span>
        <span class="text-xs font-semibold" style="font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05em; font-size: 12px;">首页</span>
      </RouterLink>
      <RouterLink to="/interview/setup" class="flex flex-col items-center py-1 px-4" style="text-decoration: none; color: #444651;">
        <span class="material-symbols-outlined" style="font-size: 24px;">video_chat</span>
        <span class="text-xs" style="font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05em; font-size: 12px;">面试</span>
      </RouterLink>
      <RouterLink to="/results" class="flex flex-col items-center py-1 px-4" style="text-decoration: none; color: #444651;">
        <span class="material-symbols-outlined" style="font-size: 24px;">analytics</span>
        <span class="text-xs" style="font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05em; font-size: 12px;">结果</span>
      </RouterLink>
      <RouterLink to="/profile" class="flex flex-col items-center py-1 px-4" style="text-decoration: none; color: #444651;">
        <span class="material-symbols-outlined" style="font-size: 24px;">settings</span>
        <span class="text-xs" style="font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05em; font-size: 12px;">设置</span>
      </RouterLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'

const barData = [
  { h: 92, color: '#006c49' },
  { h: 85, color: '#006c49' },
  { h: 78, color: '#4edea3' },
  { h: 88, color: '#006c49' },
  { h: 82, color: '#4edea3' },
]

const questionTags = ['系统设计', '算法', 'STAR', '行为面试', 'LLD']

const companies = ['GOOGLE', 'META', 'AMAZON', 'APPLE', 'STRIPE', 'BYTEDANCE']

const faqs = [
  {
    q: 'InterviewAI 支持哪些类型的面试？',
    a: '我们支持技术面试（算法、系统设计、代码审查）、行为面试（STAR 方法论）、产品经理面试等多种类型，覆盖软件工程、数据科学、产品管理等主流岗位方向。',
  },
  {
    q: 'AI 反馈的准确度如何保证？',
    a: 'InterviewAI 基于数百万条真实面试数据训练，结合语音情感分析、语义理解和结构化评分框架，确保每条反馈既有数据支撑，又具备实用价值。',
  },
  {
    q: '我的面试数据会被保存吗？',
    a: '是的，所有面试记录都会安全存储在你的个人账户中，仅你本人可见。你可以随时回顾历史记录、对比成长曲线。',
  },
  {
    q: '免费版有哪些限制？',
    a: '免费版每月可进行 3 次完整模拟面试，包含基础 AI 反馈报告。升级到 Pro 版可解锁无限次练习、高级分析报告和 1v1 AI 教练模式。',
  },
]

const footerProduct = ['功能特性', '价格方案', '企业版', '更新日志']
const footerCompany = ['关于我们', '博客', '招聘', '联系我们']
const footerLegal = ['隐私政策', '服务条款', 'Cookie 设置']
</script>
