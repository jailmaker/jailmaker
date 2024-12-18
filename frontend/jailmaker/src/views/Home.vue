<template>
  <div class="schedule-generator">
    <div v-if="generatedSchedule.length === 0" class="warning-message">
      <p>Não foi possível gerar a sua grade, cheque suas informações e tente novamente :(</p>
    </div>

    <div v-else class="schedule-grid">
      <div class="grid-header">
        <div class="time-slot">Horário</div>
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
            {{ classe.subject }}
            <span class="class-details">{{ classe.teacher }} - {{ classe.class }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="controls">
      <button @click="generateSchedule">Gerar grade</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      days: ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta'],
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
      completedCourses: JSON.parse(localStorage.getItem('disciplinas') || '[]')
    }
  },
  created() {
    this.generateSchedule()
  },
  methods: {
    generateSchedule() {
      const availableCourses = this.matriz.filter(
        course => !this.completedCourses.some(
          c => c.nome.toUpperCase() === course.subject.toUpperCase()
        )
      )

      const schedule = []
      const occupiedSlots = new Set()

      const courseCount =  Math.floor(Math.random() * (10 - 6 + 1) + 6)

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

.warning-message {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
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
}

.class-block.highlight {
  background-color: rgba(255, 255, 255, 0.2);
}

.class-details {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 2px;
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

.controls label {
  color: #ddd;
  font-size: 16px;
}

.controls input {
  background-color: #222;
  border: 1px solid #555;
  color: #fff;
  font-size: 16px;
  padding: 5px 8px;
  border-radius: 4px;
  width: 60px;
  text-align: center;
  outline: none;
  transition: border 0.2s;
}

.controls input:focus {
  border-color: #888;
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

.controls button:hover {
  background-color: #555;
  border-color: #666;
  color: #fff;
}
</style>
