import { createRouter, createWebHashHistory } from 'vue-router'
import MatrizHoraria from '../views/MatrizHoraria.vue'
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
    component: MatrizHoraria
  },
  {
    path: '/historico',
    name: 'History',
    component: LeitorHistoricoAcademico
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
