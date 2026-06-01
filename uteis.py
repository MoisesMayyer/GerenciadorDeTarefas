import json
import os

from random import randint

ARQUIVO = "task.json"


def ler_arquivo():

    if not os.path.exists(ARQUIVO):
        return []

    try:

        with open(ARQUIVO, "r") as file:
            lista = json.load(file)
            return lista

    except json.JSONDecodeError:
        return []


def alterar_status(status, tarefa):

    match status:

        case "1":
            tarefa["status"] = "concluida"

        case "2":
            tarefa["status"] = "não realizada"

        case "3":
            tarefa["status"] = "em andamento"


def apagar_arquivo(lista):

    while True:

        try:

            opc_apagar = int(
                input("Escolha uma ID (999 para sair): ")
            )

            if opc_apagar == 999:
                break

            tarefa_encontrada = None

            for tarefa in lista:

                if int(tarefa["id"]) == opc_apagar:
                    tarefa_encontrada = tarefa
                    break

            if tarefa_encontrada:

                lista.remove(tarefa_encontrada)

                with open(ARQUIVO, "w") as file:
                    json.dump(
                        lista,
                        file,
                        indent=3
                    )

                print(
                    "Tarefa removida com sucesso!"
                )

                break

            else:
                print(
                    "ID inválido, tente novamente!"
                )

        except ValueError:
            print("Digite apenas números!")


def gerar_id(lista):

    while True:

        id_tarefa = randint(1, 998)

        repetido = False

        for tarefa in lista:

            if tarefa["id"] == id_tarefa:
                repetido = True
                break

        if not repetido:
            return id_tarefa