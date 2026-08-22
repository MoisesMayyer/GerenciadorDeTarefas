/* =====================================================
   CONFIGURAÇÃO
   ===================================================== */

// Endereço base da sua API FastAPI. Se ela rodar em outra porta/host,
// basta trocar aqui — o resto do código não precisa mudar.
const API_URL = "http://127.0.0.1:8000";

/* =====================================================
   REFERÊNCIAS AOS ELEMENTOS DA PÁGINA
   ===================================================== */

const listaTarefasEl   = document.getElementById("task-list");
const loadingEl        = document.getElementById("loading");
const emptyStateEl     = document.getElementById("empty-state");
const feedbackEl       = document.getElementById("feedback");

const totalCountEl     = document.getElementById("total-count");
const doneCountEl      = document.getElementById("done-count");
const pendingCountEl   = document.getElementById("pending-count");

const formNovaTarefaEl = document.getElementById("form-nova-tarefa");
const inputDescricaoEl = document.getElementById("input-descricao");

const modalOverlayEl   = document.getElementById("modal-overlay");
const formEditarEl     = document.getElementById("form-editar-tarefa");
const editIdEl         = document.getElementById("edit-id");
const editDescricaoEl  = document.getElementById("edit-descricao");
const editStatusEl     = document.getElementById("edit-status");
const modalTaskIdEl    = document.getElementById("modal-task-id");
const btnCancelarEl    = document.getElementById("btn-cancelar-edicao");

let feedbackTimeoutId  = null;

/* =====================================================
   FUNÇÕES DE INTERFACE (loading / feedback / contadores)
   ===================================================== */

// Mostra ou esconde o indicador de "carregando"
function mostrarCarregando(mostrar) {
  loadingEl.hidden = !mostrar;
  if (mostrar) {
    listaTarefasEl.hidden = true;
    emptyStateEl.hidden = true;
  }
}

// Exibe uma mensagem de sucesso ou erro no topo da página por alguns segundos
function mostrarFeedback(mensagem, tipo) {
  // tipo pode ser "success" ou "error"
  clearTimeout(feedbackTimeoutId);

  feedbackEl.textContent = mensagem;
  feedbackEl.className = `feedback feedback--${tipo} is-visible`;

  feedbackTimeoutId = setTimeout(() => {
    feedbackEl.classList.remove("is-visible");
  }, 3500);
}

// Atualiza os três contadores do dashboard com base na lista de tarefas
function atualizarContadores(tarefas) {
  const total = tarefas.length;
  const concluidas = tarefas.filter((t) => t.status === "concluída").length;
  const pendentes = total - concluidas;

  totalCountEl.textContent = total;
  doneCountEl.textContent = concluidas;
  pendingCountEl.textContent = pendentes;
}

/* =====================================================
   RENDERIZAÇÃO DA LISTA DE TAREFAS
   ===================================================== */

// Cria o elemento <li> (card) correspondente a uma tarefa
function criarCardTarefa(tarefa) {
  const li = document.createElement("li");
  li.className = "task-card";
  li.dataset.status = tarefa.status;

  li.innerHTML = `
    <span class="task-card__id">#${String(tarefa.id).padStart(3, "0")}</span>
    <div class="task-card__body">
      <p class="task-card__descricao">${escaparHtml(tarefa.tarefa)}</p>
      <span class="task-card__status">${escaparHtml(tarefa.status)}</span>
    </div>
    <div class="task-card__actions">
      <button class="btn btn--small btn--edit" data-acao="editar">Editar</button>
      <button class="btn btn--small btn--delete" data-acao="excluir">Excluir</button>
    </div>
  `;

  // Conecta os botões desse card às funções de editar/excluir
  li.querySelector('[data-acao="editar"]').addEventListener("click", () => {
    abrirModalEdicao(tarefa);
  });

  li.querySelector('[data-acao="excluir"]').addEventListener("click", () => {
    excluirTarefa(tarefa.id);
  });

  return li;
}

// Evita que uma descrição de tarefa quebre o HTML da página
function escaparHtml(texto) {
  const div = document.createElement("div");
  div.textContent = texto;
  return div.innerHTML;
}

// Desenha a lista inteira de tarefas na tela
function renderizarTarefas(tarefas) {
  listaTarefasEl.innerHTML = "";

  if (tarefas.length === 0) {
    listaTarefasEl.hidden = true;
    emptyStateEl.hidden = false;
  } else {
    emptyStateEl.hidden = true;
    listaTarefasEl.hidden = false;

    tarefas.forEach((tarefa) => {
      listaTarefasEl.appendChild(criarCardTarefa(tarefa));
    });
  }

  atualizarContadores(tarefas);
}

