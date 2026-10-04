# Parabéns, você implementou um Circuit Breaker! 🎉

## O que você construiu

- **Timeout**: a vitrine não espera mais do que 1 segundo por uma dependência.
- **Fallback**: a página continua útil mesmo sem as recomendações.
- **Circuit breaker** com três estados: abre após falhas seguidas, recusa
  chamadas na hora enquanto aberto e testa sozinho se a dependência voltou.

Com isso, a falha de um serviço secundário **não derruba mais** a vitrine, e
o serviço doente ganha um respiro para se recuperar.

## Na vida real

Ninguém precisa escrever o próprio circuit breaker. Existem bibliotecas e
infraestrutura prontas:

| Ferramenta | Onde |
| --- | --- |
| Resilience4j | Java (sucessor do Hystrix, da Netflix) |
| Polly | .NET |
| pybreaker | Python |
| Istio / Envoy (*outlier detection*) | na malha de serviços (*service mesh*), sem mudar o código |

Essas ferramentas acrescentam o que simplificamos aqui: janelas de tempo e
percentual de erro em vez de "falhas seguidas", limite de chamadas
simultâneas em MEIO_ABERTO, segurança para várias threads e **métricas** do
estado do circuito para os painéis de observabilidade.

## Para refletir

1. Qual seria um bom fallback para um serviço de **pagamentos**? Existe
   fallback para tudo?
2. Por que cada dependência deve ter o **seu próprio** circuit breaker, em vez
   de um único para todas?
3. O que acontece se combinarmos *retry* (tentar de novo) **sem** circuit
   breaker com uma dependência sobrecarregada?
4. Como você escolheria os valores de `limite_falhas` e `tempo_aberto` em produção?

## Limpando o ambiente

```bash
docker compose down
```

O código completo de referência está na branch `solucao` deste repositório.
