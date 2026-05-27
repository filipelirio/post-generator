# Motor Editorial AI

Aplicação local para operar um fluxo editorial com planilha Excel, GPT com web search, geração de imagem, revisão e publicação no WordPress com metadados de SEO.

O projeto foi desenhado para ser reaproveitado em diferentes blogs/clientes. A lógica fica no código; a identidade editorial, estratégia de SEO, prompts e credenciais ficam isolados em arquivos de referência e na página **Configurações**.

## O que o app faz

- Mantém a fila de pautas em uma planilha Excel local.
- Gera novas pautas com GPT e web search.
- Gera artigos em HTML semântico para WordPress.
- Gera briefing e capa automaticamente.
- Mostra preview do artigo e da imagem.
- Publica como rascunho ou direto no WordPress.
- Prepara campos de SEO compatíveis com Yoast.
- Sincroniza status, URL e data de publicação do WordPress.
- Cria backups da planilha, artigos, imagens e documentos de configuração.
- Executa ciclos agendados via cron na VPS.

## Arquivos por cliente

Para adaptar o motor a outro blog, edite estes arquivos ou use a tela **Configurações**:

- [client_instructions.md](D:/ChatGPT/post-generator/references/client_instructions.md): marca, público, tom de voz, produtos, URLs oficiais, temas permitidos/proibidos e regras editoriais.
- [seo_guidelines.md](D:/ChatGPT/post-generator/references/seo_guidelines.md): estratégia de SEO do cliente, critérios de qualidade, links internos, cornerstones e padrões de otimização.
- [prompt_generate_pautas.md](D:/ChatGPT/post-generator/references/prompt_generate_pautas.md): template avançado para geração de pautas.
- [prompt_generate_article.md](D:/ChatGPT/post-generator/references/prompt_generate_article.md): template avançado para geração de artigos.

Ao copiar o projeto para outro cliente, normalmente você só precisa trocar esses documentos, limpar ou substituir a planilha em `backend/data`, e configurar as credenciais no `.env` ou pela página **Configurações**.

## Configurações sensíveis

As credenciais são gravadas no arquivo [`.env`](D:/ChatGPT/post-generator/.env), que não deve ser versionado.

Campos principais:

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

A API de configuração nunca devolve a chave da OpenAI, a senha de aplicação do WordPress ou o token do cron. Ela mostra apenas se esses valores já estão configurados.

## Como rodar localmente

Use [Iniciar_Local.bat](D:/ChatGPT/post-generator/Iniciar_Local.bat).

Ele sobe:

- Backend FastAPI em `http://localhost:8000`
- Frontend Next.js na primeira porta livre entre `3000` e `3005`
- Navegador automaticamente na URL do painel

Backend manual:

```powershell
cd D:\ChatGPT\post-generator\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend manual:

```powershell
cd D:\ChatGPT\post-generator\frontend
npm run dev
```

## Fluxo editorial

1. A fila editorial fica em [editorial_pautas.xlsx](D:/ChatGPT/post-generator/backend/data/editorial_pautas.xlsx).
2. O botão **Gerar 10 Novas Pautas** cria novas pautas usando o GPT e web search.
3. Cada pauta pode gerar um pacote com:
   - `artigo_[slug].txt`
   - `artigo_[slug]_seo.txt`
   - `artigo_[slug]_imagem.txt`
4. A tela de review mostra artigo, SEO e imagem.
5. O WordPress recebe conteúdo HTML, categoria, tags, Yoast e imagem destacada.
6. A fila registra status, URL, post ID e data/hora de publicação.

## Páginas do painel

- **Dashboard:** visão geral da operação.
- **Pautas:** fila editorial, geração de pautas/artigos, publicação e sincronização WordPress.
- **Saúde:** diagnóstico de GPT, web search, WordPress, cron, arquivos e backups.
- **Configurações:** editor de instruções do cliente, SEO, prompts, APIs e automação.

## Cron job na VPS

O app armazena a política do cron em `CRON_SCHEDULE`, mas quem agenda de verdade é o sistema operacional da VPS.

Exemplo de `.env` para publicação direta em dias úteis às 07:00:

```dotenv
CRON_ENABLED="true"
CRON_TOKEN="um-token-longo-aleatorio-e-privado"
CRON_MODE="publish"
CRON_MAX_ITEMS="1"
CRON_SCHEDULE="0 7 * * 1-5"
CRON_DRY_RUN="false"
CRON_ALLOW_UNREVIEWED_PUBLISH="true"
```

Exemplo de crontab usando a mesma frequência:

```cron
0 7 * * 1-5 cd /opt/motor-editorial/backend && ./venv/bin/python scripts/run_cron.py --execute >> /var/log/motor-editorial-cron.log 2>&1
```

Antes de ativar a execução real, rode sem `--execute` para simular:

```bash
cd /opt/motor-editorial/backend
./venv/bin/python scripts/run_cron.py --mode publish
```

## Segurança para VPS

Não exponha este painel publicamente sem autenticação. Ele consegue gastar créditos de IA, alterar credenciais locais e publicar no WordPress.

Recomendações:

- Servir painel e `/api/` atrás de autenticação, como Nginx Basic Auth ou Cloudflare Access.
- Manter o FastAPI ouvindo apenas em `127.0.0.1`.
- Usar apenas um worker enquanto a persistência for Excel local.
- Fazer backup externo de `backend/data`.
- Definir `CORS_ORIGINS` somente com o domínio real do painel.

## Testes

Os testes abaixo não geram pautas, não consomem créditos do GPT e não publicam conteúdo:

```powershell
cd D:\ChatGPT\post-generator\backend
.\venv\Scripts\python.exe -m unittest discover -s tests -v
.\venv\Scripts\python.exe scripts\smoke_test.py --include-wordpress

cd D:\ChatGPT\post-generator\frontend
npm run lint
npm run build
npm audit --audit-level=moderate
```

O `smoke_test.py --include-wordpress` faz apenas leitura autenticada para validar a conexão com o WordPress.
