"""Etapa 11: o circuito se recupera sozinho (containers rodando, leva ~12 s)."""
import time

import circuito
from verificador import executar, http, verificacao

contexto = {}


@verificacao("com o recomendacoes em ERRO, o circuito ABRE")
def abre():
    circuito.reiniciar_circuito()
    dados = circuito.circuito()
    contexto["tempo"] = dados["tempo_aberto_segundos"]
    with circuito.com_modo("erro"):
        for _ in range(dados["limite_falhas"]):
            circuito.pagina()
    estado = circuito.circuito()["estado"]
    assert estado == "ABERTO", f"o circuito está {estado!r}. As Etapas 6 a 10 passaram?"


@verificacao("o recomendacoes volta, mas o circuito ABERTO ainda não sabe disso: fallback sem chamá-lo")
def ainda_aberto():
    with circuito.com_modo("normal"):
        antes = circuito.chamadas_recebidas()
        _, corpo, _ = circuito.pagina()
        assert corpo.get("origem_recomendacoes") == "fallback", f"esperado fallback com o circuito ABERTO, veio: {corpo}"
        assert circuito.chamadas_recebidas() == antes, "uma chamada chegou ao recomendacoes com o circuito ABERTO."


@verificacao("passado tempo_aberto, a chamada de teste dá certo e o circuito FECHA sozinho")
def fecha():
    time.sleep(contexto["tempo"] + 0.5)
    with circuito.com_modo("normal"):
        _, corpo, _ = circuito.pagina()
    assert corpo.get("origem_recomendacoes") == "servico", (
        f"esperado recomendações do serviço depois de {contexto['tempo']:g} s, veio: {corpo}"
    )
    assert corpo.get("circuito") == "FECHADO", f"estado do circuito: {corpo.get('circuito')!r} (esperado FECHADO)."
    _, historico = http("GET", f"{circuito.VITRINE}/circuito/historico")
    assert "MEIO_ABERTO" in str(historico), f"a passagem por MEIO_ABERTO não aparece no histórico:\n{historico}"


executar(parar_na_primeira_falha=True)
