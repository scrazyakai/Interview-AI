<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const showToast = ref(true)
const openQuestion = ref<number | null>(0)

function toggleQuestion(idx: number) {
  openQuestion.value = openQuestion.value === idx ? null : idx
}

const radarDims = [
  { label: '沟通', score: 92, x: 50, y: 15 },
  { label: '技术', score: 85, x: 85, y: 40 },
  { label: '解决问题', score: 78, x: 75, y: 80 },
  { label: '自信度', score: 88, x: 25, y: 80 },
  { label: '逻辑结构', score: 82, x: 15, y: 40 },
]

const highlights = [
  '在回答 STAR 问题时表现出极佳的结构性。你的案例简洁且相关性强。',
  '优秀的目光接触和语速控制。你的非语言信号传达了高度的专业自信。',
]

const improvements = [
  '在项目描述中提供更多具体的量化指标（例如：延迟降低的百分比或用户增长数）。',
  '在讨论数据库分片时，系统设计组件需要更深入的可扩展性分析。',
]

const qaItems = [
  {
    q: '"请谈谈你处理重大技术故障的一次经历。"',
    userAnswer: '"……然后我们意识到迁移脚本有一个错误。我立即停止了部署，并与 DBA 协调进行回滚。我们在 15 分钟内恢复了服务……"',
    aiComment: '回答非常务实且具有行动导向。但是，你漏掉了描述对业务的影响。是否有客户丢失了数据？事后复盘的结果是什么？',
  },
  {
    q: '"你在高并发环境下如何处理数据库分片？"',
    userAnswer: '"我们使用了基于哈希的分片策略，并结合了读写分离……"',
    aiComment: '技术思路正确，但缺乏对实际业务场景的具体数据支撑和对潜在热点问题的讨论。',
  },
]
</script>

