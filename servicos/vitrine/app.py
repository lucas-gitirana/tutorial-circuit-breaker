"""Serviço vitrine: a página de produto da loja (porta 8021).

Para montar a página, a vitrine junta os dados do produto (que ela mesma
tem) com as recomendações, que vêm de OUTRO serviço: o recomendacoes.

Rotas:
  GET  /produtos/<id>          -> produto + recomendações
  GET  /circuito               -> estado do circuit breaker
  GET  /circuito/historico     -> linha do tempo das mudanças de estado (texto)
  POST /circuito/reiniciar     -> volta o circuit breaker para FECHADO
  GET  /saude

Este arquivo é infraestrutura: você não precisa alterá-lo no tutorial.
"""
import logging
import os
import time

import requests
from flask import Flask, jsonify

from integracao import disjuntor, obter_recomendacoes

app = Flask(__name__)
app.json.ensure_ascii = False
app.json.sort_keys = False
app.json.compact = False  # respostas indentadas: mais fáceis de ler no terminal

# Logs enxutos: só as páginas servidas e as mudanças de estado do circuito.
logging.getLogger("werkzeug").setLevel(logging.WARNING)
_log_circuito = logging.getLogger("circuito")
_log_circuito.setLevel(logging.INFO)
_saida = logging.StreamHandler()
_saida.setFormatter(logging.Formatter("[vitrine] %(message)s"))
_log_circuito.addHandler(_saida)

CATALOGO = {
    "1": {"nome": "Teclado mecânico", "preco": 349.90},
    "2": {"nome": "Mouse sem fio", "preco": 129.90},
    "3": {"nome": "Monitor 27 polegadas", "preco": 1499.00},
}


@app.errorhandler(requests.RequestException)
def falha_na_dependencia(erro: requests.RequestException):
    # Sem proteção, a falha da dependência vira falha da vitrine: efeito cascata.
    print(f"[vitrine] ✘ a página caiu junto com o recomendacoes ({type(erro).__name__})")
    return jsonify(erro=f"A vitrine falhou porque o serviço de recomendações falhou: {type(erro).__name__}"), 502


@app.get("/produtos/<produto_id>")
def detalhar_produto(produto_id: str):
    produto = CATALOGO.get(produto_id)
    if produto is None:
        return jsonify(erro=f"Produto '{produto_id}' não existe. Use 1, 2 ou 3."), 404

    inicio = time.monotonic()
    recomendacoes, origem = obter_recomendacoes(produto_id)
    tempo_ms = round((time.monotonic() - inicio) * 1000)
    print(f"[vitrine] página do produto {produto_id}: recomendações de '{origem}' em {tempo_ms} ms "
          f"(circuito {disjuntor.estado})")
    return jsonify(
        id=produto_id,
        **produto,
        recomendacoes=recomendacoes,
        origem_recomendacoes=origem,
        circuito=disjuntor.estado,
        tempo_recomendacoes_ms=tempo_ms,
    )


@app.get("/circuito")
def ver_circuito():
    return jsonify(
        estado=disjuntor.estado,
        falhas_consecutivas=disjuntor.falhas_consecutivas,
        limite_falhas=disjuntor.limite_falhas,
        tempo_aberto_segundos=disjuntor.tempo_aberto,
    )


@app.get("/circuito/historico")
def historico_do_circuito():
    if not disjuntor.transicoes:
        texto = f"(o circuito ainda não mudou de estado: está {disjuntor.estado})\n"
        return texto, 200, {"Content-Type": "text/plain; charset=utf-8"}
    inicio = disjuntor.transicoes[0][0]
    linhas = [f"+{instante - inicio:6.1f} s   {de:<11} → {para}" for instante, de, para in disjuntor.transicoes]
    return "\n".join(linhas) + "\n", 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.post("/circuito/reiniciar")
def reiniciar_circuito():
    disjuntor.reiniciar()
    return jsonify(estado=disjuntor.estado)


@app.get("/saude")
def saude():
    return jsonify(servico="vitrine", status="ok")


if __name__ == "__main__":
    # use_reloader: ao salvar um .py, o serviço reinicia sozinho com o código novo
    # (e o circuito volta a FECHADO, porque o estado dele fica só na memória).
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        print(f"[vitrine] pronta; circuito {disjuntor.estado} "
              f"(limite {disjuntor.limite_falhas} falhas, {disjuntor.tempo_aberto:g} s aberto)")
    app.run(host="0.0.0.0", port=8000, threaded=True, use_reloader=True)
