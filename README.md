# Gerenciador de Tarefas API

API REST **multi-usuário** para tarefas pessoais, com JWT e isolamento por usuário, e frontend em HTML, CSS e JavaScript puro.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.143-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.1-D71F00)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2.14-E92063)
![PyJWT](https://img.shields.io/badge/PyJWT-2.15-000000?logo=jsonwebtokens&logoColor=white)
![Frontend](https://img.shields.io/badge/Frontend-HTML%20%2B%20CSS%20%2B%20JS-F7DF1E?logo=javascript&logoColor=black)
![testes](https://img.shields.io/badge/testes-automatizados%20em%20constru%C3%A7%C3%A3o-yellow)

> **Projeto de estudo e portfólio.** Começou como CRUD em FastAPI e evoluiu para sistema multi-usuário com JWT, isolamento por dono e interface própria.

**No ar:**

- **Frontend:** https://moisesmayyer.github.io/GerenciadorDeTarefas/
- **API:** https://gerenciadordetarefas-eesn.onrender.com
- **Banco:** PostgreSQL.

## Sumário

- [Sobre o projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Stack](#stack)
- [Como rodar](#como-rodar)
- [Deploy](#deploy)
- [Como usar](#como-usar)
- [Endpoints](#endpoints)
- [Regras de negócio](#regras-de-negócio)
- [Códigos de status](#códigos-de-status)
- [Modelo de dados](#modelo-de-dados)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Frontend](#frontend)
- [Decisões técnicas](#decisões-técnicas)
- [Qualidade](#qualidade)
- [O que falta](#o-que-falta)

## Sobre o projeto

O sistema permite criar, concluir, cancelar e excluir tarefas pessoais, com nome, descrição e status (`pendente`, `concluido` ou `cancelado`).

O recorte principal é o **multi-usuário**: cada conta acessa apenas as próprias tarefas. Toda consulta filtra pelo `usuario_id` do token, nunca pelo corpo; registros de outra conta respondem **404**. O frontend em `docs/` consome a API atual — sem prioridade, vencimento, etiquetas, busca no servidor ou paginação; busca e filtros são locais.

> **Banco:** PostgreSQL via `psycopg`; schema criado com `create_all` e migrações com Alembic planejadas.

## Funcionalidades

- Cadastro, login e gestão da própria conta (`/usuarios`, `/auth`)
- Senhas com **Argon2** e autenticação **JWT** (OAuth2 Password Flow)
- CRUD de **tarefas** com status `pendente`, `concluido` e `cancelado`
- Isolamento por usuário em todas as rotas de tarefas
- Login/logout no frontend, com sessão persistida no navegador
- Tema claro/escuro com preferência salva
- Busca sem distinção de acentos ou maiúsculas, filtros por status e contadores
- Layout responsivo, foco visível, diálogos nativos, `aria-live` e `prefers-reduced-motion`

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.11+ (testado em 3.14) |
| Framework | FastAPI 0.143 |
| ORM | SQLAlchemy 2.1 |
| Validação/serialização | Pydantic 2.14 + pydantic-settings |
| Banco | PostgreSQL (psycopg) |
| Servidor | Uvicorn |
| Hash de senha | pwdlib (Argon2) |
| Token | PyJWT (HS256) |
| Frontend | HTML5, CSS3 e JS (módulos ES) |
| Comunicação | Fetch API |
| Deploy | Render + GitHub Pages |
| Qualidade | TestClient (manual) e checagem de sintaxe JS |

## Como rodar

**Requisitos:** Python 3.11+, PostgreSQL e `git`.

```bash
# 1. Clone e entre no projeto
git clone https://github.com/MoisesMayyer/GerenciadorDeTarefas.git
cd GerenciadorDeTarefas

# 2. Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Gere uma chave para o JWT
python -c "import secrets; print(secrets.token_hex(32))"
```

Crie `backend/.env` (ignorado pelo Git):

```env
SECRET_KEY=<a chave gerada acima>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql+psycopg://usuario:senha@localhost:5432/gerenciadortarefas
CORS_ORIGINS=https://moisesmayyer.github.io,http://localhost:5500,http://127.0.0.1:5500
```

Ajuste `DATABASE_URL` ao PostgreSQL local (driver `psycopg` 3). `CORS_ORIGINS` é uma lista separada por vírgulas (padrão: `https://moisesmayyer.github.io`); as origens locais permitem o frontend em `http://localhost:5500`.

```bash
# 5. Suba a API (de dentro de backend/)
cd backend
uvicorn app.main:app --reload --port 8000
```

> Rode o Uvicorn de dentro de `backend/` (módulo `app.main`). As tabelas são criadas com `create_all`. Documentação local: **http://localhost:8000/docs**.

Para **resetar**, execute `DROP SCHEMA public CASCADE; CREATE SCHEMA public;` no PostgreSQL.

## Deploy

API no Render e frontend no GitHub Pages.

### API (Render)

- **Root directory:** `backend`
- **Build command:** `pip install -r ../requirements.txt`
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Variáveis:** `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `DATABASE_URL` e, se necessário, `CORS_ORIGINS`.

Configure as chaves do `backend/.env` em **Environment** no Render.

### Frontend (GitHub Pages)

- Publicado a partir de `docs/` na branch `main`.
- `docs/js/api.js` usa `https://gerenciadordetarefas-eesn.onrender.com` como URL padrão.
- Para outra API, defina `window.TASK_API_URL` antes do `main.js` ou grave `gerenciador.apiUrl` no `localStorage`.

### CORS

A API aceita apenas a origem do frontend publicado:

```env
CORS_ORIGINS=https://moisesmayyer.github.io
```

Para o frontend local, adicione `http://localhost:5500` e `http://127.0.0.1:5500` ao `backend/.env`; em produção, use só o domínio do GitHub Pages.

### Banco de dados

PostgreSQL via `DATABASE_URL`; no Render, use um banco gerenciado (Render, Neon ou Supabase) para persistir entre deploys. Driver `psycopg` 3; Alembic planejado.

## Como usar

### 1. Criar uma conta

```bash
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Ana", "email": "ana@email.com", "senha": "senha123"}'
```

```json
{"id": 1, "nome": "Ana", "email": "ana@email.com", "ativo": true}
```

### 2. Fazer login e obter o token

Login via `application/x-www-form-urlencoded` (OAuth2), não JSON:

```bash
curl -X POST http://localhost:8000/auth/login \
  -d "username=ana@email.com&password=senha123"
```

```json
{"access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer"}
```

### 3. Usar o token nas rotas protegidas

```bash
TOKEN="cole-o-access-token-aqui"
```

Envie `Authorization: Bearer $TOKEN` nas rotas protegidas.

### 4. Criar e listar tarefas

```bash
curl -X POST http://localhost:8000/tarefas/nova_tarefa \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Estudar FastAPI", "descricao": "rotas, schemas e testes"}'
```

```json
{
  "id": 1,
  "nome": "Estudar FastAPI",
  "descricao": "rotas, schemas e testes",
  "status": "pendente"
}
```

```bash
curl http://localhost:8000/tarefas/ \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Atualizar, cancelar e excluir

```bash
# Atualização parcial: envie apenas os campos que deseja mudar
curl -X PUT http://localhost:8000/tarefas/atualizar_tarefa/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "concluido"}'

# Cancelamento (sem corpo)
curl -X PATCH http://localhost:8000/tarefas/cancelar_tarefa/1 \
  -H "Authorization: Bearer $TOKEN"

# Exclusão
curl -i -X DELETE http://localhost:8000/tarefas/deletar_tarefa/1 \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Abrir o frontend

Localmente, em outro terminal:

```bash
python -m http.server 5500 --directory docs
```

Abra **http://localhost:5500**, crie uma conta e ela já entra; depois, use e-mail e senha.

## Endpoints

As rotas de tarefas e as autenticadas de usuário exigem `Authorization: Bearer <token>`; "dono" indica que o registro pertence ao usuário autenticado, senão **404**.

### Autenticação

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| POST | `/auth/login` | público | Autentica e devolve o JWT |
| GET | `/auth/me` | autenticado | Dados do usuário do token |

### Usuários

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/usuarios/` | autenticado | Lista a própria conta |
| GET | `/usuarios/{id}` | dono | Busca o próprio usuário |
| POST | `/usuarios/` | público | Cria uma conta (`201`) |
| PUT | `/usuarios/{id}` | dono | Edita nome, e-mail e/ou senha |
| PATCH | `/usuarios/{id}/cancelar` | dono | Desativa a conta (`ativo = false`) |
| DELETE | `/usuarios/{id}` | dono | Remove a conta e suas tarefas (`204`) |

### Tarefas

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/tarefas/` | autenticado | Lista as tarefas do usuário |
| GET | `/tarefas/tarefa/{id}` | dono | Busca uma tarefa |
| POST | `/tarefas/nova_tarefa` | autenticado | Cria uma tarefa (`201`) |
| PUT | `/tarefas/atualizar_tarefa/{id}` | dono | Atualiza campos parcialmente |
| PATCH | `/tarefas/cancelar_tarefa/{id}` | dono | Marca a tarefa como `cancelado` |
| DELETE | `/tarefas/deletar_tarefa/{id}` | dono | Remove a tarefa (`204`) |

### Sistema

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/` | público | Verificação simples da API |

## Regras de negócio

| Recurso | Regra |
|---|---|
| Usuário | Nome de 1 a 50 caracteres; e-mail válido e único; senha de 6 a 128 caracteres; senha não pode ser só espaços; e-mail em minúsculas |
| Usuário | Contas inativas não autenticam nem usam o token |
| Usuário | Cada conta só lê, edita, desativa ou exclui a si mesma; outro `id` responde `404` |
| Usuário | A exclusão da conta remove todas as tarefas em cascata |
| Tarefa | `nome` e `descricao` são obrigatórios na criação; a descrição pode ser vazia |
| Tarefa | `status` aceita `pendente`, `concluido` ou `cancelado`; o padrão é `pendente` |
| Tarefa | O `usuario_id` vem sempre do token, nunca do corpo da requisição |
| Tarefa | Listagens e operações por ID são filtradas pelo dono; tarefa de outro usuário responde `404` |
| Tarefa | `PUT` é parcial: campos omitidos ou `null` são ignorados; para limpar a descrição, envie `""` |
| Tarefa | `PATCH /cancelar_tarefa/{id}` sempre define o status como `cancelado` |
| Autenticação | O token expira em 30 minutos (`ACCESS_TOKEN_EXPIRE_MINUTES`); ausente, inválido, expirado ou de usuário inativo responde `401` |

## Códigos de status

| Código | Quando acontece |
|---|---|
| `200` | Operações concluídas em usuários e tarefas |
| `201` | Criação de usuário ou tarefa |
| `204` | Exclusão de usuário ou tarefa (sem corpo) |
| `401` | Token ausente/inválido/expirado, usuário inativo ou credenciais incorretas |
| `404` | Usuário ou tarefa inexistente, ou pertencente a outra conta |
| `409` | E-mail já cadastrado |
| `422` | Corpo inválido (validação do Pydantic) |

## Modelo de dados

```
usuarios (1) ──< tarefas
```

| Tabela | Campos |
|---|---|
| `usuarios` | `id`, `nome`, `email` (único e indexado), `senha` (hash Argon2), `ativo` |
| `tarefas` | `id`, `nome`, `descricao`, `status`, `usuario_id` |

- Relacionamento **1:N**; `status` usa `CHECK` com os três valores (`native_enum=False`).
- `usuario_id` é FK anulável e não indexada para `usuarios.id`; endurecer o schema está no roadmap.
- Exclusão de usuário remove as tarefas em cascata pelo ORM (`cascade="all, delete-orphan"`). O schema usa `create_all`; a migração para Alembic deve tornar `usuario_id` `NOT NULL` e indexado.

## Estrutura do projeto

```
GerenciadorDeTarefas/
├── backend/
│   ├── app/
│   │   ├── database/        # database.py (engine/sessão/Base) e models.py
│   │   ├── routers/         # auth.py, tarefas.py e usuarios.py
│   │   ├── schemas/         # schemas de tarefas, token e usuários
│   │   ├── config.py        # settings do .env
│   │   ├── depends.py       # get_db e verificação do JWT
│   │   ├── security.py      # hash Argon2 e token
│   │   └── main.py          # app, CORS e routers
│   └── .env                 # segredos (ignorado pelo Git)
├── docs/                    # frontend (GitHub Pages)
│   ├── css/style.css
│   ├── js/                  # api, auth, main, task-model, tasks, theme e ui
│   └── index.html
├── README.md
├── requirements.txt
└── .gitignore
```

## Frontend

O frontend não usa framework nem bibliotecas de UI. A direção **Calm Ledger** combina tipografia nativa, cobalto e teal.

- A primeira tela é o **login**; com sessão válida, o app abre direto.
- O token JWT fica no `localStorage` e é enviado nas requisições; logout limpa a sessão e token inválido volta ao login.
- Tema claro/escuro salvo em `gerenciador.tema`; na primeira visita, segue o sistema.
- Busca e filtros são **locais**, sobre a lista já carregada.
- Duas colunas no desktop e uma no mobile, com foco visível e movimento reduzido.

Separação intencional: `task-model.js` é puro (sem DOM/HTTP), `tasks.js` concentra estado e ações, `ui.js` cuida do DOM, `theme.js` do tema e `main.js` orquestra.

> Módulos ES exigem HTTP; `file://` não funciona.

Versão publicada: https://moisesmayyer.github.io/GerenciadorDeTarefas/

A API padrão é `https://gerenciadordetarefas-eesn.onrender.com`. Como o Render gratuito hiberna, a primeira requisição pode levar dezenas de segundos (cold start).

## Decisões técnicas

**pwdlib/Argon2 em vez de passlib.** O `passlib` depende do `crypt`, removido no Python 3.13; o `pwdlib` mantém o Argon2.

**PyJWT, não o pacote `jwt`.** O pacote `jwt` do PyPI é outro projeto; use `PyJWT`, importado como `jwt`, e não instale os dois juntos.

**`response_model` nas rotas de usuários e tarefas.** Sem ele, o FastAPI serializa o objeto SQLAlchemy inteiro e pode vazar campos como o hash da senha.

**Isolamento por `usuario_id` na query, com `404`.** O filtro por dono fica na consulta; responder `404` em vez de `403` não confirma a existência de registros de outra conta.

**`model_dump(exclude_unset=True, exclude_none=True)` no `PUT`.** A atualização aplica apenas campos presentes e não nulos, evitando sobrescrever dados com `null`.

**`create_all` em vez de Alembic.** Decisão de escopo: o banco pode ser recriado; em produção, a evolução deve usar migrations versionadas.

**Busca local no frontend.** O backend não oferece busca ou paginação; a interface filtra em memória. Com volume maior, isso deve migrar para a API.

**Mutações atualizam o estado local.** `POST`, `PUT` e `PATCH` devolvem a tarefa alterada e `DELETE` responde `204`; o frontend aplica a resposta na lista, sem refazer `GET /tarefas/`.

**CORS restrito ao GitHub Pages.** `CORS_ORIGINS` é uma lista separada por vírgulas; como a autenticação usa Bearer token, `allow_credentials=False`.

## Qualidade

Não há suíte versionada. Validações manuais com `TestClient` e SQLite em memória cobriram `401` para token ausente/inválido, listagem vazia, criação com `usuario_id` do token, CRUD pelo dono e `404` para tarefa de outro usuário. O frontend foi validado manualmente em navegador headless (20 cenários) e em layouts de 1440×900 a 360×1600.

Verificação de sintaxe dos módulos:

```bash
node --experimental-default-type=module --check docs/js/*.js
```

> **Testes automatizados:** a suíte com `pytest` é o próximo item do roadmap; as verificações acima foram manuais e não commitadas.

## O que falta

Em ordem de prioridade:

**Essencial**

- [x] **Migrar de SQLite para PostgreSQL** (persistência entre deploys)
- [ ] Suíte de testes com `pytest` + `TestClient` (auth, isolamento, CRUD e validação)
- [x] Deploy da API
- [x] `usuario_id` `NOT NULL`, indexado e com cascade ou soft delete

**Qualidade**

- [ ] Tela de perfil (editar, desativar e excluir a conta)
- [ ] Migrations com Alembic
- [ ] `.env.example` para facilitar o setup
- [ ] Suíte de testes de frontend versionada
- [ ] Paginação e busca no servidor
- [ ] `criado_em` / `atualizado_em` nas tabelas (auditoria)
- [ ] Tratamento global de exceções e logging
- [ ] Prefixo de versão `/v1`

**Produção**

- [x] CORS restrito ao domínio do frontend
- [ ] Rate limiting no login
- [ ] Refresh token e revogação de access token
- [ ] CI no GitHub Actions com testes e checagem de sintaxe
- [ ] Dockerfile e docker-compose
- [x] Deploy com link público

## Status do projeto

Em desenvolvimento, com deploy ativo: API no Render, frontend no GitHub Pages e CRUD com JWT sobre PostgreSQL. Próximos passos: testes, Alembic e melhorias de produção.
