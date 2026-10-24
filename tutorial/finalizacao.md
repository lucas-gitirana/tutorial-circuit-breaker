## Você protegeu a vitrine 🎉

![Mapa do sistema](tutorial/img/mapa-geral.svg)

| Peça do mapa | O que você fez |
| --- | --- |
| **Timeout** | a vitrine não espera mais de 1 s por uma dependência |
| **Fallback** | a página continua de pé, com recomendações genéricas, quando a dependência falha |
| **Disjuntor** | depois de 3 falhas seguidas, para de chamar o serviço doente e falha **na hora** |
| **MEIO_ABERTO** | depois de 10 s, testa sozinho se o serviço voltou: fecha se deu certo, reabre se falhou |

Com isso, a falha de um serviço **secundário** não derruba mais a vitrine, e o
serviço doente ganha um respiro para se recuperar.

## Vale a pena usar circuit breaker?

| ✅ Ganha | ⚠️ Paga |
| --- | --- |
| a falha de um serviço não se espalha (sem cascata) | o usuário vê dados **piores** (o fallback) enquanto o circuito está aberto |
| respostas rápidas mesmo com a dependência fora | escolher `limite_falhas` e `tempo_aberto` exige medir o sistema real |
| o serviço doente para de receber carga e se recupera | nem tudo tem um bom fallback (e um **pagamento**?) |
| recuperação automática, sem intervenção humana | mais um estado para observar e testar |

## Na vida real

Ninguém precisa escrever o próprio disjuntor:

| Ferramenta | Onde |
| --- | --- |
| Resilience4j | Java (sucessor do Hystrix, da Netflix) |
| Polly | .NET |
| pybreaker | Python |
| Istio / Envoy (*outlier detection*) | na malha de serviços (*service mesh*), sem mudar o código |

Elas acrescentam o que simplificamos aqui: **percentual** de erros numa janela
de tempo (em vez de "falhas seguidas"), limite de chamadas de teste em
MEIO_ABERTO (aqui, várias podem passar ao mesmo tempo), segurança para várias
threads e **métricas** do estado do circuito para os painéis de monitoramento.

## Para pensar

1. Por que cada dependência deve ter o **seu próprio** disjuntor, em vez de um
   único para todas?
2. O que acontece se a vitrine fizer *retry* (tentar de novo 3 vezes) **sem**
   disjuntor, contra um serviço sobrecarregado?

## Limpando o ambiente

```bash
docker compose down
```

A solução completa está na branch `solucao` deste repositório.

## Formulários de pós-teste e SUS:
Após enviar o seu resultado ao professor, responda a esses dois formulários abaixo:
- [Formulário de Pós-teste][]
- [Formulário SUS][]

[Formulário de Pós-teste]: https://docs.google.com/forms/d/e/1FAIpQLSdjKXC89fdkHBYghP7NX2rBeFNVHhj0kCSrG-53F7UF2SFKHA/viewform?usp=sharing&ouid=103537969988084746732
[Formulário SUS]: https://docs.google.com/forms/d/e/1FAIpQLSf_2BOW8VR3QeK4oJAORaNrIfw803TcrqspXP8xAwcXXbuuPQ/viewform?usp=sharing&ouid=103537969988084746732
