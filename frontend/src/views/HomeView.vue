<template>
  <div class="min-h-screen" style="background-color: #f8f9ff; color: #0b1c30;">
    <main class="pt-16">
      <!-- Hero Section -->
      <section class="max-w-7xl mx-auto px-6 py-20 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <!-- Left: Headline + CTAs + Social Proof -->
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full mb-6"
               style="background-color: #eff4ff; border: 1px solid #c5c5d3;">
            <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" style="width:16px;height:16px;color:#006c49;"><path d="M10.007 2.10377C8.60544 1.65006 7.08181 2.28116 6.41156 3.59306L5.60578 5.17023C5.51004 5.35763 5.35763 5.51004 5.17023 5.60578L3.59306 6.41156C2.28116 7.08181 1.65006 8.60544 2.10377 10.007L2.64923 11.692C2.71404 11.8922 2.71404 12.1078 2.64923 12.308L2.10377 13.993C1.65006 15.3946 2.28116 16.9182 3.59306 17.5885L5.17023 18.3942C5.35763 18.49 5.51004 18.6424 5.60578 18.8298L6.41156 20.407C7.08181 21.7189 8.60544 22.35 10.007 21.8963L11.692 21.3508C11.8922 21.286 12.1078 21.286 12.308 21.3508L13.993 21.8963C15.3946 22.35 16.9182 21.7189 17.5885 20.407L18.3942 18.8298C18.49 18.6424 18.6424 18.49 18.8298 18.3942L20.407 17.5885C21.7189 16.9182 22.35 15.3946 21.8963 13.993L21.3508 12.308C21.286 12.1078 21.286 11.8922 21.3508 11.692L21.8963 10.007C22.35 8.60544 21.7189 7.08181 20.407 6.41156L18.8298 5.60578C18.6424 5.51004 18.49 5.35763 18.3942 5.17023L17.5885 3.59306C16.9182 2.28116 15.3946 1.65006 13.993 2.10377L12.308 2.64923C12.1078 2.71403 11.8922 2.71404 11.692 2.64923L10.007 2.10377ZM6.75977 11.7573L8.17399 10.343L11.0024 13.1715L16.6593 7.51465L18.0735 8.92886L11.0024 15.9999L6.75977 11.7573Z"></path></svg>
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
              开始模拟
            </RouterLink>
            <RouterLink to="/interview/setup"
              class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-lg font-semibold text-base transition-all"
              style="background: transparent; color: #00236f; border: 1px solid #00236f; text-decoration: none; font-family: 'Inter', sans-serif;">
              查看演示
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
                <span v-for="i in 5" :key="i" class="material-symbols-outlined text-sm" style="color: #006c49; font-size: 16px; font-variation-settings: 'FILL' 1;"></span>
              </div>
              <p class="text-sm" style="color: #444651; font-family: 'Inter', sans-serif;">
                <span class="font-semibold" style="color: #0b1c30;"></span> 多名求职者已在使用
              </p>
            </div>
          </div>
        </div>

        <!-- Right: Glass Card with Video Preview -->
        <div class="relative">
          <div class="rounded-2xl p-6" style="background: rgba(255,255,255,0.7); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.08);">
            <!-- Mock video -->
            <div class="w-full aspect-video rounded-xl mb-4 relative overflow-hidden flex items-center justify-center"
                 style="background: url('/src/assets/InterviewDemo.png') center/cover no-repeat;">

              <!-- Timer pill -->
              <div class="absolute top-3 right-3 px-3 py-1 rounded-full flex items-center gap-1"
                   style="background: rgba(255,255,255,0.15); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.2);">
                <svg t="1778295613857" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="22958" width="16" height="16"><path d="M938.666667 512c0 235.648-191.018667 426.666667-426.666667 426.666667S85.333333 747.648 85.333333 512 276.352 85.333333 512 85.333333s426.666667 191.018667 426.666667 426.666667z" fill="#d81e06" p-id="22959"></path></svg>
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
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="color:#00236f;width:20px;height:20px;"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"></path><path d="M7 12h2v5H7zm8-5h2v10h-2zm-4 7h2v3h-2zm0-4h2v2h-2z"></path></svg>
              </div>
              <div>
                <h3 class="font-semibold text-lg" style="color: #0b1c30; font-family: 'Inter', sans-serif;">实时 AI 反馈</h3>
                <p class="text-sm" style="color: #444651;">即时分析您的肢体语言、语气和内容质量。我们的 AI 会识别口头禅并即时建议更好的表达方式。</p>
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
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor" style="color:#90a8ff;width:20px;height:20px;"><path d="M184,89.57V84c0-25.08-37.83-44-88-44S8,58.92,8,84v40c0,20.89,26.25,37.49,64,42.46V172c0,25.08,37.83,44,88,44s88-18.92,88-44V132C248,111.3,222.58,94.68,184,89.57ZM232,172c0,13.22-30.79,28-72,28s-72-14.78-72-28V155.01c7.67,1.32,15.72,2.01,24,2.01,3.23,0,6.44-.1,9.62-.28C137.37,166.06,159.32,172,184,172c8.28,0,16.33-.69,24-2.01Zm-72-20a165.17,165.17,0,0,1-20.2-1.23l-1-.17-.7-.1A130.52,130.52,0,0,1,96,140.87V126.27a165.21,165.21,0,0,0,21.58,2.69C119.7,129,121.84,129,124,129s4.31-.05,6.43-.08A183.16,183.16,0,0,0,160,126.29V141A165.83,165.83,0,0,1,160,152ZM24,124V109.01C31.67,110.33,39.72,111,48,111s16.33-.67,24-1.99V124c0,13.22-30.79,28-72,28S24,137.22,24,124Zm96,0V109.03c4.13.61,8.37.97,12.76.97,2.16,0,4.3-.05,6.43-.08a183.56,183.56,0,0,0,28.81-2.86V120.87A148.44,148.44,0,0,1,160,124C149.3,124,138.26,122.69,120,120Zm48-11.03V94.59C181.43,97,193.26,104.18,196,112.35,183.54,115.27,167.68,116.61,168,108.97ZM88,68c41.21,0,72,14.78,72,28S129.21,124,88,124,16,109.22,16,96,46.79,68,88,68Zm-64,96V149.01C31.67,150.33,39.72,151,48,151s16.33-.67,24-1.99V164c0,13.22-30.79,28-72,28S24,177.22,24,164Zm160,28c-41.21,0-72-14.78-72-28V149.03c4.13.61,8.37.97,12.76.97,2.16,0,4.3-.05,6.43-.08a182.21,182.21,0,0,0,28.81-2.88V162c0,13.22,30.79,28,72,28,1.34,0,2.67-.02,4-.06C232.72,193.63,224,200,216,192Z"></path></svg>
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
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="color:#006c49;width:20px;height:20px;"><path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/></svg>
            </div>
            <h3 class="font-semibold text-lg mb-2" style="color: #0b1c30; font-family: 'Inter', sans-serif;">语音 & 文字双模式</h3>
            <p class="text-sm" style="color: #444651; font-family: 'Inter', sans-serif; line-height: 1.5;">支持语音作答和文字输入，灵活适配不同练习场景</p>
          </div>

          <!-- AI Tutor (col-span-2) -->
          <div class="md:col-span-2 rounded-2xl p-6 flex flex-col md:flex-row items-center gap-6" style="background: rgba(255,255,255,0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
            <div class="flex-1">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style="background-color: #e1e0ff;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" fill="currentColor" style="color:#0d0097;width:20px;height:20px;"><path d="M880 836H144c-17.7 0-32 14.3-32 32v36c0 4.4 3.6 8 8 8h784c4.4 0 8-3.6 8-8v-36c0-17.7-14.3-32-32-32zm-622.3-84c2 0 4-.2 6-.5L431.9 722c2-.4 3.9-1.3 5.3-2.8l423.9-423.9a9.96 9.96 0 0 0 0-14.1L694.9 114.9c-1.9-1.9-4.4-2.9-7.1-2.9s-5.2 1-7.1 2.9L256.8 538.8c-1.5 1.5-2.4 3.3-2.8 5.3l-29.5 168.2a33.5 33.5 0 0 0 9.4 29.8c6.6 6.4 14.9 9.9 23.8 9.9z"/></svg>
              </div>
              <h3 class="font-semibold text-lg mb-2" style="color: #0b1c30; font-family: 'Inter', sans-serif;">AI 面试教练</h3>
              <p class="text-sm" style="color: #444651; font-family: 'Inter', sans-serif; line-height: 1.5;">
                专属 AI 教练根据你的简历和目标岗位，制定个性化训练计划，追踪成长轨迹
              </p>
            </div>
            <div class="w-full md:w-48 h-32 rounded-xl flex items-center justify-center"
                 style="background: linear-gradient(135deg, #e1e0ff, #dce1ff);">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 120" fill="currentColor" style="color:#0d0097;width:80%;height:60%;"><rect x="0" y="20" width="620" height="18" rx="9" fill="currentColor" opacity="0.25"/><rect x="0" y="52" width="480" height="18" rx="9" fill="currentColor" opacity="0.4"/><rect x="0" y="84" width="540" height="18" rx="9" fill="currentColor" opacity="0.2"/></svg>
            </div>
          </div>
        </div>
      </section>

      <!-- Trust Section -->
      <section class="max-w-7xl mx-auto px-6 py-12">
        <p class="text-center text-sm mb-8" style="color: #444651; font-family: 'Inter', sans-serif;">
          已帮助求职者成功入职
        </p>
        <LogoLoop>
          <img src="@/assets/companys/google.png"     alt="Google"    style="height:28px;opacity:0.5;flex-shrink:0;object-fit:contain;" />
          <img src="@/assets/companys/meta.png"       alt="Meta"      style="height:24px;opacity:0.5;flex-shrink:0;object-fit:contain;" />
          <img src="@/assets/companys/amazon.png"     alt="Amazon"    style="height:26px;opacity:0.5;flex-shrink:0;object-fit:contain;" />
          <img src="@/assets/companys/apple.png"      alt="Apple"     style="height:28px;opacity:0.5;flex-shrink:0;object-fit:contain;" />
          <img src="@/assets/companys/bytedance.png"  alt="ByteDance" style="height:22px;opacity:0.5;flex-shrink:0;object-fit:contain;" />
          <img src="@/assets/companys/Tencent_EN.png" alt="Tencent"   style="height:24px;opacity:0.5;flex-shrink:0;object-fit:contain;" />
        </LogoLoop>
      </section>
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
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="color:#444651;width:24px;height:24px;"><path d="M16.59 8.59 12 13.17 7.41 8.59 6 10l6 6 6-6z"></path></svg>
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
              准备好在面试中脱颖而出了吗？
            </h2>
            <p class="mb-8 text-lg" style="color: #90a8ff; font-family: 'Inter', sans-serif; line-height: 1.6;">
              加入数千名成功候选人的行列，他们利用我们的 AI 在顶级科技公司获得了理想职位。
            </p>
            <RouterLink to="/interview/setup"
  class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl font-semibold text-base transition-all whitespace-nowrap"
  style="background-color: #006c49; color: #ffffff; text-decoration: none; font-family: 'Inter', sans-serif;">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M6 15c-.83 0-1.58.34-2.12.88C2.7 17.06 2 22 2 22s4.94-.7 6.12-1.88A2.996 2.996 0 0 0 6 15zm.71 3.71c-.28.28-2.17.76-2.17.76s.47-1.88.76-2.17c.17-.19.42-.3.7-.3a1.003 1.003 0 0 1 .71 1.71zm10.71-5.06c6.36-6.36 4.24-11.31 4.24-11.31S16.71.22 10.35 6.58l-2.49-.5a2.03 2.03 0 0 0-1.81.55L2 10.69l5 2.14L11.17 17l2.14 5 4.05-4.05c.47-.47.68-1.15.55-1.81l-.49-2.49zM7.41 10.83l-1.91-.82 1.97-1.97 1.44.29c-.57.83-1.08 1.7-1.5 2.5zm6.58 7.67-.82-1.91c.8-.42 1.67-.93 2.49-1.5l.29 1.44-1.96 1.97zM16 12.24c-1.32 1.32-3.38 2.4-4.04 2.73l-2.93-2.93c.32-.65 1.4-2.71 2.73-4.04 4.68-4.68 8.23-3.99 8.23-3.99s.69 3.55-3.99 8.23zM15 11c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2z"></path></svg>
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
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="color: #00236f; width:20px; height:20px;" transform="matrix(-1, 0, 0, 1, 0, 0)"><path d="M13 8.57a1.43 1.43 0 1 0 0 2.86 1.43 1.43 0 0 0 0-2.86z"></path><path d="M13 3C9.25 3 6.2 5.94 6.02 9.64L4.1 12.2a.5.5 0 0 0 .4.8H6v3c0 1.1.9 2 2 2h1v3h7v-4.68A6.999 6.999 0 0 0 13 3zm3 7c0 .13-.01.26-.02.39l.83.66c.08.06.1.16.05.25l-.8 1.39c-.05.09-.16.12-.24.09l-.99-.4c-.21.16-.43.29-.67.39L14 13.83c-.01.1-.1.17-.2.17h-1.6c-.1 0-.18-.07-.2-.17l-.15-1.06c-.25-.1-.47-.23-.68-.39l-.99.4c-.09.03-.2 0-.25-.09l-.8-1.39a.19.19 0 0 1 .05-.25l.84-.66c-.01-.13-.02-.26-.02-.39s.02-.27.04-.39l-.85-.66c-.08-.06-.1-.16-.05-.26l.8-1.38c.05-.09.15-.12.24-.09l1 .4c.2-.15.43-.29.67-.39L12 6.17c.02-.1.1-.17.2-.17h1.6c.1 0 .18.07.2.17l.15 1.06c.24.1.46.23.67.39l1-.4c.09-.03.2 0 .24.09l.8 1.38a.2.2 0 0 1-.05.26l-.85.66c.03.12.04.25.04.39z"></path></svg>
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
          © 2026 InterviewAI. 保留所有权利。
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
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import LogoLoop from '../components/LogoLoop.vue'

const barData = [
  { h: 92, color: '#006c49' },
  { h: 85, color: '#006c49' },
  { h: 78, color: '#4edea3' },
  { h: 88, color: '#006c49' },
  { h: 82, color: '#4edea3' },
]

const questionTags = ['系统设计', '算法', 'STAR', '行为面试', 'LLD']


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
