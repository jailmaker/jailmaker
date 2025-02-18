<template>
  <div class="matriz-horaria">
    <h1 class="titulo">Matriz do Semestre Atual</h1>
    <div class="container-disciplinas">
      <div v-for="disciplina in disciplinas" :key="disciplina.id" class="card-disciplina">
        <h2 class="titulo-disciplina">{{ disciplina.nome }}</h2>
        <p class="professor">Professor: {{ disciplina.professor }}</p>
        <p class="turma-badge">Turma: {{ disciplina.turma }}</p>

        <div class="secao-informacoes">
          <div class="secao-horario">
            <h3 class="titulo-secao">Horário</h3>
            <ul class="lista-horarios">
              <li v-for="(horario, index) in disciplina.horarios" :key="index">
                {{ disciplina.dias[index] }}: {{ horario }}
              </li>
            </ul>
          </div>

          <div class="secao-detalhes">
            <h3 class="titulo-secao">Detalhes</h3>
            <ul class="lista-detalhes">
              <li>Curso: {{ disciplina.curso }}</li>
              <li>Termo: {{ disciplina.termo }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'MatrizHoraria',
  data() {
    return {
      disciplinas: []
    }
  },
  async created() {
    const savedMatrizHoraria = localStorage.getItem('matrizHoraria')
    
    if (savedMatrizHoraria) {
      this.disciplinas = JSON.parse(savedMatrizHoraria)
    } else {
      try {
        const response = await api.get('/api/matriz-horaria')
        this.disciplinas = response.data
        localStorage.setItem('matrizHoraria', JSON.stringify(this.disciplinas))
      } catch (erro) {
        console.error('Erro ao carregar a matriz horária atual:', erro)
      }
    }
  }
}
</script>

<style scoped>
.matriz-horaria {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  color: #fff;
}

.titulo {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 30px;
}

.container-disciplinas {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-disciplina {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.titulo-disciplina {
  font-size: 20px;
  font-weight: bold;
  margin: 0 0 10px 0;
}

.professor {
  color: rgba(255, 255, 255, 0.8);
  margin: 5px 0;
}

.turma-badge {
  display: inline-block;
  background-color: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
  margin: 10px 0;
}

.secao-informacoes {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 15px;
}

.titulo-secao {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
  color: rgba(255, 255, 255, 0.9);
}

.lista-horarios, .lista-detalhes {
  list-style: none;
  padding: 0;
  margin: 0;
}

.lista-horarios li, .lista-detalhes li {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 5px;
  font-size: 14px;
}

@media (max-width: 600px) {
  .secao-informacoes {
    grid-template-columns: 1fr;
  }
}
</style>