/* =====================================================
   CHAMADAS À API — GET / POST / PUT / DELETE
   ===================================================== */

// Busca todas as tarefas na API e atualiza a tela
async function carregarTarefas() {
  mostrarCarregando(true);

  try {
    const resposta = await fetch(`${API_URL}/tarefas`);

    if (!resposta.ok) {
      throw new Error("Não foi possível carregar as tarefas.");
    }

    const tarefas = await resposta.json();
    renderizarTarefas(tarefas);
  } catch (erro) {
    mostrarFeedback(erro.message, "error");
  } finally {
    mostrarCarregando(false);
  }
}

// Envia uma nova tarefa para a API
async function adicionarTarefa(descricao) {
  try {
    const resposta = await fetch(`${API_URL}/adicionar_tarefa`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ descricao }),
    });

    if (!resposta.ok) {
      throw new Error("Não foi possível adicionar a tarefa.");
    }

    mostrarFeedback("Tarefa adicionada com sucesso!", "success");
    await carregarTarefas();
  } catch (erro) {
    mostrarFeedback(erro.message, "error");
  }
}

// Envia as alterações (descrição/status) de uma tarefa existente
async function atualizarTarefa(id, descricao, status) {
  try {
    const resposta = await fetch(`${API_URL}/atualizar_tarefa/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ descricao, status }),
    });

    if (!resposta.ok) {
      throw new Error("Não foi possível atualizar a tarefa.");
    }

    mostrarFeedback("Tarefa atualizada com sucesso!", "success");
    fecharModalEdicao();
    await carregarTarefas();
  } catch (erro) {
    mostrarFeedback(erro.message, "error");
  }
}

// Remove uma tarefa, pedindo confirmação antes
async function excluirTarefa(id) {
  const confirmou = confirm("Tem certeza que deseja excluir esta tarefa?");
  if (!confirmou) return;

  try {
    const resposta = await fetch(`${API_URL}/deletar_tarefa/${id}`, {
      method: "DELETE",
    });

    if (!resposta.ok) {
      throw new Error("Não foi possível excluir a tarefa.");
    }

    mostrarFeedback("Tarefa excluída com sucesso!", "success");
    await carregarTarefas();
  } catch (erro) {
    mostrarFeedback(erro.message, "error");
  }
}

/* =====================================================
   MODAL DE EDIÇÃO
   ===================================================== */

function abrirModalEdicao(tarefa) {
  editIdEl.value = tarefa.id;
  editDescricaoEl.value = tarefa.tarefa;
  editStatusEl.value = tarefa.status;
  modalTaskIdEl.textContent = `#${String(tarefa.id).padStart(3, "0")}`;

  modalOverlayEl.hidden = false;
  editDescricaoEl.focus();
}

function fecharModalEdicao() {
  modalOverlayEl.hidden = true;
  formEditarEl.reset();
}

/* =====================================================
   EVENTOS
   ===================================================== */

// Envio do formulário de nova tarefa
formNovaTarefaEl.addEventListener("submit", (evento) => {
  evento.preventDefault();

  const descricao = inputDescricaoEl.value.trim();
  if (!descricao) return;

  adicionarTarefa(descricao);
  inputDescricaoEl.value = "";
});

// Envio do formulário de edição (dentro do modal)
formEditarEl.addEventListener("submit", (evento) => {
  evento.preventDefault();

  const id = editIdEl.value;
  const descricao = editDescricaoEl.value.trim();
  const status = editStatusEl.value;

  if (!descricao) return;

  atualizarTarefa(id, descricao, status);
});

// Fecha o modal ao clicar em "Cancelar"
btnCancelarEl.addEventListener("click", fecharModalEdicao);

// Fecha o modal ao clicar fora dele (no fundo escurecido)
modalOverlayEl.addEventListener("click", (evento) => {
  if (evento.target === modalOverlayEl) {
    fecharModalEdicao();
  }
});

// Fecha o modal ao pressionar a tecla Esc
document.addEventListener("keydown", (evento) => {
  if (evento.key === "Escape" && !modalOverlayEl.hidden) {
    fecharModalEdicao();
  }
});

/* =====================================================
   INICIALIZAÇÃO
   ===================================================== */

carregarTarefas();
