# Padrão Circuit Breaker na prática

**Tempo estimado:** 35 minutos · **Linguagem:** Python (Flask) · **Infra:** Docker Compose

## O problema: falhas em cascata

Em microsserviços, um serviço depende de outros pela rede, e a rede falha.
Quando uma dependência fica **lenta** ou **fora do ar**, quem a chama fica
esperando, prende threads e conexões e logo também para de responder. A
falha se espalha de serviço em serviço até derrubar o sistema inteiro
(Richardson, 2018).

Bruce e Pereira (2019) resumem como um serviço deve se comportar diante de falhas:

1. **Falhar rápido**: comunicar a falha logo, em vez de gastar recursos
   esperando uma resposta que pode nunca chegar.
2. **Parar de insistir**: se uma dependência falha com frequência, deixar de
   enviar requisições até que ela se recupere.

## A ideia do Circuit Breaker

O padrão funciona como um **disjuntor elétrico**. A chamada à dependência é
envolvida por um objeto que conta as falhas. Ao atingir um limite, o circuito
**abre** e as próximas chamadas falham na hora, sem nem tentar (Fowler, 2014).
O circuito tem três estados:

| Estado | Comportamento |
| --- | --- |
| **FECHADO** | chamadas passam normalmente; falhas seguidas são contadas |
| **ABERTO** | chamadas são recusadas imediatamente; usa-se um *fallback* |
| **MEIO_ABERTO** | depois de um tempo, uma chamada de teste é liberada: se der certo, o circuito fecha; se falhar, reabre |

## O cenário

```text
                       GET /produtos/1
   cliente ──────────▶ ┌──────────────┐  GET /recomendacoes/1  ┌─────────────────┐
                       │   vitrine    │ ─────────────────────▶ │  recomendacoes  │
                       │  (porta 8021)│ ◀───────────────────── │  (porta 8022)   │
                       └──────────────┘                        └─────────────────┘
                        dados do produto                        painel de falhas:
                        + recomendações                         normal | erro | lento
```

A **vitrine** monta a página de um produto e busca recomendações em outro
serviço. O **recomendacoes** tem um "painel de falhas" para simular os
problemas do mundo real: responder com erro ou demorar 5 segundos.

## O que você vai fazer

1. Provocar falhas e ver a vitrine cair junto (falha em cascata).
2. Adicionar **timeout** e **fallback**.
3. Implementar o circuit breaker: **FECHADO → ABERTO**.
4. Implementar a recuperação: **ABERTO → MEIO_ABERTO → FECHADO**.
5. Proteger a vitrine com o circuit breaker e vê-lo em ação.

## Como funciona este tutorial

- Blocos de comando têm um botão **▶ Executar**, que roda o comando no terminal integrado.
- Etapas com avaliação têm o botão **Verificar**. Se algo falhar, leia a saída:
  ela diz o que está faltando.
- Os arquivos que você vai editar abrem sozinhos, na linha do `TODO`.

## Preparando o ambiente

Ao abrir esta introdução, o terminal já começou a subir os containers. Se
precisar rodar de novo:

```bash
docker compose up -d --build --wait
```

> Pré-requisitos: Docker com Docker Compose e Python 3 (usado pelas
> verificações). No GitHub Codespaces, tudo já vem instalado.
