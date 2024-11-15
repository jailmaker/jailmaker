import { createRouter, createWebHistory } from 'vue-router'
import MatrizSemestre from '../views/MatrizSemestre.vue'
import Home from '../views/Home.vue'
import LeitorHistoricoAcademico from '../views/LeitorHistoricoAcademico.vue'

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
