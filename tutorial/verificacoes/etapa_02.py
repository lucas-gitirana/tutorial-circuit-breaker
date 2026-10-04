"""Etapa 2: timeout + fallback na vitrine."""
import time

from verificador import executar, http, verificacao

VITRINE = "http://localhost:8021"
RECOMENDACOES = "http://localhost:8022"


def modo(nome):
    http("POST", f"{RECOMENDACOES}/falhas", {"modo": nome})


def produto():
    inicio = time.monotonic()
    status, corpo = http("GET", f"{VITRINE}/produtos/1", timeout=15)
    return status, corpo, time.monotonic() - inicio


@verificacao("com o recomendacoes LENTO, a vitrine responde em menos de 2,5s usando o fallback")
def lento():
    http("POST", f"{VITRINE}/circuito/reiniciar")
    modo("lento")
    try:
        status, corpo, duracao = produto()
    finally:
        modo("normal")
    assert duracao < 2.5, (
        f"a vitrine levou {duracao:.1f}s. Passe timeout=TIMEOUT_SEGUNDOS no requests.get "
        "e reinicie a vitrine (docker compose restart vitrine)."
    )
    assert status == 200, f"a vitrine devolveu HTTP {status}: {corpo}. Trate a exceção e use o fallback."
    assert corpo.get("origem_recomendacoes") == "fallback", f"origem_recomendacoes = {corpo.get('origem_recomendacoes')!r}."
    assert corpo.get("recomendacoes"), "a lista de recomendações do fallback veio vazia."


@verificacao("com o recomendacoes com ERRO, a vitrine responde 200 usando o fallback")
def erro():
    http("POST", f"{VITRINE}/circuito/reiniciar")
    modo("erro")
    try:
        status, corpo, _ = produto()
    finally:
        modo("normal")
    assert status == 200, f"a vitrine devolveu HTTP {status}: {corpo}. Trate a exceção e use o fallback."
    assert corpo.get("origem_recomendacoes") == "fallback", f"origem_recomendacoes = {corpo.get('origem_recomendacoes')!r}."


@verificacao("com o recomendacoes NORMAL, a vitrine usa as recomendações reais")
def normal():
    http("POST", f"{VITRINE}/circuito/reiniciar")
    status, corpo, _ = produto()
    assert status == 200 and corpo.get("origem_recomendacoes") == "servico", (
        f"esperado origem_recomendacoes 'servico', veio HTTP {status}: {corpo}"
    )


executar()
