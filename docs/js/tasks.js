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
  TAMANHO_PAGINA,
  textoVazio,
  normalizarPagina,
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
  let carregandoMais = false;
  let total = 0;
  let temMais = false;
  let filtro = FILTRO_TODAS;
  let busca = "";
  let erro = null;
  let carregamentoAtual = 0;
  // Muda quando criar/excluir altera a lista; invalida uma página em trânsito.
  let versaoLista = 0;

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
      carregandoMais,
      total,
      temMais,
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

    if (indice === -1) {
      proxima.push(tarefa);
      // Uma tarefa nova ocupa a primeira posição da paginação do servidor.
      total += 1;
      versaoLista += 1;
    } else {
      proxima[indice] = tarefa;
    }

    tarefas = ordenarTarefas(proxima);
    temMais = tarefas.length < total;
    erro = null;
    notificar();
    return true;
  }

  /** Remove a tarefa do estado local depois de um DELETE 204. */
  function removerTarefa(id) {
    const proxima = tarefas.filter((tarefa) => tarefa.id !== id);
    if (proxima.length === tarefas.length) return false;

    tarefas = proxima;
    total = Math.max(0, total - 1);
    temMais = tarefas.length < total;
    versaoLista += 1;
    erro = null;
    notificar();
    return true;
  }

  /** Junta uma nova página sem duplicar tarefas já carregadas. */
  function mesclarPagina(novas) {
    const porId = new Map(tarefas.map((tarefa) => [tarefa.id, tarefa]));
    for (const tarefa of novas) porId.set(tarefa.id, tarefa);
    tarefas = ordenarTarefas([...porId.values()]);
  }

  /** Recarrega a primeira página a partir da API. Em falha, guarda o erro e devolve-o. */
  async function carregar(signal) {
    const carregamento = ++carregamentoAtual;
    carregando = true;
    carregandoMais = false;
    erro = null;
    notificar();

    try {
      const pagina = normalizarPagina(
        await api.listar({ skip: 0, limit: TAMANHO_PAGINA, signal }),
        { limit: TAMANHO_PAGINA }
      );
      if (carregamento !== carregamentoAtual) return null;
      tarefas = ordenarTarefas(pagina.tarefas);
      total = pagina.total;
      temMais = pagina.temMais;
    } catch (falha) {
      if (carregamento !== carregamentoAtual) return null;
      if (falha?.name === "AbortError") return null;
      erro =
        falha instanceof ApiError
          ? falha
          : new ApiError("Falha ao carregar as tarefas.");
      tarefas = [];
      total = 0;
      temMais = false;
    } finally {
      if (carregamento === carregamentoAtual) {
        carregando = false;
        notificar();
      }
    }

    return erro;
  }

  /**
   * Carrega a próxima página e anexa ao estado atual.
   * Ignora chamadas enquanto uma carga está em andamento.
   */
  async function carregarMais() {
    if (carregando || carregandoMais || !temMais) return null;

    const carregamento = carregamentoAtual;
    const versao = versaoLista;
    const skip = tarefas.length;
    carregandoMais = true;
    erro = null;
    notificar();

    try {
      const pagina = normalizarPagina(
        await api.listar({ skip, limit: TAMANHO_PAGINA }),
        { skip, limit: TAMANHO_PAGINA }
      );
      if (carregamento !== carregamentoAtual || versao !== versaoLista) return null;

      mesclarPagina(pagina.tarefas);
      total = Math.max(pagina.total, tarefas.length);
      temMais = tarefas.length < total;
    } catch (falha) {
      if (carregamento !== carregamentoAtual) return null;
      if (falha?.name === "AbortError") return null;
      erro =
        falha instanceof ApiError
          ? falha
          : new ApiError("Falha ao carregar mais tarefas.");
    } finally {
      if (carregamento === carregamentoAtual) {
        carregandoMais = false;
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
    carregarMais,
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
