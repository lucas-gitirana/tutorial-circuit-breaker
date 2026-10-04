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
        if self.estado == ABERTO:
            # Etapa 4: passado o tempo_aberto, deixa UMA chamada de teste passar
            if self.relogio() - self.aberto_em >= self.tempo_aberto:
                self.estado = MEIO_ABERTO
                return True
            # Etapa 3: aberto = falhar rápido
            return False
        return True

    def _registrar_falha(self) -> None:
        """Chamado quando a função protegida lançou uma exceção."""
        self.falhas_consecutivas += 1
        # Etapa 4: em MEIO_ABERTO, a chamada de teste falhou -> volta a ABERTO
        if self.estado == MEIO_ABERTO or self.falhas_consecutivas >= self.limite_falhas:
            self.estado = ABERTO
            self.aberto_em = self.relogio()

    def _registrar_sucesso(self) -> None:
        """Chamado quando a função protegida terminou sem exceção."""
        self.falhas_consecutivas = 0
        # Etapa 4: em MEIO_ABERTO, a chamada de teste deu certo -> FECHADO
        self.estado = FECHADO
