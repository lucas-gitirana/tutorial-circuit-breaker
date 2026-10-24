![Estados: abrir o circuito](tutorial/img/estados-abrir.svg)

📍 **Você está aqui:** dentro do disjuntor (`circuit_breaker.py`), na seta
**FECHADO → ABERTO**.

## Como o disjuntor funciona por dentro

O método `chamar`, já pronto no arquivo aberto ao lado, envolve qualquer
função e consulta três métodos que **você** vai escrever:

```text
disjuntor.chamar(funcao)
  ├─ _permite_chamada()?   não ──▶ lança CircuitoAbertoError (a função nem roda)
  │                        sim
  ├─ roda funcao()
  │     ├─ deu erro ──▶ _registrar_falha()   e repassa o erro
  │     └─ deu certo ──▶ _registrar_sucesso() e devolve o resultado
```

| Etapa | Você escreve |
| --- | --- |
| **esta** | contar as falhas seguidas e **abrir** no limite |
| 7 | **recusar** as chamadas enquanto estiver aberto |
| 8 | liberar a **chamada de teste** (MEIO_ABERTO) |
| 9 | **fechar** ou **reabrir** conforme o resultado do teste |

## O que deve acontecer

Com `limite_falhas = 3`:

| Chamada | Resultado | `falhas_consecutivas` | `estado` |
| --- | --- | --- | --- |
| 1ª | falhou | 1 | FECHADO |
| 2ª | **deu certo** | **0** (zera!) | FECHADO |
| 3ª | falhou | 1 | FECHADO |
| 4ª | falhou | 2 | FECHADO |
| 5ª | falhou | **3** | **ABERTO** |

As falhas precisam ser **seguidas**: um sucesso no meio prova que o serviço
ainda funciona, e a contagem recomeça.

## 🐍 Python rápido

| Código | Significa |
| --- | --- |
| `self.falhas_consecutivas += 1` | soma 1 ao que já estava lá |
| `self.estado = ABERTO` | muda o estado (e aparece nos logs da vitrine) |
| `self.relogio()` | a hora atual, em segundos |

## ✏️ Faça 1: contar e abrir

Abaixo do marcador **"Etapa 6 · FALHA"** (em `_registrar_falha`),
cole o código abaixo e complete o `___` com `self.limite_falhas`:

```python
        self.falhas_consecutivas += 1
        if self.falhas_consecutivas >= ___:
            self.estado = ABERTO
            self.aberto_em = self.relogio()     # anota QUANDO abriu (a Etapa 8 usa)
```

> **Atenção:** mantenha a mesma **indentação** do bloco acima (8
> espaços, alinhado com o comentário do marcador).

## ✏️ Faça 2: um sucesso zera a contagem

Abaixo do marcador **"Etapa 6 · SUCESSO"** (em `_registrar_sucesso`), escreva:

```python
        self.falhas_consecutivas = 0
```

**Salve** (`Ctrl+S`).

## Clique em Verificar ✔

Esta verificação **não precisa dos containers**: ela importa o
`circuit_breaker.py` e o testa com uma função que sempre falha.
