"""
Clientes da GlobalSIM armazenados em uma Árvore B, indexados pelo CPF.

Ao iniciar, o arquivo JSON (uma lista de clientes) é carregado na árvore.
Depois de cada alteração, a árvore é gravada de volta no arquivo,
percorrida em ordem, então o JSON fica sempre ordenado por CPF.
"""
import os

from arvore_b import ArvoreB
from json_handler import json_read, json_write

ARQUIVO_CLIENTES = "clientes.json"
ORDEM_ARVORE = 2

CAMPOS_CLIENTE = ["cpf", "nome", "email", "telefone", "pais_origem", "pacote"]


def carregar_clientes(arquivo=ARQUIVO_CLIENTES, ordem=ORDEM_ARVORE):
    arvore = ArvoreB(ordem)
    if not os.path.exists(arquivo):
        return arvore
    for cliente in json_read(arquivo):
        arvore.inserir(cliente["cpf"], cliente)
    return arvore


def salvar_clientes(arvore, arquivo=ARQUIVO_CLIENTES):
    json_write(arvore.listar(), arquivo)
