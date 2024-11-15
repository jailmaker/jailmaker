<template>
  <div class="academic-history">
    <h1 class="title">Academic History Viewer</h1>
    
    <div class="upload-section" v-if="!studentInfo">
      <div 
        class="upload-area"
        @drag.prevent
        @dragstart.prevent
        @dragend.prevent
        @dragover.prevent
        @dragenter.prevent
        @dragleave.prevent
        @drop.prevent="handleDrop"
        :class="{ 'dragging': isDragging }"
        @click="$refs.fileInput.click()"
      >
        <input
          type="file"
          ref="fileInput"
          @change="handleFileSelect"
          accept=".pdf"
          class="hidden"
        >
        <div class="upload-content">
          <i class="upload-icon">📄</i>
          <p class="upload-text">Drop your academic history PDF here or click to browse</p>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>Processing academic history...</p>
    </div>

    <div v-if="studentInfo" class="content-container">
      <button class="upload-new" @click="resetUpload">Upload New Document</button>
      
      <div class="student-info-card">
        <h2 class="student-name">{{ studentInfo.nome }}</h2>
        <p class="student-course">{{ studentInfo.curso }}</p>
      </div>

      <div 
        v-for="(group, index) in groupedDisciplines" 
        :key="index" 
        class="semester-group"
      >
        <h2 class="semester-title">
          {{ group.ano_letivo }} - Semester {{ group.semestre }}
        </h2>
        
        <div class="records-grid">
          <div 
            v-for="discipline in group.disciplines" 
            :key="`${discipline.codigo}-${discipline.ano_letivo}-${discipline.semestre}`" 
            class="record-card"
          >
            <div class="record-header">
              <h3 class="discipline-name">{{ discipline.nome }}</h3>
              <span class="code-badge">{{ discipline.codigo }}</span>
            </div>
            
            <div class="record-details">
              <div class="details-column">
                <p><strong>Group:</strong> {{ discipline.grupo }}</p>
                <p><strong>Category:</strong> {{ discipline.categoria }}</p>
                <p><strong>Credits:</strong> {{ discipline.creditos }}</p>
                <p><strong>Hours:</strong> {{ discipline.carga_horaria }}</p>
              </div>
              
              <div class="details-column">
                <p><strong>Absences:</strong> {{ discipline.faltas }}</p>
                <p><strong>Attendance:</strong> {{ discipline.frequencia }}%</p>
                <p><strong>Grade:</strong> {{ discipline.conceito }}</p>
                <p class="status" :class="discipline.situacao.toLowerCase()">
                  {{ discipline.situacao }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'AcademicHistory',
  data() {
    return {
      studentInfo: null,
      disciplines: [],
      isLoading: false,
      isDragging: false
    }
  },
  computed: {
    groupedDisciplines() {
      const grouped = this.disciplines.reduce((acc, discipline) => {
        const key = `${discipline.ano_letivo}-${discipline.semestre}`
        if (!acc[key]) {
          acc[key] = {
            ano_letivo: discipline.ano_letivo,
            semestre: discipline.semestre,
            disciplines: []
          }
        }
        acc[key].disciplines.push(discipline)
        return acc
      }, {})

      return Object.values(grouped).sort((a, b) => {
        if (a.ano_letivo !== b.ano_letivo) {
          return b.ano_letivo - a.ano_letivo
        }
        return b.semestre - a.semestre
      })
    }
  },
  methods: {
    async uploadFile(file) {
      this.isLoading = true
      try {
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await api.post('/api/get_academic_history', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        this.studentInfo = response.data.informacoes_aluno
        this.disciplines = response.data.disciplinas
      } catch (error) {
        console.error('Error uploading academic history:', error)
      } finally {
        this.isLoading = false
      }
    },
    handleDrop(e) {
      this.isDragging = false
      const file = e.dataTransfer.files[0]
      if (file && file.type === 'application/pdf') {
        this.uploadFile(file)
      }
    },
    handleFileSelect(e) {
      const file = e.target.files[0]
      if (file) {
        this.uploadFile(file)
      }
    },
    resetUpload() {
      this.studentInfo = null
      this.disciplines = []
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    }
  }
}
</script>

<style scoped>
.academic-history {
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

.upload-section {
  margin: 40px auto;
  max-width: 600px;
}

.upload-area {
  border: 2px dashed rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-area:hover, .upload-area.dragging {
  border-color: rgba(255, 255, 255, 0.6);
  background-color: rgba(255, 255, 255, 0.1);
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.upload-text {
  color: rgba(255, 255, 255, 0.8);
}

.hidden {
  display: none;
}

.loading {
  text-align: center;
  padding: 40px;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  border-top: 4px solid #fff;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.content-container {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.student-info-card {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  text-align: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.student-name {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
}

.student-course {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
}

.semester-group {
  margin-bottom: 40px;
}

.semester-title {
  font-size: 20px;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.record-card {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.2s ease;
}

.record-card:hover {
  transform: translateY(-2px);
}

.record-header {
  margin-bottom: 15px;
}

.discipline-name {
  font-size: 18px;
  font-weight: bold;
  margin: 0 0 10px 0;
}

.code-badge {
  display: inline-block;
  background-color: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
}

.record-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.details-column p {
  margin: 8px 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.status {
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 4px;
  text-align: center;
}

.status.aprovado {
  background-color: rgba(46, 204, 113, 0.2);
  color: #2ecc71;
}

.status.reprovado {
  background-color: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
}

.upload-new {
  background-color: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 20px;
  transition: background-color 0.3s ease;
}

.upload-new:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

@media (max-width: 600px) {
  .record-details {
    grid-template-columns: 1fr;
  }
  
  .records-grid {
    grid-template-columns: 1fr;
  }
  
  .student-name {
    font-size: 20px;
  }
  
  .student-course {
    font-size: 14px;
  }
}
</style>
