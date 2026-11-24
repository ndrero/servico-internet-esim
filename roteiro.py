from instrumentacao import agora, registrar


def ler_destinos(texto):
    # aceita "BR, PT, FR", "BR PT FR" ou "BR -> PT -> FR"
    texto = texto.upper().replace(",", " ").replace("->", " ").replace("→", " ")
    return texto.split()


def gerar_relatorio(cliente, codigos, paises, pacotes):
    destinos = [] # uma linha do relatório para cada país do roteiro
    regioes_viagem = [] # regiões que a viagem passa, sem repetir
    sem_cobertura = [] # códigos que não estão na tabela hash

    # pacote atual do cliente (busca na Árvore B de pacotes)
    pacote_atual = None
    if cliente.get("pacote"):
        pacote_atual = pacotes.buscar(cliente["pacote"])

    # consulta cada destino na Tabela Hash
    for codigo in codigos:
        inicio = agora()
        pais = paises.get(codigo)
        registrar("busca", inicio)

        if pais is None:
            sem_cobertura.append(codigo)
            destinos.append({"codigo": codigo, "pais": None, "coberto_pacote": False})
            continue

        if pais["regiao"] not in regioes_viagem:
            regioes_viagem.append(pais["regiao"])

        coberto = pacote_atual is not None and pais["regiao"] in pacote_atual["regioes"]
        destinos.append({"codigo": codigo, "pais": pais, "coberto_pacote": coberto})

    # regiões da viagem que o pacote atual não cobre
    regioes_faltando = []
    for regiao in regioes_viagem:
        if pacote_atual is None or regiao not in pacote_atual["regioes"]:
            regioes_faltando.append(regiao)

    # se faltar alguma região, procura o pacote mais barato que cubra todas
    recomendado = None
    if regioes_faltando:
        for pacote in pacotes.listar():
            cobre_tudo = True
            for regiao in regioes_viagem:
                if regiao not in pacote["regioes"]:
                    cobre_tudo = False
                    break
            if cobre_tudo:
                if recomendado is None or pacote["preco"] < recomendado["preco"]:
                    recomendado = pacote

    return {
        "cliente": cliente,
        "destinos": destinos,
        "regioes_viagem": regioes_viagem,
        "sem_cobertura": sem_cobertura,
        "pacote_atual": pacote_atual,
        "regioes_faltando": regioes_faltando,
        "recomendado": recomendado,
    }
