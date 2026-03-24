import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import InterviewMockView from '../views/InterviewMockView.vue'
import InterviewSetupView from '../views/InterviewSetupView.vue'
import ProfileView from '../views/ProfileView.vue'
import { loadInterviewSetup } from '../utils/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
    },
    {
      path: '/interview/setup',
      name: 'interview-setup',
      component: InterviewSetupView,
    },
    {
      path: '/interview',
      name: 'interview',
      component: InterviewMockView,
      meta: { requiresInterviewSetup: true },
    },
  ],
})

router.beforeEach((to) => {
  if (to.meta.requiresInterviewSetup && !loadInterviewSetup()) {
    return { name: 'interview-setup' }
  }

  return true
})

export default router
