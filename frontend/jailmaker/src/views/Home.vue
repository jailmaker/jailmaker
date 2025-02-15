<template>
  <div class="schedule-generator">
    <div v-if="generatedSchedule.length === 0" class="warning-message">
      <p>Não foi possível gerar a sua grade, cheque suas informações e tente novamente :(</p>
    </div>

    <div v-else class="schedule-grid">
      <div class="grid-header">
        <div class="time-slot">HORÁRIO</div>
        <div v-for="day in days" :key="day" class="day-header">{{ day }}</div>
      </div>

      <div v-for="timeSlot in timeSlots" :key="timeSlot" class="schedule-row">
        <div class="time-slot">{{ timeSlot }}</div>
        <div v-for="day in days" :key="day" class="day-slot">
          <div 
            v-for="classe in getClassesForSlot(day, timeSlot)"
            :key="classe.subject"
            class="class-block"
            :class="{ 'highlight': classe.subject }"
          >
            <div class="class-content">
              {{ classe.subject }}
              <span class="class-details">{{ classe.teacher }} - {{ classe.class }}</span>
            </div>
            <button 
              v-if="classe.subject"
              @click="rerollCourse(classe)"
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
      <button @click="generateOptimalSchedule" :disabled="isLoading">
        Gerar Grade Ideal
      </button>
      <button @click="generateRandomSchedule" :disabled="isLoading">
        Gerar Grade Aleatória
      </button>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'Home',
  data() {
    return {
      days: ['SEGUNDA', 'TERÇA', 'QUARTA', 'QUINTA', 'SEXTA'],
      timeSlots: [
        '08h00 - 10h00', 
        '10h00 - 12h00', 
        '13h30 - 15h30', 
        '15h30 - 17h30', 
        '19h00 - 21h00', 
        '21h00 - 23h00'
      ],
      generatedSchedule: [],
      matriz: JSON.parse(localStorage.getItem('matriz') || '[]'),
      completedCourses: JSON.parse(localStorage.getItem('disciplinas') || '[]'),
      isLoading: false,
      error: null
    }
  },
  created() {
    this.generateRandomSchedule()
  },
  methods: {
    async generateOptimalSchedule() {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await api.post('/api/grade-ideal', {
          matriz_horaria: this.matriz, 
          historico_academico: this.completedCourses
        })

        this.generatedSchedule = response.data.flatMap(course => {
          return course.day.map((day, index) => ({
            subject: course.subject,
            teacher: course.teacher,
            class: course.class,
            day: day,
            timeSlot: course.schedule[index]
          }))
        })
      } catch (err) {
        this.error = 'Erro ao gerar grade ideal: ' + err.message
      } finally {
        this.isLoading = false
      }
    },
    generateRandomSchedule() {
      const availableCourses = this.matriz.filter(
        course => !this.completedCourses.some(
          c => c.nome.toUpperCase() === course.subject.toUpperCase()
        )
      )

      const schedule = []
      const occupiedSlots = new Set()

      const courseCount = Math.floor(Math.random() * (10 - 6 + 1) + 6)

      while (occupiedSlots.size < courseCount) {
        const randomIndex = Math.floor(Math.random() * availableCourses.length)
        const course = availableCourses[randomIndex]
        course.schedule.forEach((timeSlot, index) => {
          const day = course.day[index]
          const key = `${day}-${timeSlot}`
          if (!occupiedSlots.has(key)) {
            schedule.push({
              subject: course.subject,
              teacher: course.teacher,
              class: course.class,
              day: day,
              timeSlot: timeSlot
            })
            occupiedSlots.add(key)
          }
        })
      }

      this.generatedSchedule = schedule
    },
    getClassesForSlot(day, timeSlot) {
      const classesInSlot = this.generatedSchedule.filter(
        c => c.day === day && c.timeSlot === timeSlot
      )

      return classesInSlot.length > 0 
        ? classesInSlot 
        : [{ subject: '', teacher: '', class: '' }]
    },
    rerollCourse(course) {
      const oldScheduleEntries = this.generatedSchedule.filter(
        c => c.subject === course.subject
      )
      this.generatedSchedule = this.generatedSchedule.filter(
        c => c.subject !== course.subject
      )

      const availableCourses = this.matriz.filter(availableCourse => {
        const notCompleted = !this.completedCourses.some(
          completed => completed.nome.toUpperCase() === availableCourse.subject.toUpperCase()
        )

        const notInSchedule = !this.generatedSchedule.some(
          scheduled => scheduled.subject === availableCourse.subject
        )

        const hasCompatibleSlots = oldScheduleEntries.every(oldEntry => {
          return availableCourse.schedule.some((timeSlot, index) => 
            timeSlot === oldEntry.timeSlot && availableCourse.day[index] === oldEntry.day
          )
        })

        const isNotSameCourse = availableCourse.subject !== course.subject

        return notCompleted && notInSchedule && hasCompatibleSlots && isNotSameCourse
      })

      if (availableCourses.length > 0) {
        const randomIndex = Math.floor(Math.random() * availableCourses.length)
        const newCourse = availableCourses[randomIndex]

        oldScheduleEntries.forEach(oldEntry => {
          const slotIndex = newCourse.schedule.findIndex((timeSlot, index) => 
            timeSlot === oldEntry.timeSlot && newCourse.day[index] === oldEntry.day
          )

          if (slotIndex !== -1) {
            this.generatedSchedule.push({
              subject: newCourse.subject,
              teacher: newCourse.teacher,
              class: newCourse.class,
              day: oldEntry.day,
              timeSlot: oldEntry.timeSlot
            })
          }
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
