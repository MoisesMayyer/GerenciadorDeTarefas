/**
 * ui.js — renderização e interação com o DOM.
 *
 * Concentra tudo que toca a página: formulário, busca, filtros, lista, modais
 * e feedback. Não faz requisições HTTP; isso continua em `api.js`.
 */

import { API_URL } from "./api.js";
import {
  STATUS,
  ROTULOS_STATUS,
  FILTRO_TODAS,
  textoVazio,
} from "./task-model.js";

const qs = (seletor, escopo = document) => escopo.querySelector(seletor);
const qsa = (seletor, escopo = document) =>
  Array.from(escopo.querySelectorAll(seletor));

/** Formata o id como "#001". */
const formatarId = (id) => `#${String(id).padStart(3, "0")}`;

/** Verdadeiro quando o usuário pediu menos movimento. */
const movimentoReduzido = () =>
  window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;

const esperar = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function el(tag, classe, texto) {
  const node = document.createElement(tag);
  if (classe) node.className = classe;
  if (texto !== undefined) node.textContent = texto;
  return node;
}

/** Cria um elemento com marcação de ícone estática (SVG confiável). */
function elIcone(tag, classe, svg) {
  const node = el(tag, classe);
  node.innerHTML = svg;
  return node;
}

/** Ícones da interface (SVG inline — sem bibliotecas externas). */
const ICONES = Object.freeze({
  check:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
  editar:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>',
  excluir:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>',
});

/**
 * Monta a interface e conecta os eventos.
 * @param {{gerenciador: ReturnType<import("./tasks.js").criarGerenciadorTarefas>}} deps
 */
