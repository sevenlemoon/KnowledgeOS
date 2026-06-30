import { createRouter, createWebHistory } from 'vue-router'

import MainLayout from '../layout/MainLayout.vue'

const routes = [
  {
    path: '/login',
    component: () => import('../views/LoginView.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/register',
    component: () => import('../views/RegisterView.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/',
    redirect: '/app/dashboard',
  },
  {
    path: '/app',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: 'dashboard', component: () => import('../views/DashboardView.vue') },
      { path: 'knowledge', component: () => import('../views/KnowledgeListView.vue') },
      { path: 'publish', component: () => import('../views/PublishView.vue') },
      { path: 'ranking', component: () => import('../views/RankingView.vue') },
      { path: 'profile', component: () => import('../views/ProfileView.vue') },
      {
        path: 'admin',
        component: () => import('../views/AdminAuditView.vue'),
        meta: { requiresAdmin: true },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    component: () => import('../views/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (to.meta.requiresAuth && !token) {
    return '/login'
  }
  if (to.meta.guestOnly && token) {
    return '/app/dashboard'
  }
  if (to.meta.requiresAdmin && user?.role !== 'admin') {
    return '/app/dashboard'
  }
  return true
})

export default router
