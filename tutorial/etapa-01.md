![Mapa: visão geral](tutorial/img/mapa-geral.svg)

📍 **Você está aqui:** conhecendo as peças do mapa.

## 1. Veja os containers

```bash
docker compose ps
```

Devem aparecer **2 containers** com estado `running (healthy)`:

| Container | No mapa |
| --- | --- |
| `vitrine` | monta a página do produto (porta 8021). O **disjuntor** vai morar aqui dentro |
| `recomendacoes` | sugere outros produtos (porta 8022). Tem o **painel de falhas** |

O `docker-compose.yml`, aberto ao lado, descreve esses dois containers.

## 2. Peça uma página de produto

**`GET http://localhost:8021/produtos/1`**

```bash
curl -s localhost:8021/produtos/1 -w '← HTTP %{http_code}\n'
```

```text
{
  "id": "1",
  "nome": "Teclado mecânico",
  "preco": 349.9,
  "recomendacoes": [ "Mouse sem fio", "Mousepad gamer", "Suporte para notebook" ],
  "origem_recomendacoes": "servico",
  "circuito": "FECHADO",
  "tempo_recomendacoes_ms": 10
}
← HTTP 200
```

| Repare em | O que significa |
| --- | --- |
| `"origem_recomendacoes": "servico"` | as recomendações vieram do serviço `recomendacoes` |
| `"tempo_recomendacoes_ms": 10` | quanto a vitrine **esperou** pelo recomendacoes |
| `"circuito": "FECHADO"` | o estado do disjuntor. Por enquanto ele só existe no nome: você vai construí-lo |

## 3. O atalho para várias chamadas

Nas próximas etapas, você vai pedir a página várias vezes seguidas. Este
script faz isso e resume cada resposta numa linha:

```bash
bash tutorial/chamar-vitrine.sh 3
```

```text
#1  HTTP 200   0.01s  origem=servico   circuito=FECHADO
#2  HTTP 200   0.01s  origem=servico   circuito=FECHADO
#3  HTTP 200   0.01s  origem=servico   circuito=FECHADO
```

> Algum container não está `healthy`? Rode `docker compose up -d --build --wait` de novo.

## 4. Clique em Verificar ✔

A verificação confere se os dois serviços estão respondendo.
