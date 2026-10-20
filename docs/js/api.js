/**
 * api.js — camada de comunicação com a API.
 *
 * Responsabilidade única: falar HTTP com o backend e devolver dados já
 * tratados (JSON) ou lançar um ApiError com uma mensagem amigável.
 * Nenhum outro módulo chama `fetch` diretamente.
 *
 * Endpoints usados (ver README.md):
 *   POST   /auth/login                      -> token JWT (form-urlencoded)
 *   GET    /auth/me                         -> usuário autenticado
 *   GET    /tarefas/                        -> lista de tarefas
 *   GET    /tarefas/tarefa/{id}             -> uma tarefa
 *   POST   /tarefas/nova_tarefa             -> cria (201)
 *   PUT    /tarefas/atualizar_tarefa/{id}   -> atualiza campos enviados
 *   PATCH  /tarefas/cancelar_tarefa/{id}    -> marca como cancelada
 *   DELETE /tarefas/deletar_tarefa/{id}     -> remove (204)
 */

const API_URL_PADRAO = "http://127.0.0.1:8000";

/** Chave usada para lembrar a URL escolhida no navegador. */
const CHAVE_STORAGE = "gerenciador.apiUrl";

/** Lê a URL base da API, na ordem: global > localStorage > padrão. */
function resolverApiUrl() {
  let url = null;

  if (typeof window !== "undefined" && typeof window.TASK_API_URL === "string") {
    url = window.TASK_API_URL;
  }

  if (!url) {
    try {
      url = localStorage.getItem(CHAVE_STORAGE);
    } catch {
      /* localStorage pode estar bloqueado; seguimos para o padrão */
    }
  }

  return (url || API_URL_PADRAO).replace(/\/+$/, "");
}

export const API_URL = resolverApiUrl();

/** Chave usada para guardar o token JWT no navegador. */
const CHAVE_TOKEN = "gerenciador.token";

/** Lê o token salvo no navegador. */
export function obterToken() {
  try {
    return localStorage.getItem(CHAVE_TOKEN);
  } catch {
    return null;
  }
}

/** Salva o token no navegador; com valor vazio, remove. */
export function definirToken(token) {
  try {
    if (token) localStorage.setItem(CHAVE_TOKEN, token);
    else localStorage.removeItem(CHAVE_TOKEN);
  } catch {
    /* localStorage pode estar bloqueado */
  }
}

/** Remove o token salvo (logout ou sessão expirada). */
export function removerToken() {
  definirToken(null);
}

/**
 * Guarda uma nova URL base no navegador.
 * @param {string} url
 * @returns {string} a URL normalizada (sem barra final)
 */
export function definirApiUrl(url) {
  const limpa = String(url ?? "").trim().replace(/\/+$/, "");
  try {
    localStorage.setItem(CHAVE_STORAGE, limpa);
  } catch {
    /* ignora falha de armazenamento */
  }
  return limpa;
}

/**
 * Erro padronizado da camada de API.
 * `tipo` ajuda a UI a escolher a mensagem: "rede" | "http" | "validacao" | "servidor".
 */
export class ApiError extends Error {
  constructor(mensagem, { status = 0, tipo = "http", detalhes = null } = {}) {
    super(mensagem);
    this.name = "ApiError";
    this.status = status;
    this.tipo = tipo;
    this.detalhes = detalhes;
  }
}

/** Extrai a mensagem de erro do corpo devolvido pelo FastAPI. */
async function lerErro(resposta) {
  try {
    const corpo = await resposta.json();
    const detalhe = corpo?.detail;

    if (typeof detalhe === "string") return detalhe;

    // Erros de validação do Pydantic vêm como lista de objetos.
    if (Array.isArray(detalhe)) {
      return detalhe
        .map((item) => item?.msg ?? String(item))
        .filter(Boolean)
        .join("; ");
    }
  } catch {
    /* corpo vazio ou sem JSON */
  }
  return null;
}

/**
 * Executa uma requisição HTTP e trata resposta e falhas.
 * @param {string} caminho - caminho relativo, ex.: "/tarefas/"
 * @param {{
 *   method?: string,
 *   body?: unknown,
 *   signal?: AbortSignal,
 *   autenticado?: boolean,
 *   formulario?: boolean
 * }} [opcoes]
 */
async function requisitar(
  caminho,
  { method = "GET", body, signal, autenticado = true, formulario = false } = {}
) {
  const url = `${API_URL}${caminho}`;
  const headers = {};

  if (formulario) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  if (autenticado) {
    const token = obterToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  let resposta;

  try {
    resposta = await fetch(url, {
      method,
      headers: Object.keys(headers).length ? headers : undefined,
      body:
        body === undefined
          ? undefined
          : formulario
            ? body.toString()
            : JSON.stringify(body),
      signal,
    });
  } catch (erro) {
    if (erro?.name === "AbortError") throw erro;
    throw new ApiError(
      `Não foi possível falar com a API em ${API_URL}. Verifique se o backend está rodando.`,
      { tipo: "rede" }
    );
  }

  // 204 No Content (DELETE) não tem corpo.
  if (resposta.status === 204) return null;

  if (!resposta.ok) {
    if (resposta.status === 401 && autenticado) {
      removerToken();
      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event("auth:expirado"));
      }
    }

    const mensagem = await lerErro(resposta);
    const tipo =
      resposta.status >= 500 ? "servidor"
      : resposta.status === 422 ? "validacao"
      : "http";

    throw new ApiError(mensagem || `A API respondeu com o status ${resposta.status}.`, {
      status: resposta.status,
      tipo,
    });
  }

  try {
    return await resposta.json();
  } catch {
    return null;
  }
}

export const authApi = {
  login: (email, senha) =>
    requisitar("/auth/login", {
      method: "POST",
      body: new URLSearchParams({ username: email, password: senha }),
      autenticado: false,
      formulario: true,
    }),
  me: (signal) => requisitar("/auth/me", { signal }),
};

export const tarefasApi = {
  listar: (signal) => requisitar("/tarefas/", { signal }),
  buscar: (id, signal) => requisitar(`/tarefas/tarefa/${id}`, { signal }),
  criar: (dados) => requisitar("/tarefas/nova_tarefa", { method: "POST", body: dados }),
  atualizar: (id, dados) =>
    requisitar(`/tarefas/atualizar_tarefa/${id}`, { method: "PUT", body: dados }),
  cancelar: (id) => requisitar(`/tarefas/cancelar_tarefa/${id}`, { method: "PATCH" }),
  excluir: (id) => requisitar(`/tarefas/deletar_tarefa/${id}`, { method: "DELETE" }),
};
