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
injetável para que os testes controlem a passagem do tempo.
"""
from __future__ import annotations

import time
from typing import Callable

FECHADO = "FECHADO"
ABERTO = "ABERTO"
MEIO_ABERTO = "MEIO_ABERTO"


class CircuitoAbertoError(Exception):
    """Lançada quando o circuito está ABERTO e a chamada nem é tentada."""


class CircuitBreaker:
    def __init__(self, limite_falhas: int = 3, tempo_aberto: float = 10.0,
                 relogio: Callable[[], float] = time.monotonic) -> None:
        self.limite_falhas = limite_falhas  # falhas SEGUIDAS para abrir o circuito
        self.tempo_aberto = tempo_aberto    # segundos em ABERTO antes de testar de novo
        self.relogio = relogio
        self.reiniciar()

    def reiniciar(self) -> None:
        self.estado = FECHADO
        self.falhas_consecutivas = 0
        self.aberto_em: float | None = None  # instante em que o circuito abriu

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
    # Etapas 3 e 4: complete os três métodos abaixo.
    # -----------------------------------------------------------------------
    def _permite_chamada(self) -> bool:
        """Decide se a chamada pode seguir para a dependência."""
        # TODO (Etapa 3): se o circuito está ABERTO, devolva False (falhar rápido).
        #
        # TODO (Etapa 4): se está ABERTO mas já se passaram self.tempo_aberto
        # segundos desde self.aberto_em (use self.relogio() para saber a hora
        # atual), mude para MEIO_ABERTO e devolva True: é a chamada de teste.
        return True

    def _registrar_falha(self) -> None:
        """Chamado quando a função protegida lançou uma exceção."""
        # TODO (Etapa 3): some 1 em self.falhas_consecutivas. Ao atingir
        # self.limite_falhas, mude para ABERTO e guarde self.aberto_em = self.relogio().
        #
        # TODO (Etapa 4): se a falha aconteceu em MEIO_ABERTO (a chamada de
        # teste falhou), volte para ABERTO na hora e reinicie self.aberto_em.
        pass

    def _registrar_sucesso(self) -> None:
        """Chamado quando a função protegida terminou sem exceção."""
        # TODO (Etapa 3): zere self.falhas_consecutivas.
        #
        # TODO (Etapa 4): se o estado é MEIO_ABERTO (a chamada de teste deu
        # certo), feche o circuito: estado = FECHADO.
        pass
