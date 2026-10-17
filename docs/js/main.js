/* main.js — ponto de entrada: cria o gerenciador, monta a interface e carrega. */

import { criarGerenciadorTarefas } from "./tasks.js";
import { criarInterface } from "./ui.js";

const gerenciador = criarGerenciadorTarefas();
const interfaceApp = criarInterface({ gerenciador });

interfaceApp.iniciar();

// Primeira carga: em caso de falha, o próprio render já mostra o estado de erro.
gerenciador.carregar();