<template>
  <div class="min-h-screen pb-32" style="background-color: #f8f9ff; color: #0b1c30;">
    <!-- TopAppBar -->
    <header class="fixed top-0 w-full z-50 h-16 flex justify-between items-center px-6"
            style="background: rgba(248,249,255,0.8); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-bottom: 1px solid rgba(197,197,211,0.2); box-shadow: 0 1px 4px rgba(30,58,138,0.04);">
      <div class="flex items-center gap-3 cursor-pointer">
        <span class="material-symbols-outlined" style="color: #00236f;">menu</span>
        <span class="font-bold text-2xl leading-tight" style="color: #00236f; font-family: 'Inter', sans-serif;">InterviewAI</span>
      </div>
      <div class="flex items-center gap-6">
        <nav class="hidden md:flex gap-6 items-center">
          <RouterLink to="/" class="text-base transition-colors px-3 py-1 rounded-full" style="font-family: 'Inter', sans-serif; color: #444651;">首页</RouterLink>
          <RouterLink to="/interview/setup" class="text-base transition-colors px-3 py-1 rounded-full" style="font-family: 'Inter', sans-serif; color: #444651;">面试</RouterLink>
          <RouterLink to="/results" class="text-2xl font-semibold px-3 py-1 rounded-full" style="font-family: 'Inter', sans-serif; color: #00236f;">结果</RouterLink>
          <RouterLink to="/profile" class="text-base transition-colors px-3 py-1 rounded-full" style="font-family: 'Inter', sans-serif; color: #444651;">设置</RouterLink>
        </nav>
        <div class="w-10 h-10 rounded-full overflow-hidden flex items-center justify-center" style="background-color: #1e3a8a;">
          <span class="font-bold text-sm" style="color: #90a8ff; font-family: 'Inter', sans-serif;">A</span>
        </div>
      </div>
    </header>

    <main class="max-w-screen-xl mx-auto px-6 pt-24 pb-12">

      <!-- Summary Header -->
      <section class="rounded-xl p-12 mb-6 flex flex-col md:flex-row justify-between items-center gap-6"
               style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
        <div>
          <span class="text-xs font-semibold tracking-widest uppercase block mb-2" style="font-family: 'JetBrains Mono', monospace; color: #006c49;">会话已完成</span>
          <h2 class="font-bold mb-4" style="font-family: 'Inter', sans-serif; font-size: 48px; line-height: 1.2; letter-spacing: -0.02em; color: #00236f;">
            面试完成！您的得分：88/100
          </h2>
          <p class="max-w-2xl" style="font-family: 'Inter', sans-serif; font-size: 18px; line-height: 1.6; color: #444651;">
            表现出色！你展示了扎实的技术功底和清晰的逻辑结构。你的得分在高级工程师候选人中排名前 12%。
          </p>
        </div>
        <!-- Circular Progress Ring -->
        <div class="relative w-48 h-48 flex-shrink-0 flex items-center justify-center">
          <svg class="w-full h-full" style="transform: rotate(-90deg);" viewBox="0 0 192 192">
            <circle cx="96" cy="96" r="80" fill="transparent" stroke="#d3e4fe" stroke-width="12"/>
            <circle cx="96" cy="96" r="80" fill="transparent" stroke="#006c49" stroke-width="12"
                    stroke-dasharray="502.6" stroke-dashoffset="60"/>
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="font-bold" style="font-family: 'Inter', sans-serif; font-size: 36px; line-height: 1.2; color: #00236f;">88%</span>
            <span class="text-xs font-semibold tracking-widest uppercase" style="font-family: 'JetBrains Mono', monospace; color: #444651;">总体得分</span>
          </div>
        </div>
      </section>

      <!-- Bento Grid -->
      <div class="grid grid-cols-1 md:grid-cols-12 gap-6">

        <!-- Skill Radar -->
        <div class="md:col-span-5 rounded-xl p-6 flex flex-col"
             style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
          <h3 class="font-semibold mb-6" style="font-family: 'Inter', sans-serif; font-size: 24px; line-height: 1.3; color: #00236f;">技能分析</h3>
          <div class="flex-grow flex items-center justify-center relative py-6">
            <!-- Radar Grids -->
            <div class="absolute radar-grid opacity-20" style="width: 256px; height: 256px; border: 1px solid #c5c5d3;"></div>
            <div class="absolute radar-grid opacity-40" style="width: 192px; height: 192px; border: 1px solid #c5c5d3;"></div>
            <div class="absolute radar-grid opacity-60" style="width: 128px; height: 128px; border: 1px solid #c5c5d3;"></div>
            <!-- Radar SVG -->
            <svg class="w-64 h-64 drop-shadow-lg" viewBox="0 0 100 100">
              <polygon points="50,15 85,40 75,80 25,80 15,40"
                       fill="rgba(0,108,73,0.2)" stroke="#006c49" stroke-width="2"/>
              <circle v-for="dim in radarDims" :key="dim.label" :cx="dim.x" :cy="dim.y" r="2.5" fill="#006c49"/>
            </svg>
            <!-- Labels -->
            <span class="absolute top-4 left-1/2 -translate-x-1/2 text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace; color: #00236f;">沟通 (92)</span>
            <span class="absolute right-0 font-semibold text-xs tracking-widest" style="top: 33%; font-family: 'JetBrains Mono', monospace; color: #00236f;">技术 (85)</span>
            <span class="absolute right-4 bottom-4 text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace; color: #00236f;">解决问题 (78)</span>
            <span class="absolute left-4 bottom-4 text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace; color: #00236f;">自信度 (88)</span>
            <span class="absolute left-0 text-xs font-semibold tracking-widest" style="top: 33%; font-family: 'JetBrains Mono', monospace; color: #00236f;">逻辑结构 (82)</span>
          </div>
          <div class="mt-4 pt-4" style="border-top: 1px solid rgba(197,197,211,0.1);">
            <p class="text-sm italic" style="font-family: 'Inter', sans-serif; color: #444651; line-height: 1.5;">
              "沟通是你最强的特质，尤其是你清晰阐述复杂权衡的能力。"
            </p>
          </div>
        </div>

        <!-- Highlights & Improvements -->
        <div class="md:col-span-7 flex flex-col gap-6">
          <!-- Highlights -->
          <div class="rounded-xl p-6" style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3); border-left: 4px solid #006c49; box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
            <div class="flex items-center gap-3 mb-4">
              <span class="material-symbols-outlined" style="color: #006c49; font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;">check_circle</span>
              <h3 class="font-semibold" style="font-family: 'Inter', sans-serif; font-size: 24px; line-height: 1.3; color: #006c49;">核心亮点</h3>
            </div>
            <ul class="space-y-4">
              <li v-for="item in highlights" :key="item" class="flex gap-4">
                <span class="w-2 h-2 rounded-full flex-shrink-0 mt-2" style="background-color: #006c49;"></span>
                <p style="font-family: 'Inter', sans-serif; font-size: 16px; line-height: 1.6; color: #0b1c30;" v-html="item"></p>
              </li>
            </ul>
          </div>

          <!-- Improvements -->
          <div class="rounded-xl p-6" style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3); border-left: 4px solid #ba1a1a; box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
            <div class="flex items-center gap-3 mb-4">
              <span class="material-symbols-outlined" style="color: #ba1a1a; font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;">error</span>
              <h3 class="font-semibold" style="font-family: 'Inter', sans-serif; font-size: 24px; line-height: 1.3; color: #ba1a1a;">改进建议</h3>
            </div>
            <ul class="space-y-4">
              <li v-for="item in improvements" :key="item" class="flex gap-4">
                <span class="w-2 h-2 rounded-full flex-shrink-0 mt-2" style="background-color: #ba1a1a;"></span>
                <p style="font-family: 'Inter', sans-serif; font-size: 16px; line-height: 1.6; color: #0b1c30;">{{ item }}</p>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Q&A Review -->
      <section class="mt-20">
        <h2 class="font-semibold mb-12" style="font-family: 'Inter', sans-serif; font-size: 36px; line-height: 1.2; letter-spacing: -0.01em; color: #00236f;">
          问答详情回顾
        </h2>
        <div class="space-y-6">
          <div v-for="(item, idx) in qaItems" :key="idx"
               class="rounded-xl overflow-hidden"
               style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
            <button
              class="w-full flex justify-between items-center p-6 text-left transition-all"
              style="font-family: 'Inter', sans-serif;"
              :style="openQuestion === idx ? 'background-color: rgba(220,233,255,0.5);' : ''"
              @click="toggleQuestion(idx)">
              <div class="flex items-center gap-6">
                <span class="text-xs font-semibold tracking-widest uppercase px-3 py-1 rounded-full"
                      style="font-family: 'JetBrains Mono', monospace; background-color: #1e3a8a; color: #90a8ff;">
                  Q{{ idx + 1 }}
                </span>
                <span class="font-semibold text-lg" style="color: #00236f;">{{ item.q }}</span>
              </div>
              <span class="material-symbols-outlined flex-shrink-0 transition-transform" style="color: #757682;"
                    :style="openQuestion === idx ? 'transform: rotate(180deg);' : ''">
                expand_more
              </span>
            </button>
            <div v-if="openQuestion === idx" class="p-6" style="background: rgba(239,244,255,0.5); border-top: 1px solid rgba(197,197,211,0.1);">
              <div class="grid md:grid-cols-2 gap-6">
                <div class="space-y-2">
                  <h4 class="text-xs font-semibold tracking-widest uppercase" style="font-family: 'JetBrains Mono', monospace; color: #444651;">你的回答片段</h4>
                  <div class="p-4 rounded-lg text-sm italic" style="font-family: 'Inter', sans-serif; background-color: #f8f9ff; border: 1px solid rgba(197,197,211,0.1); color: #0b1c30; line-height: 1.6;">
                    {{ item.userAnswer }}
                  </div>
                </div>
                <div class="space-y-2">
                  <h4 class="text-xs font-semibold tracking-widest uppercase" style="font-family: 'JetBrains Mono', monospace; color: #006c49;">AI 评语</h4>
                  <p class="text-sm" style="font-family: 'Inter', sans-serif; color: #0b1c30; line-height: 1.6;">{{ item.aiComment }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA Section -->
      <section class="mt-20 rounded-xl p-12 text-center"
               style="background: linear-gradient(135deg, #00236f 0%, #1e3a8a 100%); box-shadow: 0 10px 30px rgba(30,58,138,0.15);">
        <h2 class="font-semibold mb-4" style="font-family: 'Inter', sans-serif; font-size: 36px; line-height: 1.2; letter-spacing: -0.01em; color: #dce1ff;">
          准备好进阶了吗？
        </h2>
        <p class="mb-6 max-w-xl mx-auto" style="font-family: 'Inter', sans-serif; font-size: 18px; line-height: 1.6; color: rgba(220,225,255,0.9);">
          根据你的表现，我们建议你在下一次练习中重点关注 <strong>系统设计</strong> 和 <strong>数据指标</strong>。
        </p>
        <div class="flex flex-col sm:flex-row justify-center gap-6">
          <RouterLink to="/interview/setup"
            class="flex items-center justify-center gap-2 px-12 py-4 rounded-lg font-semibold transition-all active:scale-95"
            style="background-color: #006c49; color: #ffffff; font-family: 'Inter', sans-serif; font-size: 16px; line-height: 1;">
            <span class="material-symbols-outlined">play_circle</span>
            开始下一次练习
          </RouterLink>
          <button
            class="px-12 py-4 rounded-lg font-semibold transition-all active:scale-95"
            style="background: transparent; border: 1px solid #b6c4ff; color: #b6c4ff; font-family: 'Inter', sans-serif; font-size: 16px; line-height: 1;">
            下载完整 PDF 报告
          </button>
        </div>
      </section>

    </main>

    <!-- Mobile Bottom Nav -->
    <nav class="md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-2 rounded-t-xl"
         style="background: rgba(248,249,255,0.8); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-top: 1px solid rgba(197,197,211,0.2); box-shadow: 0 -10px 30px rgba(30,58,138,0.05);">
      <RouterLink to="/" class="flex flex-col items-center justify-center py-1 px-4 transition-all" style="color: #444651;">
        <span class="material-symbols-outlined">home</span>
        <span class="text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace;">首页</span>
      </RouterLink>
      <RouterLink to="/interview/setup" class="flex flex-col items-center justify-center py-1 px-4 transition-all" style="color: #444651;">
        <span class="material-symbols-outlined">video_chat</span>
        <span class="text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace;">面试</span>
      </RouterLink>
      <RouterLink to="/results" class="flex flex-col items-center justify-center py-1 px-4 rounded-full transition-all" style="background-color: #1e3a8a; color: #90a8ff;">
        <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;">analytics</span>
        <span class="text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace;">结果</span>
      </RouterLink>
      <RouterLink to="/profile" class="flex flex-col items-center justify-center py-1 px-4 transition-all" style="color: #444651;">
        <span class="material-symbols-outlined">settings</span>
        <span class="text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace;">设置</span>
      </RouterLink>
    </nav>

    <!-- AI Feedback Toast -->
    <div v-if="showToast"
         class="fixed right-6 bottom-6 z-40 hidden md:flex items-center gap-4 max-w-sm rounded-xl p-4"
         style="background: rgba(255,255,255,0.9); backdrop-filter: blur(30px); -webkit-backdrop-filter: blur(30px); border: 1px solid rgba(255,255,255,0.5); border-left: 4px solid #006c49; box-shadow: 0 20px 60px rgba(30,58,138,0.12);">
      <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" style="background: rgba(0,108,73,0.1); color: #006c49;">
        <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;">psychology</span>
      </div>
      <div class="flex-1">
        <h5 class="font-semibold text-sm mb-1" style="font-family: 'Inter', sans-serif; color: #00236f;">专业贴士</h5>
        <p class="text-sm leading-tight" style="font-family: 'Inter', sans-serif; color: #444651;">下次试试用"X-Y-Z 公式"来描述你的项目指标！</p>
      </div>
      <button @click="showToast = false" class="transition-colors flex-shrink-0" style="color: #757682;">
        <span class="material-symbols-outlined">close</span>
      </button>
    </div>
  </div>
</template>
