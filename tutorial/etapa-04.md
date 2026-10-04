# Etapa 4 — Recuperando: o estado MEIO_ABERTO

**Objetivo:** permitir que o circuito **feche sozinho** quando a dependência
se recuperar.

Do jeito que está, o circuito abre e nunca mais fecha. Mas como saber se o
`recomendacoes` voltou sem chamá-lo? A resposta é o estado **MEIO_ABERTO**:
depois de `tempo_aberto` segundos, o circuito deixa **uma chamada de teste**
passar.

```text
            limite de falhas                    passou tempo_aberto
 FECHADO ───────────────────────▶ ABERTO ───────────────────────────▶ MEIO_ABERTO
    ▲                               ▲                                     │
    │                               └──────── teste falhou ───────────────┤
    └──────────────────────────────────────── teste deu certo ────────────┘
```

## O que implementar (Etapa 4)

Continue em `servicos/vitrine/circuit_breaker.py`:

| Método | O que acrescentar |
| --- | --- |
| `_permite_chamada` | se está `ABERTO` **e** `self.relogio() - self.aberto_em >= self.tempo_aberto`: muda para `MEIO_ABERTO` e devolve `True` |
| `_registrar_sucesso` | se está `MEIO_ABERTO`, o teste deu certo: muda para `FECHADO` |
| `_registrar_falha` | se está `MEIO_ABERTO`, o teste falhou: volta para `ABERTO` **na hora** (sem esperar o limite) e reinicia `self.aberto_em` |

> Uma única falha em MEIO_ABERTO já reabre o circuito. A dependência acabou de
> provar que ainda não está bem, então não há por que insistir.

## Teste

Também verificada sem containers. O relógio falso simula a passagem do tempo.

Clique em **Verificar**.
