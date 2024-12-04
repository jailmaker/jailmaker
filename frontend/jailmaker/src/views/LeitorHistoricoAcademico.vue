<template>
  <div class="academic-history">
    <h1 class="title">Leitor de Histórico Acadêmico</h1>
    
    <div class="upload-section" v-if="!alunoInfo">
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
        @click="$refs.arquivo.click()"
      >
        <input
          type="file"
          ref="arquivo"
          @change="handleFileSelect"
          accept=".pdf"
          class="hidden"
        >
        <div class="upload-content">
          <i class="upload-icon">📄</i>
          <p class="upload-text">Arraste o seu histórico acadêmico em PDF ou clique aqui para selecioná-lo</p>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>Processando histórico acadêmico...</p>
    </div>

    <div v-if="alunoInfo" class="content-container">
      <button class="upload-new" @click="resetUpload">Fazer upload de outro histórico</button>
      
      <div class="student-info-card">
        <h2 class="student-name">{{ alunoInfo.nome }}</h2>
        <p class="student-course">{{ alunoInfo.curso }}</p>
      </div>

      <div 
        v-for="(group, index) in disciplinasAgrupadas" 
        :key="index" 
        class="semester-group"
      >
        <h2 class="semester-title">
          {{ group.ano_letivo }} - Semestre {{ group.semestre }}
        </h2>
        
        <div class="records-grid">
          <div 
            v-for="discipline in group.disciplinas" 
            :key="`${discipline.codigo}-${discipline.ano_letivo}-${discipline.semestre}`" 
            class="record-card"
          >
            <div class="record-header">
              <h3 class="discipline-name">{{ discipline.nome }}</h3>
              <span class="code-badge">{{ discipline.codigo }}</span>
            </div>
            
            <div class="record-details">
              <div class="details-column">
                <p><strong>Grupo:</strong> {{ discipline.grupo }}</p>
                <p><strong>Categoria:</strong> {{ discipline.categoria }}</p>
                <p><strong>Créditos:</strong> {{ discipline.creditos }}</p>
                <p><strong>Horas:</strong> {{ discipline.carga_horaria }}</p>
              </div>
              
              <div class="details-column">
                <p><strong>Faltas:</strong> {{ discipline.faltas }}</p>
                <p><strong>Frequência:</strong> {{ discipline.frequencia }}%</p>
                <p><strong>Conceito:</strong> {{ discipline.conceito }}</p>
                <p class="status" :class="discipline.situacao.toLowerCase().replace(/\s+/g, '-')">
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
      alunoInfo: null,
      disciplinas: [],
      isLoading: false,
      isDragging: false
    }
  },
  created() {
    const savedAlunoInfo = localStorage.getItem('alunoInfo')
    const savedDisciplinas = localStorage.getItem('disciplinas')
    
    if (savedAlunoInfo && savedDisciplinas) {
      this.alunoInfo = JSON.parse(savedAlunoInfo)
      this.disciplinas = JSON.parse(savedDisciplinas)
    }
  },
  computed: {
    disciplinasAgrupadas() {
      const agrupado = this.disciplinas.reduce((acc, discipline) => {
        const key = `${discipline.ano_letivo}-${discipline.semestre}`
        if (!acc[key]) {
          acc[key] = {
            ano_letivo: discipline.ano_letivo,
            semestre: discipline.semestre,
            disciplinas: []
          }
        }
        acc[key].disciplinas.push(discipline)
        return acc
      }, {})

      return Object.values(agrupado).sort((a, b) => {
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

        this.alunoInfo = response.data.informacoes_aluno
        this.disciplinas = response.data.disciplinas

        localStorage.setItem('alunoInfo', JSON.stringify(this.alunoInfo))
        localStorage.setItem('disciplinas', JSON.stringify(this.disciplinas))
      } catch (error) {
        console.error('Erro ao fazer upload do histórico acadêmico:', error)
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
      this.alunoInfo = null
      this.disciplinas = []

      localStorage.removeItem('alunoInfo')
      localStorage.removeItem('disciplinas')
      
      if (this.$refs.arquivo) {
        this.$refs.arquivo.value = ''
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

.status.aprovado,
.status.cumprido {
  background-color: rgba(46, 204, 113, 0.2);
  color: #2ecc71;
}

.status.em-curso {
  background-color: rgba(241, 196, 15, 0.2);
  color: #f1c40f;
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
