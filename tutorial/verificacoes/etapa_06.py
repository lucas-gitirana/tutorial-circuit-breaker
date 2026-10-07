"""Etapa 6: contar as falhas seguidas e ABRIR o circuito no limite (sem containers)."""
from circuito import Relogio, falhar
from verificador import executar, importar, verificacao

cb = importar("servicos/vitrine", "circuit_breaker")


def novo(relogio=None):
    return cb.CircuitBreaker(limite_falhas=3, tempo_aberto=10, relogio=relogio or Relogio())


@verificacao("cada falha soma 1 em falhas_consecutivas e, abaixo do limite, o circuito segue FECHADO")
def conta():
    disjuntor = novo()
    falhar(disjuntor, 2)
    assert disjuntor.falhas_consecutivas == 2, (
        f"depois de 2 falhas, falhas_consecutivas = {disjuntor.falhas_consecutivas} (esperado 2)."
    )
    assert disjuntor.estado == cb.FECHADO, f"com 2 falhas (limite 3) o estado deveria ser FECHADO, é {disjuntor.estado!r}."


@verificacao("na 3ª falha seguida (o limite), o circuito ABRE e anota em aberto_em a hora da abertura")
def abre():
    relogio = Relogio()
    disjuntor = novo(relogio)
    falhar(disjuntor, 2)
    relogio.agora += 5
    falhar(disjuntor, 1)
    assert disjuntor.estado == cb.ABERTO, f"depois de 3 falhas o estado deveria ser ABERTO, é {disjuntor.estado!r}."
    assert disjuntor.aberto_em == relogio.agora, (
        f"aberto_em = {disjuntor.aberto_em!r}; deveria ser a hora em que o circuito abriu: self.relogio()."
    )


@verificacao("um sucesso zera a contagem: falhas intercaladas com sucessos não abrem o circuito")
def sucesso_zera():
    disjuntor = novo()
    falhar(disjuntor, 2)
    disjuntor.chamar(lambda: "ok")
    assert disjuntor.falhas_consecutivas == 0, (
        f"depois de um sucesso, falhas_consecutivas = {disjuntor.falhas_consecutivas} (esperado 0)."
    )
    falhar(disjuntor, 2)
    assert disjuntor.estado == cb.FECHADO, "2 falhas, 1 sucesso e mais 2 falhas não são 3 falhas SEGUIDAS."


executar(parar_na_primeira_falha=True)
