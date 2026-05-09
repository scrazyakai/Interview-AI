import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import InterviewMockView from '../views/InterviewMockView.vue'
import InterviewSetupView from '../views/InterviewSetupView.vue'
import ProfileView from '../views/ProfileView.vue'
import ResultsView from '../views/ResultsView.vue'
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
    {
      path: '/results',
      name: 'results',
      component: ResultsView,
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
