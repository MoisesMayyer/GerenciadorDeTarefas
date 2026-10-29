"""Testes de /usuarios.

POST /usuarios/
  - 201 criando conta e devolvendo id, nome, email, ativo (sem senha).
  - 409 para e-mail já cadastrado.
  - 422 para nome vazio/curto, e-mail inválido, senha < 6 ou > 128.
  - E-mail salvo em minúsculas.

GET /usuarios/
  - 200 devolvendo apenas a própria conta, mesmo com outras no banco.

GET /usuarios/{id}
  - 200 para o próprio id.
  - 404 para id de outra conta.
  - 401 sem token.

PUT /usuarios/{id}
  - 200 atualizando só os campos enviados.
  - 200 ao trocar a senha e o login funcionar com a nova.
  - 409 ao tentar e-mail de outra conta.
  - 404 para id de outra conta.

PATCH /usuarios/{id}/cancelar
  - 200 com ativo=False.
  - Token do usuário deixa de autenticar (401) após o cancelamento.
  - 404 para id de outra conta.

DELETE /usuarios/{id}
  - 204 e o usuário não autentica mais.
  - 404 para id de outra conta.
  - Exclusão em cascata: as tarefas do usuário somem do banco.
"""
