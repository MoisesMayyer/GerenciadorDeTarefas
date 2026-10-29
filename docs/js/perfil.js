/**
 * perfil.js — tela de perfil (modal) da conta autenticada.
 *
 * Responsabilidades: montar o formulário com os dados do usuário, validar com
 * as mesmas regras do backend e delegar o HTTP para `api.js`. A sessão
 * continua em `auth.js`; aqui só avisamos o `main.js` quando ela muda.
 */

import { ApiError, usuariosApi } from "./api.js";
import { salvarUsuario } from "./auth.js";

const qs = (seletor, escopo = document) => escopo.querySelector(seletor);
const qsa = (seletor, escopo = document) =>
  Array.from(escopo.querySelectorAll(seletor));

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const NOME_MAX = 50;
const SENHA_MIN = 6;
const SENHA_MAX = 128;

/**
 * Cria o controlador do modal de perfil.
 * @param {{
 *   aoAtualizar: (usuario: object) => void,
 *   aoEncerrar: (mensagem: string) => void
 * }} deps
 */
export function criarTelaPerfil({ aoAtualizar, aoEncerrar }) {
  const dom = {
    modal: qs("#modal-perfil"),
    form: qs("#form-perfil"),
    nome: qs("#perfil-nome"),
    email: qs("#perfil-email"),
    senha: qs("#perfil-senha"),
    confirmar: qs("#perfil-confirmar"),
    erro: qs("#perfil-erro"),
    salvar: qs("#perfil-salvar"),
    desativar: qs("#perfil-desativar"),
    excluir: qs("#perfil-excluir"),

    modalConta: qs("#modal-conta"),
    contaTitulo: qs("#conta-titulo"),
    contaTexto: qs("#conta-texto"),
    contaConfirmar: qs("#conta-confirmar"),
  };

  const campos = [dom.nome, dom.email, dom.senha, dom.confirmar];

  let usuario = null;
  let acaoPendente = null;

  /* ---------------- Erros dos campos ---------------- */

  function limparErroCampo(campo) {
    campo.removeAttribute("aria-invalid");
    campo.removeAttribute("aria-describedby");
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

  /* ---------------- Validação (espelha o backend) ---------------- */

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

    // A senha é opcional: só é validada quando o campo é preenchido.
    if (senha || dom.confirmar.value) {
      if (!senha.trim()) {
        marcarErro(dom.senha, "Informe a nova senha.");
        valido = false;
      } else if (senha.length < SENHA_MIN) {
        marcarErro(dom.senha, `A senha deve ter pelo menos ${SENHA_MIN} caracteres.`);
        valido = false;
      } else if (senha.length > SENHA_MAX) {
        marcarErro(dom.senha, `A senha deve ter no máximo ${SENHA_MAX} caracteres.`);
        valido = false;
      } else if (dom.confirmar.value !== senha) {
        marcarErro(dom.confirmar, "As senhas não são iguais.");
        valido = false;
      }
    }

    if (!valido) qs('[aria-invalid="true"]', dom.form)?.focus();
    return valido;
  }

  /* ---------------- Editar dados ---------------- */

  async function salvar(evento) {
    evento.preventDefault();
    if (!usuario || !validar()) return;

    const dados = {
      nome: dom.nome.value.trim(),
      email: dom.email.value.trim().toLowerCase(),
    };

    // Envia a senha somente quando o usuário digitou uma nova.
    if (dom.senha.value) dados.senha = dom.senha.value;

    dom.salvar.dataset.rotulo = dom.salvar.textContent;
    dom.salvar.disabled = true;
    dom.salvar.setAttribute("aria-busy", "true");
    dom.salvar.textContent = "Salvando…";
    esconderErroGeral();

    try {
      const atualizado = await usuariosApi.atualizar(usuario.id, dados);
      usuario = atualizado;
      salvarUsuario(atualizado);
      fechar();
      aoAtualizar(atualizado);
    } catch (falha) {
      let mensagem = "Não foi possível salvar. Tente novamente.";

      if (falha instanceof ApiError) {
        if (falha.status === 409) mensagem = "Este e-mail já está cadastrado.";
        else if (falha.status === 422) mensagem = "Confira os dados informados.";
        else mensagem = falha.message;
      }

      mostrarErroGeral(mensagem);
    } finally {
      dom.salvar.disabled = false;
      dom.salvar.removeAttribute("aria-busy");
      dom.salvar.textContent = dom.salvar.dataset.rotulo;
    }
  }

  /* ---------------- Desativar / excluir ---------------- */

  function pedirAcao(tipo) {
    if (!usuario) return;

    acaoPendente = tipo;
    const desativar = tipo === "desativar";

    dom.contaTitulo.textContent = desativar ? "Desativar conta?" : "Excluir conta?";
    dom.contaTexto.textContent = desativar
      ? "Sua conta não poderá mais entrar no sistema. As tarefas continuam salvas."
      : "Esta ação é permanente e apaga também todas as suas tarefas.";
    dom.contaConfirmar.textContent = desativar ? "Desativar" : "Excluir";
    dom.contaConfirmar.dataset.rotulo = dom.contaConfirmar.textContent;
    dom.contaConfirmar.className = "btn btn--danger";

    dom.modalConta.showModal();
    dom.contaConfirmar.focus();
  }

  async function confirmarAcao() {
    const tipo = acaoPendente;
    if (!tipo || !usuario) return;

    dom.contaConfirmar.disabled = true;
    dom.contaConfirmar.setAttribute("aria-busy", "true");
    dom.contaConfirmar.textContent =
      tipo === "desativar" ? "Desativando…" : "Excluindo…";

    try {
      if (tipo === "desativar") await usuariosApi.cancelar(usuario.id);
      else await usuariosApi.excluir(usuario.id);

      dom.modalConta.close();
      fechar();
      aoEncerrar(
        tipo === "desativar"
          ? "Conta desativada. Esta conta não pode mais entrar."
          : "Conta excluída. Até a próxima."
      );
    } catch (falha) {
      dom.modalConta.close();
      mostrarErroGeral(
        falha instanceof ApiError
          ? falha.message
          : "Não foi possível concluir a ação. Tente novamente."
      );
    } finally {
      dom.contaConfirmar.disabled = false;
      dom.contaConfirmar.removeAttribute("aria-busy");
      dom.contaConfirmar.textContent = dom.contaConfirmar.dataset.rotulo;
      acaoPendente = null;
    }
  }

  /* ---------------- Abrir / fechar ---------------- */

  function abrir(dados) {
    if (!dados) return;

    usuario = dados;
    dom.form.reset();
    dom.nome.value = dados.nome ?? "";
    dom.email.value = dados.email ?? "";
    limparErros();

    dom.modal.showModal();
    dom.nome.focus();
  }

  function fechar() {
    if (dom.modal.open) dom.modal.close();
  }

  /* ---------------- Eventos ---------------- */

  dom.form.addEventListener("submit", salvar);
  dom.desativar.addEventListener("click", () => pedirAcao("desativar"));
  dom.excluir.addEventListener("click", () => pedirAcao("excluir"));
  dom.contaConfirmar.addEventListener("click", confirmarAcao);

  for (const campo of campos) {
    campo.addEventListener("input", () => {
      limparErroCampo(campo);
      esconderErroGeral();

      if (campo === dom.senha) limparErroCampo(dom.confirmar);
    });
  }

  for (const botao of qsa("[data-fechar-perfil]")) {
    botao.addEventListener("click", () => botao.closest("dialog")?.close());
  }

  dom.modal.addEventListener("close", () => {
    usuario = null;
    dom.form.reset();
    limparErros();
  });

  dom.modalConta.addEventListener("close", () => {
    acaoPendente = null;
  });

  return { abrir, fechar };
}
