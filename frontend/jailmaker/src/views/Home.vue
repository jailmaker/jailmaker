<template>
  <div class="schedule-generator">
    <div class="schedule-grid">
      <div class="grid-header">
        <div class="time-slot">HORÁRIO</div>
        <div v-for="dia in dias" :key="dia" class="day-header">{{ dia }}</div>
      </div>

      <div v-for="horario in horarios" :key="horario" class="schedule-row">
        <div class="time-slot">{{ horario }}</div>
        <div v-for="dia in dias" :key="dia" class="day-slot">
          <div 
            v-for="disciplina in getDisciplinasHorario(dia, horario)"
            :key="disciplina.nome"
            class="class-block"
            :class="{ 'highlight': disciplina.nome }"
          >
            <div class="class-content">
              {{ disciplina.nome }}
              <span class="class-details">{{ disciplina.professor }} - {{ disciplina.turma }}</span>
            </div>
            <button 
              v-if="disciplina.nome"
              @click="trocarDisciplina(disciplina)"
              class="reroll-button"
              title="Trocar disciplina"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.3"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="controls">
      <button @click="gerarGradeIdeal" :disabled="isLoading">
        Gerar Grade Ideal
      </button>
      <button @click="gerarGradeAleatoria" :disabled="isLoading">
        Gerar Grade Aleatória
      </button>
    </div>

    <div v-if="erro" class="error-message">
      {{ erro }}
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'Home',
  data() {
    return {
      dias: ['SEGUNDA', 'TERÇA', 'QUARTA', 'QUINTA', 'SEXTA'],
      horarios: [
        '08h00 - 10h00', 
        '10h00 - 12h00', 
        '13h30 - 15h30', 
        '15h30 - 17h30', 
        '19h00 - 21h00', 
        '21h00 - 23h00'
      ],
      gradeGerada: [],
      matriz_horaria: JSON.parse(localStorage.getItem('matrizHoraria') || '[]'),
      historico_academico: JSON.parse(localStorage.getItem('historicoAcademico') || '[]'),
      isLoading: false,
      erro: null
    }
  },
  async created() {
    this.matriz_horaria = JSON.parse(localStorage.getItem('matrizHoraria') || '[]')
    this.historico_academico = JSON.parse(localStorage.getItem('historicoAcademico') || '[]')
  
    if (this.matriz_horaria.length === 0) {
      try {
        const response = await api.get('/api/matriz-horaria')
        this.matriz_horaria = response.data
        localStorage.setItem('matrizHoraria', JSON.stringify(this.matriz_horaria))
      } catch (erro) {
        this.erro = 'Erro ao carregar a matriz horária atual :('
        return
      }
    }

    if (this.historico_academico.length > 0) {
      this.gerarGradeIdeal()
    } else {
      this.gerarGradeAleatoria()
    }
  },
  methods: {
    async gerarGradeIdeal() {
      this.isLoading = true
      this.erro = null
      
      try {
        const response = await api.post('/api/grade-ideal', {
          matriz_horaria: this.matriz_horaria,
          historico_academico: this.historico_academico
        })

        this.gradeGerada = response.data.flatMap(disciplina => {
          return disciplina.dias.map((dia, index) => ({
            nome: disciplina.nome,
            professor: disciplina.professor,
            turma: disciplina.turma,
            dia: dia,
            horario: disciplina.horarios[index]
          }))
        })
      } catch (err) {
        this.erro = 'Erro ao gerar grade ideal: ' + err.message
      } finally {
        this.isLoading = false
      }
    },
    gerarGradeAleatoria() {
      const disciplinasDisponiveis = this.matriz_horaria.filter(
        disciplina => !this.historico_academico.some(
          d => d.nome.toUpperCase() === disciplina.nome.toUpperCase()
        )
      )

      const gradeGerada = []
      const horariosOcupados = new Set()

      const numDisciplinas = Math.floor(Math.random() * (10 - 6 + 1) + 6)

      while (horariosOcupados.size < numDisciplinas) {
        const indiceAleatorio = Math.floor(Math.random() * disciplinasDisponiveis.length)
        const disciplina = disciplinasDisponiveis[indiceAleatorio]
        disciplina.horarios.forEach((horario, index) => {
          const dia = disciplina.dias[index]
          const key = `${dia}-${horario}`
          if (!horariosOcupados.has(key)) {
            gradeGerada.push({
              nome: disciplina.nome,
              professor: disciplina.professor,
              turma: disciplina.turma,
              dia: dia,
              horario: horario
            })
            horariosOcupados.add(key)
          }
        })
      }

      this.gradeGerada = gradeGerada
    },
    getDisciplinasHorario(dia, horario) {
      const disciplinasHorario = this.gradeGerada.filter(
        d => d.dia === dia && d.horario === horario
      )

      return disciplinasHorario.length > 0 
        ? disciplinasHorario 
        : [{ nome: '', professor: '', turma: '' }]
    },
    trocarDisciplina(disciplina) {
      this.gradeGerada = this.gradeGerada.filter(
        d => d.nome !== disciplina.nome
      )

      const disciplinasDisponiveis = this.matriz_horaria.filter(disciplinaDisponivel => {
        return (
          !this.historico_academico.some(d => d.nome.toUpperCase() === disciplinaDisponivel.nome.toUpperCase()) &&
          !this.gradeGerada.some(d => d.nome === disciplinaDisponivel.nome) &&
          disciplinaDisponivel.nome !== disciplina.nome
        )
      })

      if (disciplinasDisponiveis.length > 0) {
        const indiceAleatorio = Math.floor(Math.random() * disciplinasDisponiveis.length)
        const novaDisciplina = disciplinasDisponiveis[indiceAleatorio]

        novaDisciplina.horarios.forEach((horario, index) => {
          this.gradeGerada.push({
            nome: novaDisciplina.nome,
            professor: novaDisciplina.professor,
            turma: novaDisciplina.turma,
            dia: novaDisciplina.dias[index],
            horario: horario
          })
        })
      }
    }
  }
}
</script>

