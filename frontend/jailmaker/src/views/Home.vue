<template>
  <div class="home">
    <div class="content">
      <div class="container">
        <div class="grade-section">
          <h1 class="title">JailMaker</h1>
          <div class="schedule-grid">
            <!-- A grade será gerada dinamicamente pelo método gerarGradeVazia() -->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  mounted() {
    this.gerarGradeVazia();
  },
  methods: {
    gerarGradeVazia() {
      const scheduleGrid = this.$el.querySelector(".schedule-grid");
      scheduleGrid.innerHTML = ""; 

      const horarios = [
        "08:00 - 10:00", 
        "10:00 - 12:00", 
        "13:30 - 15:30", 
        "15:30 - 17:30", 
        "19:00 - 21:00", 
        "21:00 - 23:00"
      ];
      const dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"];

      // Célula vazia no canto superior esquerdo
      scheduleGrid.insertAdjacentHTML("beforeend", `<div class="header-cell"></div>`);
      
      // Cabeçalho dos dias
      dias.forEach(dia => {
        scheduleGrid.insertAdjacentHTML("beforeend", `
          <div class="header-cell day-header">
            <strong>${dia}</strong>
          </div>
        `);
      });

      // Grade de horários
      horarios.forEach(horario => {
        // Célula de horário
        scheduleGrid.insertAdjacentHTML("beforeend", `
          <div class="header-cell time-header">
            <strong>${horario}</strong>
          </div>
        `);
        
        // Células editáveis para cada dia
        dias.forEach(() => {
          scheduleGrid.insertAdjacentHTML("beforeend", `
            <div class="schedule-cell" contenteditable="true"></div>
          `);
        });
      });
    }
  }
};
</script>

<style scoped>
.home {
  min-height: calc(100vh - 61px);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background-color: #1a1a1a;
}

.container {
  width: 90%;
  max-width: 1200px;
  background: #1e1e1e;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  padding: 20px;
  box-sizing: border-box;
}

.title {
  text-align: center;
  width: 100%;
  font-size: 2rem;
  color: #0d8044;
  margin-bottom: 20px;
}

.schedule-grid {
  display: grid;
  grid-template-columns: auto repeat(5, 1fr);
  grid-template-rows: auto repeat(6, 1fr);
  gap: 8px;
  width: 100%;
}

.header-cell {
  background: #2c2c2c;
  border: 1px solid #333;
  border-radius: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #b0b0b0;
  font-size: 14px;
  text-align: center;
  padding: 10px;
}

.day-header {
  background-color: #0d8044;
  color: white;
  font-weight: bold;
}

.time-header {
  background-color: #333;
  color: #b0b0b0;
  white-space: nowrap;
}

.schedule-cell {
  background: #2c2c2c;
  border: 1px solid #333;
  border-radius: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #b0b0b0;
  font-size: 14px;
  text-align: center;
  transition: background-color 0.3s ease;
  cursor: text;
}

.schedule-cell:hover {
  background-color: #3c3c3c;
}

.schedule-cell:focus {
  outline: 2px solid #0d8044;
  background-color: #3a3a3a;
}
</style>
