"""Testes de /tarefas.

Autenticação
  - 401 sem token, com token inválido e com token de usuário inativo.

POST /tarefas/nova_tarefa
  - 201 com status "pendente" por padrão.
  - usuario_id vem do token e é ignorado se enviado no corpo.
  - 422 sem nome, sem descricao ou com status fora do enum.

GET /tarefas/
  - 200 listando só as tarefas do dono.
  - 200 com lista vazia para usuário sem tarefas.
  - Tarefas com deletado=True NÃO aparecem.

GET /tarefas/tarefa/{id}
  - 200 para o dono.
  - 404 para tarefa de outro usuário.
  - 404 para id inexistente.
  - 404 para tarefa com deletado=True.

PUT /tarefas/atualizar_tarefa/{id}
  - 200 atualização parcial (só o campo enviado muda).
  - Campos null/omitidos não sobrescrevem.
  - 404 para tarefa de outro usuário.
  - 404 para tarefa deletada.
  - 422 com status inválido.

PATCH /tarefas/cancelar_tarefa/{id}
  - 200 e status vira "cancelado".
  - 404 para tarefa de outro usuário.
  - 404 para tarefa já deletada.

DELETE /tarefas/deletar_tarefa/{id}   (soft delete)
  - 204 e o corpo vem vazio.
  - A tarefa some de GET /tarefas/ e GET /tarefas/tarefa/{id} dá 404.
  - PUT, PATCH e um segundo DELETE respondem 404.
  - A linha continua no banco com deletado=True
  - 404 para tarefa de outro usuário (não deleta nada).
"""
