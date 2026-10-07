"""Etapa 10: o disjuntor protegendo a vitrine de verdade (containers rodando)."""
import circuito
from verificador import executar, verificacao


@verificacao("com o recomendacoes em ERRO, a vitrine segue respondendo e o circuito ABRE")
def abre():
    circuito.reiniciar_circuito()
    limite = circuito.circuito()["limite_falhas"]
    with circuito.com_modo("erro"):
        antes = circuito.chamadas_recebidas()
        for _ in range(limite + 3):
            status, corpo, _ = circuito.pagina()
            assert status == 200 and corpo.get("origem_recomendacoes") == "fallback", (
                f"esperado HTTP 200 com fallback, veio HTTP {status}: {corpo}. {circuito.dica_logs()}"
            )
        estado = circuito.circuito()["estado"]
        assert estado == "ABERTO", (
            f"depois de {limite + 3} falhas o circuito está {estado!r}. "
            "A chamada em obter_recomendacoes passa por disjuntor.chamar(...)? Salvou o arquivo?"
        )
        recebidas = circuito.chamadas_recebidas() - antes
    assert recebidas == limite, (
        f"o recomendacoes recebeu {recebidas} chamadas; com o circuito aberto, só as {limite} primeiras deveriam chegar até ele."
    )


@verificacao("com o circuito ABERTO, a página sai na hora com fallback, sem chamar o recomendacoes")
def falha_rapido():
    with circuito.com_modo("lento"):
        antes = circuito.chamadas_recebidas()
        status, corpo, segundos = circuito.pagina()
        depois = circuito.chamadas_recebidas()
    assert status == 200 and corpo.get("origem_recomendacoes") == "fallback", (
        f"esperado HTTP 200 com fallback, veio HTTP {status}: {corpo}. Trate também CircuitoAbertoError."
    )
    assert depois == antes, "uma chamada chegou ao recomendacoes com o circuito ABERTO."
    assert segundos < 0.5, f"a página levou {segundos:.2f} s; com o circuito ABERTO ela nem deveria esperar o timeout."


executar(parar_na_primeira_falha=True)
