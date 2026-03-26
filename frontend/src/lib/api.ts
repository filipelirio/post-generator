import axios from "axios";

// Instância do Axios para o Backend FastAPI
// Prioriza a variável de ambiente se disponível (Docker/Produção)
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
