![Estados do disjuntor](tutorial/img/estados-geral.svg)

📍 **Você está aqui:** o diagrama inteiro funcionando, ao vivo. Agora o
recomendacoes vai **se recuperar**, e o circuito tem que perceber sozinho.

## 1. Abra o circuito e "conserte" o recomendacoes

Este bloco derruba o recomendacoes, abre o circuito com 3 falhas, conserta o
recomendacoes e pede **mais uma** página logo em seguida:

```bash
curl -s -X POST localhost:8022/falhas -H 'Content-Type: application/json' -d '{"modo": "lento"}'
bash tutorial/chamar-vitrine.sh 3
curl -s -X POST localhost:8022/falhas -H 'Content-Type: application/json' -d '{"modo": "normal"}'
bash tutorial/chamar-vitrine.sh 1
```

```text
#1  HTTP 200   1.01s  origem=fallback  circuito=FECHADO
#2  HTTP 200   1.02s  origem=fallback  circuito=FECHADO
#3  HTTP 200   1.04s  origem=fallback  circuito=ABERTO
...
#1  HTTP 200   0.00s  origem=fallback  circuito=ABERTO
```

🤔 O recomendacoes **já voltou**, mas a última página ainda veio com
`fallback`. O circuito está ABERTO e **não sabe** que o serviço voltou: ele
só vai testar depois de 10 s.

## 2. Espere 10 s e peça de novo

```bash
sleep 10
bash tutorial/chamar-vitrine.sh 2
curl -s localhost:8021/circuito/historico
```

```text
#1  HTTP 200   0.01s  origem=servico   circuito=FECHADO
#2  HTTP 200   0.00s  origem=servico   circuito=FECHADO
+   0.0 s   FECHADO     → ABERTO
+  10.1 s   ABERTO      → MEIO_ABERTO
+  10.1 s   MEIO_ABERTO → FECHADO
```

A chamada #1 foi a **chamada de teste**: o circuito passou para MEIO_ABERTO,
ela deu certo e o circuito **fechou**. Tudo voltou ao normal **sem ninguém
mexer em nada**. ✅

## 3. E se o teste falhar?

Repita com o recomendacoes **quebrado** o tempo todo:

```bash
curl -s -X POST localhost:8021/circuito/reiniciar
curl -s -X POST localhost:8022/falhas -H 'Content-Type: application/json' -d '{"modo": "erro"}'
bash tutorial/chamar-vitrine.sh 3
sleep 10
bash tutorial/chamar-vitrine.sh 1
curl -s localhost:8021/circuito/historico
curl -s -X POST localhost:8022/falhas -H 'Content-Type: application/json' -d '{"modo": "normal"}'
```

```text
+   0.0 s   FECHADO     → ABERTO
+  10.0 s   ABERTO      → MEIO_ABERTO
+  10.0 s   MEIO_ABERTO → ABERTO
```

O teste falhou e o circuito **reabriu na hora**, por mais 10 s: a regra que
você escreveu na Etapa 9.

## 4. Clique em Verificar ✔

A verificação repete a recuperação de ponta a ponta e leva cerca de **12
segundos**.
