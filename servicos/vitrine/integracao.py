"""Integração da vitrine com o serviço de recomendações.

Toda chamada remota pode falhar ou demorar. Este módulo concentra as
estratégias de proteção da vitrine:

  - timeout (Etapa 2): falhar RÁPIDO em vez de esperar para sempre;
  - fallback (Etapa 2): ter uma resposta alternativa quando a dependência falha;
  - circuit breaker (Etapa 5): parar de chamar uma dependência que está falhando.
"""
import os

import requests

from circuit_breaker import CircuitBreaker, CircuitoAbertoError

URL_RECOMENDACOES = os.environ.get("URL_RECOMENDACOES", "http://localhost:8022")
TIMEOUT_SEGUNDOS = float(os.environ.get("TIMEOUT_RECOMENDACOES_SEGUNDOS", "1.0"))

# Resposta "boa o suficiente" quando o serviço de recomendações não ajuda:
# melhor mostrar algo genérico do que derrubar a página inteira do produto.
RECOMENDACOES_PADRAO = ["Mais vendidos da semana", "Ofertas do dia"]

disjuntor = CircuitBreaker(
    limite_falhas=int(os.environ.get("CB_LIMITE_FALHAS", "3")),
    tempo_aberto=float(os.environ.get("CB_TEMPO_ABERTO_SEGUNDOS", "10")),
)


def buscar_no_servico(produto_id: str) -> list:
    """Chamada HTTP crua ao serviço de recomendações."""
    resposta = requests.get(f"{URL_RECOMENDACOES}/recomendacoes/{produto_id}", timeout=TIMEOUT_SEGUNDOS)
    resposta.raise_for_status()  # HTTP 4xx/5xx vira exceção
    return resposta.json()["recomendacoes"]


def obter_recomendacoes(produto_id: str) -> tuple[list, str]:
    """Devolve (recomendações, origem), onde origem é "servico" ou "fallback"."""
    try:
        return disjuntor.chamar(buscar_no_servico, produto_id), "servico"
    except CircuitoAbertoError:
        print("[vitrine] circuito ABERTO: usando fallback sem chamar recomendacoes")
        return RECOMENDACOES_PADRAO, "fallback"
    except requests.RequestException as erro:
        print(f"[vitrine] falha ao chamar recomendacoes ({type(erro).__name__}): usando fallback")
        return RECOMENDACOES_PADRAO, "fallback"
