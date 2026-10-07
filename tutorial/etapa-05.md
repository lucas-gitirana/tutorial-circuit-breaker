![Mapa: fallback](tutorial/img/mapa-fallback.svg)

📍 **Você está aqui:** dentro da vitrine, na seta **falhou?** que leva ao
**fallback**.

## O que é fallback?

**Fallback** é o **plano B**: uma resposta menos boa, porém útil, para quando
a dependência falha. Se o GPS perde o sinal, ele não apaga o mapa: mostra a
última posição conhecida.

Aqui, o plano B já está pronto no topo do `integracao.py`:

```python
RECOMENDACOES_PADRAO = ["Mais vendidos da semana", "Ofertas do dia"]
```

Não é personalizado, mas a página **continua de pé**.

## 🐍 Python rápido: `try` / `except`

```python
try:
    ...                                  # tenta fazer isto
except requests.RequestException:
    ...                                  # se der QUALQUER erro de HTTP, faz isto
```

`requests.RequestException` pega todos os problemas de uma chamada HTTP:
timeout, conexão recusada e respostas de erro (4xx/5xx).

## ✏️ Faça

Abaixo do marcador **Etapa 5**, **troque** a linha
`return buscar_no_servico(produto_id), "servico"` por este bloco e complete o
`___`:

```python
    try:
        return buscar_no_servico(produto_id), "servico"
    except requests.RequestException:
        return ___, "fallback"
```

> Dica: o plano B é a lista `RECOMENDACOES_PADRAO`.

**Salve** (`Ctrl+S`).

## 🧪 Teste: o recomendacoes ainda está lento

```bash
bash tutorial/chamar-vitrine.sh 2
```

```text
#1  HTTP 200   1.12s  origem=fallback  circuito=FECHADO
#2  HTTP 200   1.12s  origem=fallback  circuito=FECHADO
```

**200** em **1 s**, com as recomendações do plano B. A página sobreviveu! ✅

## 🤔 Ainda não basta

Conte quantos pedidos o recomendacoes recebeu antes e depois de 3 páginas:

```bash
curl -s localhost:8022/estatisticas
bash tutorial/chamar-vitrine.sh 3
curl -s localhost:8022/estatisticas
```

O contador subiu **3**. A vitrine **sabe** que o recomendacoes está mal, mas
continua chamando ele **toda vez**:

- cada página ainda **paga 1 s** de espera pelo timeout;
- o recomendacoes, que já está sobrecarregado, continua **recebendo carga**,
  o que atrapalha a recuperação dele.

Falta a segunda atitude: **parar de insistir**. É o trabalho do disjuntor,
que você vai construir nas próximas 4 etapas.

## Clique em Verificar ✔
