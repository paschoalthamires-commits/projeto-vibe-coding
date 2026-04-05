import os
import uuid
import logging
import time
from functools import wraps
from flask import Flask, request, jsonify, render_template, send_from_directory, abort
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# ==============================
# CONFIGURAÇÕES INICIAIS
# ==============================
load_dotenv()

# No Render, a pasta templates está um nível acima da pasta /app
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, 
            template_folder=template_dir, 
            static_folder=template_dir)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # Aumentado para 5MB
PORT = int(os.getenv("PORT", 5000))

# ==============================
# IMPORTS DOS SEUS SERVIÇOS
# ==============================
try:
    from services.ai_service import gerar_codigo, remodelar_codigo
    from utils.code_utils import salvar_codigo, OUTPUT_DIR
except ImportError as e:
    print(f"Erro de importação: {e}. Verifique as pastas services e utils.")

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VibeCoding")

# ==============================
# RATE LIMIT (CONTROLE DE ABUSO)
# ==============================
rate_limit_store = {}

def require_rate_limit(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        ip = request.remote_addr or "unknown"
        now = time.time()
        if ip not in rate_limit_store:
            rate_limit_store[ip] = []
        
        # Mantém apenas requisições do último minuto
        rate_limit_store[ip] = [t for t in rate_limit_store[ip] if now - t < 60]

        if len(rate_limit_store[ip]) >= 10: # Limite de 10 p/ minuto
            return jsonify({"erro": "Muitas solicitações. Aguarde um minuto."}), 429

        rate_limit_store[ip].append(now)
        return f(*args, **kwargs)
    return wrapper

# ==============================
# ROTAS DO SAAS
# ==============================

@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Erro ao carregar index.html: {e}")
        return "Erro: Arquivo index.html não encontrado na pasta templates.", 404

@app.route("/executar", methods=["POST"])
@require_rate_limit
def executar():
    data = request.get_json() or {}
    prompt = data.get("prompt", "").strip()

    if len(prompt) < 5:
        return jsonify({"erro": "Descreva melhor o site que deseja criar."}), 400

    projeto_id = uuid.uuid4().hex[:10]
    logger.info(f"Gerando projeto: {projeto_id}")

    try:
        codigo = gerar_codigo(prompt)
        if not codigo:
            return jsonify({"erro": "A IA não conseguiu gerar o código. Tente novamente."}), 500
            
        nome_arquivo = salvar_codigo(projeto_id, prompt, codigo)

        return jsonify({
            "sucesso": True,
            "projeto_id": projeto_id,
            "arquivo": nome_arquivo,
            "codigo": codigo
        })
    except Exception as e:
        logger.exception("Erro na rota /executar")
        return jsonify({"erro": "Erro interno ao processar IA."}), 500

@app.route("/download/<filename>")
def download(filename):
    filename = secure_filename(filename)
    path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(path):
        logger.error(f"Arquivo não encontrado para download: {filename}")
        abort(404)

    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

# Rota de Saúde para o Render
@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    # Roda em 0.0.0.0 para o Render conseguir acessar
    app.run(host="0.0.0.0", port=PORT)
