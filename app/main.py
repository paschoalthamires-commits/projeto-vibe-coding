import os
import uuid
import logging
from flask import Flask, request, jsonify, render_template, abort
from dotenv import load_dotenv

load_dotenv()

# Configuração de caminhos para o Render encontrar a pasta templates
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir, static_folder=template_dir)
PORT = int(os.getenv("PORT", 5000))

# Imports dos seus serviços (certifique-se que as pastas existem)
from services.ai_service import gerar_codigo
from utils.code_utils import salvar_codigo

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/executar", methods=["POST"])
def executar():
    data = request.get_json() or {}
    prompt = data.get("prompt", "").strip()
    if len(prompt) < 5:
        return jsonify({"sucesso": False, "erro": "Prompt muito curto."}), 400

    try:
        codigo = gerar_codigo(prompt)
        projeto_id = uuid.uuid4().hex[:10]
        nome_arquivo = salvar_codigo(projeto_id, prompt, codigo)
        return jsonify({"sucesso": True, "codigo": codigo, "arquivo": nome_arquivo})
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
