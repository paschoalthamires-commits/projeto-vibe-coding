import os
import logging
from datetime import datetime
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ==============================
# CONFIGURAÇÃO DE PASTA DE SAÍDA
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_CODIGO_SIZE = 2 * 1024 * 1024  # 2MB máximo por arquivo

# ==============================
# FUNÇÕES PRINCIPAIS
# ==============================
def salvar_codigo(projeto_id: str, prompt: str, codigo: str, extensao: str = "py") -> str:
    """
    Salva o código gerado em arquivo seguro (.py ou .txt) com cabeçalho.
    
    :param projeto_id: ID único do projeto
    :param prompt: Prompt que gerou o código
    :param codigo: Código a ser salvo
    :param extensao: 'py' ou 'txt'
    :return: Nome do arquivo salvo
    """
    if not projeto_id or not codigo:
        raise ValueError("Projeto ID e código são obrigatórios.")

    if len(codigo.encode("utf-8")) > MAX_CODIGO_SIZE:
        raise ValueError("Código excede o tamanho máximo permitido.")

    # Nome seguro do arquivo
    nome_arquivo = secure_filename(f"projeto_{projeto_id}.{extensao}")
    caminho_completo = os.path.join(OUTPUT_DIR, nome_arquivo)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt_preview = prompt.replace("\n", " ")[:100]

    conteudo_final = (
        f"# ==============================\n"
        f"# Gerado por Vibe Coding SaaS\n"
        f"# Data: {timestamp}\n"
        f"# Projeto ID: {projeto_id}\n"
        f"# Prompt (preview): {prompt_preview}...\n"
        f"# ==============================\n\n"
        f"{codigo}"
    )

    try:
        with open(caminho_completo, "w", encoding="utf-8") as f:
            f.write(conteudo_final)
        logger.info(f"✅ Código salvo com sucesso: {caminho_completo}")
        return nome_arquivo
    except Exception as e:
        logger.exception(f"❌ Falha ao salvar arquivo {nome_arquivo}: {e}")
        raise IOError(f"Não foi possível salvar o arquivo {nome_arquivo}")

def listar_projetos(order_by_date: bool = True):
    """
    Lista arquivos salvos na pasta OUTPUT_DIR.
    
    :param order_by_date: Se True, retorna do mais recente para o mais antigo
    :return: Lista de dicionários [{'arquivo': nome, 'modificado': datetime}]
    """
    projetos = []
    for arquivo in os.listdir(OUTPUT_DIR):
        caminho = os.path.join(OUTPUT_DIR, arquivo)
        if os.path.isfile(caminho):
            mod_time = datetime.fromtimestamp(os.path.getmtime(caminho))
            projetos.append({"arquivo": arquivo, "modificado": mod_time})

    if order_by_date:
        projetos.sort(key=lambda x: x["modificado"], reverse=True)

    return projetos