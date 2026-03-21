<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import {
  API_BASE_URL,
  clearAuthSession,
  loadAuthSession,
  saveAuthSession,
  type TokenResponse,
} from '../utils/auth'

type AuthMode = 'login' | 'register'

const USERNAME_PATTERN = /^[A-Za-z0-9]+$/

const router = useRouter()

const navItems = ['首页', '模拟面试', '简历诊断']

const heroMetrics = [
  { label: '高频模拟场景', value: '1000+' },
  { label: '在线面试官', value: '7 x 24' },
  { label: '专项训练主题', value: '400+' },
]

const interviewModes = [
  {
    tag: '核心功能',
    title: '全流程模拟面试',
    description:
      '从开场介绍到项目追问，再到压力提问与总结反馈，完整还原一次真实面试的推进方式。',
    points: ['围绕岗位生成问题', '模拟连续追问场景', '输出结构化复盘结果'],
    cta: '开始模拟',
  },
  {
    tag: '专项训练',
    title: '聚焦短板强化练习',
    description:
      '项目表达、八股基础、场景问题、HR 沟通，都可以拆开单练，集中提升最拖后腿的部分。',
    points: ['按主题连续练习', '逐题给出建议', '支持反复打磨同一能力'],
    cta: '进入专项训练',
  },
  {
    tag: '简历能力',
    title: '基于简历预测提问',
    description:
      '根据简历经历识别高概率问题，补充答题框架、追问路径和需要提前准备的表达重点。',
    points: ['识别重点追问项', '提供回答结构', '补充延伸问题'],
    cta: '上传简历',
  },
]

const reportPoints = [
  '表达结构是否清楚',
  '项目细节是否经得起追问',
  '关键亮点是否被准确表达',
  '回答深度是否匹配目标岗位',
]

const advantages = [
  {
    title: '更接近真实面试节奏',
    description: '把紧张、卡顿和思路断层留在练习里，正式面试时更容易进入状态。',
  },
  {
    title: '反馈不止对错判断',
    description: '除了答案内容，还会关注表达方式、逻辑组织、信息密度和亮点呈现。',
  },
  {
    title: '任何时间都能开练',
    description: '不用约人，不用等排期，碎片时间也能完成一轮高质量练习。',
  },
  {
    title: '题目会随目标变化',
    description: '岗位方向、工作年限和简历背景不同，训练内容也会相应调整。',
  },
]

const testimonials = [
  {
    name: 'Hikari',
    target: '目标公司：字节 · 后端开发',
    quote: '连续练了几次项目追问后，正式面试时表达明显更稳，也更知道该先讲什么。',
  },
  {
    name: 'Simple',
    target: '目标公司：阿里 · 前端工程师',
    quote: '模拟里的追问节奏和真实场景很像，提前适应以后，现场不容易被打乱。',
  },
  {
    name: 'Jerry',
    target: '目标公司：小米 · Java 开发',
    quote: '复盘结果拆得很细，知道自己该先补逻辑还是补内容，训练效率高很多。',
  },
  {
    name: 'Rain',
    target: '目标公司：美团 · 算法工程师',
    quote: '比单纯刷题更有效，因为每次练完都知道问题出在哪，下一轮能马上修正。',
  },
]

const faqs = [
  {
    question: '和真人模拟相比，这种训练方式最大的价值是什么？',
    answer:
      '最大的价值是高频、低成本和可重复。你可以把它当作正式面试前的常规训练，用来不断暴露问题、快速修正。',
  },
  {
    question: '适合哪些求职阶段的人使用？',
    answer:
      '无论是应届求职、准备跳槽，还是计划转岗，只要你正在为面试做准备，都可以从这里开始练习。',
  },
  {
    question: '第一次使用前需要准备什么？',
    answer:
      '准备一个明确的目标岗位就可以开始。如果同时上传简历，系统给出的提问会更贴近你的真实背景。',
  },
  {
    question: '练习之后能得到什么反馈？',
    answer:
      '每次练习后都会生成复盘结果，帮助你判断回答是否清晰、内容是否扎实，以及下一步该重点补哪一部分。',
  },
]

const footerLinks = [
  {
    title: '产品',
    items: ['模拟面试', '专项训练', '简历诊断', '复盘报告'],
  },
  {
    title: '资源',
    items: ['岗位题单', '准备路线', '经验参考', '求职指南'],
  },
  {
    title: '支持',
    items: ['服务协议', '隐私说明', '商务合作', '联系我们'],
  },
]

