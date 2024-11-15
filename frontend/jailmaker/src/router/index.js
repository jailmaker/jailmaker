// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import ClassSchedule from '../components/ClassSchedule.vue'
import AcademicHistory from '../components/AcademicHistory.vue'
import Home from '../views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/matrix',
    name: 'Matrix',
    component: ClassSchedule
  },
  {
    path: '/history',
    name: 'History',
    component: AcademicHistory
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
