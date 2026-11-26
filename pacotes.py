"""
Pacotes de dados da GlobalSIM: Árvore B como índice + DataFrame como dados.

Funciona como o clientes.py:
- o pacotes.json é carregado num DataFrame; o id de cada pacote é o número
  da linha (0, 1, 2...), como a posição de um registro num arquivo binário;
- a Árvore B tem como chave o código do pacote (ex.: EUR30) e como elemento
  esse id; a busca desce a árvore pelo código e lê a linha no DataFrame.
"""
import os

import pandas as pd

from estruturas.arvore_b import ArvoreB
from json_handler import json_read, json_write

ARQUIVO_PACOTES = "pacotes.json"
ORDEM_ARVORE = 2

CAMPOS_PACOTE = ["codigo", "nome", "regioes", "dados_gb", "validade_dias", "preco"]


class Pacotes:
    def __init__(self, arquivo=ARQUIVO_PACOTES, ordem=ORDEM_ARVORE):
        self.arquivo = arquivo
        self.arvore = ArvoreB(ordem)  # índice: codigo -> id (linha do df)

        registros = json_read(arquivo) if os.path.exists(arquivo) else []
        self.df = pd.DataFrame(registros, columns=CAMPOS_PACOTE)

        for id_pacote, codigo in self.df["codigo"].items():
            self.arvore.inserir(codigo, int(id_pacote))

    def _linha(self, id_pacote):
        pacote = self.df.loc[id_pacote].to_dict()
        pacote["id"] = int(id_pacote)
        return pacote

    def salvar(self):
        # grava na ordem das linhas, então o id (posição) de cada pacote se mantém
        json_write(self.df.to_dict("records"), self.arquivo)

    def buscar(self, codigo):
        id_pacote = self.arvore.buscar(codigo)
        if id_pacote is None:
            return None
        return self._linha(id_pacote)

    def inserir(self, pacote):
        # o pacote novo vai para o fim do DataFrame; o id é a nova posição
        id_pacote = len(self.df)
        self.df.loc[id_pacote] = [pacote.get(campo) for campo in CAMPOS_PACOTE]
        self.arvore.inserir(pacote["codigo"], id_pacote)
        return id_pacote

    def atualizar(self, codigo, pacote):
        id_pacote = self.arvore.buscar(codigo)
        if id_pacote is None:
            return False
        for campo in CAMPOS_PACOTE:
            if campo != "codigo":  # o código é a chave da árvore e não muda
                self.df.at[id_pacote, campo] = pacote.get(campo)
        return True

    def listar(self):
        # percurso em ordem na árvore (ordenado por código) e leitura no df
        return [self._linha(id_pacote) for id_pacote in self.arvore.listar()]

    def tamanho(self):
        return len(self.df)

    def altura(self):
        return self.arvore.altura()

    def resumo(self):
        return self.arvore.resumo()
