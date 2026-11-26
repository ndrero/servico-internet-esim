from flask import Flask, render_template, redirect, request
from json_handler import json_read, json_write
from instrumentacao import agora, registrar, estatisticas, estatisticas_arvore
from clientes import carregar_clientes, salvar_clientes, esims_em_uso, novo_esim, CAMPOS_CLIENTE, STATUS_CLIENTE
from pacotes import carregar_pacotes, salvar_pacotes
from roteiro import ler_destinos, gerar_relatorio

app = Flask(__name__)

paises = json_read("paises.json")
clientes = carregar_clientes()
pacotes = carregar_pacotes()

@app.route("/")
def home():
    return render_template(
        "inicio.html",
        total_clientes=clientes.tamanho()
        )

@app.route("/cadastro")
def pagina_cadastro():
    return render_template("cadastro.html")

@app.route("/paises")
def listar_paises():
    inicio = agora()
    lista = list(paises.values())
    registrar("listagem", inicio)

    return render_template(
        "paises.html",
        paises=lista
        )

@app.route("/cadastrar", methods = ["POST"])
def cadastrar_pais():

    pais = {
        "codigo" : request.form["codigo"],
        "pais" : request.form["pais"],
        "regiao" : request.form["regiao"],
        "operadora" : request.form["operadora"],
        "tecnologia" : request.form["tecnologia"]
    }

    if pais["codigo"] in paises.keys():
        return "Esse país já foi cadastrado", 400

    inicio = agora()
    paises[pais["codigo"]] = pais
    registrar("insercao", inicio)

    json_write(paises, "paises.json")

    return redirect("/paises")

@app.route("/atualizar/<pais_id>", methods = ["GET", "POST"])
def atualizar_pais(pais_id):
    if pais_id not in paises:
        return "País não encontrado", 404

    pais_atual = paises[pais_id]

    if request.method == 'POST':
        inicio = agora()
        pais_atual["codigo"] = request.form["codigo"]
        pais_atual["pais"] = request.form["pais"]
        pais_atual["regiao"] = request.form["regiao"]
        pais_atual["operadora"] = request.form["operadora"]
        pais_atual["tecnologia"] = request.form["tecnologia"]
        registrar("alteracao", inicio)

        json_write(paises, "paises.json")

        return redirect("/paises")

    return render_template("atualizar.html", pais=pais_atual)

@app.route("/buscar")
def buscar_pais():
    codigo = request.args.get("codigo", "").strip()
    pais = None

    if codigo:
        inicio = agora()
        pais = paises.get(codigo)
        registrar("busca", inicio)

    return render_template("buscar.html", codigo=codigo, pais=pais)

@app.route("/buscar/<pais_id>")
def informacoes_por_codigo(pais_id):
    inicio = agora()
    pais = paises.get(pais_id)
    registrar("busca", inicio)

    if pais:
        return pais
    return "Código não encontrado", 404

@app.route("/deletar/<pais_id>", methods = ["POST"])
def deletar_por_codigo(pais_id):
    if pais_id in paises:
        inicio = agora()
        del paises[pais_id]
        registrar("remocao", inicio)

        json_write(paises, "paises.json")

        return redirect("/paises")

    return "Código não encontrado", 404

@app.route("/estatisticas")
def pagina_estatisticas():
    return render_template(
        "estatisticas.html",
        estatisticas=estatisticas,
        estatisticas_arvore=estatisticas_arvore,
        total_registros=len(paises),
        resumo_clientes=clientes.resumo(),
        resumo_pacotes=pacotes.resumo()
        )


# ---------------- Clientes (Árvore B) ----------------

POR_PAGINA = 50

def ler_id(texto):
    # o id é a chave da árvore e é numérico; devolve None se não for número
    texto = (texto or "").strip()
    return int(texto) if texto.isdigit() else None

def ler_cliente_do_form():
    cliente = {campo: request.form.get(campo, "").strip() for campo in CAMPOS_CLIENTE}
    cliente["esim"] = cliente["esim"].upper()
    if cliente["status"] not in STATUS_CLIENTE:
        cliente["status"] = "ativo"
    return cliente

