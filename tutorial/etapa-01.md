# Etapa 1 — Provocando falhas em cascata

**Objetivo:** ver o que acontece com a vitrine quando a dependência dela falha.

## 1. Tudo funcionando

```bash
curl -s -w '\n' localhost:8021/produtos/1
```

A resposta junta os dados do produto e as `recomendacoes` vindas do outro
serviço (`"origem_recomendacoes": "servico"`).

Para acompanhar várias chamadas de uma vez, use o script auxiliar. Ele mostra,
para cada chamada, o status HTTP, o tempo total e de onde vieram as recomendações:

```bash
bash tutorial/chamar-vitrine.sh 3
```

## 2. Dependência lenta

Coloque o `recomendacoes` no modo **lento** (5 segundos por resposta):

```bash
curl -s -w '\n' -X POST localhost:8022/falhas -H 'Content-Type: application/json' -d '{"modo": "lento"}'
bash tutorial/chamar-vitrine.sh 2
```

Cada página da vitrine agora leva **5 segundos**. A vitrine está saudável, mas
fica refém da dependência. Com muitos usuários, as threads da vitrine se
esgotariam esperando, e ela pararia de responder até as páginas que não usam
recomendações.

## 3. Dependência com erro

```bash
curl -s -w '\n' -X POST localhost:8022/falhas -H 'Content-Type: application/json' -d '{"modo": "erro"}'
bash tutorial/chamar-vitrine.sh 2
```

A vitrine devolve **HTTP 502**: a falha do `recomendacoes` virou falha da
vitrine. Um item secundário da página (as recomendações) derrubou a página
inteira. Essa é a **falha em cascata**.

## 4. Volte ao normal

```bash
curl -s -w '\n' -X POST localhost:8022/falhas -H 'Content-Type: application/json' -d '{"modo": "normal"}'
```

Clique em **Verificar** para concluir a etapa.
