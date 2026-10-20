/**
 * task-model.js — modelo de domínio puro das tarefas.
 *
 * Não toca no DOM nem faz HTTP. Normaliza o que vem da API, monta os payloads
 * enviados ao backend e concentra as regras de busca, ordenação e estado vazio.
 * É o ponto de extensão para futuros campos sem espalhar detalhes pela UI.
 */

/** Valores de status aceitos pela API. */
export const STATUS = Object.freeze({
  PENDENTE: "pendente",
  CONCLUIDO: "concluido",
  CANCELADO: "cancelado",
});

/** Rótulos acentuados para exibição (o valor enviado à API não muda). */
export const ROTULOS_STATUS = Object.freeze({
  [STATUS.PENDENTE]: "Pendente",
  [STATUS.CONCLUIDO]: "Concluído",
  [STATUS.CANCELADO]: "Cancelado",
});

export const FILTRO_TODAS = "todas";

const PESO_STATUS = {
  [STATUS.PENDENTE]: 0,
  [STATUS.CONCLUIDO]: 1,
  [STATUS.CANCELADO]: 2,
};

const VAZIO_POR_FILTRO = {
  [FILTRO_TODAS]: {
    titulo: "Nenhuma tarefa por aqui",
    texto: "Adicione a primeira tarefa no painel ao lado para começar.",
  },
  [STATUS.PENDENTE]: {
    titulo: "Nada pendente",
    texto: "Tudo o que você tinha para fazer está em dia.",
  },
  [STATUS.CONCLUIDO]: {
    titulo: "Nenhuma tarefa concluída",
    texto: "Marque o círculo de uma tarefa para concluí-la.",
  },
  [STATUS.CANCELADO]: {
    titulo: "Nenhuma tarefa cancelada",
    texto: "Tarefas canceladas ficam guardadas aqui.",
  },
};

/** Normaliza texto para busca: sem acentos, sem caixa alta e sem espaços extras. */
export function normalizarTexto(texto) {
  return String(texto ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

/** Converte uma tarefa da API no formato de domínio usado pela interface. */
export function normalizarTarefa(bruta) {
  if (!bruta || typeof bruta !== "object") return null;

  const id = Number(bruta.id);
  if (!Number.isFinite(id)) return null;

  const status = Object.values(STATUS).includes(bruta.status)
    ? bruta.status
    : STATUS.PENDENTE;

  return {
    id,
    nome: typeof bruta.nome === "string" ? bruta.nome : "",
    descricao: typeof bruta.descricao === "string" ? bruta.descricao : "",
    status,
  };
}

/** Normaliza a lista devolvida pela API, descartando itens inválidos. */
export function normalizarLista(lista) {
  if (!Array.isArray(lista)) return [];
  return lista.map(normalizarTarefa).filter(Boolean);
}

/** Monta o corpo aceito por POST /tarefas/nova_tarefa. */
export function payloadCriacao({ nome, descricao = "" }) {
  return {
    nome: String(nome ?? "").trim(),
    descricao: String(descricao ?? "").trim(),
  };
}

/** Mantém apenas os campos que o PUT aceita, ignorando undefined. */
export function payloadAtualizacao(dados = {}) {
  const payload = {};

  if (typeof dados.nome === "string") payload.nome = dados.nome.trim();
  if (typeof dados.descricao === "string") payload.descricao = dados.descricao.trim();
  if (Object.values(STATUS).includes(dados.status)) payload.status = dados.status;

  return payload;
}

/** Confere se a tarefa corresponde ao termo de busca atual. */
export function correspondeBusca(tarefa, busca) {
  const termo = normalizarTexto(busca);
  if (!termo) return true;

  return normalizarTexto(`${tarefa.nome} ${tarefa.descricao}`).includes(termo);
}

/** Filtra por status e busca, sem alterar a lista original. */
export function filtrarTarefas(tarefas, filtro = FILTRO_TODAS, busca = "") {
  return tarefas.filter((tarefa) => {
    const combinaStatus = filtro === FILTRO_TODAS || tarefa.status === filtro;
    return combinaStatus && correspondeBusca(tarefa, busca);
  });
}

/** Conta todos os status de uma vez para alimentar os contadores da interface. */
export function contarTarefas(tarefas) {
  const contagem = {
    total: tarefas.length,
    [STATUS.PENDENTE]: 0,
    [STATUS.CONCLUIDO]: 0,
    [STATUS.CANCELADO]: 0,
  };

  for (const tarefa of tarefas) {
    if (contagem[tarefa.status] !== undefined) contagem[tarefa.status] += 1;
  }

  return contagem;
}

/** Pendentes primeiro, concluídas depois, canceladas por último; mais novas no topo. */
export function ordenarTarefas(tarefas) {
  return tarefas
    .slice()
    .sort(
      (a, b) =>
        (PESO_STATUS[a.status] - PESO_STATUS[b.status]) || (b.id - a.id)
    );
}

/** Texto do estado vazio, considerando filtro e busca. */
export function textoVazio(filtro, busca = "") {
  if (normalizarTexto(busca)) {
    return {
      titulo: "Nenhuma tarefa encontrada",
      texto: "Tente outro termo ou limpe a busca para ver tudo.",
    };
  }

  return VAZIO_POR_FILTRO[filtro] ?? VAZIO_POR_FILTRO[FILTRO_TODAS];
}
