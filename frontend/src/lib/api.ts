import axios from "axios";

// Instância do Axios para o Backend FastAPI
// Prioriza a variável de ambiente se disponível (Docker/Produção)
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptação de Erros para Diagnóstico (Ajuda com "Network Error")
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log detalhado para depuração
    console.group("❌ Erro de API");
    console.error("Mensagem:", error.message);
    if (error.response) {
      console.error("Status:", error.response.status);
      console.error("Dados:", error.response.data);
    }
    if (error.config) {
      console.error("URL:", error.config.url);
      console.error("Método:", error.config.method);
    }
    console.groupEnd();
    
    if (error.message === "Network Error") {
      console.warn("💡 Dica: Verifique se o container backend está rodando em http://localhost:8000");
    }
    
    return Promise.reject(error);
  }
);

export default api;
