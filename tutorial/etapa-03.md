![Mapa: falha em cascata](tutorial/img/mapa-cascata.svg)

📍 **Você está aqui:** no mesmo caminho. Agora, uma falha mais traiçoeira: o
recomendacoes não quebra, ele fica **lento**.

## 1. Ligue o modo "lento"

No modo **`lento`**, o recomendacoes responde certinho, mas só depois de
**5 segundos**, como um serviço sobrecarregado ou numa rede ruim.

**`POST http://localhost:8022/falhas`**

```json
{ "modo": "lento" }
```

```bash
curl -s -X POST localhost:8022/falhas \
  -H 'Content-Type: application/json' \
  -d '{"modo": "lento"}' \
  -w '← HTTP %{http_code}\n'
```

## 2. Peça a página duas vezes

```bash
bash tutorial/chamar-vitrine.sh 2
```

```text
#1  HTTP 200   5.02s  origem=servico   circuito=FECHADO
#2  HTTP 200   5.25s  origem=servico   circuito=FECHADO
```

Deu **200**... mas cada página levou **5 segundos**. 🐢

## 3. Por que lentidão é pior que erro?

Enquanto espera, a vitrine **prende recursos**: uma thread, uma conexão,
memória. Com poucos usuários, ninguém percebe. Com muitos:

| Usuários por segundo | Cada um espera | Threads presas na vitrine |
| --- | --- | --- |
| 1 | 5 s | ~5 |
| 100 | 5 s | ~500 |

Uma hora as threads acabam e a vitrine **para de responder**, até as páginas
que nem usam recomendações. O erro da Etapa 2 pelo menos era **rápido**.

| Falha do recomendacoes | Efeito na vitrine |
| --- | --- |
| `erro` (Etapa 2) | a página cai, mas **na hora** |
| `lento` (esta etapa) | a página **demora**, e a vitrine vai sendo sufocada |

Na próxima etapa você ensina a vitrine a **não esperar para sempre**.

## 4. Clique em Verificar ✔

> Deixe o painel no modo `lento`: a verificação confere isso (e leva uns 5 s).
