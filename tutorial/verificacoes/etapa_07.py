"""Etapa 7: com o circuito ABERTO, falhar rápido (sem containers)."""
from circuito import Relogio, aberto, recusou
from verificador import executar, importar, verificacao

cb = importar("servicos/vitrine", "circuit_breaker")


@verificacao("ABERTO: chamar() lança CircuitoAbertoError SEM executar a função protegida")
def recusa():
    disjuntor = aberto(cb, Relogio())
    executou = []
    try:
        disjuntor.chamar(lambda: executou.append("chamou a dependência"))
    except cb.CircuitoAbertoError:
        pass
    else:
        raise AssertionError("com o circuito ABERTO, chamar() deveria lançar CircuitoAbertoError. "
                             "_permite_chamada precisa devolver False.")
    assert not executou, "a função protegida foi executada mesmo com o circuito ABERTO."


@verificacao("ABERTO: continua recusando nas chamadas seguintes")
def continua_recusando():
    disjuntor = aberto(cb, Relogio())
    assert all(recusou(cb, disjuntor) for _ in range(5)), "uma das chamadas passou com o circuito ABERTO."


@verificacao("FECHADO: as chamadas continuam passando e devolvem o resultado")
def fechado_passa():
    disjuntor = cb.CircuitBreaker(limite_falhas=3, tempo_aberto=10, relogio=Relogio())
    assert disjuntor.chamar(lambda x: x * 2, 21) == 42, "com o circuito FECHADO, chamar() deveria devolver o resultado."


executar(parar_na_primeira_falha=True)
