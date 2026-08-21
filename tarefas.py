from uteis import (
    STATUS_NAO_REALIZADA,
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

    def atualizar_tarefa(self, identificacao, nova_descricao=None, novo_status=None,):
        tarefa = self.buscar_por_id(identificacao)

        if tarefa is None:
            return None

        if nova_descricao is not None:
            tarefa["tarefa"] = nova_descricao

        if novo_status is not None:
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