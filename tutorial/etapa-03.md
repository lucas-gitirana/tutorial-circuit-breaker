# Etapa 3 — Abrindo o circuito

**Objetivo:** implementar a transição **FECHADO → ABERTO** do circuit breaker.

O arquivo `servicos/vitrine/circuit_breaker.py` foi aberto ao lado. O método
`chamar` já está pronto e segue este fluxo:

```text
chamar(funcao)
  ├─ _permite_chamada()?  não ──▶ lança CircuitoAbertoError (sem chamar a função)
  │                       sim
  ├─ executa funcao()
  │     ├─ lançou exceção ──▶ _registrar_falha() e repassa a exceção
  │     └─ deu certo      ──▶ _registrar_sucesso() e devolve o resultado
```

Você vai completar os três métodos que ele usa.

## O que implementar (Etapa 3)

| Método | Comportamento |
| --- | --- |
| `_registrar_falha` | soma 1 em `self.falhas_consecutivas`; se chegou a `self.limite_falhas`, muda `self.estado` para `ABERTO` e guarda `self.aberto_em = self.relogio()` |
| `_registrar_sucesso` | zera `self.falhas_consecutivas` (as falhas precisam ser **seguidas**) |
| `_permite_chamada` | se `self.estado == ABERTO`, devolve `False`; caso contrário, `True` |

Por enquanto, ignore os comentários marcados como **Etapa 4**.

> **Por que `self.relogio()` e não `time.time()`?** O relógio é injetado no
> construtor. Em produção ele é o `time.monotonic`. Nos testes, é um relógio
> falso que só avança quando o teste manda, e assim dá para testar "passaram
> 10 segundos" sem esperar 10 segundos.

## Teste

Esta etapa é verificada **sem containers**: a verificação importa
`circuit_breaker.py` e o exercita com uma função que sempre falha.

Clique em **Verificar**.
