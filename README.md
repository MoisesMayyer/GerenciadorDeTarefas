# Gerenciador de Tarefas

API REST para gerenciar tarefas, feita com **FastAPI**, **SQLAlchemy** e
**SQLite**. O front-end (HTML, CSS e JavaScript puro) fica em `docs/` e consome
esta API.

> **Importante:** esta API **não possui deploy**. Ela roda apenas na sua máquina
> (`http://127.0.0.1:8000`). O front-end tem uma versão publicada no GitHub
> Pages, mas, como a API não está hospedada, essa versão publicada serve só como
> demonstração da interface — as operações de criar, editar e excluir dependem da
> API rodando localmente.

## Tecnologias

| Backend | Frontend |
|---|---|
| Python 3 | HTML5 |
| FastAPI | CSS3 |
| SQLAlchemy | JavaScript (módulos ES) |
| Pydantic | Fetch API |
| SQLite | |
| Uvicorn | |

## Como executar localmente

### 1. Clonar o projeto

```bash
git clone https://github.com/MoisesMayyer/GerenciadorDeTarefas.git
cd GerenciadorDeTarefas
```

### 2. Criar e ativar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows
```

### 3. Instalar as dependências

```bash
pip install fastapi uvicorn sqlalchemy
```

### 4. Iniciar a API

A partir da pasta `backend/`:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

- API: `http://127.0.0.1:8000`
- Documentação interativa: `http://127.0.0.1:8000/docs`

O banco SQLite (`backend/database.db`) é criado automaticamente na primeira
execução, junto com a tabela `tarefas`.

## Como testar a API

### Pelo navegador (Swagger UI)

Com a API no ar, abra `http://127.0.0.1:8000/docs`. O FastAPI gera essa
documentação automaticamente e permite disparar cada rota direto pela página,
informando os parâmetros e o corpo da requisição. Existe também a versão ReDoc
em `http://127.0.0.1:8000/redoc`.

### Pela linha de comando (`curl`)

Os exemplos abaixo assumem a API rodando em `http://127.0.0.1:8000`.

## Modelo de dados

Uma tarefa tem o seguinte formato:

```json
{
  "id": 1,
  "nome": "Estudar FastAPI",
  "descricao": "rotas, schemas e dependências",
  "status": "pendente"
}
```

| Campo | Tipo | Observação |
|---|---|---|
| `id` | inteiro | Gerado automaticamente pelo banco |
| `nome` | texto | Obrigatório |
| `descricao` | texto | Obrigatório |
| `status` | texto | `pendente`, `concluido` ou `cancelado` (padrão: `pendente`) |

## Rotas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Verificação simples da API |
| GET | `/tarefas/` | Lista todas as tarefas |
| GET | `/tarefas/tarefa/{id}` | Busca uma tarefa por ID |
| POST | `/tarefas/nova_tarefa` | Cria uma nova tarefa |
| PUT | `/tarefas/atualizar_tarefa/{id}` | Atualiza uma tarefa (parcial) |
| PATCH | `/tarefas/cancelar_tarefa/{id}` | Marca a tarefa como cancelada |
| DELETE | `/tarefas/deletar_tarefa/{id}` | Exclui uma tarefa |

### `GET /` — verificação

Confirma que a API está no ar.

```bash
curl http://127.0.0.1:8000/
```

```json
{ "message": "teste" }
```

### `GET /tarefas/` — listar todas

Retorna um array com todas as tarefas cadastradas.

```bash
curl http://127.0.0.1:8000/tarefas/
```

```json
[
  {
    "id": 1,
    "nome": "Estudar FastAPI",
    "descricao": "rotas, schemas e dependências",
    "status": "pendente"
  }
]
```

### `GET /tarefas/tarefa/{id}` — buscar por ID

Retorna uma única tarefa. Se o `id` não existir, responde **404** com
`{"detail": "tarefa nao encontrada"}`.

```bash
curl http://127.0.0.1:8000/tarefas/tarefa/1
```