<style scoped>
.schedule-generator {
  max-width: 1300px;
  margin: 0 auto;
  padding: 20px;
  color: #fff;
}

.title {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 30px;
}

.warning-message, .error-message {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  margin-bottom: 20px;
}

.error-message {
  background-color: rgba(255, 0, 0, 0.1);
  color: #ff6b6b;
}

.schedule-grid {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.grid-header, .schedule-row {
  display: grid;
  grid-template-columns: 1fr repeat(5, 1fr);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.grid-header {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: bold;
}

.time-slot, .day-header, .day-slot {
  padding: 10px;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  box-sizing: border-box;
}

.day-slot {
  min-height: 110px;
  height: 110px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
  overflow: hidden;
}

.class-block {
  width: 100%;
  height: 100%;
  padding: 5px;
  border-radius: 4px;
  font-size: 12px;
  text-align: center;
  box-sizing: border-box;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
}

.class-block.highlight {
  background-color: rgba(255, 255, 255, 0.2);
}

.class-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.class-details {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 2px;
}

.reroll-button {
  position: absolute;
  bottom: 5px;
  right: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px;
  color: rgba(255, 255, 255, 0.7);
  opacity: 0;
  transition: opacity 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.class-block:hover .reroll-button {
  opacity: 1;
}

.reroll-button:hover {
  color: white;
}

.controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin: 20px auto;
  padding: 10px;
  background-color: #333;
  border: 1px solid #444;
  border-radius: 8px;
  width: fit-content;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.controls button {
  background-color: #444;
  color: #ddd;
  border: 1px solid #555;
  font-size: 16px;
  padding: 5px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s, border 0.2s;
}

.controls button:not(:disabled):hover {
  background-color: #555;
  border-color: #666;
  color: #fff;
}

.controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
