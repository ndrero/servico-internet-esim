"""
Clientes da GlobalSIM: Árvore B como índice + DataFrame como arquivo de dados.

- O clientes.json é carregado num DataFrame do pandas, indexado pelo id do
  cliente. Ele faz o papel do arquivo binário de registros: cada linha é um
  registro e o id é o "endereço" dele.
- A Árvore B é o índice: a chave é o CPF do cliente e o elemento guardado
  é só o id (a linha do DataFrame), não o cliente inteiro.
- Buscar = descer a Árvore B pelo CPF, pegar o id e ler a linha no DataFrame.

Depois de cada alteração o DataFrame é gravado de volta no clientes.json.

Campos do enunciado: id, nome, email, esim, pacote, status.
Campos extras: cpf, telefone e pais_origem (o país de origem é usado
como ponto de partida das rotas no roteiro de viagem).
"""
import os
import random

import pandas as pd

from estruturas.arvore_b import ArvoreB
from json_handler import json_read, json_write

ARQUIVO_CLIENTES = "clientes.json"
ORDEM_ARVORE = 2

CAMPOS_CLIENTE = ["id", "nome", "email", "esim", "pacote", "status", "cpf", "telefone", "pais_origem"]
CAMPOS_DADOS = CAMPOS_CLIENTE[1:]  # colunas do DataFrame (o id é o índice)
STATUS_CLIENTE = ["ativo", "inativo", "suspenso"]


def limpar_cpf(texto):
    # guarda o CPF só com os dígitos, para a comparação na árvore ser exata
    return "".join(c for c in str(texto or "") if c.isdigit())


class Clientes:
    def __init__(self, arquivo=ARQUIVO_CLIENTES, ordem=ORDEM_ARVORE):
        self.arquivo = arquivo
        self.arvore = ArvoreB(ordem)  # índice: cpf -> id

        registros = json_read(arquivo) if os.path.exists(arquivo) else []
        self.df = pd.DataFrame(registros, columns=CAMPOS_CLIENTE)
        self.df["id"] = self.df["id"].astype(int)
        self.df = self.df.set_index("id").fillna("")
        self.df["cpf"] = self.df["cpf"].map(limpar_cpf)

        for id_cliente, cpf in self.df["cpf"].items():
            self.arvore.inserir(cpf, int(id_cliente))

    # ---------------- DataFrame ----------------

    def _linha(self, id_cliente):
        # lê o registro do id no DataFrame e devolve como dict
        cliente = self.df.loc[id_cliente].to_dict()
        cliente["id"] = int(id_cliente)
        return cliente

    def salvar(self):
        json_write(self.df.reset_index().to_dict("records"), self.arquivo)

    def proximo_id(self):
        return int(self.df.index.max()) + 1 if len(self.df) else 1

    # ---------------- Operações (sempre passando pela Árvore B) ----------------

    def buscar(self, cpf):
        id_cliente = self.arvore.buscar(limpar_cpf(cpf))
        if id_cliente is None:
            return None
        return self._linha(id_cliente)

    def inserir(self, cliente):
        # grava a linha nova no DataFrame e põe cpf -> id na árvore
        cliente["cpf"] = limpar_cpf(cliente["cpf"])
        id_cliente = self.proximo_id()
        self.df.loc[id_cliente] = [cliente.get(campo, "") for campo in CAMPOS_DADOS]
        self.arvore.inserir(cliente["cpf"], id_cliente)
        cliente["id"] = id_cliente
        return id_cliente

    def atualizar(self, cpf, cliente):
        # a árvore só diz em que linha está; a alteração é feita no DataFrame
        id_cliente = self.arvore.buscar(limpar_cpf(cpf))
        if id_cliente is None:
            return False
        for campo in CAMPOS_DADOS:
            if campo != "cpf":  # o cpf é a chave da árvore e não muda
                self.df.at[id_cliente, campo] = cliente.get(campo, "")
        return True

    def listar(self):
        # percurso em ordem na árvore (ordenado por cpf) e leitura das linhas no df
        ids = self.arvore.listar()
        tabela = self.df.loc[ids].reset_index()
        return tabela.to_dict("records")

    def esims_em_uso(self):
        return set(self.df["esim"][self.df["esim"] != ""])

    def esim_repetido(self, esim, cpf):
        # um eSIM só pode estar com um cliente
        donos = self.df[self.df["esim"] == esim]
        return (donos["cpf"] != limpar_cpf(cpf)).any()

    # ---------------- Instrumentação (vem da árvore) ----------------

    @property
    def ultima_busca(self):
        return self.arvore.ultima_busca

    def tamanho(self):
        return len(self.df)

    def altura(self):
        return self.arvore.altura()

    def resumo(self):
        return self.arvore.resumo()


def novo_esim(em_uso):
    # sorteia um ESIM-XXXXX que ainda não esteja com nenhum cliente
    while True:
        esim = "ESIM-" + str(random.randint(10000, 99999))
        if esim not in em_uso:
            return esim
