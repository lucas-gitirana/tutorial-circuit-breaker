# Etapa 5 — Circuit breaker em ação

**Objetivo:** proteger a chamada da vitrine com o circuit breaker e observar
os três estados funcionando de verdade.

## O que fazer

Em `servicos/vitrine/integracao.py`, na função `obter_recomendacoes`:

1. troque a chamada direta `buscar_no_servico(produto_id)` por
   `disjuntor.chamar(buscar_no_servico, produto_id)`;
2. trate também `CircuitoAbertoError`, devolvendo o mesmo fallback.

O `disjuntor` já foi criado no topo do arquivo com `limite_falhas=3` e
`tempo_aberto=10` segundos (variáveis `CB_*` do `docker-compose.yml`).

## Veja o circuito abrir

```bash
docker compose restart vitrine && sleep 2
echo "Antes:  $(curl -s localhost:8022/estatisticas)"
curl -s -w '\n' -X POST localhost:8022/falhas -H 'Content-Type: application/json' -d '{"modo": "erro"}'
bash tutorial/chamar-vitrine.sh 6
echo "Depois: $(curl -s localhost:8022/estatisticas)"
```

Nas três primeiras chamadas, a vitrine tentou o `recomendacoes` e falhou. A
partir da terceira falha o circuito **abriu**, e as chamadas seguintes nem
saíram da vitrine. Compare o contador do `recomendacoes` antes e depois: ele
aumentou só 3, não 6.

## Veja o circuito fechar

Recupere o serviço e chame a vitrine logo em seguida:

```bash
curl -s -w '\n' -X POST localhost:8022/falhas -H 'Content-Type: application/json' -d '{"modo": "normal"}'
bash tutorial/chamar-vitrine.sh 1
```

Ainda vem `fallback`: o circuito está aberto e não sabe que o serviço voltou.
Espere os 10 segundos e chame de novo:

```bash
sleep 10
bash tutorial/chamar-vitrine.sh 2
```

A primeira chamada foi a de teste (MEIO_ABERTO). Como deu certo, o circuito
**fechou** e tudo voltou ao normal sem intervenção humana.

Clique em **Verificar**. A verificação repete esse experimento e leva cerca de
15 segundos.
