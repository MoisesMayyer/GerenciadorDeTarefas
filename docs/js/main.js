/* main.js — ponto de entrada: tema, sessão, cadastro, interface e carga inicial. */

import { criarGerenciadorTarefas } from "./tasks.js";
import { criarInterface } from "./ui.js";
import {
  criarTelaCadastro,
  criarTelaLogin,
  encerrarSessao,
  temSessao,
  usuarioAtual,
} from "./auth.js";
import { iniciarTema } from "./theme.js";

iniciarTema();

const gerenciador = criarGerenciadorTarefas();
const interfaceApp = criarInterface({ gerenciador });

const dom = {
  app: document.querySelector("#app"),
  saudacao: document.querySelector("#saudacao"),
  usuarioNome: document.querySelector("#usuario-nome"),
  logout: document.querySelector("#logout"),
  linkCriarConta: document.querySelector("#login-criar-conta"),
  voltarLogin: document.querySelector("#cadastro-voltar"),
};

async function entrarNoApp(usuario) {
  exibirApp(usuario);
  await gerenciador.carregar();
}

const login = criarTelaLogin({ aoEntrar: entrarNoApp });
const cadastro = criarTelaCadastro({ aoCadastrar: entrarNoApp });

function primeiroNome(nome) {
  return String(nome ?? "").trim().split(/\s+/)[0] || "";
}

function exibirApp(usuario) {
  login.esconder();
  cadastro.esconder();
  dom.app.hidden = false;

  if (usuario?.nome) {
    const nome = primeiroNome(usuario.nome);
    dom.saudacao.textContent = nome ? `Olá, ${nome}` : "Olá";
    dom.usuarioNome.textContent = nome || usuario.nome;
    dom.usuarioNome.title = usuario.email ?? "";
    dom.usuarioNome.hidden = false;
  }
}

function exibirLogin(mensagem = "") {
  dom.app.hidden = true;
  dom.usuarioNome.hidden = true;
  cadastro.esconder();
  login.mostrar(mensagem);
}

function sair() {
  encerrarSessao();
  window.location.reload();
}

dom.logout.addEventListener("click", sair);

dom.linkCriarConta.addEventListener("click", () => {
  login.esconder();
  cadastro.mostrar();
});

dom.voltarLogin.addEventListener("click", () => {
  cadastro.esconder();
  login.mostrar();
});

window.addEventListener("auth:expirado", () => {
  encerrarSessao();
  exibirLogin("Sua sessão expirou. Entre novamente.");
});

interfaceApp.iniciar();

if (temSessao()) {
  exibirApp(usuarioAtual());
  gerenciador.carregar();
} else {
  exibirLogin();
}
