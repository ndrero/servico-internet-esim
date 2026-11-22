"""
Pacotes de dados da GlobalSIM armazenados em uma Árvore B,
indexados pelo código do pacote (ex.: EUR30).

Funciona do mesmo jeito que o clientes.py: ao iniciar, o JSON é
carregado na árvore e, quando algo muda, a árvore é gravada de volta.
"""
import os

from arvore_b import ArvoreB
from json_handler import json_read, json_write

ARQUIVO_PACOTES = "pacotes.json"
ORDEM_ARVORE = 2


def carregar_pacotes(arquivo=ARQUIVO_PACOTES, ordem=ORDEM_ARVORE):
    arvore = ArvoreB(ordem)
    if not os.path.exists(arquivo):
        return arvore
    for pacote in json_read(arquivo):
        arvore.inserir(pacote["codigo"], pacote)
    return arvore


def salvar_pacotes(arvore, arquivo=ARQUIVO_PACOTES):
    json_write(arvore.listar(), arquivo)
