"""Etapa 3: circuito FECHADO -> ABERTO (testado sem subir containers)."""
from verificador import executar, importar, verificacao

cb = importar("servicos/vitrine", "circuit_breaker")


class Relogio:
    """Relógio falso: o tempo só anda quando o teste manda."""

    def __init__(self):
        self.agora = 1000.0

    def __call__(self):
        return self.agora


def falha():
    raise ConnectionError("dependência fora do ar")


def falhar(disjuntor, vezes):
    for _ in range(vezes):
        try:
            disjuntor.chamar(falha)
        except ConnectionError:
            pass


@verificacao("começa FECHADO e repassa o resultado das chamadas bem-sucedidas")
def inicio():
    disjuntor = cb.CircuitBreaker(limite_falhas=3, tempo_aberto=10, relogio=Relogio())
    assert disjuntor.estado == cb.FECHADO, f"estado inicial: {disjuntor.estado!r}."
    assert disjuntor.chamar(lambda x: x * 2, 21) == 42, "chamar() deveria devolver o resultado da função."


@verificacao("conta as falhas seguidas e continua FECHADO abaixo do limite")
def abaixo_do_limite():
    disjuntor = cb.CircuitBreaker(limite_falhas=3, tempo_aberto=10, relogio=Relogio())
    falhar(disjuntor, 2)
    assert disjuntor.falhas_consecutivas == 2, f"falhas_consecutivas = {disjuntor.falhas_consecutivas} (esperado 2)."
    assert disjuntor.estado == cb.FECHADO, f"com 2 falhas (limite 3) o estado deveria ser FECHADO, é {disjuntor.estado!r}."


@verificacao("abre o circuito (ABERTO) ao atingir limite_falhas falhas seguidas")
def abre():
    disjuntor = cb.CircuitBreaker(limite_falhas=3, tempo_aberto=10, relogio=Relogio())
    falhar(disjuntor, 3)
    assert disjuntor.estado == cb.ABERTO, f"após 3 falhas o estado deveria ser ABERTO, é {disjuntor.estado!r}."
    assert disjuntor.aberto_em == 1000.0, "guarde em self.aberto_em o instante (self.relogio()) em que o circuito abriu."


@verificacao("ABERTO: recusa na hora com CircuitoAbertoError, SEM chamar a dependência")
def falha_rapido():
    disjuntor = cb.CircuitBreaker(limite_falhas=3, tempo_aberto=10, relogio=Relogio())
    falhar(disjuntor, 3)
    chamadas = []
    try:
        disjuntor.chamar(lambda: chamadas.append("chamou"))
    except cb.CircuitoAbertoError:
        pass
    else:
        raise AssertionError("com o circuito ABERTO, chamar() deveria lançar CircuitoAbertoError.")
    assert not chamadas, "a função protegida foi executada mesmo com o circuito ABERTO."


@verificacao("um sucesso zera a contagem de falhas seguidas")
def sucesso_zera():
    disjuntor = cb.CircuitBreaker(limite_falhas=3, tempo_aberto=10, relogio=Relogio())
    falhar(disjuntor, 2)
    disjuntor.chamar(lambda: "ok")
    assert disjuntor.falhas_consecutivas == 0, f"após um sucesso, falhas_consecutivas = {disjuntor.falhas_consecutivas}."
    falhar(disjuntor, 2)
    assert disjuntor.estado == cb.FECHADO, "falhas intercaladas com sucesso não devem abrir o circuito."


executar()
