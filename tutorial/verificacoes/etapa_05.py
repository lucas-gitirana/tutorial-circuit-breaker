"""Etapa 5: fallback (plano B) quando o recomendacoes falha."""
import circuito
from verificador import executar, verificacao


def pagina_com_fallback(modo: str) -> float:
    circuito.reiniciar_circuito()
    with circuito.com_modo(modo):
        status, corpo, segundos = circuito.pagina()
    assert status != 500, (
        f"a vitrine deu erro interno (HTTP 500). Ainda há um ___ no código? {circuito.dica_logs()}"
    )
    assert status == 200, (
        f"a vitrine devolveu HTTP {status}: {corpo}. Escreva o try/except e salve. {circuito.dica_logs()}"
    )
    assert corpo.get("origem_recomendacoes") == "fallback", (
        f"origem_recomendacoes = {corpo.get('origem_recomendacoes')!r} (esperado 'fallback')."
    )
    assert corpo.get("recomendacoes") == ["Mais vendidos da semana", "Ofertas do dia"], (
        f"recomendações do fallback: {corpo.get('recomendacoes')!r}. Devolva RECOMENDACOES_PADRAO."
    )
    return segundos


@verificacao("com o recomendacoes com ERRO, a página responde 200 usando o fallback")
def erro():
    pagina_com_fallback("erro")


@verificacao("com o recomendacoes LENTO, a página responde 200 com fallback em cerca de 1 s")
def lento():
    segundos = pagina_com_fallback("lento")
    assert segundos < 2.5, f"a página levou {segundos:.1f} s. O timeout da Etapa 4 continua lá?"


@verificacao("com o recomendacoes NORMAL, a página usa as recomendações reais")
def normal():
    with circuito.com_modo("normal"):
        status, corpo, _ = circuito.pagina()
    assert status == 200 and corpo.get("origem_recomendacoes") == "servico", (
        f"esperado HTTP 200 com origem 'servico', veio HTTP {status}: {corpo}"
    )


executar(parar_na_primeira_falha=True)
