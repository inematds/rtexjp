#!/usr/bin/env python3
"""Desenho-herói (objeto ilustrado grande) no flux2-klein LOCAL, no mesmo estilo flat do avatar, em fundo verde recortado.
Biblioteca reaproveitável: motor/assets/objetos/<nome>.png + motor/assets/objetos/indice.json (nome, prompt, seed, data).
Uso: python3 motor/gerar_objeto.py <nome> "<o objeto, em inglês>" [seed]
     python3 motor/gerar_objeto.py --lista            (mostra o índice)"""
import base64, datetime, json, os, sys, urllib.request
from pathlib import Path
from gerar_avatar import recortar
from PIL import Image
import numpy as np


def tirar_sombra(png):
    """sombra do objeto sobre o verde vira oliva escuro (r≈g, pouco azul) e escapa do recorte: zera esse tom."""
    im = np.array(Image.open(png).convert("RGBA")).astype(int)
    r, g, b, a = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
    oliva = (g > 30) & (b < g * 0.6) & (np.abs(r - g) < 45) & (g >= r - 10)
    im[..., 3] = np.where(oliva, 0, a)
    out = Image.fromarray(im.astype("uint8"))
    out.crop(out.getbbox()).save(png)

AQUI = Path(__file__).resolve().parent
DIR = AQUI / "assets/objetos"
INDICE = DIR / "indice.json"
URL = os.environ.get("RTEXJP_IMG_URL", "http://localhost:8000/generate")
ESTILO = ("flat 2D vector cartoon illustration, single big object centered, {obj}. Clean flat colors in navy blue, royal blue, "
          "steel blue and white, with red only for damage or alert, soft cel shading, smooth dark outlines, modern explainer-video style, "
          "slight 3/4 view with volume, no cast shadow. Solid plain flat bright chroma green background (#00FF00), nothing else, "
          "no text, no letters, no numbers, no logo.")


def gerar(nome, obj, seed=11):
    DIR.mkdir(parents=True, exist_ok=True)
    body = {"model": "flux2-klein", "prompt": ESTILO.format(obj=obj), "width": 1024, "height": 1024, "steps": 4, "seed": seed}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=900).read())
    bruto = DIR / "brutos" / f"{nome}.png"
    bruto.parent.mkdir(exist_ok=True)
    bruto.write_bytes(base64.b64decode(r["image"]))
    recortar(bruto, DIR / f"{nome}.png")
    tirar_sombra(DIR / f"{nome}.png")
    ind = json.loads(INDICE.read_text()) if INDICE.exists() else {}
    ind[nome] = {"prompt": obj, "seed": seed, "data": datetime.date.today().isoformat()}
    INDICE.write_text(json.dumps(ind, ensure_ascii=False, indent=1, sort_keys=True))
    print("OK", nome, DIR / f"{nome}.png", flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--lista"]:
        print(INDICE.read_text() if INDICE.exists() else "{}")
    else:
        gerar(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 11)
