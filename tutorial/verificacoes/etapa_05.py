"""Etapa 5: circuit breaker integrado à vitrine (containers rodando)."""
import time

from verificador import executar, http, verificacao

VITRINE = "http://localhost:8021"
RECOMENDACOES = "http://localhost:8022"
contexto = {}


def chamadas_recebidas():
    return http("GET", f"{RECOMENDACOES}/estatisticas")[1]["requisicoes_recebidas"]


@verificacao("preparação: circuito reiniciado e recomendacoes em modo ERRO")
def preparar():
    status, _ = http("POST", f"{VITRINE}/circuito/reiniciar")
    assert status == 200, f"POST /circuito/reiniciar devolveu HTTP {status}."
    _, circuito = http("GET", f"{VITRINE}/circuito")
    contexto["limite"] = circuito["limite_falhas"]
    contexto["tempo"] = circuito["tempo_aberto_segundos"]
    http("POST", f"{RECOMENDACOES}/falhas", {"modo": "erro"})


@verificacao("com falhas seguidas o circuito ABRE e a vitrine segue respondendo com fallback")
def abre():
    antes = chamadas_recebidas()
    for _ in range(contexto["limite"] + 3):
        status, corpo = http("GET", f"{VITRINE}/produtos/2")
        assert status == 200 and corpo.get("origem_recomendacoes") == "fallback", (
            f"esperado HTTP 200 com fallback, veio HTTP {status}: {corpo}"
        )
    _, circuito = http("GET", f"{VITRINE}/circuito")
    assert circuito["estado"] == "ABERTO", (
        f"após {contexto['limite'] + 3} falhas o circuito está {circuito['estado']!r}. "
        "A chamada em integracao.py passa por disjuntor.chamar(...)? Reiniciou a vitrine?"
    )
    contexto["depois_de_abrir"] = chamadas_recebidas()
    recebidas = contexto["depois_de_abrir"] - antes
    assert recebidas == contexto["limite"], (
        f"o recomendacoes recebeu {recebidas} chamadas; com o circuito aberto, só as "
        f"{contexto['limite']} primeiras deveriam chegar até ele."
    )


@verificacao("o serviço se recupera, mas enquanto o circuito está ABERTO nenhuma chamada passa")
def aberto_nao_chama():
    http("POST", f"{RECOMENDACOES}/falhas", {"modo": "normal"})
    _, corpo = http("GET", f"{VITRINE}/produtos/2")
    assert corpo.get("origem_recomendacoes") == "fallback", "com o circuito ABERTO, a vitrine deveria usar o fallback."
    assert chamadas_recebidas() == contexto["depois_de_abrir"], "uma chamada chegou ao recomendacoes com o circuito ABERTO."


@verificacao("após tempo_aberto, a chamada de teste passa e o circuito FECHA")
def fecha():
    time.sleep(contexto["tempo"] + 0.5)
    _, corpo = http("GET", f"{VITRINE}/produtos/2")
    assert corpo.get("origem_recomendacoes") == "servico", (
        f"esperado recomendações do serviço após {contexto['tempo']}s, veio: {corpo}"
    )
    assert corpo.get("circuito") == "FECHADO", f"estado do circuito: {corpo.get('circuito')!r}."


try:
    executar(parar_na_primeira_falha=True)
finally:
    http("POST", f"{RECOMENDACOES}/falhas", {"modo": "normal"})
