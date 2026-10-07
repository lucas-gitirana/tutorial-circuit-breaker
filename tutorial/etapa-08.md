![Estados: meio-aberto](tutorial/img/estados-meio-aberto.svg)

📍 **Você está aqui:** na seta **ABERTO → MEIO_ABERTO**.

## Como saber se o serviço voltou... sem chamá-lo?

Não dá. Então o disjuntor faz um meio-termo: depois de `tempo_aberto`
segundos (10 s, no `docker-compose.yml`), ele deixa passar **uma chamada de
teste**. Esse estado de "vamos ver" é o **MEIO_ABERTO**.

| Tempo desde que abriu | `_permite_chamada()` |
| --- | --- |
| 9,9 s | `False`: ainda ABERTO, recusa |
| 10 s ou mais | muda para **MEIO_ABERTO** e devolve `True`: a chamada de teste passa |

Ao entrar em MEIO_ABERTO, a contagem de falhas **recomeça do zero**: é um
período de teste, com ficha limpa.

## 🐍 Python rápido

| Código | Significa |
| --- | --- |
| `self.relogio() - self.aberto_em` | quantos segundos se passaram desde que o circuito abriu |
| `a and b` | verdadeiro só se **os dois** forem verdadeiros |

## ✏️ Faça

Abaixo do marcador **Etapa 8** (o primeiro de `_permite_chamada`, **acima** do
`if` da Etapa 7), escreva e complete o `___`:

```python
        if self.estado == ABERTO and self.relogio() - self.aberto_em >= ___:
            self.estado = MEIO_ABERTO
            self.falhas_consecutivas = 0    # período de teste: a contagem recomeça
```

> Dica: o tempo de espera fica em `self.tempo_aberto`.

**Por que acima do `if` da Etapa 7?** Se o tempo já passou, este `if` troca o
estado para MEIO_ABERTO **antes** de o `if self.estado == ABERTO` ser
avaliado. Aí a chamada não é recusada e segue até o `return True`. Se ficasse
abaixo, o `return False` da Etapa 7 terminaria a função antes.

**Salve** (`Ctrl+S`).

## Clique em Verificar ✔

Sem containers: o relógio falso avança 9,9 s, depois 10 s, e a verificação
confere o estado **durante** a chamada de teste.