const authMode = ref<AuthMode>('login')
const authDialogOpen = ref(false)
const authLoading = ref(false)
const authError = ref('')
const authSuccess = ref('')
const activeUser = ref<TokenResponse | null>(null)
const userMenuOpen = ref(false)

const authForm = ref({
  username: '',
  password: '',
})

const authTitle = computed(() => (authMode.value === 'login' ? '登录账号' : '创建账号'))
const authDescription = computed(() =>
  authMode.value === 'login'
    ? '登录后即可开始调用后端认证接口，并保存登录状态。'
    : '先创建一个账号，再返回登录或直接完成注册登录。',
)
const authSubmitLabel = computed(() => (authMode.value === 'login' ? '登录' : '注册'))
const authToggleLabel = computed(() =>
  authMode.value === 'login' ? '没有账号？立即注册' : '已有账号？去登录',
)
const heroPrimaryLabel = computed(() => (activeUser.value ? '进入训练' : '开始模拟'))
const userInitial = computed(() => activeUser.value?.username.slice(0, 1).toUpperCase() ?? 'U')

function handleDocumentClick(event: MouseEvent) {
  const target = event.target
  if (!(target instanceof HTMLElement)) return
  if (!target.closest('.user-menu')) {
    userMenuOpen.value = false
  }
}

function handlePrimaryAction() {
  if (!activeUser.value) {
    openAuthDialog('register')
    return
  }

  router.push('/interview')
}

function handleNavClick(item: string) {
  if (item === '妯℃嫙闈㈣瘯') {
    router.push('/interview')
    return
  }

  if (item === '棣栭〉') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }

  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })
}

function openAuthDialog(mode: AuthMode) {
  authMode.value = mode
  authDialogOpen.value = true
  authError.value = ''
  authSuccess.value = ''
}

function closeAuthDialog() {
  authDialogOpen.value = false
  authError.value = ''
  authSuccess.value = ''
}

function toggleAuthMode() {
  authMode.value = authMode.value === 'login' ? 'register' : 'login'
  authError.value = ''
  authSuccess.value = ''
}

function syncSession() {
  activeUser.value = loadAuthSession()
}

function logout() {
  userMenuOpen.value = false
  activeUser.value = null
  clearAuthSession()
}

function toggleUserMenu() {
  userMenuOpen.value = !userMenuOpen.value
}

function goToProfile() {
  userMenuOpen.value = false
  router.push('/profile')
}

async function submitAuthForm() {
  authError.value = ''
  authSuccess.value = ''

  const username = authForm.value.username.trim()
  const password = authForm.value.password.trim()

  if (username.length < 3 || password.length < 3) {
    authError.value = '用户名和密码至少需要 3 个字符。'
    return
  }

  if (!USERNAME_PATTERN.test(username)) {
    authError.value = '用户名只能包含英文和数字。'
    return
  }

  authLoading.value = true

  try {
    const endpoint = authMode.value === 'login' ? '/auth/login' : '/auth/register'
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        password,
      }),
    })

    const data = (await response.json().catch(() => null)) as
      | TokenResponse
      | { detail?: string; message?: string }
      | null

    if (!response.ok) {
      const errorData = data as { detail?: string; message?: string } | null
      authError.value =
        errorData?.detail ??
        errorData?.message ??
        (authMode.value === 'login' ? '登录失败，请稍后重试。' : '注册失败，请稍后重试。')
      return
    }

    const session = data as TokenResponse
    saveAuthSession(session)
    syncSession()
    authSuccess.value = authMode.value === 'login' ? '登录成功。' : '注册成功，已为你保存登录状态。'
    authForm.value.password = ''

    window.setTimeout(() => {
      closeAuthDialog()
    }, 500)
  } catch (error) {
    authError.value =
      error instanceof Error ? error.message : '请求后端接口失败，请确认 8000 端口服务已启动。'
  } finally {
    authLoading.value = false
  }
}

