"""Gera os diagramas "você está aqui" usados no texto das etapas.

  mapa-*.svg     o caminho de uma página: você → vitrine → disjuntor → recomendacoes
  estados-*.svg  os três estados do disjuntor e as transições entre eles

Cada diagrama é sempre o mesmo desenho, com uma parte destacada.
Para regenerar depois de mudar algo:  python3 tutorial/img/gerar_mapas.py
"""
from pathlib import Path

VITRINE, DISJUNTOR, RECOMENDACOES, FALLBACK = "#1971c2", "#e67700", "#2f9e44", "#7048e8"
FALHA, VOCE, APAGADO = "#c92a2a", "#495057", "#adb5bd"
FECHADO, ABERTO, MEIO = "#2f9e44", "#c92a2a", "#e67700"
FUNDO = {VITRINE: "#e7f5ff", DISJUNTOR: "#fff4e6", RECOMENDACOES: "#ebfbee", FALLBACK: "#f3f0ff",
         VOCE: "#f1f3f5", FALHA: "#fff5f5"}

# ---------------------------------------------------------------------------
# Mapa da arquitetura
# ---------------------------------------------------------------------------
# nome: (x, y, largura, altura, linha 1, linha 2, cor quando destacado, tracejado)
CAIXAS = {
    "voce": (15, 118, 100, 54, "Você", "(curl)", VOCE, False),
    "integracao": (250, 113, 160, 64, "integracao.py", "obter_recomendacoes", VITRINE, False),
    "disjuntor": (480, 113, 165, 64, "disjuntor", "circuit_breaker.py", DISJUNTOR, False),
    "fallback": (250, 212, 160, 50, "fallback (plano B)", "Mais vendidos da semana", FALLBACK, True),
    "recomendacoes": (825, 113, 180, 64, "recomendacoes", "porta 8022", RECOMENDACOES, False),
    "painel": (825, 212, 180, 50, "painel de falhas", "normal · erro · lento", RECOMENDACOES, True),
}

# nome: (pontos da linha, rótulo, posição do rótulo, cor quando destacada)
SETAS = {
    "pagina": ([(117, 145), (248, 145)], "GET /produtos/1", (178, 133), VOCE),
    "chamar": ([(412, 145), (478, 145)], "chamar", (445, 133), VITRINE),
    "chamada": ([(647, 145), (823, 145)], "GET /recomendacoes/1", (745, 133), RECOMENDACOES),
    "plano_b": ([(330, 179), (330, 210)], "falhou?", (338, 199), FALLBACK),
    "post": ([(65, 174), (65, 296), (915, 296), (915, 264)], "POST /falhas: você provoca a falha", (480, 289), VOCE),
}

# rótulos extras, destacados junto com uma seta: (texto, x, y, seta)
NOTAS = [("timeout 1 s", 745, 164, "timeout")]

TUDO = set(CAIXAS) | set(SETAS) | {"vitrine", "timeout"}
MAPAS = {
    "mapa-geral": TUDO,
    "mapa-cascata": {"voce", "pagina", "vitrine", "integracao", "chamar", "chamada",
                     "recomendacoes", "painel", "post"},
    "mapa-timeout": {"vitrine", "integracao", "chamar", "chamada", "timeout", "recomendacoes"},
    "mapa-fallback": {"vitrine", "integracao", "plano_b", "fallback"},
    "mapa-disjuntor": {"vitrine", "integracao", "chamar", "disjuntor", "chamada", "timeout",
                       "recomendacoes", "plano_b", "fallback"},
}

# ---------------------------------------------------------------------------
# Mapa dos estados do disjuntor
# ---------------------------------------------------------------------------
ESTADOS = {
    "FECHADO": (40, 100, 200, 60, "tudo passa; falhas são contadas", FECHADO),
    "ABERTO": (415, 100, 200, 60, "recusa na hora, sem chamar", ABERTO),
    "MEIO_ABERTO": (790, 100, 200, 60, "libera UMA chamada de teste", MEIO),
}

TRANSICOES = {
    "abrir": ([(242, 118), (413, 118)], "3 falhas seguidas", (327, 108), ABERTO),
    "testar": ([(617, 118), (788, 118)], "passou tempo_aberto", (702, 108), MEIO),
    "reabrir": ([(788, 145), (617, 145)], "teste falhou", (702, 165), ABERTO),
    "fechar": ([(890, 162), (890, 222), (140, 222), (140, 162)], "teste deu certo", (515, 215), FECHADO),
}

TODOS_ESTADOS = set(ESTADOS) | set(TRANSICOES)
DIAGRAMAS_ESTADOS = {
    "estados-geral": TODOS_ESTADOS,
    "estados-abrir": {"FECHADO", "abrir", "ABERTO"},
    "estados-aberto": {"ABERTO"},
    "estados-meio-aberto": {"ABERTO", "testar", "MEIO_ABERTO"},
    "estados-desfecho": {"MEIO_ABERTO", "fechar", "reabrir", "FECHADO", "ABERTO"},
}


# ---------------------------------------------------------------------------
# Desenho
# ---------------------------------------------------------------------------
def _recuar(origem, destino, distancia):
    """Ponto a `distancia` px antes do destino (a linha termina na base da ponta)."""
    (x1, y1), (x2, y2) = origem, destino
    dx, dy = x2 - x1, y2 - y1
    tamanho = (dx * dx + dy * dy) ** 0.5
    return round(x2 - dx / tamanho * distancia, 1), round(y2 - dy / tamanho * distancia, 1)


