"""Atalhos das verificações: relógio falso para testar o disjuntor sem esperar
e chamadas aos serviços que estão rodando nos containers."""
import time
from contextlib import contextmanager

from verificador import http

VITRINE, RECOMENDACOES = "http://localhost:8021", "http://localhost:8022"


# ---------------------------------------------------------------------------
# Testes do circuit_breaker.py sem containers
# ---------------------------------------------------------------------------
class Relogio:
    """Relógio falso: o tempo só anda quando a verificação manda (relogio.agora += 10)."""

    def __init__(self):
        self.agora = 1000.0

    def __call__(self):
        return self.agora


def falha():
    raise ConnectionError("dependência fora do ar")


def falhar(disjuntor, vezes: int = 1) -> None:
    """Faz `vezes` chamadas que falham (as recusadas pelo circuito também contam)."""
    for _ in range(vezes):
        try:
            disjuntor.chamar(falha)
        except Exception:  # noqa: BLE001 - ConnectionError ou CircuitoAbertoError
            pass


def aberto(cb, relogio: Relogio):
    """Um disjuntor (limite 3, 10 s) que acabou de ABRIR depois de 3 falhas."""
    disjuntor = cb.CircuitBreaker(limite_falhas=3, tempo_aberto=10, relogio=relogio)
    falhar(disjuntor, 3)
    assert disjuntor.estado == cb.ABERTO, (
        f"depois de 3 falhas o circuito está {disjuntor.estado!r}. Volte à Etapa 6: ela precisa passar antes desta."
    )
    return disjuntor


def recusou(cb, disjuntor) -> bool:
    """True se o disjuntor recusou a chamada com CircuitoAbertoError."""
    try:
        disjuntor.chamar(lambda: None)
    except cb.CircuitoAbertoError:
        return True
    return False


# ---------------------------------------------------------------------------
# Serviços rodando nos containers
# ---------------------------------------------------------------------------
def modo_atual() -> str:
    return http("GET", f"{RECOMENDACOES}/falhas")[1].get("modo")


def mudar_modo(modo: str) -> None:
    http("POST", f"{RECOMENDACOES}/falhas", {"modo": modo})


@contextmanager
def com_modo(modo: str):
    """Muda o painel de falhas durante o teste e depois devolve o modo que o aluno tinha."""
    anterior = modo_atual()
    mudar_modo(modo)
    try:
        yield
    finally:
        mudar_modo(anterior)


def pagina(produto_id: str = "1") -> tuple[int, dict, float]:
    """GET /produtos/<id> da vitrine. Devolve (status, corpo, segundos)."""
    inicio = time.monotonic()
    status, corpo = http("GET", f"{VITRINE}/produtos/{produto_id}", timeout=15)
    return status, corpo if isinstance(corpo, dict) else {"resposta": corpo}, time.monotonic() - inicio


def reiniciar_circuito() -> None:
    status, _ = http("POST", f"{VITRINE}/circuito/reiniciar")
    assert status == 200, f"POST /circuito/reiniciar devolveu HTTP {status}."


def circuito() -> dict:
    return http("GET", f"{VITRINE}/circuito")[1]


def chamadas_recebidas() -> int:
    return http("GET", f"{RECOMENDACOES}/estatisticas")[1]["requisicoes_recebidas"]


def dica_logs() -> str:
    return "O arquivo foi salvo? Veja se a vitrine reiniciou sem erro: docker compose logs vitrine --tail 20"
