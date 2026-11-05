#!/usr/bin/env python3
"""Espera UMA edição sair da produção — é a última fase do /rtexjp no inemaccbot (05/11/2026; cópia do esperar do r7ex).

Só lê `producao/estado.json` (quem anda é o timer rtexjp-producao); não mexe em nada.
  na_fila → imprime o recibo (pasta, estado, canal, título) e sai 0
  parado  → imprime o motivo e sai 1
  outro   → imprime o estado a cada volta (o bot vê o log andando) e espera

Uso: esperar.py <pasta> [--intervalo 60]
O teto de tempo é do bot (`espera.timeout` no flow.json), não daqui.
"""
import json, os, sys, time
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ESTADO = Path(os.environ.get("RTEXJP_ESTADO", AQUI / "estado.json"))


def ler(pasta):
    try:
        return json.loads(ESTADO.read_text()).get(pasta)
    except (OSError, ValueError):
        return None                                # arquivo sendo trocado agora: tenta na próxima volta


def publicar(pasta):
    try:
        return json.loads((Path(pasta) / "roteiro.json").read_text()).get("publicar") or {}
    except Exception:
        return {}


def main(argv):
    if not argv or argv[0].startswith("-"):
        sys.exit("uso: esperar.py <pasta> [--intervalo 60]")
    pasta = str(Path(argv[0]).resolve())
    intervalo = int(argv[argv.index("--intervalo") + 1]) if "--intervalo" in argv else 60
    ultimo = None
    while True:
        it = ler(pasta)
        if it is None and ESTADO.exists():
            print(f"erro: {Path(pasta).name} não está na produção (producao.py --add não rodou?)", flush=True)
            return 1
        st = (it or {}).get("estado")
        if st == "na_fila":
            pub = publicar(pasta)
            frente = (Path(pasta) / "FRENTE").exists()
            fim = Path(pasta) / "BOT-FIM.md"
            linhas = [f"Terminei: rtexjp {Path(pasta).name} revisado e na fila do {pub.get('fila', 'lives11')}"
                      + (" (na frente)" if frente else ""),
                      f"Título: {pub.get('titulo', '')}",
                      "A fila publica 1 a cada 2 h (9 h–21 h) e avisa no v3 com o link."]
            if it.get("sugestoes"):
                linhas.append("🟥 Sugestão do revisor: " + " | ".join(it["sugestoes"]))
            fim.write_text("\n".join(linhas) + "\n")
            print(f"pasta: {pasta}")
            print("estado: na_fila")
            print(f"fim: {fim}", flush=True)
            return 0
        if st == "parado":
            print(f"erro: produção parou — {it.get('motivo', 'sem motivo')}", flush=True)
            print(f"(depois de corrigir: python3 producao/producao.py --retomar {Path(pasta).name})", flush=True)
            return 1
        if st != ultimo:
            print(f"{datetime.now():%H:%M} estado: {st}", flush=True)
            ultimo = st
        else:
            print(f"{datetime.now():%H:%M} ainda {st}", flush=True)   # log andando = vivo para o bot
        time.sleep(intervalo)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
