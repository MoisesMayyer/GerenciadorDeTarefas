"""Testes de /auth.

POST /auth/login
  - 200 com access_token e token_type="bearer" usando form-urlencoded
    (não JSON).
  - 401 para senha incorreta.
  - 401 para e-mail inexistente.
  - 401 para usuário com ativo=False.

GET /auth/me
  - 200 devolvendo o usuário do token, sem expor o hash da senha.
  - 401 sem header Authorization.
  - 401 com token de assinatura inválida.
  - 401 com token expirado (montar token com exp no passado).
  - 401 com token sem "sub".
  - 401 com "sub" não numérico.
  - 401 com token de usuário inativo.
"""
