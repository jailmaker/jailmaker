// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import MatrizSemestre from '../components/MatrizSemestre.vue'
import Home from '../views/Home.vue'
import LeitorHistoricoAcademico from '../components/LeitorHistoricoAcademico.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/matriz',
    name: 'Matriz',
    component: MatrizSemestre
  },
  {
    path: '/historico',
    name: 'History',
    component: LeitorHistoricoAcademico
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
