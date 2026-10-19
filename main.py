from flask import Flask, render_template, redirect, request
from json_handler import json_read, json_write

app = Flask(__name__)

paises = json_read("paises.json")

@app.route("/")
def home():
    return render_template("cadastro.html")

@app.route("/paises")
def listar_paises():
    return render_template(
        "paises.html",
        paises=paises
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
    
    paises[pais["codigo"]] = pais
    json_write(paises, "paises.json")
    
    return redirect("/paises")

@app.route("/atualizar/<pais_id>", methods = ["GET", "POST"])
def atualizar_pais(pais_id):
    if pais_id not in paises:
        return "País não encontrado", 404

    pais_atual = paises[pais_id]

    if request.method == 'POST':
        pais_atual["codigo"] = request.form["codigo"]
        pais_atual["pais"] = request.form["pais"]
        pais_atual["regiao"] = request.form["regiao"]
        pais_atual["operadora"] = request.form["operadora"]
        pais_atual["tecnologia"] = request.form["tecnologia"]

        json_write(paises, "paises.json")

        return redirect("/paises")
    
    return render_template("atualizar.html", pais=pais_atual)

@app.route("/buscar")
def buscar_pais():
    codigo = request.args.get("codigo", "").strip()
    pais = paises.get(codigo) if codigo else None
    return render_template("buscar.html", codigo=codigo, pais=pais)

@app.route("/buscar/<pais_id>")
def informacoes_por_codigo(pais_id):
    if pais_id in paises:
        return paises[pais_id]
    return "Código não encontrado", 404

@app.route("/deletar/<pais_id>", methods = ["POST"])
def deletar_por_codigo(pais_id):
    if pais_id in paises:
        del paises[pais_id]

        json_write(paises, "paises.json")

        return redirect("/paises")
    
    return "Código não encontrado", 404


if __name__ == "__main__":
    app.run(debug=True)