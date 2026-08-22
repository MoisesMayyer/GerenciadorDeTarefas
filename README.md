# Gerenciador de Tarefas
 
Aplicação de gerenciamento de tarefas desenvolvida em Python, com uma API REST utilizando FastAPI e uma interface web desenvolvida em HTML, CSS e JavaScript.
 
O projeto começou como uma aplicação de linha de comando (CLI) e posteriormente evoluiu para uma arquitetura com backend e frontend separados.
 
## Funcionalidades
 
### Backend
 
- Criar tarefas
- Listar todas as tarefas
- Buscar tarefa por ID
- Editar tarefas
- Excluir tarefas
- Alterar status das tarefas
- Persistência dos dados em JSON
- API REST com operações CRUD
- Validação de dados utilizando Pydantic
- CORS configurado para comunicação com o frontend
### Frontend
 
- Dashboard com contadores de tarefas
- Criação de tarefas
- Edição de tarefas
- Exclusão de tarefas
- Alteração de status
- Feedback visual para operações
- Modal para edição
- Indicador de carregamento
- Estado vazio quando não existem tarefas
- Layout responsivo para dispositivos móveis
- Interface publicada utilizando GitHub Pages
## Tecnologias utilizadas
 
### Backend
 
- Python 3
- FastAPI
- Pydantic
- Uvicorn
- JSON
- Programação Orientada a Objetos (POO)
### Frontend
 
- HTML5
- CSS3
- JavaScript
- Fetch API
- GitHub Pages
## Arquitetura
 
O projeto utiliza uma arquitetura simples de frontend e backend separados:
 
```
Frontend
HTML + CSS + JavaScript
        |
        | HTTP / Fetch
        v
FastAPI
        |
        v
Classe Tarefas
        |
        v
task.json
```
 
O frontend é responsável pela interface e pelas requisições HTTP.
 
O backend é responsável pelas regras de negócio e pela persistência das tarefas.
 
## API
 
A API possui os seguintes endpoints:
 
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Página inicial da API |
| GET | `/tarefas` | Lista todas as tarefas |
| GET | `/tarefas/{id}` | Busca uma tarefa por ID |
| POST | `/adicionar_tarefa` | Cria uma nova tarefa |
| PUT | `/atualizar_tarefa/{id}` | Atualiza uma tarefa |
| DELETE | `/deletar_tarefa/{id}` | Exclui uma tarefa |
 
A documentação interativa da API é disponibilizada automaticamente pelo FastAPI em:
 
```
http://127.0.0.1:8000/docs
```
 
## Testes
 
Durante o desenvolvimento, a API foi testada utilizando a documentação interativa do FastAPI e o frontend foi utilizado para validar a comunicação entre cliente e servidor.
 
Os endpoints CRUD foram testados individualmente:
 
- GET para listagem e consulta por ID
- POST para criação
- PUT para atualização
- DELETE para remoção
O projeto também foi utilizado para praticar conceitos de requisições HTTP, códigos de resposta, JSON e integração entre frontend e backend.
 
## Frontend desenvolvido com auxílio de IA
 
A primeira versão do frontend foi desenvolvida com auxílio de Inteligência Artificial.
 
A IA foi utilizada principalmente para:
 
- Estrutura inicial do HTML
- Estilização com CSS
- Criação da interface visual
- Implementação inicial do JavaScript
- Integração do frontend com a API através de fetch
- Criação de componentes de interface como modal, feedbacks e estados de carregamento
O frontend não representa a parte principal do estudo deste projeto. O objetivo foi utilizar uma interface funcional para testar e consumir a API desenvolvida em Python.
 
A integração, configuração da API, endpoints, modelos Pydantic, CORS e lógica do backend foram implementados e ajustados durante o desenvolvimento do projeto.
 
## Objetivo
 
O projeto foi desenvolvido como parte dos estudos de desenvolvimento backend com Python.
 
Os principais conceitos praticados foram:
 
- CRUD
- Programação Orientada a Objetos
- Modularização
- Persistência de dados
- Manipulação de arquivos JSON
- Tratamento de exceções
- APIs REST
- FastAPI
- Pydantic
- Uvicorn
- HTTP
- Métodos GET, POST, PUT e DELETE
- CORS
- Requisições com JavaScript fetch
- Integração entre frontend e backend
- Git e GitHub
- Publicação de frontend com GitHub Pages
## Estrutura do projeto
 
```
GerenciadorDeTarefas/
│
├── docs/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── api.py
├── tarefas.py
├── uteis.py
├── task.json
├── __main__.py
├── README.md
└── .gitignore
```
 
## Como executar localmente
 
### 1. Clonar o projeto
 
```bash
git clone https://github.com/MoisesMayyer/GerenciadorDeTarefas.git
cd GerenciadorDeTarefas
```
 
### 2. Criar e ativar o ambiente virtual
 
**Linux/macOS:**
 
```bash
python3 -m venv .venv
source .venv/bin/activate
```
 
**Windows:**
 
```bash
python -m venv .venv
.venv\Scripts\activate
```
 
### 3. Instalar as dependências
 
```bash
pip install fastapi uvicorn pydantic
```
 
### 4. Iniciar a API
 
```bash
uvicorn api:app --reload
```
 
A API estará disponível em:
 
```
http://127.0.0.1:8000
```
 
A documentação interativa estará disponível em:
 
```
http://127.0.0.1:8000/docs
```
 
### 5. Executar o frontend
 
O frontend pode ser aberto utilizando um servidor HTTP local, como o Live Server.
 
Por exemplo:
 
```
http://127.0.0.1:5500
```
 
Com a API e o frontend executando simultaneamente:
 
```
Frontend
127.0.0.1:5500
        |
        v
FastAPI
127.0.0.1:8000
        |
        v
task.json
```
 
## Publicação
 
O frontend possui uma versão publicada através do GitHub Pages:
 
https://moisesmayyer.github.io/GerenciadorDeTarefas/
 
A versão publicada atualmente funciona como demonstração da interface.
 
A API permanece executando localmente durante o desenvolvimento, portanto as operações de CRUD não ficam disponíveis publicamente através do GitHub Pages.
 
## Próximos passos
 
Algumas melhorias planejadas para versões futuras:
 
- Migrar a persistência de JSON para um banco de dados
- Adicionar testes automatizados com Pytest
- Melhorar a validação dos dados
- Implementar autenticação
- Melhorar a arquitetura do backend
- Criar uma versão completa do frontend sem depender de código gerado por IA
- Hospedar a API
- Adicionar documentação mais detalhada da API
- Criar deploy completo de frontend e backend
## Status do projeto
 
Em desenvolvimento.
 
O projeto atualmente possui um CRUD funcional, API REST com FastAPI e frontend integrado para consumo da API.
