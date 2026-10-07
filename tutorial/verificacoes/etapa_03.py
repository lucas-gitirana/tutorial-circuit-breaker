"""Etapa 3: falha em cascata por lentidão (a vitrine fica refém da dependência)."""
import circuito
from verificador import executar, verificacao


@verificacao("o painel de falhas do recomendacoes está no modo 'lento'")
def modo_lento():
    modo = circuito.modo_atual()
    assert modo == "lento", (
        f"o modo atual é {modo!r}. Clique em ▶ Executar no bloco 'curl -s -X POST localhost:8022/falhas ...' desta etapa."
    )


@verificacao("com o recomendacoes lento, a página da vitrine também fica lenta (~5 s)")
def vitrine_lenta():
    status, corpo, segundos = circuito.pagina()
    assert segundos >= 4, f"a página levou só {segundos:.1f} s (HTTP {status}): {corpo}"


executar(parar_na_primeira_falha=True)
