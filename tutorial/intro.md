## O problema

Numa loja online, a **página de um produto** é montada por **dois serviços**:

| Serviço | O que faz na página |
| --- | --- |
| **vitrine** | mostra nome e preço, que ela mesma guarda |
| **recomendacoes** | sugere outros produtos ("quem comprou, levou também...") |

As recomendações são um **detalhe** da página. Mas, para montá-la, a vitrine
**chama** o recomendacoes pela rede e **espera** a resposta.

E se o recomendacoes der **erro**? E se ele ficar **lento** e demorar 5
segundos para responder? **A página inteira cai junto?**

Quando a falha de um serviço derruba quem depende dele, temos uma **falha em
cascata**. Em microsserviços, isso pode derrubar o sistema inteiro.

## A ideia do Circuit Breaker

Duas atitudes protegem a vitrine:

1. **Falhar rápido**: não esperar para sempre por quem não responde.
2. **Parar de insistir**: se o recomendacoes falhou várias vezes seguidas,
   não adianta chamá-lo de novo agora. Melhor dar um tempo para ele se recuperar.

O **circuit breaker** (disjuntor) cuida da segunda atitude. É o mesmo disjuntor
do quadro de luz da sua casa:

| | Disjuntor elétrico | **Circuit breaker** (este tutorial) |
| --- | --- | --- |
| Vigia | a corrente elétrica | as chamadas a outro serviço |
| Desarma quando | há um curto-circuito | há **falhas seguidas demais** |
| Desarmado | a energia não passa | as chamadas **nem saem**: falham na hora |
| Religa | alguém sobe a alavanca | **sozinho**, depois de testar se o serviço voltou |

O disjuntor tem **três estados**:

![Estados do disjuntor](tutorial/img/estados-geral.svg)

| Estado | Comportamento |
| --- | --- |
| **FECHADO** | tudo normal: as chamadas passam e as falhas seguidas são contadas |
| **ABERTO** | as chamadas são recusadas **na hora**, sem nem tentar |
| **MEIO_ABERTO** | depois de um tempo, **uma** chamada de teste passa: se der certo, fecha; se falhar, reabre |

Este é o mapa do sistema que você vai proteger. Ele aparece em toda etapa,
destacando a parte em que você está:

![Mapa do sistema](tutorial/img/mapa-geral.svg)

## As ferramentas

| Peça | O que é | Papel aqui |
| --- | --- | --- |
| **Docker Compose** | sobe vários containers com um único comando, a partir do `docker-compose.yml` | liga os 2 serviços do mapa |
| **Flask** | microframework web em Python | faz a API HTTP de cada serviço |
| **requests** | biblioteca Python para fazer chamadas HTTP | a vitrine usa para chamar o recomendacoes |
| **Painel de falhas** | uma rota do recomendacoes (`POST /falhas`) | **você** decide quando ele funciona, dá erro ou fica lento |
| **curl** | faz requisições HTTP pelo terminal | é o "cliente" que você vai usar |

## Como funciona este tutorial

- **▶ Executar**, embaixo de um bloco de comando, roda o comando no terminal.
- **Verificar** confere o seu código e diz o que falta quando algo dá errado.
- O arquivo a editar abre sozinho, ao lado. Procure o marcador **✏️**.
- Os serviços recarregam sozinhos quando você **salva** um arquivo (`Ctrl+S`).

## Preparando o ambiente

Ao abrir esta tela, o terminal já começou a rodar:

```bash
docker compose up -d --build --wait
```

- `up`: cria e liga os containers descritos no `docker-compose.yml`;
- `-d`: roda em segundo plano e devolve o terminal para você;
- `--build`: constrói a imagem dos serviços Python antes de subir;
- `--wait`: só termina quando todos os serviços estiverem **saudáveis**
  (respondendo). Assim você não começa com o ambiente pela metade.

Na primeira vez demora 1 ou 2 minutos, porque as imagens são baixadas. Quando o
terminal voltar ao prompt, clique em **Começar**.

> Pré-requisitos: Docker com Docker Compose e Python 3 (usado pelas
> verificações). No GitHub Codespaces já vem tudo instalado.
