# Motor Editorial AI

Aplicacao para operar um fluxo editorial com planilha Excel local, GPT com web search, geracao de imagem, revisao e publicacao no WordPress com metadados de SEO.

O motor foi desenhado para ser reaproveitado em diferentes blogs/clientes. A logica fica no codigo; identidade editorial, estrategia de SEO, prompts e credenciais ficam isolados em `references/`, `.env` e na pagina **Configuracoes**.

## O que o app faz

- Mantem a fila de pautas em uma planilha Excel local.
- Gera novas pautas com GPT e web search.
- Gera artigos em HTML semantico para WordPress.
- Gera briefing e capa automaticamente.
- Mostra preview do artigo e da imagem.
- Publica como rascunho ou direto no WordPress.
- Prepara campos de SEO compativeis com Yoast.
- Sincroniza status, URL e data de publicacao do WordPress.
- Cria backups da planilha, artigos, imagens e documentos de configuracao.
- Executa ciclos agendados via cron na VPS.

## Arquivos por cliente

Para adaptar o motor a outro blog, edite estes arquivos ou use a tela **Configuracoes**:

- `references/client_instructions.md`: marca, publico, tom de voz, produtos, URLs oficiais, temas permitidos/proibidos e regras editoriais.
- `references/seo_guidelines.md`: estrategia de SEO do cliente, criterios de qualidade, links internos, cornerstones e padroes de otimizacao.
- `references/prompt_generate_pautas.md`: template avancado para geracao de pautas.
- `references/prompt_generate_article.md`: template avancado para geracao de artigos.

Ao copiar o projeto para outro cliente, normalmente voce so precisa trocar esses documentos, limpar ou substituir `backend/data/editorial_pautas.xlsx`, e configurar as credenciais no `.env` ou pela pagina **Configuracoes**.

## Configuracao local

1. Crie o `.env` da raiz a partir de `backend/.env.example`.
2. Opcionalmente crie `frontend/.env.local` a partir de `frontend/.env.example`.
3. Nunca versione `.env`, `.env.local`, planilhas reais, imagens geradas ou artigos gerados.

Campos principais do `.env`:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_IMAGE_MODEL`
- `OPENAI_IMAGE_SIZE`
- `OPENAI_IMAGE_QUALITY`
- `OPENAI_WEBSEARCH_ENABLED`
- `WORDPRESS_URL`
- `WORDPRESS_USERNAME`
- `WORDPRESS_APPLICATION_PASSWORD`
- `CRON_ENABLED`
- `CRON_TOKEN`
- `CRON_MODE`
- `CRON_MAX_ITEMS`
- `CRON_SCHEDULE`
- `CRON_DRY_RUN`
- `CRON_ALLOW_UNREVIEWED_PUBLISH`

A API de configuracao nunca devolve a chave da OpenAI, a senha de aplicacao do WordPress ou o token do cron. Ela mostra apenas se esses valores ja estao configurados.

## Como rodar no Windows

Use `Iniciar_Local.bat`.

Ele sobe:

- Backend FastAPI em `http://localhost:8000`
- Frontend Next.js na primeira porta livre entre `3000` e `3005`
- Navegador automaticamente na URL do painel

Backend manual:

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend manual:

```powershell
cd frontend
npm run dev
```

## Fluxo editorial

1. A fila editorial fica em `backend/data/editorial_pautas.xlsx`.
2. O botao **Gerar 10 Novas Pautas** cria novas pautas usando GPT e web search.
3. Cada pauta pode gerar um pacote com:
   - `artigo_[slug].txt`
   - `artigo_[slug]_seo.txt`
   - `artigo_[slug]_imagem.txt`
4. A tela de review mostra artigo, SEO e imagem.
5. O WordPress recebe conteudo HTML, categoria, tags, Yoast e imagem destacada.
6. A fila registra status, URL, post ID e data/hora de publicacao.

## Paginas do painel

- **Dashboard:** visao geral da operacao.
- **Pautas:** fila editorial, geracao de pautas/artigos, publicacao e sincronizacao WordPress.
- **Saude:** diagnostico de GPT, web search, WordPress, cron, arquivos e backups.
- **Configuracoes:** editor de instrucoes do cliente, SEO, prompts, APIs e automacao.

## Deploy na VPS

Exemplo usando Ubuntu, Nginx e systemd.

### 1. Clonar

```bash
sudo mkdir -p /opt
sudo git clone https://github.com/filipelirio/post-generator.git /opt/motor-editorial
sudo chown -R www-data:www-data /opt/motor-editorial
cd /opt/motor-editorial
```

### 2. Configurar variaveis

```bash
sudo cp backend/.env.example .env
sudo nano .env
```

