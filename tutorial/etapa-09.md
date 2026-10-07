![Estados: desfecho do teste](tutorial/img/estados-desfecho.svg)

📍 **Você está aqui:** em **MEIO_ABERTO**, decidindo o que fazer com o
resultado da chamada de teste.

## O que deve acontecer

| A chamada de teste... | Novo estado | Por quê |
| --- | --- | --- |
| **deu certo** | **FECHADO** | o serviço voltou: tudo normal de novo |
| **falhou** | **ABERTO**, na hora | o serviço ainda está mal: espera mais `tempo_aberto` |

Repare: em MEIO_ABERTO, **uma única falha** já reabre o circuito. Não faz
sentido esperar 3 falhas: o serviço acabou de provar que ainda não está bem.

## ✏️ Faça 1: o teste deu certo

Abaixo do marcador **Etapa 9 · ... deu certo** (em `_registrar_sucesso`),
escreva:

```python
        if self.estado == MEIO_ABERTO:
            self.estado = FECHADO
```

## ✏️ Faça 2: o teste falhou

Abaixo do marcador **Etapa 9 · ... falhou** (o primeiro de `_registrar_falha`,
**acima** do código da Etapa 6), escreva e complete o `___`:

```python
        if self.estado == MEIO_ABERTO:
            self.estado = ___
            self.aberto_em = self.relogio()     # a espera recomeça
            return                              # não precisa contar: já reabriu
```

> É o mesmo truque da Etapa 8: o `return` antecipado termina a função antes
> de chegar na contagem da Etapa 6.

**Salve** (`Ctrl+S`).

## Clique em Verificar ✔

Sem containers. Com esta etapa, o disjuntor está **completo**: as quatro setas
do diagrama funcionam. Na próxima, ele sai dos testes e vai proteger a vitrine
de verdade.
