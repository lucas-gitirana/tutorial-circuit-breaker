# Etapa 2 — Falhar rápido: timeout e fallback

**Objetivo:** aplicar o primeiro princípio, **falhar rápido**, e degradar com
elegância em vez de devolver erro.

O arquivo `servicos/vitrine/integracao.py` foi aberto ao lado. Ele tem duas funções:

- `buscar_no_servico`: a chamada HTTP crua ao `recomendacoes`;
- `obter_recomendacoes`: o que a vitrine usa. Devolve `(lista, origem)`.

## O que fazer

**1. Timeout.** Em `buscar_no_servico`, passe `timeout=TIMEOUT_SEGUNDOS` para o
`requests.get`. O valor (1 segundo) vem da variável de ambiente
`TIMEOUT_RECOMENDACOES_SEGUNDOS` do `docker-compose.yml`.

**2. Fallback.** Em `obter_recomendacoes`, envolva a chamada em `try/except`.
Se `buscar_no_servico` lançar `requests.RequestException` (timeout, conexão
recusada ou HTTP 500), devolva a resposta alternativa:

```python
return RECOMENDACOES_PADRAO, "fallback"
```

> **Fallback** é o "plano B": uma resposta menos boa, porém útil. Aqui, uma
> lista genérica de produtos. A página do produto continua funcionando sem as
> recomendações personalizadas.

## Teste no serviço

```bash
docker compose restart vitrine && sleep 2
curl -s -w '\n' -X POST localhost:8022/falhas -H 'Content-Type: application/json' -d '{"modo": "lento"}'
bash tutorial/chamar-vitrine.sh 3
```

Agora cada chamada leva cerca de **1 segundo** e devolve `origem=fallback`.
Teste também o modo `erro`, que deve dar HTTP 200 com fallback:

```bash
curl -s -w '\n' -X POST localhost:8022/falhas -H 'Content-Type: application/json' -d '{"modo": "erro"}'
bash tutorial/chamar-vitrine.sh 3
curl -s -w '\n' -X POST localhost:8022/falhas -H 'Content-Type: application/json' -d '{"modo": "normal"}'
```

## Ainda não é o suficiente

Repare que a vitrine **continua chamando** o `recomendacoes` toda vez, mesmo
sabendo que ele está com problema. Cada página ainda paga 1 segundo de
espera, e o serviço doente segue recebendo carga, o que dificulta a
recuperação. Falta o segundo princípio: **parar de insistir**. É aí que entra
o circuit breaker.

Clique em **Verificar**. A verificação muda o modo do `recomendacoes` e mede
o tempo de resposta da vitrine.
