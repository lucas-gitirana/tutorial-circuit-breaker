"""Etapa 9: o resultado da chamada de teste fecha ou reabre o circuito (sem containers)."""
from circuito import Relogio, aberto, falhar, recusou
from verificador import executar, importar, verificacao

cb = importar("servicos/vitrine", "circuit_breaker")


def em_teste(relogio):
    disjuntor = aberto(cb, relogio)
    relogio.agora += 10  # passou tempo_aberto: a próxima chamada é a de teste
    return disjuntor


@verificacao("chamada de teste com SUCESSO: o circuito FECHA")
def fecha():
    disjuntor = em_teste(Relogio())
    disjuntor.chamar(lambda: "ok")
    assert disjuntor.estado == cb.FECHADO, f"depois do teste bem-sucedido o estado é {disjuntor.estado!r} (esperado FECHADO)."
    assert disjuntor.falhas_consecutivas == 0, f"falhas_consecutivas = {disjuntor.falhas_consecutivas} (esperado 0)."


@verificacao("chamada de teste com FALHA: o circuito REABRE na hora (sem esperar 3 falhas)")
def reabre():
    disjuntor = em_teste(Relogio())
    falhar(disjuntor, 1)
    assert disjuntor.estado == cb.ABERTO, (
        f"depois do teste que falhou o estado é {disjuntor.estado!r}. Uma única falha em MEIO_ABERTO deve reabrir o circuito."
    )


@verificacao("ao reabrir, a espera de tempo_aberto recomeça do zero")
def espera_de_novo():
    relogio = Relogio()
    disjuntor = em_teste(relogio)
    falhar(disjuntor, 1)
    relogio.agora += 9
    assert recusou(cb, disjuntor), "9 s depois de reabrir, a chamada ainda deveria ser recusada. Atualize self.aberto_em."
    relogio.agora += 1
    assert not recusou(cb, disjuntor), "10 s depois de reabrir, uma nova chamada de teste deveria ser liberada."


executar(parar_na_primeira_falha=True)
