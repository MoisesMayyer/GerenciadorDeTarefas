from tarefas import Tarefas
from uteis import (
    Cores,
    cabecalho,
    escolher_status,
    limpar_tela,
    mensagem_aviso,
    mensagem_erro,
    mensagem_sucesso,
    pausar,
)


def mostrar_menu():
    cabecalho("GERENCIADOR DE TAREFAS")
    print(f"{Cores.AZUL}1{Cores.RESET} - Criar tarefa")
    print(f"{Cores.AZUL}2{Cores.RESET} - Editar tarefa")
    print(f"{Cores.AZUL}3{Cores.RESET} - Apagar tarefa")
    print(f"{Cores.AZUL}4{Cores.RESET} - Ver tarefas")
    print(f"{Cores.AZUL}0{Cores.RESET} - Sair")
    print(f"{Cores.CIANO}{'-' * 54}{Cores.RESET}")


def ler_id(mensagem):
    try:
        return int(input(mensagem).strip())
    except ValueError:
        mensagem_erro("Digite apenas números.")
        return None


def criar_tarefa(gerenciador):
    cabecalho("CRIAR TAREFA")
    descricao = input("Descrição: ").strip()

    if not descricao:
        mensagem_erro("A descrição não pode ficar vazia.")
        return

    tarefa = gerenciador.criar_tarefa(descricao)
    mensagem_sucesso(f"Tarefa #{tarefa['id']} adicionada com sucesso.")


def editar_tarefa(gerenciador):
    cabecalho("EDITAR TAREFA")
    gerenciador.exibir_tarefas()

    if not gerenciador.listar_tarefas():
        return

    identificacao = ler_id("\nID da tarefa que deseja editar: ")

    if identificacao is None:
        return

    tarefa = gerenciador.buscar_por_id(identificacao)

    if tarefa is None:
        mensagem_erro("ID não encontrado.")
        return

    print(f"\nSelecionada: {Cores.NEGRITO}{tarefa['tarefa']}{Cores.RESET}")
    nova_descricao = input("Nova descrição (Enter para manter): ").strip()

    alterar_status = input("Deseja alterar o status? [S/N]: ").strip().lower()
    novo_status = None

    if alterar_status == "s":
        novo_status = escolher_status()

        if novo_status is None:
            mensagem_erro("Status inválido. A tarefa não foi alterada.")
            return

    if not nova_descricao and novo_status is None:
        mensagem_aviso("Nenhuma alteração foi feita.")
        return

    gerenciador.atualizar_tarefa(identificacao, nova_descricao, novo_status)
    mensagem_sucesso("Tarefa atualizada com sucesso.")


def apagar_tarefa(gerenciador):
    cabecalho("APAGAR TAREFA")
    gerenciador.exibir_tarefas()

    if not gerenciador.listar_tarefas():
        return

    identificacao = ler_id("\nID da tarefa que deseja apagar: ")

    if identificacao is None:
        return

    tarefa = gerenciador.buscar_por_id(identificacao)

    if tarefa is None:
        mensagem_erro("ID não encontrado.")
        return

    confirmar = input(
        f"Apagar '{tarefa['tarefa']}'? [S/N]: "
    ).strip().lower()

    if confirmar != "s":
        mensagem_aviso("Operação cancelada.")
        return

    gerenciador.deletar_tarefa(identificacao)
    mensagem_sucesso("Tarefa removida com sucesso.")


def listar_tarefas(gerenciador):
    cabecalho("LISTA DE TAREFAS")
    gerenciador.exibir_tarefas()


def main():
    gerenciador = Tarefas()

    while True:
        limpar_tela()
        mostrar_menu()
        opcao = input("Digite sua opção: ").strip()
        limpar_tela()

        if opcao == "1":
            criar_tarefa(gerenciador)
            pausar()
        elif opcao == "2":
            editar_tarefa(gerenciador)
            pausar()
        elif opcao == "3":
            apagar_tarefa(gerenciador)
            pausar()
        elif opcao == "4":
            listar_tarefas(gerenciador)
            pausar()
        elif opcao == "0":
            mensagem_sucesso("Até logo!")
            break
        else:
            mensagem_erro("Opção inválida.")
            pausar()


if __name__ == "__main__":
    main()