onMounted(() => {
  syncSession()
  document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>

<template>
  <main class="landing-page">
    <header class="topbar-wrap">
      <div class="topbar">
        <div class="brand">
          <div class="brand-mark">M</div>
          <div>
            <p class="brand-name">面试起跑线</p>
            <p class="brand-subtitle">AI Interview Training</p>
          </div>
        </div>

        <nav class="nav">
          <button v-for="item in navItems" :key="item" class="nav-link" type="button" @click="handleNavClick(item)">
            {{ item }}
          </button>
        </nav>

        <div class="topbar-actions">
          <template v-if="activeUser">
            <div class="user-menu">
              <button class="avatar-button" type="button" @click.stop="toggleUserMenu">
                <span class="avatar-circle">{{ userInitial }}</span>
                <span class="avatar-name">{{ activeUser.username }}</span>
                <span class="avatar-caret">&#9662;</span>
              </button>

              <div v-if="userMenuOpen" class="user-dropdown">
                <button class="dropdown-item" type="button" @click="goToProfile">个人中心</button>
                <button class="dropdown-item dropdown-item-danger" type="button" @click="logout">退出登录</button>
              </div>
            </div>
          </template>
          <template v-else>
            <button class="ghost-link ghost-button" type="button" @click="openAuthDialog('login')">
              登录
            </button>
            <button class="primary-link" type="button" @click="openAuthDialog('register')">
              立即注册
            </button>
          </template>
        </div>
      </div>
    </header>

    <section class="hero-shell">
      <section class="hero-grid">
        <div class="hero-copy">
          <span class="eyebrow">反复练习，比临场发挥更可靠</span>
          <h1>在正式面试前，先把高压问题练熟</h1>
          <p class="hero-text">
            从岗位选择、完整模拟，到专项突破和简历诊断，把准备过程拆成可执行的训练步骤。
            每练一次，都能更清楚自己该怎么答、哪里还不够稳。
          </p>

          <div class="hero-actions">
            <button class="button button-primary" type="button" @click="handlePrimaryAction">
              {{ heroPrimaryLabel }}
            </button>
            <a class="button button-secondary" href="#features">了解功能</a>
          </div>

          <div class="metric-row">
            <div v-for="item in heroMetrics" :key="item.label" class="metric-pill">
              <strong>{{ item.value }}</strong>
              <span>{{ item.label }}</span>
            </div>
          </div>
        </div>

        <div class="hero-panel">
          <div class="panel-glow"></div>
          <div class="interview-card">
            <div class="interview-head">
              <div>
                <p class="panel-label">沉浸式模拟面试</p>
                <h2>Java 后端开发</h2>
              </div>
              <span class="status-dot">LIVE</span>
            </div>

            <div class="selector-grid">
              <label>
                <span>目标岗位</span>
                <div class="fake-select">Java 后端开发</div>
              </label>
              <label>
                <span>工作年限</span>
                <div class="fake-select">3-5 年</div>
              </label>
            </div>

            <div class="interview-stage">
              <div class="stage-card">
                <div class="stage-avatar">AI</div>
                <div>
                  <p class="stage-title">AI 面试官</p>
                  <p class="stage-text">请先用 90 秒介绍最近一个最能体现你价值的项目，我会继续追问细节。</p>
                </div>
              </div>

              <div class="stage-card user">
                <div class="stage-avatar user-avatar">我</div>
                <div>
                  <p class="stage-title">候选人</p>
                  <p class="stage-text">我会从业务背景、技术难点、解决方案和最终结果四部分展开。</p>
                </div>
              </div>
            </div>

            <div class="panel-footer">
              <div class="panel-signal">
                <span class="signal-bar active"></span>
                <span class="signal-bar active"></span>
                <span class="signal-bar"></span>
                <span>当前阶段：项目细节追问</span>
              </div>
              <button class="panel-button" type="button" @click="handlePrimaryAction">
                {{ activeUser ? '进入训练' : '开始面试' }}
              </button>
            </div>
          </div>
        </div>
      </section>
    </section>

    <section id="features" class="content-section">
      <div class="section-heading">
        <span>核心功能</span>
        <h2>把面试准备拆成可重复执行的训练流程</h2>
        <p>先做完整模拟，再针对弱项集中提升，最后围绕简历做定向准备，整个节奏更清晰。</p>
      </div>

      <div class="feature-grid">
        <article v-for="mode in interviewModes" :key="mode.title" class="feature-card">
          <p class="feature-tag">{{ mode.tag }}</p>
          <h3>{{ mode.title }}</h3>
          <p class="feature-description">{{ mode.description }}</p>
          <ul>
            <li v-for="point in mode.points" :key="point">{{ point }}</li>
          </ul>
          <a href="#">{{ mode.cta }}</a>
        </article>
      </div>
    </section>

    <section class="product-showcase">
      <div class="showcase-copy">
        <span>反馈结果</span>
        <h2>练完之后，不只知道答得怎么样，还知道下一步该练什么</h2>
        <p>
          每次训练结束后，系统会从表达方式、回答深度、项目细节和岗位匹配度几个维度给出结果，
          帮你快速判断短板所在，并继续调整下一轮训练重点。
        </p>
        <ul class="report-list">
          <li v-for="item in reportPoints" :key="item">{{ item }}</li>
        </ul>
      </div>

      <div class="showcase-board">
        <div class="board-window">
          <div class="window-top">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <div class="window-content">
            <div class="report-card score">
              <p>综合表现</p>
              <strong>86</strong>
              <span>超过 79% 同岗位练习记录</span>
            </div>
            <div class="report-card">
              <p>表达结构</p>
              <div class="progress"><i style="width: 82%"></i></div>
            </div>
            <div class="report-card">
              <p>项目追问</p>
              <div class="progress"><i style="width: 76%"></i></div>
            </div>
            <div class="report-card">
              <p>岗位匹配度</p>
              <div class="progress"><i style="width: 88%"></i></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="stats-strip">
      <div v-for="item in heroMetrics" :key="item.label" class="stat-card">
        <strong>{{ item.value }}</strong>
        <span>{{ item.label }}</span>
      </div>
      <div class="stat-card">
        <strong>120%</strong>
        <span>面试备战效率</span>
      </div>
    </section>

    <section class="content-section why-section">
      <div class="section-heading">
        <span>为什么选择</span>
        <h2>更适合面试前高频练习的准备方式</h2>
      </div>

      <div class="advantage-grid">
        <article v-for="item in advantages" :key="item.title" class="advantage-card">
          <div class="advantage-index">{{ item.title.slice(0, 2) }}</div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
        </article>
      </div>
    </section>

    <section class="content-section testimonial-section">
      <div class="section-heading">
        <span>用户反馈</span>
        <h2>来自真实训练者的使用感受</h2>
      </div>

      <div class="testimonial-grid">
        <article v-for="item in testimonials" :key="item.name" class="testimonial-card">
          <div class="testimonial-avatar">{{ item.name.slice(0, 1) }}</div>
          <h3>{{ item.name }}</h3>
          <p class="testimonial-target">{{ item.target }}</p>
          <p class="testimonial-quote">“{{ item.quote }}”</p>
        </article>
      </div>
    </section>

    <section class="content-section faq-section">
      <div class="section-heading">
        <span>常见问题</span>
        <h2>开始训练前，你可能最关心的几个问题</h2>
      </div>

      <div class="faq-list">
        <article v-for="item in faqs" :key="item.question" class="faq-item">
          <h3>{{ item.question }}</h3>
          <p>{{ item.answer }}</p>
        </article>
      </div>
    </section>

    <section class="cta-section">
      <p class="cta-label">练得越充分，正式面试越从容</p>
      <h2>现在开始，把下一次面试前的不确定感提前消化掉</h2>
      <button class="button button-primary" type="button" @click="handlePrimaryAction">
        {{ activeUser ? '继续训练' : '立即开始' }}
      </button>
    </section>

    <footer class="site-footer">
      <div class="footer-brand">
        <div class="brand-mark footer-mark">M</div>
        <div>
          <p class="brand-name">面试起跑线</p>
          <p class="brand-subtitle">为每一次正式面试提前做好准备</p>
        </div>
      </div>

      <div class="footer-links">
        <div v-for="group in footerLinks" :key="group.title" class="footer-column">
          <h3>{{ group.title }}</h3>
          <a v-for="item in group.items" :key="item" href="#">{{ item }}</a>
        </div>
      </div>
    </footer>

    <div v-if="authDialogOpen" class="auth-overlay">
      <section class="auth-dialog">
        <button class="auth-close" type="button" @click="closeAuthDialog">×</button>
        <p class="auth-kicker">{{ authMode === 'login' ? '账号登录' : '账号注册' }}</p>
        <h2>{{ authTitle }}</h2>
        <p class="auth-description">{{ authDescription }}</p>

        <form class="auth-form" @submit.prevent="submitAuthForm">
          <label class="auth-field">
            <span>用户名</span>
            <input
              v-model.trim="authForm.username"
              type="text"
              minlength="3"
              maxlength="32"
              pattern="[A-Za-z0-9]+"
              inputmode="text"
              placeholder="请输入英文或数字用户名"
            />
          </label>

          <label class="auth-field">
            <span>密码</span>
            <input
              v-model.trim="authForm.password"
              type="password"
              minlength="3"
              maxlength="128"
              placeholder="请输入密码"
            />
          </label>

          <p v-if="authError" class="auth-message auth-message-error">{{ authError }}</p>
          <p v-if="authSuccess" class="auth-message auth-message-success">{{ authSuccess }}</p>

          <button class="auth-submit" type="submit" :disabled="authLoading">
            {{ authLoading ? '提交中...' : authSubmitLabel }}
          </button>
        </form>

        <button class="auth-switch" type="button" @click="toggleAuthMode">
          {{ authToggleLabel }}
        </button>
      </section>
    </div>
  </main>
</template>
