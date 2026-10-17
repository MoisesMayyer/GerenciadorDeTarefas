/**
 * tasks.js — estado das tarefas e operações.
 *
 * Guarda a lista de tarefas em memória, expõe as operações (criar, atualizar,
 * alternar conclusão, cancelar, excluir) delegando o HTTP para `api.js`, e
 * avisa a interface através de um pequeno sistema de inscrição (observer).
 *
 * Nenhuma regra de negócio do backend é duplicada aqui: a API é a fonte da
 * verdade e, após cada operação, a lista é recarregada.
 */

import { tarefasApi, ApiError } from "./api.js";

/** Valores de status aceitos pela API. */
export const STATUS = Object.freeze({
  PENDENTE: "pendente",
  CONCLUIDO: "concluido",
  CANCELADO: "cancelado",
});

/** Rótulos acentuados para exibição (o valor enviado à API não muda). */
export const ROTULOS_STATUS = Object.freeze({
  pendente: "Pendente",
  concluido: "Concluído",
  cancelado: "Cancelado",
});

export const FILTRO_TODAS = "todas";

const PESO_STATUS = { pendente: 0, concluido: 1, cancelado: 2 };

/** Textos do estado vazio para cada filtro. */
const VAZIO_POR_FILTRO = {
  todas: {
    titulo: "Nada por aqui ainda",
    texto: "Use o botão “Nova tarefa”, na área de criação, para começar.",
  },
  pendente: {
    titulo: "Nenhuma tarefa pendente",
    texto: "Tudo em ordem por aqui.",
  },
  concluido: {
    titulo: "Nenhuma tarefa concluída",
    texto: "Marque o checkbox de uma tarefa para concluí-la.",
  },
  cancelado: {
    titulo: "Nenhuma tarefa cancelada",
    texto: "Tarefas canceladas aparecem aqui.",
  },
};

export function textoVazio(filtro) {
  return VAZIO_POR_FILTRO[filtro] ?? VAZIO_POR_FILTRO[FILTRO_TODAS];
}

/**
 * Cria o gerenciador de tarefas.
 * @param {typeof tarefasApi} [api] permite injetar uma API falsa em testes
 */
export function criarGerenciadorTarefas(api = tarefasApi) {
  /** @type {Array<{id:number,nome:string,descricao:string,status:string}>} */
  let tarefas = [];
  let carregando = false;
  let filtro = FILTRO_TODAS;
  let erro = null;

  const inscritos = new Set();

  function notificar() {
    const snapshot = estado();
    for (const fn of inscritos) fn(snapshot);
  }

  function contagens() {
    const total = tarefas.length;
    let pendente = 0;
    let concluido = 0;
    let cancelado = 0;

    for (const tarefa of tarefas) {
      if (tarefa.status === STATUS.PENDENTE) pendente += 1;
      else if (tarefa.status === STATUS.CONCLUIDO) concluido += 1;
      else if (tarefa.status === STATUS.CANCELADO) cancelado += 1;
    }

    return { total, pendente, concluido, cancelado };
  }

  function visiveis() {
    if (filtro === FILTRO_TODAS) return tarefas.slice();
    return tarefas.filter((tarefa) => tarefa.status === filtro);
  }

  /** Ordena: pendentes primeiro, depois concluídas, canceladas por último; mais novas no topo. */
  function ordenar(lista) {
    return lista
      .slice()
      .sort((a, b) => (PESO_STATUS[a.status] - PESO_STATUS[b.status]) || (b.id - a.id));
  }

  function estado() {
    const contagem = contagens();
    return {
      tarefas,
      visiveis: visiveis(),
      contagem,
      carregando,
      filtro,
      erro,
    };
  }

  /** Recarrega a lista a partir da API. Em falha, guarda o erro e devolve-o. */
  async function carregar(signal) {
    carregando = true;
    erro = null;
    notificar();

    try {
      const lista = await api.listar(signal);
      tarefas = ordenar(Array.isArray(lista) ? lista : []);
    } catch (falha) {
      if (falha?.name === "AbortError") return null;
      erro = falha instanceof ApiError ? falha : new ApiError("Falha ao carregar as tarefas.");
      tarefas = [];
    } finally {
      carregando = false;
      notificar();
    }

    return erro;
  }

  /** Cria uma tarefa. Lança ApiError em falha; devolve o erro de recarga, se houver. */
  async function adicionar({ nome, descricao }) {
    await api.criar({ nome, descricao });
    return carregar();
  }

  async function atualizar(id, dados) {
    await api.atualizar(id, dados);
    return carregar();
  }

  async function alternarConclusao(id) {
    const tarefa = tarefas.find((item) => item.id === id);
    if (!tarefa || tarefa.status === STATUS.CANCELADO) return null;

    const novoStatus = tarefa.status === STATUS.CONCLUIDO ? STATUS.PENDENTE : STATUS.CONCLUIDO;
    return atualizar(id, { status: novoStatus });
  }

  /** Marca a tarefa como cancelada (endpoint PATCH). */
  async function cancelar(id) {
    await api.cancelar(id);
    return carregar();
  }

  async function excluir(id) {
    await api.excluir(id);
    return carregar();
  }

  function definirFiltro(novoFiltro) {
    filtro = novoFiltro;
    notificar();
  }

  return {
    /** Inscreve uma função para receber o estado. Devolve uma função para cancelar. */
    inscrever(fn) {
      inscritos.add(fn);
      fn(estado());
      return () => inscritos.delete(fn);
    },
    estado,
    carregar,
    adicionar,
    atualizar,
    alternarConclusao,
    cancelar,
    excluir,
    definirFiltro,
    buscarPorId: (id) => tarefas.find((item) => item.id === id),
  };
}
