# Gerador de Artigos AI para WordPress - Easy Medicina

Aplicação local completa e robusta para geração de artigos otimizados para SEO utilizando Inteligência Artificial (Gemini) a partir de pautas editoriais importadas via planilha Excel (.xlsx), com publicação automatizada no WordPress.

## 🚀 Stack Tecnológica

- **Backend**: FastAPI (Python) + SQLAlchemy (ORM) + Pydantic (Validação)
- **Frontend**: Next.js (React/TypeScript) + Tailwind CSS + Lucide Icons + React-Quill (Editor)
- **Banco de Dados**: SQLite hospedado na pasta `/data` (Persistência local)
- **IA**: Gemini API (`google-genai` SDK oficial)
- **Integração CMS**: WordPress REST API via `httpx`
- **Ambiente**: Docker Compose

---

## 📂 Estrutura de Pastas

```text
/backend
  /app
    /api/v1          # Endpoint de Pautas, Geração, WordPress
    /core            # Configurações e Logs
    /db              # Sessão e Base Class
    /models          # Tabelas SQLAlchemy (Pauta, Draft, etc.)
    /repositories    # Camada de Acesso a Dados (Queries)
    /services        # Lógica de Orquestração da IA
    /integrations     # Cliente Gemini e WordPress
    /prompts         # Prompts estruturados (.txt)
    /utils           # Parser de Excel (pandas)
/frontend
  /src
    /app             # Páginas (Dashboard, Import, Pautas)
    /components      # Sidebar, Editor Rico, UI
    /lib             # Cliente Axios
/data                # Volumes Docker para SQLite e Uploads
/docker              # Dockerfiles
```

---

## ⚙️ Como Configurar

1. **Clonar/Instalar**:
   - Certifique-se de ter **Docker** e **Docker Compose** instalados na sua máquina.

2. **Variáveis de Ambiente**:
   - Copie o arquivo `.env.example` na raiz para `.env`:
     ```bash
     cp .env.example .env
     ```
   - Abra o `.env` e preencha as variáveis obrigatórias:
     - `GEMINI_API_KEY`: Sua chave de API do Google AI Studio.
     - `WORDPRESS_URL`: URL do seu blog (ex: `https://easymedicina.com`).
     - `WORDPRESS_USERNAME`: Seu usuário administrativo.
     - `WORDPRESS_APPLICATION_PASSWORD`: Senha de App gerada no seu perfil WordPress.

---

## 🐳 Como Rodar com Docker (Recomendado)

Na raiz do projeto, execute o comando para subir os containers do Backend e Frontend:

```bash
docker-compose up -d --build
```

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend (API Docs)**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

---

## 🏃‍♂️ Como Rodar Sem Docker (Localmente)

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Gere o banco criando o diretório `/data` na raiz antes.*

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🧠 Fluxo de Uso Simplificado

1. **Importação**: Acesse a tela "Importar Planilha" e faça o upload de um `.xlsx` contendo a coluna `tema` (obrigatória).
2. **Lista**: Vá para "Pautas" para ver as linhas importadas.
3. **Geração**: Clique em "Visualizar" em uma pauta e depois em "Gerar com IA".
   - O sistema criará o Planejamento Editorial -> Redigirá o Artigo -> Criará o Rascunho.
4. **Revisão**: Use o **Editor Rico** para fazer ajustes manuais ou ler o que a IA gerou.
5. **Publicação**: Tudo aprovado? Clique em "Publicar no WP" para enviar como `draft` (Rascunho) diretamente para o painel do seu WordPress.

---

## ⚠️ Limitações do MVP e Próximos Passos
- Integração de Upload de Imagem de Capa para o WordPress (Mídia).
- Autenticação de Usuários (Uso Local Seguro por ser Multi-Volume).
- Filas de Tarefas (Redis) para geração assíncrona se houver muitos artigos simultâneos.
