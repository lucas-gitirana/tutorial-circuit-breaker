"""Etapa 4: timeout na chamada ao recomendacoes."""
import circuito
from verificador import executar, verificacao


@verificacao("com o recomendacoes LENTO, a vitrine desiste em cerca de 1 s (timeout)")
def desiste_rapido():
    circuito.reiniciar_circuito()
    with circuito.com_modo("lento"):
        status, corpo, segundos = circuito.pagina()
    assert status != 500, (
        f"a vitrine deu erro interno (HTTP 500). Ainda há um ___ no código? {circuito.dica_logs()}"
    )
    assert segundos < 2.5, (
        f"a página levou {segundos:.1f} s. Acrescente timeout=TIMEOUT_SEGUNDOS no requests.get e salve. "
        f"{circuito.dica_logs()}"
    )


@verificacao("com o recomendacoes NORMAL, a página continua com as recomendações reais")
def normal():
    with circuito.com_modo("normal"):
        status, corpo, _ = circuito.pagina()
    assert status == 200 and corpo.get("origem_recomendacoes") == "servico", (
        f"esperado HTTP 200 com origem 'servico', veio HTTP {status}: {corpo}"
    )


executar(parar_na_primeira_falha=True)
