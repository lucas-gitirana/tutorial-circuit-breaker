![Mapa: falha em cascata](tutorial/img/mapa-cascata.svg)

📍 **Você está aqui:** no caminho de uma página, de ponta a ponta. Agora você
vai **quebrar** o recomendacoes e ver o que acontece com a vitrine.

## 1. Ligue o modo "erro" no painel de falhas

O painel de falhas é uma rota do recomendacoes. No modo **`erro`**, ele
responde **HTTP 500** a todo pedido, como um serviço com um bug ou com o banco
fora do ar (veja o `if modo == "erro"` no arquivo aberto ao lado).

**`POST http://localhost:8022/falhas`**

```json
{ "modo": "erro" }
```

```bash
curl -s -X POST localhost:8022/falhas \
  -H 'Content-Type: application/json' \
  -d '{"modo": "erro"}' \
  -w '← HTTP %{http_code}\n'
```

## 2. Peça a página do produto

```bash
bash tutorial/chamar-vitrine.sh 3
```

```text
#1  HTTP 502   0.00s  A vitrine falhou porque o serviço de recomendações falhou: HTTPError
#2  HTTP 502   0.01s  A vitrine falhou porque o serviço de recomendações falhou: HTTPError
#3  HTTP 502   0.06s  A vitrine falhou porque o serviço de recomendações falhou: HTTPError
```

😱 A vitrine está no ar, tem o nome e o preço do produto... e mesmo assim
devolveu **502**. O cliente não vê **nada** da página.

## 3. Isso é falha em cascata

| | O que falhou | O que o cliente viu |
| --- | --- | --- |
| Esperado | só as recomendações (um **detalhe**) | a página, sem as recomendações |
| **O que aconteceu** | só as recomendações | **erro na página inteira** |

A falha do recomendacoes **escorreu** para a vitrine. Se outros serviços
dependessem da vitrine, cairiam também, como peças de dominó.

## 4. Clique em Verificar ✔

> Deixe o painel no modo `erro`: a verificação confere isso.
