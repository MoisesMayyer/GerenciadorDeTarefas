import json
import os

ARQUIVO = "task.json"

STATUS_CONCLUIDA = "concluída"
STATUS_NAO_REALIZADA = "não realizada"
STATUS_EM_ANDAMENTO = "em andamento"


class Cores:
    RESET = "\033[0m"
    NEGRITO = "\033[1m"
    VERMELHO = "\033[31m"
    VERDE = "\033[32m"
    AMARELO = "\033[33m"
    AZUL = "\033[34m"
    CIANO = "\033[36m"
    CINZA = "\033[90m"


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input(f"\n{Cores.CINZA}Pressione Enter para continuar...{Cores.RESET}")


def cabecalho(titulo):
    largura = 54
    print(f"{Cores.CIANO}{'=' * largura}{Cores.RESET}")
    print(f"{Cores.NEGRITO}{titulo.center(largura)}{Cores.RESET}")
    print(f"{Cores.CIANO}{'=' * largura}{Cores.RESET}")


def mensagem_sucesso(texto):
    print(f"{Cores.VERDE}{texto}{Cores.RESET}")


def mensagem_erro(texto):
    print(f"{Cores.VERMELHO}{texto}{Cores.RESET}")


def mensagem_aviso(texto):
    print(f"{Cores.AMARELO}{texto}{Cores.RESET}")


def ler_arquivo():
    if not os.path.exists(ARQUIVO):
        return []

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as file:
            tarefas = json.load(file)
            return normalizar_tarefas(tarefas)
    except json.JSONDecodeError:
        return []


def salvar_arquivo(lista):
    with open(ARQUIVO, "w", encoding="utf-8") as file:
        json.dump(lista, file, indent=3, ensure_ascii=False)


def gerar_id(lista):
    if not lista:
        return 1

    maior_id = max(int(tarefa["id"]) for tarefa in lista)
    return maior_id + 1


def normalizar_status(status):
    status_antigos = {
        "concluida": STATUS_CONCLUIDA,
        "não realizada": STATUS_NAO_REALIZADA,
        "nao realizada": STATUS_NAO_REALIZADA,
        "em andamento": STATUS_EM_ANDAMENTO,
    }

    return status_antigos.get(status, status)


def normalizar_tarefas(tarefas):
    for tarefa in tarefas:
        tarefa["status"] = normalizar_status(tarefa.get("status", ""))

    return tarefas


def dados_status(status):
    status = normalizar_status(status)
    cores_por_status = {
        STATUS_CONCLUIDA: Cores.VERDE,
        STATUS_NAO_REALIZADA: Cores.VERMELHO,
        STATUS_EM_ANDAMENTO: Cores.AMARELO,
    }
    simbolos_por_status = {
        STATUS_CONCLUIDA: "[x]",
        STATUS_NAO_REALIZADA: "[ ]",
        STATUS_EM_ANDAMENTO: "[...]",
    }

    cor = cores_por_status.get(status, Cores.CINZA)
    simbolo = simbolos_por_status.get(status, "[?]")
    return cor, f"{simbolo} {status}"


def colorir_status(status):
    cor, texto = dados_status(status)
    return f"{cor}{texto}{Cores.RESET}"


def escolher_status():
    print(f"{Cores.AZUL}1{Cores.RESET} - {STATUS_CONCLUIDA}")
    print(f"{Cores.AZUL}2{Cores.RESET} - {STATUS_NAO_REALIZADA}")
    print(f"{Cores.AZUL}3{Cores.RESET} - {STATUS_EM_ANDAMENTO}")

    opcao = input("Escolha o status: ").strip()

    status_por_opcao = {
        "1": STATUS_CONCLUIDA,
        "2": STATUS_NAO_REALIZADA,
        "3": STATUS_EM_ANDAMENTO,
    }

    return status_por_opcao.get(opcao)
