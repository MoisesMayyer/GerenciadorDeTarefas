/**
 * tasks.js — estado das tarefas e operações.
 *
 * Guarda a lista em memória, aplica filtros e busca, delega o HTTP para
 * `api.js` e avisa a interface por um pequeno observer. Nenhuma regra de
 * negócio do backend é duplicada: a API é a fonte da verdade.
 */

import { tarefasApi, ApiError } from "./api.js";
import {
  STATUS,
  ROTULOS_STATUS,
  FILTRO_TODAS,
  textoVazio,
  normalizarLista,
  normalizarTarefa,
  normalizarTexto,
  filtrarTarefas,
  contarTarefas,
  ordenarTarefas,
  payloadCriacao,
  payloadAtualizacao,
} from "./task-model.js";

export { STATUS, ROTULOS_STATUS, FILTRO_TODAS, textoVazio };

/**
 * Cria o gerenciador de tarefas.
 * @param {typeof tarefasApi} [api] permite injetar uma API falsa em testes
 */
export function criarGerenciadorTarefas(api = tarefasApi) {
  /** @type {Array<{id:number,nome:string,descricao:string,status:string}>} */
  let tarefas = [];
  let carregando = false;
  let filtro = FILTRO_TODAS;
  let busca = "";
  let erro = null;
  let carregamentoAtual = 0;

  const inscritos = new Set();

  function notificar() {
    const snapshot = estado();
    for (const fn of inscritos) fn(snapshot);
  }

  function visiveis() {
    return filtrarTarefas(tarefas, filtro, busca);
  }

  function estado() {
    return {
      tarefas,
      visiveis: visiveis(),
      contagem: contarTarefas(tarefas),
      carregando,
      filtro,
      busca,
      buscaAtiva: Boolean(normalizarTexto(busca)),
      erro,
    };
  }

  /**
   * Aplica no estado local a tarefa devolvida pela API.
   * Evita um GET /tarefas/ extra depois de criar, editar ou cancelar.
   */
  function aplicarTarefa(bruta) {
    const tarefa = normalizarTarefa(bruta);
    if (!tarefa) return false;

    const indice = tarefas.findIndex((item) => item.id === tarefa.id);
    const proxima = tarefas.slice();

    if (indice === -1) proxima.push(tarefa);
    else proxima[indice] = tarefa;

    tarefas = ordenarTarefas(proxima);
    erro = null;
    notificar();
    return true;
  }

  /** Remove a tarefa do estado local depois de um DELETE 204. */
  function removerTarefa(id) {
    const proxima = tarefas.filter((tarefa) => tarefa.id !== id);
    if (proxima.length === tarefas.length) return false;

    tarefas = proxima;
    erro = null;
    notificar();
    return true;
  }

  /** Recarrega a lista a partir da API. Em falha, guarda o erro e devolve-o. */
  async function carregar(signal) {
    const carregamento = ++carregamentoAtual;
    carregando = true;
    erro = null;
    notificar();

    try {
      const lista = await api.listar(signal);
      if (carregamento !== carregamentoAtual) return null;
      tarefas = ordenarTarefas(normalizarLista(lista));
    } catch (falha) {
      if (carregamento !== carregamentoAtual) return null;
      if (falha?.name === "AbortError") return null;
      erro =
        falha instanceof ApiError
          ? falha
          : new ApiError("Falha ao carregar as tarefas.");
      tarefas = [];
    } finally {
      if (carregamento === carregamentoAtual) {
        carregando = false;
        notificar();
      }
    }

    return erro;
  }

  /** Cria uma tarefa. Lança ApiError em falha; devolve o erro de recarga, se houver. */
  async function adicionar({ nome, descricao }) {
    const criada = await api.criar(payloadCriacao({ nome, descricao }));
    if (!aplicarTarefa(criada)) return carregar();
    return null;
  }

  async function atualizar(id, dados) {
    const atualizada = await api.atualizar(id, payloadAtualizacao(dados));
    if (!aplicarTarefa(atualizada)) return carregar();
    return null;
  }

  async function alternarConclusao(id) {
    const tarefa = tarefas.find((item) => item.id === id);
    if (!tarefa || tarefa.status === STATUS.CANCELADO) return null;

    const novoStatus =
      tarefa.status === STATUS.CONCLUIDO ? STATUS.PENDENTE : STATUS.CONCLUIDO;

    return atualizar(id, { status: novoStatus });
  }

  /** Marca a tarefa como cancelada (endpoint PATCH). */
  async function cancelar(id) {
    const cancelada = await api.cancelar(id);
    if (!aplicarTarefa(cancelada)) return carregar();
    return null;
  }

  async function excluir(id) {
    await api.excluir(id);
    removerTarefa(id);
    return null;
  }

  function definirFiltro(novoFiltro) {
    filtro =
      novoFiltro === FILTRO_TODAS || Object.values(STATUS).includes(novoFiltro)
        ? novoFiltro
        : FILTRO_TODAS;
    notificar();
  }

  function definirBusca(texto) {
    busca = String(texto ?? "");
    notificar();
  }

  function limparBusca() {
    definirBusca("");
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
    definirBusca,
    limparBusca,
    buscarPorId: (id) => tarefas.find((item) => item.id === id),
  };
}
