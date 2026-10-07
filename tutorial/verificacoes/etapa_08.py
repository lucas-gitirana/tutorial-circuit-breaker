"""Etapa 8: passado tempo_aberto, liberar a chamada de TESTE em MEIO_ABERTO (sem containers)."""
from circuito import Relogio, aberto, recusou
from verificador import executar, importar, verificacao

cb = importar("servicos/vitrine", "circuit_breaker")


def chamada_de_teste(disjuntor):
    """Faz uma chamada e devolve (estado, falhas_consecutivas) vistos DURANTE a execução da função."""
    visto = []
    try:
        disjuntor.chamar(lambda: visto.append((disjuntor.estado, disjuntor.falhas_consecutivas)))
    except cb.CircuitoAbertoError:
        raise AssertionError(
            "passados 10 s, a chamada de teste deveria ser liberada, mas foi recusada. "
            "O `if` da Etapa 8 precisa ficar ACIMA do `if` da Etapa 7."
        ) from None
    return visto[0]


@verificacao("antes de tempo_aberto (9,9 s de 10 s), o circuito continua recusando")
def ainda_aberto():
    relogio = Relogio()
    disjuntor = aberto(cb, relogio)
    relogio.agora += 9.9
    assert recusou(cb, disjuntor), "com 9,9 s de 10 s, a chamada ainda deveria ser recusada."


@verificacao("passados 10 s, a chamada de TESTE é executada, com o circuito em MEIO_ABERTO")
def meio_aberto():
    relogio = Relogio()
    disjuntor = aberto(cb, relogio)
    relogio.agora += 10
    estado, _ = chamada_de_teste(disjuntor)
    assert estado == cb.MEIO_ABERTO, f"durante a chamada de teste o estado deveria ser MEIO_ABERTO, era {estado!r}."


@verificacao("ao entrar em MEIO_ABERTO, a contagem de falhas recomeça do zero")
def recomeca():
    relogio = Relogio()
    disjuntor = aberto(cb, relogio)
    relogio.agora += 10
    _, falhas = chamada_de_teste(disjuntor)
    assert falhas == 0, f"durante a chamada de teste, falhas_consecutivas = {falhas} (esperado 0)."


executar(parar_na_primeira_falha=True)
