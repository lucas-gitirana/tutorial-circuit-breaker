"""Serviço recomendacoes: a DEPENDÊNCIA instável (porta 8022).

Devolve produtos recomendados para um produto. Tem um "painel de falhas"
para simular problemas reais:

  normal -> responde na hora
  erro   -> responde HTTP 500 (bug, banco fora do ar...)
  lento  -> demora 5 segundos para responder (sobrecarga, rede ruim...)

Rotas:
  GET  /recomendacoes/<produto_id>  -> lista de recomendações
  POST /falhas  {"modo": "..."}     -> muda o modo de falha
  GET  /falhas                      -> modo atual
  GET  /estatisticas                -> quantas requisições chegaram até aqui
  GET  /saude

Você não precisa alterar este serviço.
"""
import logging
import threading
import time

from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False
app.json.sort_keys = False
app.json.compact = False  # respostas indentadas: mais fáceis de ler no terminal
logging.getLogger("werkzeug").setLevel(logging.WARNING)  # logs mostram só o que importa

MODOS = ("normal", "erro", "lento")
ATRASO_MODO_LENTO = 5.0

RECOMENDACOES = {
    "1": ["Mouse sem fio", "Mousepad gamer", "Suporte para notebook"],
    "2": ["Teclado mecânico", "Mousepad gamer", "Headset"],
    "3": ["Cabo HDMI", "Suporte articulado", "Webcam Full HD"],
}

estado = {"modo": "normal", "requisicoes_recebidas": 0}
trava = threading.Lock()


@app.get("/recomendacoes/<produto_id>")
def recomendar(produto_id: str):
    with trava:
        estado["requisicoes_recebidas"] += 1
        modo = estado["modo"]
    print(f"[recomendacoes] ← pedido de recomendações do produto {produto_id} (modo {modo})")

    if modo == "erro":
        return jsonify(erro="Falha interna no serviço de recomendações."), 500
    if modo == "lento":
        time.sleep(ATRASO_MODO_LENTO)
    return jsonify(produto_id=produto_id, recomendacoes=RECOMENDACOES.get(produto_id, []))


@app.post("/falhas")
def mudar_modo():
    modo = (request.get_json(silent=True) or {}).get("modo")
    if modo not in MODOS:
        return jsonify(erro=f"Modo inválido. Use um destes: {', '.join(MODOS)}."), 400
    with trava:
        estado["modo"] = modo
    print(f"[recomendacoes] painel de falhas: modo agora é '{modo}'")
    return jsonify(modo=modo)


@app.get("/falhas")
def ver_modo():
    return jsonify(modo=estado["modo"])


@app.get("/estatisticas")
def estatisticas():
    return jsonify(requisicoes_recebidas=estado["requisicoes_recebidas"])


@app.get("/saude")
def saude():
    return jsonify(servico="recomendacoes", status="ok", modo=estado["modo"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
