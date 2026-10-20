/**
 * auth.js — sessão do usuário, tela de login e tela de cadastro.
 *
 * Guarda o token e os dados básicos do usuário no localStorage, valida os
 * formulários com as mesmas regras do backend e delega o HTTP para `api.js`.
 */

import {
  ApiError,
  authApi,
  definirToken,
  obterToken,
  removerToken,
  usuariosApi,
} from "./api.js";

const CHAVE_USUARIO = "gerenciador.usuario";
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const NOME_MAX = 50;
const SENHA_MIN = 6;
const SENHA_MAX = 128;

const qs = (seletor, escopo = document) => escopo.querySelector(seletor);

/** Lê o usuário salvo, ignorando conteúdo inválido. */
export function usuarioAtual() {
  try {
    const usuario = JSON.parse(localStorage.getItem(CHAVE_USUARIO));

    if (
      !usuario ||
      typeof usuario.nome !== "string" ||
      typeof usuario.email !== "string"
    ) {
      return null;
    }

    return usuario;
  } catch {
    return null;
  }
}

function salvarUsuario(usuario) {
  try {
    localStorage.setItem(
      CHAVE_USUARIO,
      JSON.stringify({ id: usuario.id, nome: usuario.nome, email: usuario.email })
    );
  } catch {
    /* localStorage pode estar bloqueado */
  }
}

/** Verdadeiro quando há token e usuário salvos. */
export function temSessao() {
  return Boolean(obterToken()) && Boolean(usuarioAtual());
}

/** Encerra a sessão local (o JWT é stateless; não há chamada ao backend). */
export function encerrarSessao() {
  removerToken();
  try {
    localStorage.removeItem(CHAVE_USUARIO);
  } catch {
    /* localStorage pode estar bloqueado */
  }
}

/** Autentica, salva o token e devolve o usuário vindo de /auth/me. */
async function entrar(email, senha) {
  const { access_token } = await authApi.login(email, senha);

  if (!access_token) {
    throw new ApiError("A API não devolveu um token de acesso.");
  }

  definirToken(access_token);

  try {
    const usuario = await authApi.me();
    salvarUsuario(usuario);
    return usuario;
  } catch (falha) {
    removerToken();
    throw falha;
  }
}

/**
 * Cria o controlador da tela de login.
 * @param {{aoEntrar: (usuario: object) => Promise<void> | void}} deps
 */
export function criarTelaLogin({ aoEntrar }) {
  const dom = {
    tela: qs("#tela-login"),
    form: qs("#form-login"),
    email: qs("#login-email"),
    senha: qs("#login-senha"),
    erro: qs("#login-erro"),
    botao: qs("#login-submit"),
  };

  function limparErroCampo(campo) {
    campo.removeAttribute("aria-invalid");
    const aviso = qs(`[data-erro-de="${campo.id}"]`, dom.form);
    if (aviso) {
      aviso.textContent = "";
      aviso.hidden = true;
    }
  }

  function marcarErro(campo, mensagem) {
    campo.setAttribute("aria-invalid", "true");
    const aviso = qs(`[data-erro-de="${campo.id}"]`, dom.form);
    if (aviso) {
      aviso.textContent = mensagem;
      aviso.hidden = false;
    }
  }

  function esconderErroGeral() {
    dom.erro.textContent = "";
    dom.erro.hidden = true;
  }

  function mostrarErroGeral(mensagem) {
    dom.erro.textContent = mensagem;
    dom.erro.hidden = false;
  }

  function limparErros() {
    limparErroCampo(dom.email);
    limparErroCampo(dom.senha);
    esconderErroGeral();
  }

  /** Valida e-mail e senha com as regras aceitas pelo backend. */
  function validar() {
    limparErros();

    const email = dom.email.value.trim();
    const senha = dom.senha.value;
    let valido = true;

    if (!email) {
      marcarErro(dom.email, "Informe seu e-mail.");
      valido = false;
    } else if (!EMAIL_REGEX.test(email)) {
      marcarErro(dom.email, "Informe um e-mail válido.");
      valido = false;
    }

    if (!senha.trim()) {
      marcarErro(dom.senha, "Informe sua senha.");
      valido = false;
    } else if (senha.length < SENHA_MIN) {
      marcarErro(dom.senha, `A senha deve ter pelo menos ${SENHA_MIN} caracteres.`);
      valido = false;
    } else if (senha.length > SENHA_MAX) {
      marcarErro(dom.senha, `A senha deve ter no máximo ${SENHA_MAX} caracteres.`);
      valido = false;
    }

    if (!valido) qs('[aria-invalid="true"]', dom.form)?.focus();
    return valido;
  }

  function definirOcupado(ocupado) {
    dom.botao.disabled = ocupado;
    dom.botao.setAttribute("aria-busy", String(ocupado));
    dom.botao.textContent = ocupado ? "Entrando…" : "Entrar";
  }

  async function enviar(evento) {
    evento.preventDefault();
    if (!validar()) return;

    const email = dom.email.value.trim().toLowerCase();
    const senha = dom.senha.value;

    definirOcupado(true);
    esconderErroGeral();

    try {
      const usuario = await entrar(email, senha);
      esconder();
      await aoEntrar(usuario);
    } catch (falha) {
      dom.tela.hidden = false;

      const mensagem =
        falha instanceof ApiError
          ? falha.status === 401
            ? "E-mail ou senha inválidos."
            : falha.message
          : "Não foi possível entrar. Tente novamente.";

      mostrarErroGeral(mensagem);
      dom.email.focus();
    } finally {
      definirOcupado(false);
    }
  }

  function mostrar(mensagem = "") {
    dom.form.reset();
    limparErros();
    if (mensagem) mostrarErroGeral(mensagem);
    dom.tela.hidden = false;
    dom.email.focus();
  }

  function esconder() {
    dom.tela.hidden = true;
    dom.form.reset();
    limparErros();
  }

  dom.form.addEventListener("submit", enviar);

  for (const campo of [dom.email, dom.senha]) {
    campo.addEventListener("input", () => {
      limparErroCampo(campo);
      esconderErroGeral();
    });
  }

  return { mostrar, esconder };
}

