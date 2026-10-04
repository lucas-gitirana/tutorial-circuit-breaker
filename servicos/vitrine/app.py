"""Serviço vitrine: a página de produto da loja (porta 8021).

Para montar a página, a vitrine junta os dados do produto (que ela mesma
tem) com as recomendações, que vêm de OUTRO serviço: o recomendacoes.

Rotas:
  GET  /produtos/<id>        -> produto + recomendações
  GET  /circuito             -> estado do circuit breaker
  POST /circuito/reiniciar   -> volta o circuit breaker para FECHADO
  GET  /saude
"""
import logging
import time

import requests
from flask import Flask, jsonify

from integracao import disjuntor, obter_recomendacoes

app = Flask(__name__)
app.json.ensure_ascii = False


class _OcultarHealthcheck(logging.Filter):
    """Esconde dos logs as chamadas do healthcheck do Docker a /saude."""

    def filter(self, registro: logging.LogRecord) -> bool:
        return "/saude" not in registro.getMessage()


logging.getLogger("werkzeug").addFilter(_OcultarHealthcheck())

CATALOGO = {
    "1": {"nome": "Teclado mecânico", "preco": 349.90},
    "2": {"nome": "Mouse sem fio", "preco": 129.90},
    "3": {"nome": "Monitor 27 polegadas", "preco": 1499.00},
}


@app.errorhandler(requests.RequestException)
def falha_na_dependencia(erro: requests.RequestException):
    # Sem proteção, a falha da dependência vira falha da vitrine: efeito cascata.
    return jsonify(erro=f"A vitrine falhou porque o serviço de recomendações falhou: {erro}"), 502


@app.get("/produtos/<produto_id>")
def detalhar_produto(produto_id: str):
    produto = CATALOGO.get(produto_id)
    if produto is None:
        return jsonify(erro=f"Produto '{produto_id}' não existe. Use 1, 2 ou 3."), 404

    inicio = time.monotonic()
    recomendacoes, origem = obter_recomendacoes(produto_id)
    return jsonify(
        id=produto_id,
        **produto,
        recomendacoes=recomendacoes,
        origem_recomendacoes=origem,
        circuito=disjuntor.estado,
        tempo_recomendacoes_ms=round((time.monotonic() - inicio) * 1000),
    )


@app.get("/circuito")
def ver_circuito():
    return jsonify(
        estado=disjuntor.estado,
        falhas_consecutivas=disjuntor.falhas_consecutivas,
        limite_falhas=disjuntor.limite_falhas,
        tempo_aberto_segundos=disjuntor.tempo_aberto,
    )


@app.post("/circuito/reiniciar")
def reiniciar_circuito():
    disjuntor.reiniciar()
    return jsonify(estado=disjuntor.estado)


@app.get("/saude")
def saude():
    return jsonify(servico="vitrine", status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
