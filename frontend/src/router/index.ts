import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import InterviewMockView from '../views/InterviewMockView.vue'
import InterviewSetupView from '../views/InterviewSetupView.vue'
import LoginView from '../views/LoginView.vue'
import ProfileView from '../views/ProfileView.vue'
import ResultsView from '../views/ResultsView.vue'
import { loadAuthSession, loadInterviewSetup } from '../utils/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true },
    },
    {
      path: '/interview/setup',
      name: 'interview-setup',
      component: InterviewSetupView,
      meta: { requiresAuth: true },
    },
    {
      path: '/interview',
      name: 'interview',
      component: InterviewMockView,
      meta: { requiresAuth: true, requiresInterviewSetup: true },
    },
    {
      path: '/results',
      name: 'results',
      component: ResultsView,
    },
  ],
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !loadAuthSession()) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.requiresInterviewSetup && !loadInterviewSetup()) {
    return { name: 'interview-setup' }
  }

  return true
})

export default router
