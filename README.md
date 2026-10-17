# Gerenciador de Tarefas

Aplicação de gerenciamento de tarefas com **API REST em FastAPI** e
**front-end em HTML, CSS e JavaScript puro**, servido como site estático.

O projeto começou como uma aplicação de linha de comando (CLI) e evoluiu para
uma arquitetura com backend e frontend separados.

## Funcionalidades

### Backend
- Criar tarefas
- Listar todas as tarefas
- Buscar tarefa por ID
- Editar tarefas (atualização parcial)
- Cancelar tarefas
- Excluir tarefas
- Persistência em banco SQLite
- API REST com operações CRUD
- Validação de dados com Pydantic
- CORS liberado para o frontend

### Frontend
- Interface moderna com tema escuro e destaque roxo (HTML5, CSS3 e JS puro)
- Duas áreas separadas: **criar** (formulário expansível) e **gerenciar** (lista)
- Listar tarefas com estados de carregamento, lista vazia e mensagens de erro
- Criar, editar, concluir/reabrir e excluir tarefas
- Controles próprios: botão roxo de criação, checkbox personalizado, botão de
  edição com ícone e botão de exclusão em vermelho com confirmação
- Filtro por status (todas / pendentes / concluídas / canceladas) com contadores
- Indicador de conexão com a API e mensagens de sucesso/erro
- Layout responsivo (duas colunas no desktop, empilhado no celular)
- Animações discretas que respeitam `prefers-reduced-motion`

> Detalhes do frontend (módulos, comunicação com a API e configuração da URL)
> estão em [`docs/README.md`](docs/README.md).

## Tecnologias

| Backend | Frontend |
|---|---|
| Python 3 | HTML5 |
| FastAPI | CSS3 |
| SQLAlchemy | JavaScript (módulos ES) |
| Pydantic | Fetch API |
| SQLite | |
| Uvicorn | |

## Arquitetura

```
Frontend (docs/)
HTML + CSS + JavaScript  ──fetch──►  API FastAPI (backend/)
                                          │
                                          ▼
                                     SQLAlchemy
                                          │
                                          ▼
                                    SQLite (backend/database.db)
```

O frontend cuida da interface e das requisições HTTP; o backend cuida das
regras de negócio e da persistência.

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
│   └── database.db              # banco SQLite (gerado)
├── docs/                        # frontend publicado no GitHub Pages
│   ├── index.html
│   ├── css/style.css
│   ├── js/
│   │   ├── api.js               # comunicação HTTP
│   │   ├── tasks.js             # estado e operações
│   │   ├── ui.js                # renderização e eventos
│   │   └── main.js              # inicialização
│   └── README.md
├── README.md
└── .gitignore
```

## API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Verificação simples da API |
| GET | `/tarefas/` | Lista todas as tarefas |
| GET | `/tarefas/tarefa/{id}` | Busca uma tarefa por ID |
| POST | `/tarefas/nova_tarefa` | Cria uma nova tarefa |
| PUT | `/tarefas/atualizar_tarefa/{id}` | Atualiza uma tarefa (parcial) |
| PATCH | `/tarefas/cancelar_tarefa/{id}` | Marca a tarefa como cancelada |
| DELETE | `/tarefas/deletar_tarefa/{id}` | Exclui uma tarefa |

Formato de uma tarefa:

```json
{
  "id": 1,
  "nome": "Estudar FastAPI",
  "descricao": "rotas, schemas e dependências",
  "status": "pendente"
}
```

`status` pode ser `"pendente"`, `"concluido"` ou `"cancelado"`.

A documentação interativa é gerada automaticamente em
`http://127.0.0.1:8000/docs`.

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
- Documentação: `http://127.0.0.1:8000/docs`

O banco SQLite (`backend/database.db`) é criado automaticamente na primeira
execução.

### 5. Servir o frontend

Em outro terminal, a partir da pasta `docs/`:

```bash
cd docs
python -m http.server 5500
```

Depois abra `http://127.0.0.1:5500`. Também funciona a extensão **Live Server**
do VS Code.

> O frontend usa módulos ES, então precisa ser servido por HTTP — abrir o
> `index.html` direto pelo sistema de arquivos (`file://`) não funciona.

## Publicação

O frontend tem uma versão publicada via GitHub Pages:

https://moisesmayyer.github.io/GerenciadorDeTarefas/

Como a API roda apenas localmente, a versão publicada serve como demonstração
da interface; as operações de CRUD dependem da API no ar.

## Próximos passos

- Adicionar testes automatizados com Pytest
- Hospedar a API
- Implementar autenticação
- Criar `requirements.txt`
- Melhorar a documentação da API

## Status do projeto

Em desenvolvimento. O CRUD está funcional: API REST em FastAPI com SQLite e
frontend integrado consumindo a API.
