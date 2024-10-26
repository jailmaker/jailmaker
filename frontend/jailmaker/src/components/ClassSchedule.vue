<!-- ClassSchedule.vue -->
<template>
  <div class="class-schedule">
    <h1 class="title">jailmaker</h1>
    <div class="classes-container">
      <div v-for="classItem in classes" :key="classItem.id" class="class-card">
        <h2 class="subject-title">{{ classItem.subject }}</h2>
        <p class="teacher">Teacher: {{ classItem.teacher }}</p>
        <p class="class-badge">Class: {{ classItem.class }}</p>

        <div class="info-section">
          <div class="schedule-section">
            <h3 class="section-title">Schedule</h3>
            <ul class="schedule-list">
              <li v-for="(schedule, index) in classItem.schedule" :key="index">
                {{ classItem.day[index] }}: {{ schedule }}
              </li>
            </ul>
          </div>

          <div class="details-section">
            <h3 class="section-title">Details</h3>
            <ul class="details-list">
              <li>Course: {{ classItem.course }}</li>
              <li>Period: {{ classItem.period }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ClassSchedule',
  data() {
    return {
      classes: []
    }
  },
  async created() {
    try {
      const response = await fetch('https://jailmaker.onrender.com/api/get_available_classes')
      this.classes = await response.json()
    } catch (error) {
      console.error('Error fetching classes:', error)
    }
  }
}
</script>

<style scoped>
.class-schedule {
  max-width: 1200px;
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

.classes-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.class-card {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.subject-title {
  font-size: 20px;
  font-weight: bold;
  margin: 0 0 10px 0;
}

.teacher {
  color: rgba(255, 255, 255, 0.8);
  margin: 5px 0;
}

.class-badge {
  display: inline-block;
  background-color: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
  margin: 10px 0;
}

.info-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 15px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
  color: rgba(255, 255, 255, 0.9);
}

.schedule-list, .details-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.schedule-list li, .details-list li {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 5px;
  font-size: 14px;
}

@media (max-width: 600px) {
  .info-section {
    grid-template-columns: 1fr;
  }
}
</style>