Em producao, ajuste pelo menos:

```dotenv
OPENAI_API_KEY="sua-chave"
WORDPRESS_URL="https://seublog.com"
WORDPRESS_USERNAME="usuario"
WORDPRESS_APPLICATION_PASSWORD="xxxx xxxx xxxx xxxx xxxx"
CORS_ORIGINS="https://artigos.seudominio.com"
CRON_ENABLED="true"
CRON_TOKEN="um-token-longo-e-privado"
CRON_MODE="publish"
CRON_MAX_ITEMS="1"
CRON_SCHEDULE="0 20 * * 1,3,5"
CRON_DRY_RUN="true"
CRON_ALLOW_UNREVIEWED_PUBLISH="false"
```

### 3. Instalar backend

```bash
cd /opt/motor-editorial/backend
sudo -u www-data python3 -m venv venv
sudo -u www-data ./venv/bin/pip install -r requirements.txt
```

### 4. Instalar frontend

```bash
cd /opt/motor-editorial/frontend
sudo -u www-data cp .env.example .env.local
sudo -u www-data sed -i 's#NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"#NEXT_PUBLIC_API_URL="/api/v1"#' .env.local
sudo -u www-data npm ci
sudo -u www-data npm run build
```

### 5. Instalar systemd

```bash
sudo cp /opt/motor-editorial/deploy/systemd/motor-editorial-backend.service.example /etc/systemd/system/motor-editorial-backend.service
sudo cp /opt/motor-editorial/deploy/systemd/motor-editorial-frontend.service.example /etc/systemd/system/motor-editorial-frontend.service
sudo systemctl daemon-reload
sudo systemctl enable --now motor-editorial-backend
sudo systemctl enable --now motor-editorial-frontend
sudo systemctl status motor-editorial-backend --no-pager
sudo systemctl status motor-editorial-frontend --no-pager
```

### 6. Configurar Nginx

```bash
sudo cp /opt/motor-editorial/deploy/nginx/motor-editorial.conf.example /etc/nginx/sites-available/motor-editorial
sudo nano /etc/nginx/sites-available/motor-editorial
sudo ln -s /etc/nginx/sites-available/motor-editorial /etc/nginx/sites-enabled/motor-editorial
sudo nginx -t
sudo systemctl reload nginx
```

Recomendado: ativar HTTPS com Certbot e proteger o painel com Basic Auth ou Cloudflare Access.

## Cron job na VPS

O app armazena a politica do cron em `CRON_SCHEDULE`, mas quem agenda de verdade e o sistema operacional da VPS.

Exemplo para segunda, quarta e sexta as 20:00:

```dotenv
CRON_SCHEDULE="0 20 * * 1,3,5"
```

Crontab correspondente:

```cron
0 20 * * 1,3,5 cd /opt/motor-editorial/backend && ./venv/bin/python scripts/run_cron.py --execute >> /var/log/motor-editorial-cron.log 2>&1
```

Antes de ativar execucao real, rode sem `--execute` para simular:

```bash
cd /opt/motor-editorial/backend
./venv/bin/python scripts/run_cron.py --mode publish
```

Depois de validar, desative `CRON_DRY_RUN` e habilite `CRON_ALLOW_UNREVIEWED_PUBLISH` se quiser publicar direto:

```dotenv
CRON_DRY_RUN="false"
CRON_ALLOW_UNREVIEWED_PUBLISH="true"
```

## Seguranca para VPS

Nao exponha este painel publicamente sem autenticacao. Ele consegue gastar creditos de IA, alterar credenciais locais e publicar no WordPress.

Recomendacoes:

- Servir painel e `/api/` atras de autenticacao, como Nginx Basic Auth ou Cloudflare Access.
- Manter o FastAPI ouvindo apenas em `127.0.0.1`.
- Usar apenas um worker enquanto a persistencia for Excel local.
- Fazer backup externo de `backend/data`.
- Definir `CORS_ORIGINS` somente com o dominio real do painel.

## Testes

Os testes abaixo nao geram pautas, nao consomem creditos do GPT e nao publicam conteudo:

```powershell
cd backend
.\venv\Scripts\python.exe -m unittest discover -s tests -v
.\venv\Scripts\python.exe scripts\smoke_test.py --include-wordpress

cd ..\frontend
npm run lint
npm run build
npm audit --audit-level=moderate
```

No Linux:

```bash
cd backend
./venv/bin/python -m unittest discover -s tests -v
./venv/bin/python scripts/smoke_test.py --include-wordpress

cd ../frontend
npm run lint
npm run build
npm audit --audit-level=moderate
```

O `smoke_test.py --include-wordpress` faz apenas leitura autenticada para validar a conexao com o WordPress.
