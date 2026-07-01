from uteis import (
    STATUS_NAO_REALIZADA,
    Cores,
    dados_status,
    gerar_id,
    ler_arquivo,
    salvar_arquivo,
)


class Tarefas:
    def __init__(self):
        self.tarefas = ler_arquivo()

    def recarregar(self):
        self.tarefas = ler_arquivo()

    def salvar(self):
        salvar_arquivo(self.tarefas)

    def buscar_por_id(self, identificacao):
        for tarefa in self.tarefas:
            if int(tarefa["id"]) == identificacao:
                return tarefa

        return None

    def criar_tarefa(self, descricao):
        nova_tarefa = {
            "id": gerar_id(self.tarefas),
            "tarefa": descricao,
            "status": STATUS_NAO_REALIZADA,
        }

        self.tarefas.append(nova_tarefa)
        self.salvar()
        return nova_tarefa

    def atualizar_tarefa(self, identificacao, nova_descricao=None, novo_status=None):
        tarefa = self.buscar_por_id(identificacao)

        if tarefa is None:
            return None

        if nova_descricao:
            tarefa["tarefa"] = nova_descricao

        if novo_status:
            tarefa["status"] = novo_status

        self.salvar()
        return tarefa

    def deletar_tarefa(self, identificacao):
        tarefa = self.buscar_por_id(identificacao)

        if tarefa is None:
            return False

        self.tarefas.remove(tarefa)
        self.salvar()
        return True

    def listar_tarefas(self):
        return self.tarefas

    def exibir_tarefas(self):
        if not self.tarefas:
            print("Nenhuma tarefa cadastrada.")
            return

        print("+------+------------------------------+----------------------+")
        print("| ID   | Tarefa                       | Status               |")
        print("+------+------------------------------+----------------------+")

        for tarefa in self.tarefas:
            descricao = tarefa["tarefa"][:28]
            cor_status, status_texto = dados_status(tarefa["status"])
            complemento = " " * max(0, 20 - len(status_texto))
            print(
                f"| {tarefa['id']:<4} | {descricao:<28} | "
                f"{cor_status}{status_texto}{Cores.RESET}{complemento} |"
            )

        print("+------+------------------------------+----------------------+")
