"""Etapa 2: falha em cascata (o recomendacoes com erro derruba a vitrine)."""
import circuito
from verificador import executar, verificacao


@verificacao("o painel de falhas do recomendacoes está no modo 'erro'")
def modo_erro():
    modo = circuito.modo_atual()
    assert modo == "erro", (
        f"o modo atual é {modo!r}. Clique em ▶ Executar no bloco 'curl -s -X POST localhost:8022/falhas ...' desta etapa."
    )


@verificacao("com o recomendacoes em erro, a vitrine também falha (HTTP 502)")
def vitrine_cai():
    status, corpo, _ = circuito.pagina()
    assert status == 502, f"esperado HTTP 502, veio HTTP {status}: {corpo}"


executar(parar_na_primeira_falha=True)
