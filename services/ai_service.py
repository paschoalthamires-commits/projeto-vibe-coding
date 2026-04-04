import os
import requests
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ==============================
# CONFIGURAÇÃO DE AMBIENTE
# ==============================
AI_API_KEY = os.getenv("AI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "llama3-70b-8192")
BASE_URL = os.getenv("AI_BASE_URL", "https://api.groq.com/openai/v1/chat/completions")

TIMEOUT = 45        # Para prompts complexos
MAX_RETRIES = 2     # Retry inteligente
MIN_CODIGO_LENGTH = 10

# ==============================
# HELPERS
# ==============================
def _validar_prompt(prompt: str):
    """Valida prompt antes de enviar para a IA"""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt vazio.")
    if len(prompt) < 5:
        raise ValueError("Prompt muito curto.")
    if len(prompt) > 4000:
        raise ValueError("Prompt muito longo.")

def _extrair_codigo(texto: str) -> str:
    """
    Extrai código de markdown ```...```.
    Se não houver, remove frases comuns de IA e retorna texto limpo.
    """
    if not texto:
        return ""

    padrao = re.compile(r"```(?:\w+)?\n?(.*?)```", re.DOTALL)
    match = padrao.search(texto)
    if match:
        return match.group(1).strip()

    # fallback: remover frases comuns de IA
    frases_remover = ["Aqui está o código", "Espero que ajude", "Certamente!", "```"]
    linhas = [l for l in texto.splitlines() if not any(f in l for f in frases_remover)]
    return "\n".join(linhas).strip()

def _call_ai(messages: list) -> str:
    """Chamada robusta à IA com retry, timeout e logging"""
    if not AI_API_KEY:
        logger.error("AI_API_KEY não configurada!")
        raise RuntimeError("Configuração de API ausente.")

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "temperature": 0.1,
        "top_p": 1
    }

    for tentativa in range(MAX_RETRIES + 1):
        try:
            logger.info(f"[AI] Tentativa {tentativa + 1}")
            response = requests.post(BASE_URL, headers=headers, json=payload, timeout=TIMEOUT)
            response.raise_for_status()

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            if not content:
                raise ValueError("Resposta da IA vazia ou inválida.")

            return content

        except (requests.Timeout, requests.ConnectionError) as e:
            logger.warning(f"[AI] Timeout ou conexão falhou: {e}")
        except requests.HTTPError as e:
            logger.warning(f"[AI] HTTPError: {e}")
        except Exception as e:
            logger.warning(f"[AI] Erro inesperado: {e}")

        if tentativa >= MAX_RETRIES:
            logger.error("[AI] Falha crítica após múltiplas tentativas.")
            raise RuntimeError("Não foi possível comunicar com a IA.")

    raise RuntimeError("Erro inesperado no _call_ai.")

# ==============================
# FUNÇÕES PRINCIPAIS
# ==============================
def gerar_codigo(prompt: str) -> Optional[str]:
    """Gera código do zero"""
    try:
        _validar_prompt(prompt)

        messages = [
            {
                "role": "system",
                "content": (
                    "Você é um desenvolvedor sênior e especialista em SaaS. "
                    "Retorne APENAS código funcional, dentro de blocos markdown ```...```."
                )
            },
            {"role": "user", "content": prompt}
        ]

        raw = _call_ai(messages)
        codigo = _extrair_codigo(raw)

        if len(codigo) < MIN_CODIGO_LENGTH:
            raise ValueError("Código gerado muito curto ou inválido.")

        return codigo

    except Exception as e:
        logger.exception(f"[GERAR_CODIGO] Falha: {e}")
        return None

def remodelar_codigo(codigo_atual: str, instrucao: str) -> Optional[str]:
    """Refina ou ajusta código existente"""
    try:
        _validar_prompt(codigo_atual)
        _validar_prompt(instrucao)

        messages = [
            {
                "role": "system",
                "content": (
                    "Você é especialista em refatoração. "
                    "Retorne apenas o código completo atualizado, dentro de ```...```."
                )
            },
            {"role": "user", "content": f"Código Atual:\n{codigo_atual}\n\nAjuste:\n{instrucao}"}
        ]

        raw = _call_ai(messages)
        codigo = _extrair_codigo(raw)

        if len(codigo) < MIN_CODIGO_LENGTH:
            raise ValueError("Código gerado muito curto ou inválido após ajuste.")

        return codigo

    except Exception as e:
        logger.exception(f"[REMODELO_CODIGO] Falha: {e}")
        return None