export function criarInterface({ gerenciador }) {
  /* ---------------- Referências do DOM ---------------- */
  const dom = {
    formNova: qs("#form-nova"),
    novoNome: qs("#novo-nome"),
    novoDescricao: qs("#novo-descricao"),

    feedback: qs("#feedback"),

    filtros: qsa(".chip"),
    lista: qs("#lista"),
    loading: qs("#loading"),
    vazio: qs("#vazio"),
    vazioTitulo: qs("#vazio-titulo"),
    vazioTexto: qs("#vazio-texto"),
    tasksScroll: qs("#tasks-scroll"),

    busca: qs("#busca-tarefas"),
    limparBusca: qs("#limpar-busca"),

    apiStatus: qs("#api-status"),
    apiStatusText: qs("#api-status-text"),

    modalEditar: qs("#modal-editar"),
    formEditar: qs("#form-editar"),
    editarRef: qs("#editar-ref"),
    editarNome: qs("#editar-nome"),
    editarDescricao: qs("#editar-descricao"),
    editarStatus: qs("#editar-status"),

    modalExcluir: qs("#modal-excluir"),
    excluirTexto: qs("#excluir-texto"),
    confirmarExcluir: qs("#confirmar-excluir"),
  };

  /* ---------------- Estado local da interface ---------------- */
  let timeoutFeedback = null;
  let timeoutBusca = null;
  let idEmEdicao = null;
  let tarefaParaExcluir = null;
  let idsRenderizados = new Set();
  let ultimoErro = null;

  /* ---------------- Feedback ---------------- */
  function feedback(mensagem, tipo = "sucesso") {
    clearTimeout(timeoutFeedback);

    dom.feedback.textContent = mensagem;
    dom.feedback.dataset.tipo = tipo;
    dom.feedback.classList.add("is-visible");

    timeoutFeedback = setTimeout(() => {
      dom.feedback.classList.remove("is-visible");
    }, 4000);
  }

  /* ---------------- Validação ---------------- */
  function limparErroCampo(campo, form) {
    campo.removeAttribute("aria-invalid");
    campo.removeAttribute("aria-describedby");
    const aviso = qs(`[data-erro-de="${campo.id}"]`, form);
    if (aviso) {
      aviso.textContent = "";
      aviso.hidden = true;
    }
  }

  function limparErros(form) {
    for (const campo of qsa("input, textarea, select", form)) {
      limparErroCampo(campo, form);
    }
  }

  function marcarErro(campo, mensagem) {
    const form = campo.closest("form");
    campo.setAttribute("aria-invalid", "true");

    const aviso = form ? qs(`[data-erro-de="${campo.id}"]`, form) : null;
    if (aviso) {
      aviso.textContent = mensagem;
      aviso.hidden = false;
      if (aviso.id) campo.setAttribute("aria-describedby", aviso.id);
    }
  }

  /** Valida os campos obrigatórios do formulário. */
  function validar(form) {
    limparErros(form);
    let valido = true;

    for (const campo of qsa("[required]", form)) {
      if (!campo.value.trim()) {
        marcarErro(campo, "Preencha este campo.");
        valido = false;
      }
    }

    if (!valido) qs('[aria-invalid="true"]', form)?.focus();
    return valido;
  }

  /* ---------------- Botões ocupados ---------------- */
  function definirOcupado(botao, ocupado) {
    if (!botao) return;
    botao.disabled = ocupado;
    botao.setAttribute("aria-busy", String(ocupado));
  }

  /**
   * Executa uma operação tratando carregamento, sucesso e erro.
   * @returns {Promise<boolean>} true se deu tudo certo
   */
  async function executar(acao, { sucesso, botao } = {}) {
    definirOcupado(botao, true);
    try {
      const erro = await acao();
      if (erro) {
        feedback(erro.message, "erro");
        return false;
      }
      if (sucesso) feedback(sucesso, "sucesso");
      return true;
    } catch (falha) {
      feedback(falha?.message || "Algo deu errado. Tente de novo.", "erro");
      return false;
    } finally {
      definirOcupado(botao, false);
    }
  }

  /* ---------------- Renderização ---------------- */
  function criarBadgeStatus(status) {
    const badge = el(
      "span",
      "task__status",
      ROTULOS_STATUS[status] ?? status
    );
    badge.dataset.status = status;
    return badge;
  }

  function criarCard(tarefa) {
    const card = el("li", "task");
    card.dataset.status = tarefa.status;
    card.dataset.id = tarefa.id;

    const concluido = tarefa.status === STATUS.CONCLUIDO;
    const cancelado = tarefa.status === STATUS.CANCELADO;

    const check = elIcone("button", "task__check", ICONES.check);
    check.type = "button";
    check.dataset.acao = "alternar";
    check.setAttribute("aria-pressed", String(concluido));
    check.setAttribute(
      "aria-label",
      cancelado
        ? "Tarefa cancelada"
        : concluido
          ? `Reabrir tarefa: ${tarefa.nome}`
          : `Concluir tarefa: ${tarefa.nome}`
    );
    check.title = check.getAttribute("aria-label");
    check.disabled = cancelado;

    const corpo = el("div", "task__body");
    corpo.append(el("p", "task__nome", tarefa.nome));
    if (tarefa.descricao) {
      corpo.append(el("p", "task__descricao", tarefa.descricao));
    }

    const meta = el("div", "task__meta");
    meta.append(criarBadgeStatus(tarefa.status), el("span", "task__id", formatarId(tarefa.id)));
    corpo.append(meta);

    const acoes = el("div", "task__actions");
    acoes.append(
      botaoIcone("editar", ICONES.editar, `Editar tarefa: ${tarefa.nome}`),
      botaoIcone(
        "excluir",
        ICONES.excluir,
        `Excluir tarefa: ${tarefa.nome}`,
        "icon-btn--danger"
      )
    );

    card.append(check, corpo, acoes);

    // Anima apenas os cards novos (evita reanimar a lista inteira).
    if (!idsRenderizados.has(tarefa.id)) {
      card.classList.add("task--entering");
      setTimeout(() => card.classList.remove("task--entering"), 260);
    }

    return card;
  }

  function botaoIcone(acao, svg, rotulo, extra = "") {
    const botao = elIcone("button", `icon-btn ${extra}`.trim(), svg);
    botao.type = "button";
    botao.dataset.acao = acao;
    botao.setAttribute("aria-label", rotulo);
    botao.title = rotulo;
    return botao;
  }

  function render(estado) {
    for (const campo of qsa("[data-contador]")) {
      campo.textContent = estado.contagem[campo.dataset.contador] ?? 0;
    }

    for (const botao of dom.filtros) {
      const ativo = botao.dataset.filtro === estado.filtro;
      botao.classList.toggle("is-active", ativo);
      botao.setAttribute("aria-pressed", String(ativo));
    }

    dom.limparBusca.hidden = !estado.busca;

    dom.loading.hidden = !estado.carregando;
    const semItens = estado.visiveis.length === 0;
    dom.vazio.hidden = estado.carregando || !semItens;
    dom.lista.hidden = estado.carregando || semItens;

    if (!estado.carregando && semItens) {
      const texto = textoVazio(estado.filtro, estado.busca);
      dom.vazioTitulo.textContent = texto.titulo;
      dom.vazioTexto.textContent = texto.texto;
    }

    if (!estado.carregando) {
      dom.lista.replaceChildren(...estado.visiveis.map(criarCard));
      idsRenderizados = new Set(estado.visiveis.map((tarefa) => tarefa.id));
    }

    const offline = estado.erro?.tipo === "rede";
    dom.apiStatusText.textContent = offline ? "Offline" : "Online";
    dom.apiStatus.dataset.online = offline ? "nao" : "sim";
    dom.apiStatus.title = `API: ${API_URL}`;

    if (estado.erro && estado.erro !== ultimoErro) {
      feedback(estado.erro.message, "erro");
      ultimoErro = estado.erro;
    } else if (!estado.erro) {
      ultimoErro = null;
    }
  }

  /* ---------------- Busca e filtros ---------------- */
  function aplicarBusca() {
    clearTimeout(timeoutBusca);
    gerenciador.definirBusca(dom.busca.value);
    dom.tasksScroll.scrollTop = 0;
  }

  function configurarBusca() {
    dom.busca.addEventListener("input", () => {
      dom.limparBusca.hidden = !dom.busca.value;
      clearTimeout(timeoutBusca);
      timeoutBusca = setTimeout(aplicarBusca, 120);
    });

    dom.busca.addEventListener("search", aplicarBusca);

    dom.limparBusca.addEventListener("click", () => {
      dom.busca.value = "";
      dom.limparBusca.hidden = true;
      aplicarBusca();
      dom.busca.focus();
    });
  }

  /* ---------------- Modais ---------------- */
  function abrirEdicao(tarefa) {
    idEmEdicao = tarefa.id;
    dom.editarRef.textContent = formatarId(tarefa.id);
    dom.editarNome.value = tarefa.nome;
    dom.editarDescricao.value = tarefa.descricao ?? "";
    dom.editarStatus.value = tarefa.status;
    limparErros(dom.formEditar);

    dom.modalEditar.showModal();
    dom.editarNome.focus();
  }

  function pedirExclusao(tarefa) {
    tarefaParaExcluir = tarefa;
    dom.excluirTexto.textContent = `"${tarefa.nome}" será removida permanentemente.`;
    dom.modalExcluir.showModal();
  }

  async function confirmarExclusao() {
    const tarefa = tarefaParaExcluir;
    if (!tarefa) return;

    dom.modalExcluir.close();
    tarefaParaExcluir = null;

    await animarSaida(tarefa.id);

    try {
      const erro = await gerenciador.excluir(tarefa.id);
      if (erro) feedback(erro.message, "erro");
      else feedback("Tarefa excluída.", "sucesso");
    } catch (falha) {
      dom.lista
        .querySelector(`[data-id="${tarefa.id}"]`)
        ?.classList.remove("is-leaving");
      feedback(
        falha?.message || "Não foi possível excluir a tarefa.",
        "erro"
      );
    }
  }

  /** Anima a saída do card e resolve quando terminar. */
  async function animarSaida(id) {
    if (movimentoReduzido()) return;
    const card = dom.lista.querySelector(`[data-id="${id}"]`);
    if (!card) return;

    card.classList.add("is-leaving");
    await esperar(200);
  }

  /* ---------------- Eventos ---------------- */

  dom.formNova.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    if (!validar(dom.formNova)) return;

    const nome = dom.novoNome.value.trim();
    const descricao = dom.novoDescricao.value.trim();
    const botao = qs('button[type="submit"]', dom.formNova);

    const ok = await executar(
      () => gerenciador.adicionar({ nome, descricao }),
      { sucesso: "Tarefa criada.", botao }
    );

    if (ok) {
      dom.formNova.reset();
      limparErros(dom.formNova);
      dom.novoNome.focus();
    }
  });

  for (const form of [dom.formNova, dom.formEditar]) {
    for (const campo of qsa("input, textarea, select", form)) {
      campo.addEventListener("input", () => limparErroCampo(campo, form));
    }
  }

  for (const botao of dom.filtros) {
    botao.addEventListener("click", () => {
      gerenciador.definirFiltro(botao.dataset.filtro ?? FILTRO_TODAS);
      dom.tasksScroll.scrollTop = 0;
    });
  }

  configurarBusca();

  // Ações dos cards (delegação de eventos).
  dom.lista.addEventListener("click", (evento) => {
    const botao = evento.target.closest("[data-acao]");
    if (!botao) return;

    const id = Number(botao.closest(".task")?.dataset.id);
    const tarefa = gerenciador.buscarPorId(id);
    if (!tarefa) return;

    switch (botao.dataset.acao) {
      case "alternar": {
        const reabrindo = tarefa.status === STATUS.CONCLUIDO;
        executar(() => gerenciador.alternarConclusao(id), {
          sucesso: reabrindo ? "Tarefa reaberta." : "Tarefa concluída.",
          botao,
        });
        break;
      }
      case "editar":
        abrirEdicao(tarefa);
        break;
      case "excluir":
        pedirExclusao(tarefa);
        break;
    }
  });

  dom.formEditar.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    if (!validar(dom.formEditar) || idEmEdicao === null) return;

    const dados = {
      nome: dom.editarNome.value.trim(),
      descricao: dom.editarDescricao.value.trim(),
      status: dom.editarStatus.value,
    };
    const botao = qs('button[type="submit"]', dom.formEditar);

    const ok = await executar(() => gerenciador.atualizar(idEmEdicao, dados), {
      sucesso: "Tarefa atualizada.",
      botao,
    });

    if (ok) {
      dom.modalEditar.close();
      idEmEdicao = null;
    }
  });

  dom.confirmarExcluir.addEventListener("click", confirmarExclusao);

  for (const botao of qsa("[data-fechar]")) {
    botao.addEventListener("click", () => botao.closest("dialog")?.close());
  }

  dom.modalEditar.addEventListener("close", () => {
    idEmEdicao = null;
  });
  dom.modalExcluir.addEventListener("close", () => {
    tarefaParaExcluir = null;
  });

  /* ---------------- API pública do módulo ---------------- */
  return {
    iniciar() {
      gerenciador.inscrever(render);
    },
    render,
    feedback,
  };
}
