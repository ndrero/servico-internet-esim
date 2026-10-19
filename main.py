from flask import Flask, render_template, redirect, request
from json_handler import json_read, json_write
from instrumentacao import agora, registrar, estatisticas

app = Flask(__name__)

paises = json_read("paises.json")

@app.route("/")
def home():
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
        total_registros=len(paises)
        )


if __name__ == "__main__":
    app.run(debug=True)