### `POST /tarefas/nova_tarefa` — criar

Cria uma tarefa e responde **201** com a tarefa criada (já com o `id`). O campo
`status` é opcional e, se omitido, começa como `pendente`.

Corpo da requisição:

```json
{
  "nome": "Estudar FastAPI",
  "descricao": "rotas, schemas e dependências"
}
```

```bash
curl -X POST http://127.0.0.1:8000/tarefas/nova_tarefa \
  -H "Content-Type: application/json" \
  -d '{"nome": "Estudar FastAPI", "descricao": "rotas, schemas e dependências"}'
```

### `PUT /tarefas/atualizar_tarefa/{id}` — atualizar

Atualiza **parcialmente** uma tarefa: envie apenas os campos que deseja mudar
(`nome`, `descricao` e/ou `status`). Responde **200** com a tarefa atualizada ou
**404** se o `id` não existir.

```bash
curl -X PUT http://127.0.0.1:8000/tarefas/atualizar_tarefa/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "concluido"}'
```

### `PATCH /tarefas/cancelar_tarefa/{id}` — cancelar

Marca a tarefa como `cancelado`, sem precisar enviar corpo. Responde **200** com
a tarefa atualizada ou **404** se o `id` não existir.

```bash
curl -X PATCH http://127.0.0.1:8000/tarefas/cancelar_tarefa/1
```

### `DELETE /tarefas/deletar_tarefa/{id}` — excluir

Remove a tarefa do banco. Responde **204** (sem corpo) ou **404** se o `id` não
existir.

```bash
curl -i -X DELETE http://127.0.0.1:8000/tarefas/deletar_tarefa/1
```

### Códigos de resposta

| Código | Quando acontece |
|---|---|
| `200` | Requisição bem-sucedida (listar, buscar, atualizar, cancelar) |
| `201` | Tarefa criada com sucesso |
| `204` | Tarefa excluída com sucesso (sem corpo) |
| `404` | `id` informado não existe |
| `422` | Dados inválidos (validação do Pydantic) |

## Estrutura do projeto

```
GerenciadorDeTarefas/
├── backend/
│   ├── app/
│   │   ├── database/
│   │   │   ├── database.py      # engine e sessão do SQLAlchemy
│   │   │   └── models.py        # modelo Tarefa + enum StatusTarefa
│   │   ├── routers/
│   │   │   └── tarefas.py       # rotas REST das tarefas
│   │   ├── schemas/
│   │   │   └── tarefas.py       # schemas Pydantic
│   │   ├── depends.py           # dependência de sessão do banco
│   │   └── main.py              # aplicação FastAPI + CORS
│   └── database.db              # banco SQLite (gerado na 1ª execução)
├── docs/                        # frontend (publicado no GitHub Pages)
│   ├── index.html
│   ├── css/style.css
│   ├── js/
│   │   ├── api.js               # comunicação HTTP
│   │   ├── tasks.js             # estado e operações
│   │   ├── ui.js                # renderização e eventos
│   │   └── main.js              # inicialização 
├── README.md
└── .gitignore
```

## Frontend

Para testar a interface junto da API, sirva a pasta `docs/` por HTTP em outro
terminal:

```bash
cd docs
python -m http.server 5500
```

Depois abra `http://127.0.0.1:5500`.

> O frontend usa módulos ES, então precisa ser servido por HTTP — abrir o
> `index.html` direto pelo sistema de arquivos (`file://`) não funciona.

Versão publicada (apenas a interface, sem API no ar):
https://moisesmayyer.github.io/GerenciadorDeTarefas/

## Próximos passos

- Adicionar testes automatizados com Pytest
- Hospedar a API (deploy) para o frontend publicado funcionar por completo
- Implementar autenticação
- Criar `requirements.txt`

## Status do projeto

Em desenvolvimento. O CRUD está funcional: API REST em FastAPI com SQLite e
frontend integrado consumindo a API localmente.
