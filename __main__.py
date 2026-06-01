from tarefas import Tarefas
from uteis import ler_arquivo, gerar_id


def main():
    tarefa = Tarefas()

    while True:
        print("-" * 30)
        print("MENU DE TAREFAS".center(30))
        print("-" * 30)

        print(
            "[1] Criar tarefa\n"
            "[2] Editar tarefa\n"
            "[3] Apagar tarefa\n"
            "[4] Ver Tarefas\n"
            "[0] Sair"
        )

        print("-" * 30)

        opcao = input("Digite sua opção: ")

        if opcao == "1":

            lista = ler_arquivo()

            id_tarefa = gerar_id(lista)
            descricao = input("DESCRIÇÃO: ")

            tarefa.criar_tarefa(id_tarefa, descricao)
            print("TAREFA ADICIONADA")

        elif opcao == "2":

            tarefa.listar_tarefas()
            tarefa.atualizar_tarefa()

        elif opcao == "3":

            tarefa.listar_tarefas()
            tarefa.deletar_tarefa()

        elif opcao == "4":
            tarefa.listar_tarefas()

        elif opcao == "0":

            print("Saindo...")
            break

        else:
            print("Opção inválida!")


if __name__ == "__main__":
    main()