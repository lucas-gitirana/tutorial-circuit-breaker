![Estados: aberto](tutorial/img/estados-aberto.svg)

📍 **Você está aqui:** no estado **ABERTO**. O circuito já abre, mas ainda
**não faz nada** com isso: as chamadas continuam passando.

## O que deve acontecer

| Estado | `_permite_chamada()` devolve | O que o `chamar` faz |
| --- | --- | --- |
| FECHADO | `True` | roda a função normalmente |
| **ABERTO** | **`False`** | lança `CircuitoAbertoError` **na hora**, sem rodar a função |

É aqui que mora a economia do disjuntor: com o circuito aberto, a vitrine não
gasta **nem** o 1 s de timeout, e o recomendacoes **não recebe** mais carga.

## 🐍 Python rápido: `return` antecipado

`return` termina a função **na hora**. Quem passa pelo `if` sai com `False`;
quem não passa continua até o `return True` do final.

```python
if condicao:
    return False      # termina aqui
return True           # só chega aqui quem não entrou no if
```

## ✏️ Faça

Abaixo do marcador **Etapa 7** (em `_permite_chamada`), escreva e complete o
`___`:

```python
        if self.estado == ABERTO:
            return ___
```

**Salve** (`Ctrl+S`).

## Clique em Verificar ✔

Também **sem containers**: a verificação abre o circuito com 3 falhas e
confere que a próxima chamada é recusada **sem** rodar a função.

> Repare num problema: do jeito que está, o circuito abre e **nunca mais
> fecha**. A vitrine ficaria sem recomendações para sempre, mesmo depois de o
> recomendacoes voltar. A próxima etapa resolve isso.
