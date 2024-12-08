<template>
  <div class="home">
    <div class="content">
      <h1 class="title">Eikão...</h1>
      <div class="construction-icon">🚧</div>
      <p class="description">
        Estamos trabalhando em algo incrível! Volte em breve para mais atualizações.
      </p>
      <div class="navigation-hints">
        <router-link to="/matriz" class="hint-link">
          Veja a matriz curricular do semestre atual
        </router-link>
        <router-link to="/historico" class="hint-link">
          Teste o nosso leitor de histórico acadêmico
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  min-height: calc(100vh - 61px);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background-color: #1a1a1a;
}

.content {
  text-align: center;
  max-width: 600px;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.title {
  font-size: 3rem;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #646cff, #42b883);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: bold;
  letter-spacing: -1px;
}

.construction-icon {
  font-size: 4rem;
  margin: 2rem 0;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.description {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 2rem;
  line-height: 1.6;
  letter-spacing: -0.5px;
}

.navigation-hints {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.hint-link {
  color: #646cff;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  transition: all 0.3s ease;
  border: 1px solid rgba(100, 108, 255, 0.3);
  font-weight: 500;
  letter-spacing: -0.5px;
  background-color: rgba(100, 108, 255, 0.1);
}

.hint-link:hover {
  background-color: rgba(100, 108, 255, 0.2);
  border-color: rgba(100, 108, 255, 0.5);
  transform: translateY(-2px);
}

@media (max-width: 600px) {
  .title {
    font-size: 2rem;
  }
  
  .description {
    font-size: 1rem;
  }
  
  .hint-link {
    padding: 0.5rem 1rem;
  }
}
</style>
