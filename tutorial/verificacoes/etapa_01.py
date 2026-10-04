"""Etapa 1: ambiente no ar e falhas observadas."""
from verificador import executar, http, verificacao

VITRINE = "http://localhost:8021"
RECOMENDACOES = "http://localhost:8022"


@verificacao("vitrine responde em http://localhost:8021/saude")
def vitrine_no_ar():
    status, _ = http("GET", f"{VITRINE}/saude")
    assert status == 200, f"/saude devolveu HTTP {status}."


@verificacao("recomendacoes responde em http://localhost:8022/saude")
def recomendacoes_no_ar():
    status, _ = http("GET", f"{RECOMENDACOES}/saude")
    assert status == 200, f"/saude devolveu HTTP {status}."


@verificacao("a vitrine já chamou o serviço de recomendações ao menos uma vez")
def houve_chamadas():
    _, corpo = http("GET", f"{RECOMENDACOES}/estatisticas")
    assert corpo.get("requisicoes_recebidas", 0) >= 1, (
        "nenhuma requisição chegou ao recomendacoes. Rode os comandos 'curl' desta etapa."
    )


@verificacao("o recomendacoes voltou ao modo normal")
def modo_normal():
    _, corpo = http("GET", f"{RECOMENDACOES}/falhas")
    assert corpo.get("modo") == "normal", (
        f"o modo atual é {corpo.get('modo')!r}. Rode o último comando da etapa para voltar ao normal."
    )


executar(parar_na_primeira_falha=True)