def esim_repetido(esim, id_cliente):
    # um eSIM só pode estar com um cliente
    for cliente in clientes.listar():
        if cliente.get("esim") == esim and cliente["id"] != id_cliente:
            return True
    return False

@app.route("/clientes")
def pagina_clientes():
    texto_id = request.args.get("id", "").strip()
    pagina = max(ler_id(request.args.get("pagina")) or 1, 1)

    encontrado = None
    busca = None
    if texto_id:
        id_cliente = ler_id(texto_id)
        if id_cliente is not None:
            inicio = agora()
            encontrado = clientes.buscar(id_cliente)
            registrar("busca", inicio, estatisticas_arvore)
            busca = clientes.ultima_busca

    inicio = agora()
    todos = clientes.listar()
    total = len(todos)
    lista = todos[(pagina - 1) * POR_PAGINA : pagina * POR_PAGINA]
    registrar("listagem", inicio, estatisticas_arvore)

    total_paginas = max((total + POR_PAGINA - 1) // POR_PAGINA, 1)
    resumo = clientes.resumo()

    return render_template(
        "clientes.html",
        clientes=lista,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        id_busca=texto_id,
        encontrado=encontrado,
        busca=busca,
        pacotes=pacotes.listar(),
        status_cliente=STATUS_CLIENTE,
        resumo=resumo,
        # o desenho das páginas só é legível com poucos registros
        altura=resumo["altura"]
        )

@app.route("/clientes/cadastrar", methods = ["POST"])
def cadastrar_cliente():
    cliente = ler_cliente_do_form()
    cliente["id"] = ler_id(cliente["id"])

    if cliente["id"] is None or not cliente["nome"]:
        return "Id (numérico) e nome são obrigatórios", 400
    if clientes.buscar(cliente["id"]) is not None:
        return "Já existe um cliente com esse id", 400

    if not cliente["esim"]:
        cliente["esim"] = novo_esim(esims_em_uso(clientes))
    elif esim_repetido(cliente["esim"], cliente["id"]):
        return "Esse eSIM já está associado a outro cliente", 400

    inicio = agora()
    clientes.inserir(cliente["id"], cliente)
    registrar("insercao", inicio, estatisticas_arvore)
    salvar_clientes(clientes)

    return redirect("/clientes?id=" + str(cliente["id"]))

@app.route("/clientes/atualizar/<int:id_cliente>", methods = ["GET", "POST"])
def atualizar_cliente(id_cliente):
    cliente_atual = clientes.buscar(id_cliente)
    if cliente_atual is None:
        return "Cliente não encontrado", 404

    if request.method == "POST":
        cliente = ler_cliente_do_form()
        cliente["id"] = id_cliente  # o id é a chave da árvore e não muda
        if not cliente["nome"]:
            return "O nome é obrigatório", 400
        if not cliente["esim"]:
            cliente["esim"] = novo_esim(esims_em_uso(clientes))
        elif esim_repetido(cliente["esim"], id_cliente):
            return "Esse eSIM já está associado a outro cliente", 400

        inicio = agora()
        clientes.atualizar(id_cliente, cliente)
        registrar("alteracao", inicio, estatisticas_arvore)
        salvar_clientes(clientes)

        return redirect("/clientes?id=" + str(id_cliente))

    return render_template(
        "cliente_atualizar.html",
        cliente=cliente_atual,
        pacotes=pacotes.listar(),
        status_cliente=STATUS_CLIENTE
        )


# ---------------- Consulta integrada: Árvore B x Tabela Hash ----------------

@app.route("/consulta")
def consulta_cliente_destino():
    texto_id = request.args.get("id", "").strip()
    destino = request.args.get("destino", "").strip().upper()
    resultado = None
    erro = None

    if texto_id or destino:
        id_cliente = ler_id(texto_id)
        if id_cliente is None or not destino:
            erro = "Informe o id do cliente (número) e o código do destino."
        else:
            # 1. Árvore B: cliente pelo id
            inicio = agora()
            cliente = clientes.buscar(id_cliente)
            tempo_arvore = agora() - inicio
            registrar("busca", inicio, estatisticas_arvore)
            busca_arvore = dict(clientes.ultima_busca)

            # 2. Tabela Hash: país pelo código
            inicio = agora()
            pais = paises.get(destino)
            tempo_hash = agora() - inicio
            registrar("busca", inicio)

            # pacote do cliente (Árvore B de pacotes)
            pacote = None
            if cliente and cliente.get("pacote"):
                pacote = pacotes.buscar(cliente["pacote"])

            resultado = {
                "cliente": cliente,
                "pais": pais,
                "pacote": pacote,
                "pacote_cobre": bool(pacote and pais and pais["regiao"] in pacote["regioes"]),
                "tempo_arvore": tempo_arvore,
                "tempo_hash": tempo_hash,
                "busca_arvore": busca_arvore,
                "altura": clientes.altura(),
                "total_clientes": clientes.tamanho(),
            }

    return render_template(
        "consulta.html",
        id_busca=texto_id,
        destino=destino,
        resultado=resultado,
        erro=erro,
        paises=sorted(paises.values(), key=lambda pais: pais["pais"])
        )


# ---------------- Pacotes (Árvore B) ----------------

def ler_pacote_do_form():
    regioes = request.form.get("regioes", "").replace(";", ",").split(",")
    return {
        "codigo": request.form.get("codigo", "").strip().upper(),
        "nome": request.form.get("nome", "").strip(),
        "regioes": [regiao.strip() for regiao in regioes if regiao.strip()],
        "dados_gb": int(request.form.get("dados_gb") or 0),
        "validade_dias": int(request.form.get("validade_dias") or 0),
        "preco": float(request.form.get("preco") or 0)
    }

@app.route("/pacotes")
def pagina_pacotes():
    inicio = agora()
    lista = pacotes.listar()
    registrar("listagem", inicio, estatisticas_arvore)

    return render_template(
        "pacotes.html",
        pacotes=lista,
        regioes=sorted({pais["regiao"] for pais in paises.values()}),
        altura=pacotes.altura()
        )

@app.route("/pacotes/cadastrar", methods = ["POST"])
def cadastrar_pacote():
    pacote = ler_pacote_do_form()

    if not pacote["codigo"] or not pacote["nome"]:
        return "Código e nome são obrigatórios", 400
    if pacotes.buscar(pacote["codigo"]) is not None:
        return "Esse pacote já foi cadastrado", 400

    inicio = agora()
    pacotes.inserir(pacote["codigo"], pacote)
    registrar("insercao", inicio, estatisticas_arvore)
    salvar_pacotes(pacotes)

    return redirect("/pacotes")

@app.route("/pacotes/atualizar/<codigo>", methods = ["GET", "POST"])
def atualizar_pacote(codigo):
    pacote_atual = pacotes.buscar(codigo)
    if pacote_atual is None:
        return "Pacote não encontrado", 404

    if request.method == "POST":
        pacote = ler_pacote_do_form()
        pacote["codigo"] = codigo  # o código é a chave da árvore e não muda
        if not pacote["nome"]:
            return "O nome é obrigatório", 400

        inicio = agora()
        pacotes.atualizar(codigo, pacote)
        registrar("alteracao", inicio, estatisticas_arvore)
        salvar_pacotes(pacotes)

        return redirect("/pacotes")

    return render_template("pacote_atualizar.html", pacote=pacote_atual)

@app.route("/roteiro", methods = ["GET", "POST"])
def planejar_viagem():
    texto_id = ""
    texto_destinos = ""
    relatorio = None
    erro = None

    if request.method == "POST":
        texto_id = request.form.get("id", "").strip()
        texto_destinos = request.form.get("destinos", "").strip()
        codigos = ler_destinos(texto_destinos)

        id_cliente = ler_id(texto_id)
        cliente = clientes.buscar(id_cliente) if id_cliente is not None else None
        if cliente is None:
            erro = "Nenhum cliente com id " + texto_id + "."
        elif len(codigos) == 0:
            erro = "Informe pelo menos um destino."
        else:
            relatorio = gerar_relatorio(cliente, codigos, paises, pacotes)

    return render_template(
        "roteiro.html",
        id_cliente=texto_id,
        destinos=texto_destinos,
        relatorio=relatorio,
        erro=erro
        )


if __name__ == "__main__":
    app.run(debug=True)