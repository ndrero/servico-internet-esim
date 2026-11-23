import random
import sys

from clientes import ARQUIVO_CLIENTES, STATUS_CLIENTE
from json_handler import json_read, json_write

NOMES = ["Ana", "Bruno", "Carla", "Daniel", "Eduarda", "Felipe", "Gabriela", "Henrique",
         "Isabela", "João", "Larissa", "Lucas", "Mariana", "Mateus", "Natália", "Otávio",
         "Paula", "Rafael", "Sofia", "Thiago", "Vitória", "Yuri", "Beatriz", "Caio",
         "Fernanda", "Gustavo", "Helena", "Igor", "Júlia", "Leonardo", "Maria", "Pedro"]
SOBRENOMES = ["Silva", "Souza", "Oliveira", "Santos", "Lima", "Pereira", "Costa", "Ferreira",
              "Almeida", "Ribeiro", "Carvalho", "Gomes", "Martins", "Rocha", "Barbosa", "Mendes",
              "Araújo", "Cardoso", "Nascimento", "Teixeira", "Moreira", "Rodrigues", "Alves", "Dias"]


def sem_acento(texto):
    trocas = str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc")
    return texto.translate(trocas)


def gerar(quantidade, semente=None):
    random.seed(semente)
    codigos_pacote = [pacote["codigo"] for pacote in json_read("pacotes.json")]
    codigos_pais = list(json_read("paises.json").keys())

    ids = random.sample(range(10000, 100000), quantidade)
    esims = random.sample(range(10000, 100000), quantidade)
    cpfs = random.sample(range(10**10, 10**11), quantidade)

    clientes = []
    for n in range(quantidade):
        nome = random.choice(NOMES) + " " + random.choice(SOBRENOMES)
        usuario = sem_acento(nome.lower()).replace(" ", ".")
        clientes.append({
            "id": ids[n],
            "nome": nome,
            "email": usuario + str(ids[n] % 1000) + "@email.com",
            "esim": "ESIM-" + str(esims[n]),
            "pacote": random.choice(codigos_pacote),
            "status": random.choices(STATUS_CLIENTE, weights=[80, 12, 8])[0],
            "cpf": str(cpfs[n]).zfill(11),
            "telefone": "+55 71 9" + str(random.randint(1000, 9999)) + "-" + str(random.randint(1000, 9999)),
            "pais_origem": random.choice(codigos_pais)
        })

    clientes.sort(key=lambda cliente: cliente["id"])
    json_write(clientes, ARQUIVO_CLIENTES)
    return clientes


if __name__ == "__main__":
    quantidade = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    semente = int(sys.argv[2]) if len(sys.argv) > 2 else None
    gerados = gerar(quantidade, semente)
    print(len(gerados), "clientes gravados em", ARQUIVO_CLIENTES)
