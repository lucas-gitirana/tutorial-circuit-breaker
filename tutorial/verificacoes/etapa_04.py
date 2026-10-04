"""Etapa 4: ABERTO -> MEIO_ABERTO -> FECHADO/ABERTO (testado sem subir containers)."""
from verificador import executar, importar, verificacao

cb = importar("servicos/vitrine", "circuit_breaker")


class Relogio:
    def __init__(self):
        self.agora = 1000.0

    def __call__(self):
        return self.agora


def falha():
    raise ConnectionError("dependência fora do ar")


def aberto(relogio):
    disjuntor = cb.CircuitBreaker(limite_falhas=3, tempo_aberto=10, relogio=relogio)
    for _ in range(3):
        try:
            disjuntor.chamar(falha)
        except ConnectionError:
            pass
    assert disjuntor.estado == cb.ABERTO, "pré-requisito da Etapa 3: 3 falhas deveriam abrir o circuito."
    return disjuntor


def recusa(disjuntor):
    try:
        disjuntor.chamar(lambda: None)
    except cb.CircuitoAbertoError:
        return True
    return False


@verificacao("antes de tempo_aberto passar, o circuito continua recusando")
def ainda_aberto():
    relogio = Relogio()
    disjuntor = aberto(relogio)
    relogio.agora += 9.9
    assert recusa(disjuntor), "com 9,9s de 10s, a chamada ainda deveria ser recusada."


@verificacao("depois de tempo_aberto, passa para MEIO_ABERTO e deixa a chamada de teste passar")
def meio_aberto():
    relogio = Relogio()
    disjuntor = aberto(relogio)
    relogio.agora += 10
    estado_durante = []
    try:
        disjuntor.chamar(lambda: estado_durante.append(disjuntor.estado))
    except cb.CircuitoAbertoError:
        raise AssertionError("passados 10s, a chamada de teste deveria ser permitida.") from None
    assert estado_durante == [cb.MEIO_ABERTO], (
        f"durante a chamada de teste o estado deveria ser MEIO_ABERTO, era {estado_durante[0] if estado_durante else '?'}."
    )


@verificacao("chamada de teste com sucesso -> FECHADO e contagem zerada")
def teste_ok():
    relogio = Relogio()
    disjuntor = aberto(relogio)
    relogio.agora += 10
    disjuntor.chamar(lambda: "ok")
    assert disjuntor.estado == cb.FECHADO, f"estado após o teste bem-sucedido: {disjuntor.estado!r}."
    assert disjuntor.falhas_consecutivas == 0, f"falhas_consecutivas = {disjuntor.falhas_consecutivas}."


@verificacao("chamada de teste com falha -> ABERTO de novo, com o tempo reiniciado")
def teste_falhou():
    relogio = Relogio()
    disjuntor = aberto(relogio)
    relogio.agora += 10
    try:
        disjuntor.chamar(falha)
    except ConnectionError:
        pass
    assert disjuntor.estado == cb.ABERTO, (
        f"uma falha em MEIO_ABERTO deve reabrir o circuito NA HORA (sem esperar o limite). Estado: {disjuntor.estado!r}."
    )
    relogio.agora += 9
    assert recusa(disjuntor), "o tempo_aberto deve recomeçar a contar a partir da nova abertura."
    relogio.agora += 1
    assert not recusa(disjuntor), "após mais 10s, uma nova chamada de teste deveria ser permitida."


executar()
