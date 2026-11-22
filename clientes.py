"""
Clientes da GlobalSIM armazenados em uma Árvore B, indexados pelo id.

Ao iniciar, o arquivo JSON (uma lista de clientes) é carregado na árvore.
Depois de cada alteração, a árvore é gravada de volta no arquivo,
percorrida em ordem, então o JSON fica sempre ordenado por id.

Campos do enunciado: id, nome, email, esim, pacote, status.
Campos extras: cpf, telefone e pais_origem (o país de origem é usado
como ponto de partida das rotas no roteiro de viagem).
"""
import os
import random

from estruturas.arvore_b import ArvoreB
from json_handler import json_read, json_write

ARQUIVO_CLIENTES = "clientes.json"
ORDEM_ARVORE = 2

CAMPOS_CLIENTE = ["id", "nome", "email", "esim", "pacote", "status", "cpf", "telefone", "pais_origem"]
STATUS_CLIENTE = ["ativo", "inativo", "suspenso"]


def carregar_clientes(arquivo=ARQUIVO_CLIENTES, ordem=ORDEM_ARVORE):
    arvore = ArvoreB(ordem)
    if not os.path.exists(arquivo):
        return arvore
    for cliente in json_read(arquivo):
        cliente["id"] = int(cliente["id"])
        arvore.inserir(cliente["id"], cliente)
    return arvore


def salvar_clientes(arvore, arquivo=ARQUIVO_CLIENTES):
    json_write(arvore.listar(), arquivo)


def esims_em_uso(arvore):
    return {cliente["esim"] for cliente in arvore.listar() if cliente.get("esim")}


def novo_esim(em_uso):
    # sorteia um ESIM-XXXXX que ainda não esteja com nenhum cliente
    while True:
        esim = "ESIM-" + str(random.randint(10000, 99999))
        if esim not in em_uso:
            return esim
