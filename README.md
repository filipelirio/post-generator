# Easy Artigos — Easy Medicina

Aplicação local para operação editorial do blog Easy Medicina.

Hoje o fluxo oficial do projeto é este:
- planilha editorial local em Excel
- geração de novas pautas com GPT + web search
- geração de artigo completo com SEO, links internos, links externos e CTA comercial
- geração automática de capa
- review no dashboard
- criação de rascunho ou publicação direta no WordPress
- backup automático da planilha, dos pacotes de artigo e das imagens

## Visão geral

O projeto foi reorganizado para operar com um fluxo editorial simples e confiável:

1. A planilha local guarda as pautas.
2. O backend usa OpenAI para gerar novas pautas ou artigos.
3. O frontend mostra dashboard, fila editorial, review e settings.
4. O WordPress recebe o artigo com conteúdo, Yoast e imagem destacada.

O caminho principal de dados fica em:
- [backend/data](D:/ChatGPT/post-generator/backend/data)

## Estrutura do projeto

```text
backend/
  app/
    api/v1/
      editorial.py         # fluxo novo oficial
      pautas.py            # legado
      generation.py        # legado
      wordpress.py         # legado/teste antigo
    core/
    db/
    integrations/
      wordpress.py         # integração WordPress ativa
    schemas/
    services/
      excel_editorial_service.py
      openai_editorial_service.py
      openai_image_service.py
      article_package_service.py
      editorial_file_service.py
      editorial_publish_service.py
  data/
    editorial_pautas.xlsx
    generated_articles/
    generated_images/
    backups/
  venv/

frontend/
  src/
    app/
      page.tsx             # dashboard
      pautas/
      settings/
    components/
    lib/

references/
  manual_editorial_easy_medicina.md
  principles-seo.md
  prompt_generate_pautas.md
  prompt_generate_article.md
```

## Fluxo oficial

### 1. Gerar pautas

Use o botão do dashboard ou da tela de pautas para criar novas pautas.

O backend:
- analisa a planilha atual
- usa GPT com web search
- evita duplicação de tema e keyword
- grava as novas linhas em `editorial_pautas.xlsx`

### 2. Gerar artigo

Ao clicar em `Gerar artigo`, o backend cria:
- `artigo_[slug].txt`
- `artigo_[slug]_seo.txt`
- `artigo_[slug]_imagem.txt`

Esses arquivos ficam em:
- [generated_articles](D:/ChatGPT/post-generator/backend/data/generated_articles)

A imagem gerada fica em:
- [generated_images](D:/ChatGPT/post-generator/backend/data/generated_images)

### 3. Review

A tela de review mostra:
- prévia HTML do artigo
- SEO do Yoast
- links internos e externos
- conversão/CTA
- preview visual da capa

### 4. Publicar

Na review existem dois caminhos:
- `Criar rascunho`
- `Publicar de verdade`

O backend publica no WordPress com:
- título
- conteúdo
- slug
- excerpt
- tags
- categoria
- metadados Yoast
- imagem destacada

Depois disso, a planilha é atualizada com:
- status
- data de publicação
- URL do WordPress

## Endpoints principais

O fluxo novo usa:

- `GET /api/v1/editorial/pautas`
- `GET /api/v1/editorial/pautas/{pauta_id}`
- `POST /api/v1/editorial/pautas/generate`
- `POST /api/v1/editorial/articles/{pauta_id}/generate`
- `GET /api/v1/editorial/articles/{pauta_id}`
- `GET /api/v1/editorial/articles/{pauta_id}/image`
- `POST /api/v1/editorial/articles/publish`
- `GET /api/v1/editorial/system/status`

Os endpoints antigos ainda existem no backend por compatibilidade, mas não são o fluxo principal do app.

## Configuração

O projeto lê variáveis de ambiente do arquivo:
- [`.env`](D:/ChatGPT/post-generator/.env)

Exemplo de base:
- [`.env.example`](D:/ChatGPT/post-generator/backend/.env.example)

Campos mais importantes:
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_IMAGE_MODEL`
- `OPENAI_WEBSEARCH_ENABLED`
- `WORDPRESS_URL`
- `WORDPRESS_USERNAME`
- `WORDPRESS_APPLICATION_PASSWORD`

Observação:
- o backend já usa caminhos padrão internos para `backend/data`, então você não precisa configurar planilha ou pastas se quiser seguir a convenção atual

## Como rodar

### Opção mais simples

Use:

- [Iniciar_Local.bat](D:/ChatGPT/post-generator/Iniciar_Local.bat)

Esse arquivo:
- sobe o backend com o `venv`
- sobe o frontend com `npm run dev`

### Backend manual

```powershell
cd D:\ChatGPT\post-generator\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend manual

```powershell
cd D:\ChatGPT\post-generator\frontend
npm run dev
```

## Onde editar a estratégia editorial

Se você quiser ajustar comportamento do GPT sem mexer em código, edite estes arquivos:

- [manual_editorial_easy_medicina.md](D:/ChatGPT/post-generator/references/manual_editorial_easy_medicina.md)
- [principles-seo.md](D:/ChatGPT/post-generator/references/principles-seo.md)
- [prompt_generate_pautas.md](D:/ChatGPT/post-generator/references/prompt_generate_pautas.md)
- [prompt_generate_article.md](D:/ChatGPT/post-generator/references/prompt_generate_article.md)

O serviço que consome isso é:
- [openai_editorial_service.py](D:/ChatGPT/post-generator/backend/app/services/openai_editorial_service.py)

Os prompts aceitam placeholders como:
- `[[COUNT]]`
- `[[EDITORIAL_MANUAL]]`
- `[[SEO_PRINCIPLES]]`
- `[[EXISTING_KEYWORDS]]`
- `[[EXISTING_TOPICS]]`
- `[[FORCE_CATEGORY]]`
- `[[NOTES]]`
- `[[PAUTA_CONTEXT]]`

Esses placeholders devem continuar existindo quando fizer ajustes.

## Backups automáticos

O sistema gera versionamento automático em:
- [backups](D:/ChatGPT/post-generator/backend/data/backups)

Inclui:
- snapshots da planilha
- snapshots dos pacotes de artigo
- snapshots das imagens geradas

## Estado atual do produto

O fluxo principal está operacional.

Já funciona de ponta a ponta:
- gerar pautas
- gerar artigo
- gerar capa
- revisar no dashboard
- publicar no WordPress
- atualizar a planilha
- manter backup dos artefatos principais

## O que ainda é legado

Ainda existem partes antigas no repositório, mas não fazem parte do caminho principal:
- rotas antigas de `pautas`, `generation` e `wordpress`
- modelos e repositórios do SQLite legado

Enquanto não houver necessidade de compatibilidade, o ideal é considerar o namespace `editorial` como o fluxo oficial do projeto.