def _ponta(origem, destino, cor, escala):
    """Triângulo da ponta da seta, apontando de `origem` para `destino`."""
    (x1, y1), (x2, y2) = origem, destino
    dx, dy = x2 - x1, y2 - y1
    tamanho = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / tamanho, dy / tamanho
    comprimento, largura = 11 * escala, 6 * escala
    bx, by = x2 - ux * comprimento, y2 - uy * comprimento
    vertices = [(x2, y2), (bx - uy * largura, by + ux * largura), (bx + uy * largura, by - ux * largura)]
    return f'<polygon points="{" ".join(f"{round(x, 1)},{round(y, 1)}" for x, y in vertices)}" fill="{cor}"/>'


def _seta(pontos, rotulo, posicao, cor, ligado):
    c = cor if ligado else APAGADO
    tx, ty = posicao
    caminho = " ".join(f"{x},{y}" for x, y in pontos[:-1] + [_recuar(pontos[-2], pontos[-1], 8)])
    vertical = pontos[0][0] == pontos[-1][0] and len(pontos) == 2
    return [
        f'<polyline points="{caminho}" fill="none" stroke="{c}" stroke-width="{3 if ligado else 2}" '
        f'stroke-linejoin="round"/>',
        _ponta(pontos[-2], pontos[-1], c, 1.2 if ligado else 1.0),
        f'<text x="{tx}" y="{ty}" text-anchor="{"start" if vertical else "middle"}" font-size="12" '
        f'fill="{c}" font-weight="{600 if ligado else 400}">{rotulo}</text>',
    ]


def _caixa(x, y, w, h, l1, l2, cor, ligado, tracejado=False, tamanho_l2=12):
    c = cor if ligado else APAGADO
    fundo = FUNDO.get(cor, "#ffffff") if ligado else "#ffffff"
    traco = ' stroke-dasharray="5 3"' if tracejado else ""
    cx = x + w / 2
    return [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fundo}" stroke="{c}" '
        f'stroke-width="{2.5 if ligado else 1.5}"{traco}/>',
        f'<text x="{cx}" y="{y + h / 2 - 3}" text-anchor="middle" font-size="14" font-weight="700" fill="{c}">{l1}</text>',
        f'<text x="{cx}" y="{y + h / 2 + 14}" text-anchor="middle" font-size="{tamanho_l2}" '
        f'fill="{"#495057" if ligado else APAGADO}">{l2}</text>',
    ]


def _inicio(altura, legenda):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1030 {altura}" width="100%" '
        'font-family="Segoe UI, Helvetica, Arial, sans-serif">',
        f'<rect x="1" y="1" width="1028" height="{altura - 2}" rx="10" fill="#ffffff" stroke="#dee2e6"/>',
        f'<text x="515" y="26" text-anchor="middle" font-size="13" fill="#868e96">{legenda}</text>',
    ]


def svg_mapa(destaque: set[str]) -> str:
    partes = _inicio(310, "O caminho de uma página: a vitrine só monta a página depois que as recomendações chegam.")

    # a vitrine é o contêiner que envolve integracao.py, o disjuntor e o fallback
    ligado = "vitrine" in destaque
    c = VITRINE if ligado else APAGADO
    partes.append(f'<rect x="235" y="58" width="430" height="216" rx="12" fill="{"#f8fbff" if ligado else "#ffffff"}" '
                  f'stroke="{c}" stroke-width="{2 if ligado else 1.5}"/>')
    partes.append(f'<text x="252" y="84" font-size="14" font-weight="700" fill="{c}">vitrine · porta 8021</text>')

    for nome, (pontos, rotulo, posicao, cor) in SETAS.items():
        partes += _seta(pontos, rotulo, posicao, cor, nome in destaque)
    for texto, x, y, chave in NOTAS:
        ligado = chave in destaque
        partes.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="12" '
                      f'fill="{FALHA if ligado else APAGADO}" font-weight="{600 if ligado else 400}">{texto}</text>')
    for nome, (x, y, w, h, l1, l2, cor, tracejado) in CAIXAS.items():
        partes += _caixa(x, y, w, h, l1, l2, cor, nome in destaque, tracejado)

    partes.append('</svg>')
    return "\n".join(partes) + "\n"


def svg_estados(destaque: set[str]) -> str:
    partes = _inicio(250, "Os três estados do disjuntor (circuit_breaker.py)")
    for nome, (pontos, rotulo, posicao, cor) in TRANSICOES.items():
        partes += _seta(pontos, rotulo, posicao, cor, nome in destaque)
    for nome, (x, y, w, h, descricao, cor) in ESTADOS.items():
        ligado = nome in destaque
        c = cor if ligado else APAGADO
        fundo = {FECHADO: "#ebfbee", ABERTO: "#fff5f5", MEIO: "#fff4e6"}[cor] if ligado else "#ffffff"
        partes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="30" fill="{fundo}" stroke="{c}" '
                      f'stroke-width="{2.5 if ligado else 1.5}"/>')
        partes.append(f'<text x="{x + w / 2}" y="{y + h / 2 + 6}" text-anchor="middle" font-size="17" '
                      f'font-weight="700" fill="{c}">{nome}</text>')
        partes.append(f'<text x="{x + w / 2}" y="{y - 22}" text-anchor="middle" font-size="12" '
                      f'fill="{"#495057" if ligado else APAGADO}">{descricao}</text>')
    partes.append('</svg>')
    return "\n".join(partes) + "\n"


if __name__ == "__main__":
    pasta = Path(__file__).parent
    for nome, destaque in MAPAS.items():
        (pasta / f"{nome}.svg").write_text(svg_mapa(destaque), encoding="utf-8")
        print(f"gerado {nome}.svg")
    for nome, destaque in DIAGRAMAS_ESTADOS.items():
        (pasta / f"{nome}.svg").write_text(svg_estados(destaque), encoding="utf-8")
        print(f"gerado {nome}.svg")
