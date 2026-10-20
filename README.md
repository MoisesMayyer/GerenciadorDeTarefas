# Gerenciador de Tarefas API

API REST de gerenciamento de tarefas pessoais **multi-usuário**, com autenticação JWT e isolamento de dados por usuário. O projeto inclui um frontend próprio em HTML, CSS e JavaScript puro.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.143-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.1-D71F00)
![Pydantic](https://img.shields.io/badge/Pydantic-2.14-E92063)
![PyJWT](https://img.shields.io/badge/PyJWT-2.15-000000?logo=jsonwebtokens&logoColor=white)
![Frontend](https://img.shields.io/badge/Frontend-HTML%20%2B%20CSS%20%2B%20JS-F7DF1E?logo=javascript&logoColor=black)
![testes](https://img.shields.io/badge/testes-automatizados%20em%20constru%C3%A7%C3%A3o-yellow)

> **Projeto de estudo e portfólio.** Este projeto começou como um CRUD simples de tarefas em FastAPI e evoluiu para um sistema multi-usuário, com autenticação JWT, isolamento de dados por dono e uma interface própria.

## Sumário

- [Sobre o projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Stack](#stack)
- [Como rodar](#como-rodar)
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

O sistema permite criar, acompanhar, concluir, cancelar e excluir tarefas pessoais. Cada tarefa tem nome, descrição e um status (`pendente`, `concluido` ou `cancelado`).

O recorte principal é o **multi-usuário de verdade**: cada conta só enxerga as próprias tarefas. Toda consulta é filtrada pelo `usuario_id` extraído do token — nunca pelo que o cliente envia no corpo da requisição. Quando uma tarefa pertence a outra conta, a API responde **404** para não revelar a existência do registro.

O frontend fica em `docs/` e consome exatamente o contrato atual da API. Não existem prioridade, vencimento, etiquetas ou busca no servidor: a interface trabalha apenas com os campos que o backend oferece, e a busca e os filtros são locais, sobre as tarefas já carregadas.

A API é servida com documentação interativa automática em `/docs` (Swagger UI) e `/redoc`.

## Funcionalidades

- Cadastro, login e gerenciamento da própria conta (`/usuarios`, `/auth`)
- Senhas armazenadas com **Argon2** e autenticação via **JWT** (OAuth2 Password Flow)
- CRUD de **tarefas** com status `pendente`, `concluido` e `cancelado`
- Isolamento por usuário em todas as rotas de tarefas
- Login e logout no frontend, com sessão persistida no navegador
- Tema claro/escuro com preferência salva e respeito ao tema do sistema
- Busca sem distinção de acentos ou maiúsculas e filtros por status
- Contadores de tarefas pendentes, concluídas e canceladas
- Layout responsivo, navegação por teclado e suporte a `prefers-reduced-motion`
- Banco SQLite criado automaticamente na primeira execução

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.11+ (testado em 3.14) |
| Framework | FastAPI 0.143 |
| ORM | SQLAlchemy 2.1 |
| Validação/serialização | Pydantic 2.14 + pydantic-settings |
| Banco | SQLite |
| Servidor | Uvicorn |
| Hash de senha | pwdlib (Argon2) |
| Token | PyJWT (HS256) |
| Frontend | HTML5, CSS3 e JavaScript (módulos ES) |
| Comunicação | Fetch API |
| Qualidade | TestClient (manual) e verificação de sintaxe dos módulos JS |

## Como rodar

**Requisitos:** Python 3.11 ou superior e `git`.

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

Crie `backend/.env` (ignorado pelo Git) com a chave gerada:

```env
SECRET_KEY=<a chave gerada acima>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

```bash
# 5. Suba a API (de dentro de backend/)
cd backend
uvicorn app.main:app --reload --port 8000
```

Acesse **http://localhost:8000/docs** para a documentação interativa.

> **Atenção ao diretório:** o módulo da aplicação é `app.main`, então o Uvicorn precisa ser executado de dentro de `backend/`. O banco é criado em `backend/database.db`, com as tabelas `usuarios` e `tarefas`.

Para **resetar** os dados, pare o servidor e apague `backend/database.db`; ele será recriado vazio no próximo start. O schema é criado com `create_all`, então alterações de colunas exigem recriar o banco (ou adotar migrations).

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

O e-mail é normalizado para minúsculas. Tentar cadastrar o mesmo e-mail novamente responde **409**.

### 2. Fazer login e obter o token

O login usa `application/x-www-form-urlencoded` (padrão OAuth2), não JSON:

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

curl http://localhost:8000/tarefas/ \
  -H "Authorization: Bearer $TOKEN"
```

No Swagger (`/docs`), clique em **Authorize**, informe e-mail e senha e o próprio Swagger passa a enviar o token em todas as chamadas.

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

A resposta contém somente as tarefas do usuário do token.

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

Em outro terminal, a partir da raiz do projeto:

```bash
python -m http.server 5500 --directory docs
```

Depois abra **http://localhost:5500**, clique em **Criar conta** e informe nome, e-mail e senha. Ao concluir, a conta já entra direto no sistema; nas próximas visitas, use o e-mail e a senha cadastrados.

## Endpoints

As rotas de tarefas e as rotas autenticadas de usuário exigem `Authorization: Bearer <token>`. "Dono" significa que o registro precisa pertencer ao usuário autenticado; caso contrário, a API responde **404**.

### Autenticação

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| POST | `/auth/login` | público | Recebe `username` (e-mail) e `password` via form e devolve o JWT |
| GET | `/auth/me` | autenticado | Dados do usuário do token |

### Usuários

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/usuarios/` | autenticado | Lista o próprio usuário |
| GET | `/usuarios/{id}` | dono | Busca o próprio usuário |
| POST | `/usuarios/` | público | Cria uma conta (`201`) |
| PUT | `/usuarios/{id}` | dono | Edita nome, e-mail e/ou senha |
| PATCH | `/usuarios/{id}/cancelar` | dono | Desativa a conta (`ativo = false`) |
| DELETE | `/usuarios/{id}` | dono | Remove a conta e suas tarefas (`204`) |

> As rotas autenticadas de usuário só operam sobre a própria conta; um `id` de outra conta responde **404**. Contas desativadas não fazem login e têm o token recusado. A exclusão remove as tarefas em cascata pelo ORM.

### Tarefas

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/tarefas/` | autenticado | Lista as tarefas do usuário |
| GET | `/tarefas/tarefa/{id}` | dono | Busca uma tarefa |
| POST | `/tarefas/nova_tarefa` | autenticado | Cria uma tarefa (`201`) |
| PUT | `/tarefas/atualizar_tarefa/{id}` | dono | Atualiza parcialmente nome, descrição e/ou status |
| PATCH | `/tarefas/cancelar_tarefa/{id}` | dono | Marca a tarefa como `cancelado` |
| DELETE | `/tarefas/deletar_tarefa/{id}` | dono | Remove a tarefa (`204`) |

### Sistema

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/` | público | Verificação simples da API |

## Regras de negócio

| Recurso | Regra |
|---|---|
| Usuário | Nome entre 1 e 50 caracteres; e-mail válido e único; senha entre 6 e 128 caracteres |
| Usuário | A senha não pode conter apenas espaços; o e-mail é salvo e comparado em minúsculas |
| Usuário | Contas inativas não conseguem autenticar nem usar o token |
| Usuário | Cada conta só lê, edita, desativa ou exclui a si mesma; outro `id` responde `404` |
| Usuário | A exclusão da conta remove todas as tarefas do usuário em cascata |
| Tarefa | `nome` e `descricao` são obrigatórios na criação; a descrição pode ser uma string vazia |
| Tarefa | `status` aceita apenas `pendente`, `concluido` ou `cancelado`; o padrão é `pendente` |
| Tarefa | O `usuario_id` vem sempre do token, nunca do corpo da requisição |
| Tarefa | Listagens e operações por ID são filtradas pelo dono; tarefa de outro usuário responde `404` |
| Tarefa | `PUT` é parcial: campos não enviados (ou enviados como `null`) são ignorados |
| Tarefa | Para limpar a descrição, envie `"descricao": ""`; `null` não apaga o valor |
| Tarefa | `PATCH /cancelar_tarefa/{id}` sempre define o status como `cancelado` |
| Autenticação | O token expira em 30 minutos por padrão (`ACCESS_TOKEN_EXPIRE_MINUTES`) |
| Autenticação | Token ausente, inválido, expirado ou de usuário inativo responde `401` |

## Códigos de status

| Código | Quando acontece |
|---|---|
| `200` | Leitura, atualização, cancelamento ou desativação de usuário; operações em tarefas |
| `201` | Criação de usuário ou tarefa |
| `204` | Exclusão de usuário ou tarefa (sem corpo) |
| `401` | Sem token, token inválido/expirado, usuário inativo ou credenciais incorretas |
| `404` | Usuário ou tarefa inexistente, ou pertencente a outra conta |
| `409` | E-mail já cadastrado |
| `422` | Corpo da requisição inválido (validação do Pydantic) |

## Modelo de dados

```
usuarios (1) ──< tarefas
```

| Tabela | Campos |
|---|---|
| `usuarios` | `id`, `nome`, `email` (único e indexado), `senha` (hash Argon2), `ativo` |
| `tarefas` | `id`, `nome`, `descricao`, `status`, `usuario_id` |

- O relacionamento é **1:N**: cada usuário pode ter várias tarefas, e cada tarefa pertence a no máximo um usuário.
- `tarefas.status` usa um `CHECK` com os três valores permitidos (`native_enum=False`).
- `usuario_id` é uma chave estrangeira para `usuarios.id`. No schema atual a coluna é anulável e não indexada; as rotas sempre a preenchem, mas esse é um ponto a endurecer (ver [O que falta](#o-que-falta)).
- Não há tabela de associação nem compartilhamento de tarefas entre contas.
- A exclusão de usuário é feita pela API e remove as tarefas em cascata pelo ORM (`cascade="all, delete-orphan"`).

## Estrutura do projeto

```
GerenciadorDeTarefas/
├── backend/
│   ├── app/
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── database.py      # engine, sessão e Base do SQLAlchemy
│   │   │   └── models.py        # Tarefa, Usuario e StatusTarefa
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # login e /auth/me
│   │   │   ├── tarefas.py       # CRUD de tarefas com isolamento por dono
│   │   │   └── usuarios.py      # cadastro de usuários
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── tarefas.py       # Create / Update / Response
│   │   │   ├── token.py         # resposta do login
│   │   │   └── usuarios.py      # Create / Update / Response
│   │   ├── config.py            # settings carregadas do .env
│   │   ├── depends.py           # get_db e verificação do JWT
│   │   ├── security.py          # hash Argon2 e criação do token
│   │   └── main.py              # app FastAPI, CORS e registro dos routers
│   ├── .env                     # segredos (ignorado pelo Git)
│   └── database.db              # SQLite gerado na primeira execução
├── docs/                        # frontend (publicado no GitHub Pages)
│   ├── css/style.css
│   ├── js/
│   │   ├── api.js               # HTTP, token e tratamento de erros
│   │   ├── auth.js              # sessão e tela de login
│   │   ├── main.js              # orquestração da aplicação
│   │   ├── task-model.js        # normalização, busca e filtros
│   │   ├── tasks.js             # estado e operações das tarefas
│   │   ├── theme.js             # tema claro/escuro
│   │   └── ui.js                # renderização e eventos
│   ├── index.html
│   └── README.md
├── README.md
├── requirements.txt
└── .gitignore
```

## Frontend

O frontend foi construído sem framework e sem bibliotecas de UI. A direção visual se chama **Calm Ledger**: uma interface editorial, calma e precisa, com tipografia nativa, acento cobalto e uma linha de status teal nas tarefas.

- A primeira tela é o **login**. Com uma sessão válida, o app abre direto.
- O token JWT fica no `localStorage` e é enviado automaticamente em todas as requisições de tarefas.
- Logout limpa a sessão; token expirado ou inválido devolve o usuário ao login.
- O tema claro/escuro é salvo em `gerenciador.tema`; na primeira visita, segue o tema do sistema.
- A busca ignora acentos e maiúsculas e os filtros são **locais**, sobre a lista já carregada.
- O layout tem duas colunas no desktop e uma no mobile, com foco visível e suporte a movimento reduzido.

A separação em camadas foi intencional: `task-model.js` é puro (sem DOM e sem HTTP), `tasks.js` concentra estado e ações, `ui.js` cuida do DOM, `theme.js` do tema e `main.js` apenas orquestra. Isso permite trocar a API ou adicionar novas telas sem reescrever a lógica de apresentação.

> O frontend usa módulos ES, então precisa ser servido por HTTP — abrir o `index.html` direto pelo sistema de arquivos (`file://`) não funciona.

Versão publicada (apenas a interface, sem API no ar):
https://moisesmayyer.github.io/GerenciadorDeTarefas/

Como a API ainda não tem deploy, essa versão publicada serve como demonstração visual; criar, editar e excluir dependem da API rodando localmente.

## Decisões técnicas

**pwdlib/Argon2 em vez de passlib.** A biblioteca `passlib` depende do módulo `crypt` da stdlib, removido no Python 3.13, e não tem manutenção recente. A troca por `pwdlib` manteve o Argon2 (estado da arte para senhas) e eliminou a dependência problemática.

**PyJWT, não o pacote `jwt`.** O pacote chamado `jwt` no PyPI é outro projeto (python-jwt) e não expõe a API usada aqui. A dependência correta é `PyJWT`, importada como `jwt`. Os dois não devem ser instalados juntos, porque disputam o mesmo nome de módulo.

**`response_model` em todas as rotas.** Sem ele, o FastAPI serializa o objeto do SQLAlchemy inteiro e pode vazar campos internos, como o hash da senha. O schema de resposta é a fronteira que define o que sai da API.

**Isolamento por `usuario_id` na query, com `404`.** O padrão é filtrar por dono na própria consulta (`WHERE id = ? AND usuario_id = ?`) e responder `404` quando não encontra, em vez de `403`. Assim a API não confirma a existência de registros de outra conta.

**`model_dump(exclude_unset=True, exclude_none=True)` no `PUT`.** Sem isso, um campo omitido ou enviado como `null` sobrescreveria dados existentes. A atualização é parcial de verdade: só os campos presentes e não nulos são aplicados.

**`create_all` em vez de Alembic.** Decisão de escopo: é um projeto pessoal e o banco pode ser recriado a qualquer momento. Em um cenário de produção, a evolução do schema seria feita com migrations versionadas.

**Busca local no frontend.** O backend não oferece busca, paginação ou filtros. Em vez de inventar endpoints ou campos, a interface carrega a lista do usuário e filtra em memória. Quando o volume crescer, o próximo passo é mover isso para a API com `skip`/`limit` e parâmetros de busca.

**Frontend em camadas.** O modelo puro (`task-model.js`) não conhece DOM nem HTTP. Isso mantém regras de normalização, payloads e filtros testáveis de forma isolada e deixa a UI substituível.

**CORS liberado apenas para desenvolvimento.** O `allow_origins=["*"]` funciona para rodar o frontend em outra porta local, mas deve ser restringido antes de qualquer deploy.

## Qualidade

Ainda não há suíte de testes versionada no repositório. Durante o desenvolvimento, o backend foi validado com `TestClient` e SQLite em memória, cobrindo:

- requisição sem token e com token inválido → `401`;
- listagem vazia para um usuário novo;
- criação de tarefa com `usuario_id` vindo do token;
- leitura, atualização, cancelamento e exclusão pelo dono;
- tentativa de acessar a tarefa de outro usuário → `404` em todas as operações.

O frontend foi validado com uma suíte temporária em navegador headless, com 20 cenários: login, logout, persistência de sessão, criação, descrição opcional, conclusão, contadores, filtros, busca, edição, exclusão, estado vazio, tema e persistência do tema. Também foram verificados os layouts em 1440×900, 1024×768, 768×1400, 390×1600 e 360×1600.

Verificação de sintaxe dos módulos:

```bash
node --experimental-default-type=module --check docs/js/*.js
```

> **Testes automatizados:** a suíte com `pytest` é o próximo item do roadmap. As verificações acima foram executadas manualmente e não estão commitadas.

## O que falta

Itens conhecidos, em ordem de prioridade:

**Essencial**

- [ ] Suíte de testes com `pytest` + `TestClient` (autenticação, isolamento entre usuários, CRUD e validação)
- [ ] Deploy da API para o frontend publicado funcionar por completo
- [ ] `usuario_id` `NOT NULL`, indexado e com política de cascade ou soft delete

**Qualidade**

- [ ] Tela de perfil no frontend (editar, desativar e excluir a conta)
- [ ] Migrations com Alembic
- [ ] `.env.example` para facilitar o setup de quem clona o projeto
- [ ] Suíte de testes de frontend versionada
- [ ] Paginação e busca no servidor quando a lista crescer
- [ ] `criado_em` / `atualizado_em` nas tabelas (auditoria)
- [ ] Tratamento global de exceções e logging
- [ ] Prefixo de versão `/v1`

**Produção**

- [ ] CORS restrito aos domínios do frontend
- [ ] Rate limiting no login
- [ ] Refresh token e revogação de access token
- [ ] CI no GitHub Actions rodando testes e verificação de sintaxe
- [ ] Dockerfile e docker-compose
- [ ] Deploy com link público

## Status do projeto

Em desenvolvimento. O CRUD de tarefas, a autenticação JWT e o frontend estão funcionais. A API roda localmente com SQLite; ainda não há deploy.
