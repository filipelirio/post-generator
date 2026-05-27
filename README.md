# Easy Artigos - Easy Medicina

Aplicação para operar o fluxo editorial do blog Easy Medicina localmente e, futuramente, em uma VPS privada.

## O que o app faz

- mantém a fila de pautas em uma planilha Excel local
- gera novas pautas com GPT + web search
- gera artigo em HTML para WordPress
- gera capa automaticamente
- mostra preview no dashboard responsivo
- publica no WordPress com Yoast e imagem destacada
- sincroniza status do WordPress de volta para a planilha
- cria backups da planilha, dos artigos e das imagens

## Estrutura principal

```text
backend/
  app/
    api/v1/
      editorial.py
    core/
      config.py
    integrations/
      wordpress.py
    schemas/
      editorial.py
    services/
      article_package_service.py
      editorial_file_service.py
      editorial_publish_service.py
      excel_editorial_service.py
      openai_editorial_service.py
      openai_image_service.py
    main.py
  data/
    editorial_pautas.xlsx
    generated_articles/
    generated_images/
    backups/
  requirements.txt
  venv/

frontend/
  src/
    app/
      page.tsx
      pautas/
      settings/
    components/
      Sidebar.tsx
    lib/
      api.ts
    styles/
      globals.css

references/
  manual_editorial_easy_medicina.md
  principles-seo.md
  prompt_generate_article.md
  prompt_generate_pautas.md
```

## Fluxo oficial

1. A fila editorial fica em [editorial_pautas.xlsx](D:/ChatGPT/post-generator/backend/data/editorial_pautas.xlsx).
2. O backend gera pautas e artigos usando OpenAI com apoio de web search.
3. O pacote gerado salva:
   - `artigo_[slug].txt`
   - `artigo_[slug]_seo.txt`
   - `artigo_[slug]_imagem.txt`
4. A review mostra preview do HTML e da capa.
5. O WordPress recebe conteudo, slug, excerpt, Yoast e featured image.
6. O app pode sincronizar o status publicado de volta para a planilha.

## Endpoints principais

- `GET /api/v1/editorial/system/status`
- `GET /api/v1/editorial/pautas`
- `GET /api/v1/editorial/pautas/{pauta_id}`
- `POST /api/v1/editorial/pautas/generate`
- `POST /api/v1/editorial/pautas/sync-wordpress`
- `POST /api/v1/editorial/articles/{pauta_id}/generate`
- `GET /api/v1/editorial/articles/{pauta_id}`
- `GET /api/v1/editorial/articles/{pauta_id}/image`
- `POST /api/v1/editorial/articles/publish`

## Variáveis de ambiente

O backend le:
- [`.env`](D:/ChatGPT/post-generator/.env)
- [`.env.example`](D:/ChatGPT/post-generator/backend/.env.example)

Campos principais:
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_IMAGE_MODEL`
- `OPENAI_WEBSEARCH_ENABLED`
- `WORDPRESS_URL`
- `WORDPRESS_USERNAME`
- `WORDPRESS_APPLICATION_PASSWORD`

Os caminhos de planilha e pastas de output já apontam para `backend/data` por padrão.

Para uma VPS, defina também:

- `CORS_ORIGINS=https://seu-painel.example.com`
- `NEXT_PUBLIC_API_URL=/api/v1` no build do frontend quando o proxy expuser a API no mesmo domínio

## Onde editar os prompts

Tudo que depende de prompt ou diretriz editorial fica em [references](D:/ChatGPT/post-generator/references):

- [manual_editorial_easy_medicina.md](D:/ChatGPT/post-generator/references/manual_editorial_easy_medicina.md)
- [principles-seo.md](D:/ChatGPT/post-generator/references/principles-seo.md)
- [prompt_generate_pautas.md](D:/ChatGPT/post-generator/references/prompt_generate_pautas.md)
- [prompt_generate_article.md](D:/ChatGPT/post-generator/references/prompt_generate_article.md)

Os placeholders desses prompts precisam continuar existindo quando você editar o texto.

## Como rodar

### Jeito mais simples

Use [Iniciar_Local.bat](D:/ChatGPT/post-generator/Iniciar_Local.bat).

Ele:
- sobe o backend com o `venv`
- sobe o frontend
- detecta a porta livre do Next.js
- abre o navegador automaticamente

### Backend manual

```powershell
cd D:\ChatGPT\post-generator\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend manual

```powershell
cd D:\ChatGPT\post-generator\frontend
npm run dev
```

## Backups

Os backups automáticos ficam em [backend/data/backups](D:/ChatGPT/post-generator/backend/data/backups).

## Testes antes de publicar

Os testes abaixo não geram pauta, não consomem créditos do GPT e não publicam artigo:

```powershell
cd D:\ChatGPT\post-generator\backend
.\venv\Scripts\python.exe -m unittest discover -s tests -v
.\venv\Scripts\python.exe scripts\smoke_test.py --include-wordpress

cd D:\ChatGPT\post-generator\frontend
npm run lint
npm run build
npm audit --audit-level=moderate
```

O `smoke_test.py --include-wordpress` apenas testa leitura da conexão autenticada do WordPress.

## Preparação para VPS

Este projeto ainda não deve ser colocado publicamente na internet sem uma camada de autenticação. O painel aciona geração paga com GPT e publicação no WordPress.

Requisitos para o deploy:

- Servir o painel e `/api/` atrás de autenticação no proxy reverso, como Nginx com Basic Auth ou Cloudflare Access.
- Manter o FastAPI vinculado a `127.0.0.1`, nunca diretamente exposto na porta `8000`.
- Executar apenas um worker do backend enquanto a persistência for Excel local.
- Persistir e fazer backup externo de `backend/data`.
- Configurar `CORS_ORIGINS` apenas com o domínio real do painel.

O cron job automático ainda é o próximo módulo: hoje o painel permite executar as etapas manualmente, mas não existe um comando agendável que selecione pautas e publique sem revisão.

## Estado atual

O fluxo oficial do projeto é o namespace `editorial`.
