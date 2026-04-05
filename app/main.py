import os
import uuid
import time
import logging
from functools import wraps
from flask import Flask, request, jsonify, render_template, send_from_directory, abort
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# ==============================
# CARREGA VARIÁVEIS DE AMBIENTE
# ==============================
load_dotenv()

PORT = int(os.getenv("PORT", 5000))
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 2 * 1024 * 1024))
RATE_LIMIT_COUNT = int(os.getenv("RATE_LIMIT_COUNT", 5))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))

# ==============================
# IMPORTS INTERNOS
# ==============================
from services.ai_service import gerar_codigo, remodelar_codigo
from utils.code_utils import salvar_codigo, OUTPUT_DIR

# ==============================
# CONFIGURAÇÃO DO FLASK (AJUSTADA PARA O RENDER)
# ==============================
# Descobre o caminho da pasta 'web' que está fora da pasta 'app'
base_dir = os.path.abspath(os.path.dirname(__file__))
web_dir = os.path.join(base_dir, '..', 'web')

app = Flask(__name__, 
            template_folder=web_dir, 
            static_folder=web_dir)

app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# ==============================
# LOGGING AVANÇADO
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("VibeCodingSaaS")

# ==============================
# RATE LIMIT
# ==============================
rate_limit_store = {}

def require_rate_limit(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        ip = request.remote_addr or "unknown"
        now = time.time()
        if ip not in rate_limit_store:
            rate_limit_store[ip] = []

        rate_limit_store[ip] = [t for t in rate_limit_store[ip] if now - t < RATE_LIMIT_WINDOW]

        if len(rate_limit_store[ip]) >= RATE_LIMIT_COUNT:
            logger.warning(f"[{ip}] Rate limit atingido")
            return jsonify({
                "sucesso": False,
                "erro": f"Muitas requisições ({RATE_LIMIT_COUNT} por {RATE_LIMIT_WINDOW} segundos)."
            }), 429

        rate_limit_store[ip].append(now)
        return f(*args, **kwargs)
    return wrapper

# ==============================
# HELPERS
# ==============================
def validar_prompt(prompt: str, min_len: int = 5) -> bool:
    return bool(prompt and len(prompt.strip()) >= min_len)

def gerar_projeto_id() -> str:
    return uuid.uuid4().hex[:10]

# ==============================
# ROTAS PRINCIPAIS
# ==============================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/executar", methods=["POST"])
@require_rate_limit
def executar():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()

    if not validar_prompt(prompt):
        return jsonify({"sucesso": False, "erro": "Prompt inválido ou muito curto."}), 400

    projeto_id = gerar_projeto_id()
    logger.info(f"[{projeto_id}] Nova execução do IP {request.remote_addr}")

    try:
        codigo = gerar_codigo(prompt)
        if not codigo:
            return jsonify({"sucesso": False, "erro": "Falha na geração do código."}), 500

        nome_arquivo = salvar_codigo(projeto_id, prompt, codigo)
        return jsonify({
            "sucesso": True,
            "projeto_id": projeto_id,
            "arquivo": nome_arquivo,
            "codigo": codigo
        })

    except Exception as e:
        logger.exception(f"[{projeto_id}] Erro crítico em /executar")
        return jsonify({"sucesso": False, "erro": "Erro interno do servidor."}), 500

@app.route("/ajustar", methods=["POST"])
@require_rate_limit
def ajustar():
    data = request.get_json(silent=True) or {}
    codigo_atual = data.get("codigo_atual", "").strip()
    instrucao = data.get("ajuste", "").strip()
    projeto_id = data.get("projeto_id", gerar_projeto_id())

    if not codigo_atual or not instrucao:
        return jsonify({"sucesso": False, "erro": "Dados incompletos para ajuste."}), 400

    logger.info(f"[{projeto_id}] Ajuste solicitado pelo IP {request.remote_addr}")

    try:
        novo_codigo = remodelar_codigo(codigo_atual, instrucao)
        if not novo_codigo:
            return jsonify({"sucesso": False, "erro": "Falha ao ajustar código."}), 500

        nome_arquivo = salvar_codigo(projeto_id, instrucao, novo_codigo)
        return jsonify({
            "sucesso": True,
            "projeto_id": projeto_id,
            "arquivo": nome_arquivo,
            "codigo": novo_codigo
        })

    except Exception as e:
        logger.exception(f"[{projeto_id}] Erro crítico em /ajustar")
        return jsonify({"sucesso": False, "erro": "Erro interno do servidor."}), 500

@app.route("/download/<filename>")
def download_file(filename):
    filename = secure_filename(filename)
    caminho = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(caminho):
        abort(404)
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

# ==============================
# MONITORAMENTO
# ==============================
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/listar_projetos")
def listar_projetos():
    try:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            
        projetos = [
            {"arquivo": f, "modificado": os.path.getmtime(os.path.join(OUTPUT_DIR, f))}
            for f in os.listdir(OUTPUT_DIR)
            if os.path.isfile(os.path.join(OUTPUT_DIR, f))
        ]
        projetos.sort(key=lambda x: x["modificado"], reverse=True)
        return jsonify(projetos)
    except Exception:
        logger.exception("Erro ao listar projetos")
        return jsonify({"sucesso": False, "erro": "Falha ao listar projetos"}), 500

# ==============================
# INICIALIZAÇÃO
# ==============================
if __name__ == "__main__":
    # O Render fornece a porta via variável de ambiente PORT
    app.run(host="0.0.0.0", port=PORT)
