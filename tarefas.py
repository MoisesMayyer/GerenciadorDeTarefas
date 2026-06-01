import json
import os

from uteis import (
    ler_arquivo,
    apagar_arquivo,
    alterar_status,
    ARQUIVO
)


class Tarefas:
    def __init__(self):
        self.id = None
        self.descricao = None
        self.status = None

    def criar_tarefa(self, identificacao=0, descricao=""):
        self.id = identificacao
        self.descricao = descricao
        self.status = "não realizada"

        lista_de_tarefas = []

        dados_tarefas = {
            "id": int(self.id),
            "tarefa": self.descricao,
            "status": self.status
        }

        if os.path.exists(ARQUIVO):

            with open(ARQUIVO, "r") as file:
                lista_de_tarefas = json.load(file)

        lista_de_tarefas.append(dados_tarefas)

        with open(ARQUIVO, "w") as file:
            json.dump(lista_de_tarefas, file, indent=3)

    @staticmethod
    def atualizar_tarefa():
        lista = ler_arquivo()

        while True:
            try:
                opc_editar = int(
                    input("Digite o ID que deseja alterar (999 para sair): ")
                )

                if opc_editar == 999:
                    break

                encontrou = False

                for tarefa in lista:

                    if int(tarefa["id"]) == opc_editar:
                        encontrou = True

                        print(
                            f"ID: {tarefa['id']} ; {tarefa['tarefa']}"
                        )

                        opc_verificar = input(
                            "Deseja alterar esse? [S/N]: "
                        ).lower().strip()

                        if opc_verificar == "s":

                            tarefa["tarefa"] = input(
                                "Nova tarefa: "
                            )

                            status = input(
                                "Deseja alterar o status dela [S/N]: "
                            ).strip().lower()

                            if status == "s":

                                opc_status = input(
                                    "Pressione [1] para concluída\n"
                                    "Pressione [2] para não realizada\n"
                                    "Pressione [3] para em andamento\n"
                                )

                                alterar_status(
                                    opc_status,
                                    tarefa
                                )

                            with open(ARQUIVO, "w") as file:
                                json.dump(
                                    lista,
                                    file,
                                    indent=3
                                )

                            print(
                                "Tarefa atualizada com sucesso!"
                            )

                if not encontrou:
                    print("ID não encontrado!")

            except ValueError:
                print("Digite apenas números!")

    @staticmethod
    def deletar_tarefa():
        lista = ler_arquivo()

        apagar_arquivo(lista)

    @staticmethod
    def listar_tarefas():

        if os.path.exists(ARQUIVO):

            lista = ler_arquivo()

            for tarefa in lista:
                print(
                    f"ID:({tarefa['id']}) "
                    f"{tarefa['tarefa']} "
                    f"[{tarefa['status']}]"
                )

        else:
            print("-" * 30)
            print("Ainda não possui tarefas")

        print()