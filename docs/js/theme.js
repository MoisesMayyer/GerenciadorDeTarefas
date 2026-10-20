/**
 * theme.js — tema claro/escuro, persistência e acessibilidade.
 *
 * O primeiro paint é resolvido por um script inline no <head>. Este módulo
 * sincroniza os botões, alterna o tema e acompanha a preferência do sistema
 * enquanto o usuário ainda não fez uma escolha manual.
 */

const CHAVE_TEMA = "gerenciador.tema";
const TEMAS = ["light", "dark"];
const MEDIA_ESCURO = "(prefers-color-scheme: dark)";

const qsa = (seletor) => Array.from(document.querySelectorAll(seletor));

const media =
  typeof window !== "undefined" && window.matchMedia
    ? window.matchMedia(MEDIA_ESCURO)
    : null;

function temaDoSistema() {
  return media?.matches ? "dark" : "light";
}

function temaSalvo() {
  try {
    const valor = localStorage.getItem(CHAVE_TEMA);
    return TEMAS.includes(valor) ? valor : null;
  } catch {
    return null;
  }
}

function salvarTema(tema) {
  try {
    localStorage.setItem(CHAVE_TEMA, tema);
  } catch {
    /* localStorage pode estar bloqueado */
  }
}

/** Tema aplicado neste momento. */
export function temaAtual() {
  return document.documentElement.dataset.theme === "dark" ? "dark" : "light";
}

function atualizarMetaTema(tema) {
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.content = tema === "dark" ? "#0B1020" : "#F3F6FB";
}

function atualizarBotoes() {
  const escuro = temaAtual() === "dark";

  for (const botao of qsa("[data-theme-toggle]")) {
    const rotulo = escuro ? "Ativar tema claro" : "Ativar tema escuro";
    botao.setAttribute("aria-label", rotulo);
    botao.setAttribute("aria-pressed", String(escuro));
    botao.title = rotulo;
  }
}

function aplicarTema(tema) {
  const alvo = TEMAS.includes(tema) ? tema : temaDoSistema();
  document.documentElement.dataset.theme = alvo;
  atualizarMetaTema(alvo);
  atualizarBotoes();
}

/** Alterna o tema e registra a escolha manual. */
export function alternarTema() {
  const proximo = temaAtual() === "dark" ? "light" : "dark";
  aplicarTema(proximo);
  salvarTema(proximo);
}

/** Inicializa o tema e conecta todos os botões de alternância. */
export function iniciarTema() {
  const salvo = temaSalvo();
  aplicarTema(salvo ?? temaDoSistema());

  for (const botao of qsa("[data-theme-toggle]")) {
    botao.addEventListener("click", alternarTema);
  }

  // Sem escolha manual, acompanha mudanças do sistema operacional.
  media?.addEventListener?.("change", () => {
    if (!temaSalvo()) aplicarTema(temaDoSistema());
  });
}
