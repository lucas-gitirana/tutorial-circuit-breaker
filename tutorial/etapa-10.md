![Mapa: disjuntor na vitrine](tutorial/img/mapa-disjuntor.svg)

📍 **Você está aqui:** de volta à vitrine. O disjuntor está pronto, mas
ninguém o usa: a chamada ao recomendacoes ainda vai **direto**. Agora ela
passa **por dentro** dele.

## A mudança

O `disjuntor` já foi criado no topo do `integracao.py`, com os valores do
`docker-compose.yml` (3 falhas, 10 s). Falta só usá-lo:

| Antes (Etapa 5) | Agora |
| --- | --- |
| `buscar_no_servico(produto_id)` | `disjuntor.chamar(buscar_no_servico, produto_id)` |
| fallback quando a **chamada falha** | fallback quando a chamada falha **ou** quando o **circuito está aberto** |

> Repare: `disjuntor.chamar` recebe a **função** (`buscar_no_servico`, sem
> parênteses) e o argumento dela separado. Quem decide se a função roda ou
> não é o disjuntor.

## 🐍 Python rápido

| Código | Significa |
| --- | --- |
| `except (ErroA, ErroB):` | um único `except` que pega **qualquer um** dos dois erros |

## ✏️ Faça

No bloco `try`/`except` que você escreveu na Etapa 5 (abaixo do marcador
**Etapa 5**), troque a chamada e o `except`. Complete os `___`:

```python
    try:
        return disjuntor.chamar(___, produto_id), "servico"
    except (requests.RequestException, ___):
        return RECOMENDACOES_PADRAO, "fallback"
```

> Dica: a exceção do circuito aberto é a `CircuitoAbertoError`, já importada
> no topo do arquivo.

**Salve** (`Ctrl+S`). A vitrine reinicia com o circuito **FECHADO**.

## 🧪 Teste: veja o circuito abrir

Com o recomendacoes **lento**, peça 6 páginas e conte quantos pedidos chegaram
até ele:

```bash
curl -s -X POST localhost:8022/falhas -H 'Content-Type: application/json' -d '{"modo": "lento"}'
curl -s localhost:8022/estatisticas
bash tutorial/chamar-vitrine.sh 6
curl -s localhost:8022/estatisticas
```

```text
#1  HTTP 200   1.01s  origem=fallback  circuito=FECHADO
#2  HTTP 200   1.02s  origem=fallback  circuito=FECHADO
#3  HTTP 200   1.04s  origem=fallback  circuito=ABERTO
#4  HTTP 200   0.00s  origem=fallback  circuito=ABERTO
#5  HTTP 200   0.00s  origem=fallback  circuito=ABERTO
#6  HTTP 200   0.00s  origem=fallback  circuito=ABERTO
```

| Chamadas | O que aconteceu |
| --- | --- |
| #1 a #3 | a vitrine **tentou**, esperou 1 s (timeout) e usou o fallback. Na 3ª falha, o circuito **abriu** |
| #4 a #6 | o circuito estava aberto: fallback **na hora** (0,00 s), sem nem chamar o recomendacoes |

O contador do recomendacoes subiu só **3**, não 6. Ele ganhou um respiro. 😮‍💨

Veja a mudança de estado nos logs da vitrine:

```bash
docker compose logs --no-log-prefix vitrine --tail 7
```

```text
[vitrine] página do produto 1: recomendações de 'fallback' em 1004 ms (circuito FECHADO)
[vitrine] página do produto 1: recomendações de 'fallback' em 1004 ms (circuito FECHADO)
[vitrine] ⚡ circuito FECHADO → ABERTO
[vitrine] página do produto 1: recomendações de 'fallback' em 1006 ms (circuito ABERTO)
[vitrine] página do produto 1: recomendações de 'fallback' em 0 ms (circuito ABERTO)
...
```

## Clique em Verificar ✔

A verificação abre o circuito com o recomendacoes em `erro`, confere que só 3
pedidos chegaram até ele e que, aberto, a página sai na hora.
