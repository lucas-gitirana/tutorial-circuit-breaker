"""Etapa 1: os dois serviços estão no ar."""
from verificador import executar, http, verificacao

SERVICOS = {"vitrine": 8021, "recomendacoes": 8022}

for nome, porta in SERVICOS.items():
    def checar(porta=porta):
        status, _ = http("GET", f"http://localhost:{porta}/saude")
        assert status == 200, f"/saude devolveu HTTP {status}."
    verificacao(f"{nome} responde em http://localhost:{porta}/saude")(checar)


executar(parar_na_primeira_falha=True)
