from flask import Flask, render_template, redirect, request
from json_handler import json_read, json_write

app = Flask(__name__)

paises = json_read("paises.json")

@app.route("/")
def home():
    return render_template("index.html")

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

    paises[pais["codigo"]] = pais
    json_write(paises, "paises.json")
    
    return redirect("/paises")

@app.route("/atualizar/<pais_id>", methods = ["PUT"])
def atualizar_pais(pais_id):
    dados = request.get_json(silent=True)
    if not dados:
        return {"erro": "Envie um JSON"}, 400

    if pais_id not in paises:
        return {"erro": "País não encontrado"}, 404
    
    pais = {
        "codigo" : dados.get("codigo"),
        "pais" : dados.get("pais"),
        "regiao" : dados.get("regiao"),
        "operadora" : dados.get("operadora"),
        "tecnologia" : dados.get("tecnologia")
    }

    pais_atual = paises[pais_id]
    pais_atual["codigo"] = dados.get("codigo", pais_atual["codigo"]) 
    pais_atual["pais"] = dados.get("pais", pais_atual["pais"]) 
    pais_atual["regiao"] = dados.get("regiao", pais_atual["regiao"]) 
    pais_atual["operadora"] = dados.get("operadora", pais_atual["operadora"]) 
    pais_atual["tecnologia"] = dados.get("tecnologia", pais_atual["tecnologia"]) 

    paises[pais_id] = pais_atual
    json_write(paises, "paises.json")

    return {"message" : "País atualizado com sucesso", 
            "dados": pais_atual
            }, 200

@app.route("/buscar/<pais_id>")
def informacoes_por_codigo(pais_id):
    if pais_id in paises:
        return paises[pais_id]
    return {"erro" : "Código não encontrado"}, 404

@app.route("/deletar/<pais_id>", methods = ["POST"])
def deletar_por_codigo(pais_id):
    if pais_id in paises:
        del paises[pais_id]

        json_write(paises, "paises.json")

        return redirect("/paises")
    
    return {"erro" : "Código não encontrado"}, 404


if __name__ == "__main__":
    app.run(debug=True)