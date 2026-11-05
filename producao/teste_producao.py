#!/usr/bin/env python3
"""Teste da produção com edições falsas: sem render, sem Telegram, sem fila real. `python3 producao/teste_producao.py`"""
import json, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import producao as P  # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="rtexjp-producao-teste-"))
P.AQUI = tmp; P.ESTADO = tmp / "estado.json"; P.LOG = tmp / "producao.log"; P.FILA = tmp / "fila.json"
P.FILA.write_text("[]")
avisos, chamadas = [], []
P.avisa = lambda m: avisos.append(m)
veredito = {"v": "aprovado"}
P.revisar = lambda p: {"veredito": veredito["v"], "motivo": "teste", **({"sugestoes": veredito["s"]} if veredito.get("s") else {})}
falhar = {}


def roda(cmd, timeout, saida=None, cwd=None):
    cmd = [str(x) for x in cmd]
    if cmd[1].endswith("rtexjp.py"):
        pasta = Path(cmd[3]); chamadas.append(("tudo", pasta.name))
        if falhar.get(pasta.name):
            return 1, falhar.pop(pasta.name)
        (pasta / "final.mp4").write_text("v"); return 0, "ok"
    if cmd[0] == "node":
        chamadas.append(("v3", Path(cmd[2]).parent.name)); return 0, "enviado"
    if "--add" in cmd:
        arq = cmd[cmd.index("--add") + 1]; chamadas.append(("fila", Path(arq).parent.name, cmd[cmd.index("--canal") + 1]))
        P.FILA.write_text(P.FILA.read_text() + arq); return 0, f"na fila do {cmd[cmd.index('--canal') + 1]}: x (posição 1)"
    raise AssertionError(cmd)


P.roda = roda


def edicao(nome, canal="lives4"):
    p = tmp / nome; p.mkdir(parents=True)
    pub = {"titulo": "T #shorts", "contexto": "c"} | ({"fila": canal} if canal else {})
    (p / "roteiro.json").write_text(json.dumps({"tema": "tema " + nome, "publicar": pub}))
    return p


def estado(p):
    with P.Estado() as d:
        return d[str(p)]["estado"]


ok = 0
def confere(cond, msg):
    global ok
    assert cond, msg
    ok += 1; print("ok:", msg)


sem = edicao("sem-canal", canal=None)
try:
    P.add(str(sem)); confere(False, "sem publicar.fila deveria recusar")
except SystemExit:
    confere(True, "sem publicar.fila não entra")

a, b = edicao("a"), edicao("b", "lives1")
P.add(str(a)); P.add(str(b))
P.rodada()
confere(sum(1 for c in chamadas if c[0] == "tudo") == 1, "uma montagem por rodada (GPU)")
confere(estado(a) == "na_fila" and estado(b) == "montar", "a foi até a fila; b espera a próxima rodada")
confere(("fila", "a", "lives4") in chamadas and ("v3", "a") in chamadas, "a foi ao v3 e à fila do lives4")
confere(any(m.startswith("Terminei: rtexjp a") for m in avisos), "aviso Terminei no v3")

veredito["v"] = "reprovado"; P.rodada()
confere(estado(b) == "parado" and any(m.startswith("Falhou: rtexjp b") for m in avisos), "b reprovado fica parado com aviso")
n = len(chamadas); P.rodada()
confere(len(chamadas) == n, "parado não anda sozinho")

veredito["v"] = "aprovado"; veredito["s"] = ["3 s: manchete pequena"]
P.retomar(str(b)); P.rodada()
confere(estado(b) == "na_fila" and ("fila", "b", "lives1") in chamadas, "retomado, b vai à fila do lives1")
confere(any(m.startswith("Terminei: rtexjp b") and "SUGESTÃO" in m for m in avisos), "sugestão vai na tarja e não para")
veredito.pop("s")

c = edicao("c"); falhar["c"] = "RuntimeError: CUDA error: out of memory"; P.add(str(c)); P.rodada()
confere(estado(c) == "montar", "falta de memória é passageira: continua em montar")
with P.Estado() as d:
    d[str(c)]["tentar_apos"] = 0
falhar["c"] = "QA reprovou: trocas/min"; P.rodada()
confere(estado(c) == "parado" and any("montagem/QA" in m for m in avisos), "QA reprovado para com aviso")

x = edicao("x"); (x / "final.mp4").write_text("v"); P.FILA.write_text(P.FILA.read_text() + str(x / "final.mp4"))
P.add(str(x)); confere(estado(x) == "na_fila", "edição já na fila entra como na_fila (não duplica)")
try:
    P.add(str(a)); confere(False, "add repetido deveria recusar")
except SystemExit:
    confere(True, "add repetido é recusado")

print(f"\n{ok} conferências ok · pasta {tmp}")
