"""Integração da vitrine com o serviço de recomendações.

Toda chamada remota pode falhar ou demorar. Este módulo concentra as
estratégias de proteção da vitrine:

  - timeout (Etapa 4): falhar RÁPIDO em vez de esperar para sempre;
  - fallback (Etapa 5): ter um plano B quando a dependência falha;
  - circuit breaker (Etapa 10): parar de chamar uma dependência que está falhando.
"""
import os

import requests

from circuit_breaker import CircuitBreaker, CircuitoAbertoError

URL_RECOMENDACOES = os.environ.get("URL_RECOMENDACOES", "http://localhost:8022")
TIMEOUT_SEGUNDOS = float(os.environ.get("TIMEOUT_RECOMENDACOES_SEGUNDOS", "1.0"))

# Plano B: resposta "boa o suficiente" quando o recomendacoes não ajuda.
# Melhor mostrar algo genérico do que derrubar a página inteira do produto.
RECOMENDACOES_PADRAO = ["Mais vendidos da semana", "Ofertas do dia"]

# O disjuntor que vai proteger as chamadas ao recomendacoes (Etapa 10).
# Os valores vêm do docker-compose.yml: 3 falhas seguidas e 10 segundos.
disjuntor = CircuitBreaker(
    limite_falhas=int(os.environ.get("CB_LIMITE_FALHAS", "3")),
    tempo_aberto=float(os.environ.get("CB_TEMPO_ABERTO_SEGUNDOS", "10")),
)


def buscar_no_servico(produto_id: str) -> list:
    """Chamada HTTP crua ao recomendacoes. Erros de rede e HTTP 4xx/5xx viram exceção."""

    # ═══ Etapa 4 · TIMEOUT: esperar no máximo TIMEOUT_SEGUNDOS ════════════
    # ✏️  Acrescente o timeout na chamada requests.get, logo abaixo.
    resposta = requests.get(f"{URL_RECOMENDACOES}/recomendacoes/{produto_id}")

    resposta.raise_for_status()  # HTTP 4xx/5xx vira exceção
    return resposta.json()["recomendacoes"]


def obter_recomendacoes(produto_id: str) -> tuple[list, str]:
    """O que a página do produto usa. Devolve (recomendações, origem): "servico" ou "fallback"."""

    # ═══ Etapa 5 · FALLBACK (e, na Etapa 10, o DISJUNTOR) ═════════════════
    # ✏️  Troque a linha abaixo pelo bloco try/except do texto da etapa.
    return buscar_no_servico(produto_id), "servico"
