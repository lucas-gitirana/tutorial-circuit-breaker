![Mapa: timeout](tutorial/img/mapa-timeout.svg)

📍 **Você está aqui:** na chamada da vitrine ao recomendacoes (a seta com o
**timeout 1 s**). Primeira atitude: **falhar rápido**.

## O que é timeout?

**Timeout** é o tempo máximo que você aceita esperar. Passou disso, desiste.
É o que você faz ao telefone: se ninguém atende em 30 segundos, você desliga
em vez de ficar ouvindo o sinal sonoro para sempre.

Hoje a vitrine chama o recomendacoes **sem timeout**: espera o tempo que ele
quiser. Com o modo `lento`, isso dá 5 segundos por página.

O limite já está configurado no `docker-compose.yml` e chega ao Python na
variável `TIMEOUT_SEGUNDOS`:

| No `docker-compose.yml` | No `integracao.py` |
| --- | --- |
| `TIMEOUT_RECOMENDACOES_SEGUNDOS: "1"` | `TIMEOUT_SEGUNDOS = 1.0` |

## 🐍 Python rápido

| Código | Significa |
| --- | --- |
| `requests.get(url)` | faz um `GET` e **espera** a resposta, sem limite |
| `requests.get(url, timeout=2)` | espera no máximo 2 s. Passou disso, **lança uma exceção** (`ReadTimeout`) |

## ✏️ Faça

Abaixo do marcador **Etapa 4**, acrescente o `timeout` na chamada (a linha já
existe, é só mudar o final dela) e complete o `___`:

```python
    resposta = requests.get(f"{URL_RECOMENDACOES}/recomendacoes/{produto_id}", timeout=___)
```

> Dica: use a variável `TIMEOUT_SEGUNDOS`, definida no topo do arquivo.

**Salve** o arquivo (`Ctrl+S`).

## 🧪 Teste: o recomendacoes ainda está lento

```bash
bash tutorial/chamar-vitrine.sh 2
```

```text
#1  HTTP 502   1.01s  A vitrine falhou porque o serviço de recomendações falhou: ReadTimeout
#2  HTTP 502   1.01s  A vitrine falhou porque o serviço de recomendações falhou: ReadTimeout
```

| | Antes | Agora |
| --- | --- | --- |
| Tempo por página | 5 s | **1 s** ✅ |
| Resposta | 200 | **502** 🤔 |

A vitrine agora **falha rápido**: não fica mais sufocada esperando. Mas o
timeout virou uma exceção (`ReadTimeout`), e a página caiu do mesmo jeito que
na Etapa 2. Falta um **plano B**: é a próxima etapa.

## Clique em Verificar ✔

> Deu erro de conexão? Pode ser um erro de digitação no Python. Veja com
> `docker compose logs vitrine --tail 20`.
