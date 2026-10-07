"""Um circuit breaker (disjuntor) escrito do zero.

Funciona como um disjuntor elétrico: envolve as chamadas a uma dependência e,
quando ela falha demais, "desarma" e passa a recusar as chamadas na hora, sem
nem tentar, até que seja seguro testar de novo.

Estados:

    FECHADO ──(limite_falhas falhas seguidas)──▶ ABERTO
       ▲                                           │
       │                                   (passou tempo_aberto)
       │                                           ▼
       └────────(chamada de teste OK)────────── MEIO_ABERTO
                                                   │
                     ABERTO ◀──(chamada de teste falhou)

Este módulo não conhece Flask nem HTTP: protege QUALQUER função. O relógio é
injetável para que as verificações controlem a passagem do tempo.
"""
from __future__ import annotations

import logging
import time
from typing import Callable

FECHADO = "FECHADO"
ABERTO = "ABERTO"
MEIO_ABERTO = "MEIO_ABERTO"

log = logging.getLogger("circuito")


class CircuitoAbertoError(Exception):
    """Lançada quando o circuito está ABERTO e a chamada nem é tentada."""


class CircuitBreaker:
    def __init__(self, limite_falhas: int = 3, tempo_aberto: float = 10.0,
                 relogio: Callable[[], float] = time.monotonic) -> None:
        self.limite_falhas = limite_falhas  # falhas SEGUIDAS para abrir o circuito
        self.tempo_aberto = tempo_aberto    # segundos em ABERTO antes de testar de novo
        self.relogio = relogio              # devolve a hora atual, em segundos
        self.reiniciar()

    def chamar(self, funcao: Callable, *args, **kwargs):
        """Executa ``funcao(*args, **kwargs)`` protegida pelo circuit breaker."""
        if not self._permite_chamada():
            raise CircuitoAbertoError("Circuito ABERTO: chamada recusada sem acionar a dependência.")

        try:
            resultado = funcao(*args, **kwargs)
        except Exception:
            self._registrar_falha()
            raise

        self._registrar_sucesso()
        return resultado

    # -----------------------------------------------------------------------
    # Etapas 6 a 9: você vai completar os três métodos abaixo.
    # -----------------------------------------------------------------------
    def _permite_chamada(self) -> bool:
        """Decide se a chamada pode seguir para a dependência."""

        # ═══ Etapa 8 · MEIO_ABERTO: já passou tempo_aberto? ════════════════
        # ✏️  Escreva aqui o `if` que libera a chamada de teste.
        if self.estado == ABERTO and self.relogio() - self.aberto_em >= self.tempo_aberto:
            self.estado = MEIO_ABERTO
            self.falhas_consecutivas = 0    # período de teste: a contagem recomeça



        # ═══ Etapa 7 · ABERTO: falhar rápido ═══════════════════════════════
        # ✏️  Escreva aqui o `if` que recusa a chamada.
        if self.estado == ABERTO:
            return False



        return True

    def _registrar_falha(self) -> None:
        """Chamado quando a função protegida lançou uma exceção."""

        # ═══ Etapa 9 · MEIO_ABERTO: a chamada de teste falhou ══════════════
        # ✏️  Escreva aqui o `if` que reabre o circuito na hora.
        if self.estado == MEIO_ABERTO:
            self.estado = ABERTO
            self.aberto_em = self.relogio()     # a espera recomeça
            return                              # não precisa contar: já reabriu



        # ═══ Etapa 6 · contar a falha e, no limite, ABRIR ══════════════════
        # ✏️  Escreva aqui as 4 linhas: somar 1 e, se chegou ao limite, abrir.
        self.falhas_consecutivas += 1
        if self.falhas_consecutivas >= self.limite_falhas:
            self.estado = ABERTO
            self.aberto_em = self.relogio()     # anota QUANDO abriu (a Etapa 8 usa)



    def _registrar_sucesso(self) -> None:
        """Chamado quando a função protegida terminou sem exceção."""

        # ═══ Etapa 6 · um sucesso zera a contagem ══════════════════════════
        # ✏️  Escreva aqui a linha que zera as falhas seguidas.
        self.falhas_consecutivas = 0



        # ═══ Etapa 9 · MEIO_ABERTO: a chamada de teste deu certo ═══════════
        # ✏️  Escreva aqui o `if` que fecha o circuito.
        if self.estado == MEIO_ABERTO:
            self.estado = FECHADO



    # -----------------------------------------------------------------------
    # Infraestrutura: você não precisa alterar daqui para baixo.
    # -----------------------------------------------------------------------
    def reiniciar(self) -> None:
        """Volta ao estado inicial: FECHADO, sem falhas e sem histórico."""
        self._estado = FECHADO
        self.falhas_consecutivas = 0
        self.aberto_em: float | None = None  # instante (self.relogio()) em que o circuito abriu
        self.transicoes: list[tuple[float, str, str]] = []  # (instante, de, para): GET /circuito/historico

    @property
    def estado(self) -> str:
        return self._estado

    @estado.setter
    def estado(self, novo: str) -> None:
        # Toda vez que você escreve `self.estado = ...`, a mudança fica anotada
        # no histórico e aparece nos logs (docker compose logs vitrine).
        if novo != self._estado:
            self.transicoes.append((self.relogio(), self._estado, novo))
            log.info("⚡ circuito %s → %s", self._estado, novo)
        self._estado = novo