/**
 * Cria o controlador da tela de cadastro.
 * @param {{aoCadastrar: (usuario: object) => Promise<void> | void}} deps
 */
export function criarTelaCadastro({ aoCadastrar }) {
  const dom = {
    tela: qs("#tela-cadastro"),
    form: qs("#form-cadastro"),
    nome: qs("#cadastro-nome"),
    email: qs("#cadastro-email"),
    senha: qs("#cadastro-senha"),
    confirmar: qs("#cadastro-confirmar"),
    erro: qs("#cadastro-erro"),
    botao: qs("#cadastro-submit"),
  };

  const campos = [dom.nome, dom.email, dom.senha, dom.confirmar];

  function limparErroCampo(campo) {
    campo.removeAttribute("aria-invalid");
    const aviso = qs(`[data-erro-de="${campo.id}"]`, dom.form);
    if (aviso) {
      aviso.textContent = "";
      aviso.hidden = true;
    }
  }

  function marcarErro(campo, mensagem) {
    campo.setAttribute("aria-invalid", "true");
    const aviso = qs(`[data-erro-de="${campo.id}"]`, dom.form);
    if (aviso) {
      aviso.textContent = mensagem;
      aviso.hidden = false;
    }
  }

  function esconderErroGeral() {
    dom.erro.textContent = "";
    dom.erro.hidden = true;
  }

  function mostrarErroGeral(mensagem) {
    dom.erro.textContent = mensagem;
    dom.erro.hidden = false;
  }

  function limparErros() {
    for (const campo of campos) limparErroCampo(campo);
    esconderErroGeral();
  }

  /** Valida nome, e-mail e senha com as regras aceitas pelo backend. */
  function validar() {
    limparErros();

    const nome = dom.nome.value.trim();
    const email = dom.email.value.trim();
    const senha = dom.senha.value;
    let valido = true;

    if (!nome) {
      marcarErro(dom.nome, "Informe seu nome.");
      valido = false;
    } else if (nome.length > NOME_MAX) {
      marcarErro(dom.nome, `O nome deve ter no máximo ${NOME_MAX} caracteres.`);
      valido = false;
    }

    if (!email) {
      marcarErro(dom.email, "Informe seu e-mail.");
      valido = false;
    } else if (!EMAIL_REGEX.test(email)) {
      marcarErro(dom.email, "Informe um e-mail válido.");
      valido = false;
    }

    if (!senha.trim()) {
      marcarErro(dom.senha, "Informe uma senha.");
      valido = false;
    } else if (senha.length < SENHA_MIN) {
      marcarErro(dom.senha, `A senha deve ter pelo menos ${SENHA_MIN} caracteres.`);
      valido = false;
    } else if (senha.length > SENHA_MAX) {
      marcarErro(dom.senha, `A senha deve ter no máximo ${SENHA_MAX} caracteres.`);
      valido = false;
    }

    if (!valido) {
      qs('[aria-invalid="true"]', dom.form)?.focus();
      return false;
    }

    if (dom.confirmar.value !== senha) {
      marcarErro(dom.confirmar, "As senhas não são iguais.");
      dom.confirmar.focus();
      return false;
    }

    return true;
  }

  function definirOcupado(ocupado) {
    dom.botao.disabled = ocupado;
    dom.botao.setAttribute("aria-busy", String(ocupado));
    dom.botao.textContent = ocupado ? "Criando…" : "Criar conta";
  }

  async function enviar(evento) {
    evento.preventDefault();
    if (!validar()) return;

    const nome = dom.nome.value.trim();
    const email = dom.email.value.trim().toLowerCase();
    const senha = dom.senha.value;

    definirOcupado(true);
    esconderErroGeral();

    try {
      await usuariosApi.criar({ nome, email, senha });
      const usuario = await entrar(email, senha);
      esconder();
      await aoCadastrar(usuario);
    } catch (falha) {
      dom.tela.hidden = false;

      let mensagem = "Não foi possível criar a conta. Tente novamente.";

      if (falha instanceof ApiError) {
        if (falha.status === 409) mensagem = "Este e-mail já está cadastrado.";
        else if (falha.status === 422) mensagem = "Confira os dados informados.";
        else mensagem = falha.message;
      }

      mostrarErroGeral(mensagem);
      dom.nome.focus();
    } finally {
      definirOcupado(false);
    }
  }

  function mostrar() {
    dom.form.reset();
    limparErros();
    dom.tela.hidden = false;
    dom.nome.focus();
  }

  function esconder() {
    dom.tela.hidden = true;
    dom.form.reset();
    limparErros();
  }

  dom.form.addEventListener("submit", enviar);

  for (const campo of campos) {
    campo.addEventListener("input", () => {
      limparErroCampo(campo);
      esconderErroGeral();

      // Ao corrigir a senha, a confirmação precisa ser verificada de novo.
      if (campo === dom.senha) limparErroCampo(dom.confirmar);
    });
  }

  return { mostrar, esconder };
}
