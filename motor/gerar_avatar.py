#!/usr/bin/env python3
"""Gera as poses do avatar ilustrado do Nei no flux2-klein LOCAL (servidor inemaimg :8000) com a foto de referência,
em fundo verde chapado, e recorta o fundo (flood fill a partir das bordas) -> motor/avatar/<pose>.png (RGBA).
Uso: python3 motor/gerar_avatar.py [pose ...]   (sem argumento = todas)"""
import base64, json, os, sys, urllib.request
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np
from collections import deque

AQUI = Path(__file__).resolve().parent
REF = Path(os.environ.get("RTEXJP_AVATAR_REF", Path.home() / "projetos/inema-referencias/nei-avatar.jpg")).expanduser()
URL = os.environ.get("RTEXJP_IMG_URL", "http://localhost:8000/generate")
# traços e roupa do personagem (troque junto com RTEXJP_AVATAR_REF quando o avatar for outra pessoa)
PESSOA = os.environ.get("RTEXJP_AVATAR_DESC", "same face, black baseball cap, black rectangular glasses, short grey beard, friendly. "
                        "He wears a plain light steel-blue t-shirt (soft sky blue, like #93c5fd)")
BASE = ("flat 2D vector cartoon illustration of the person from the reference photo: " + PESSOA.replace("{", "{{").replace("}", "}}") + ". "
        "Waist-up bust, centered, {pose}. Clean flat colors, soft cel shading, "
        "smooth outlines, modern explainer-video character style. Solid plain flat bright chroma green background (#00FF00), nothing else, "
        "no text, no letters, no logo.")
POSES = {
    "bracos": "arms crossed over the chest, confident smile",
    "queixo": "one hand on his chin, thinking, curious look, looking slightly up",
    "apontando": "pointing his index finger up, explaining, mouth slightly open",
    "segurando": "holding a closed blue folder against his chest with both hands, smiling",
    "surpreso": "both hands open near his face, surprised, eyebrows raised",
    "mostrando": "pointing down to the bottom of the frame with one hand, inviting, smiling",
}


def gerar(nome, pose, seed=7):
    ref = base64.b64encode(REF.read_bytes()).decode()
    body = {"model": "flux2-klein", "prompt": BASE.format(pose=pose), "images": [ref], "width": 768, "height": 1024, "steps": 4, "seed": seed}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=900).read())
    bruto = AQUI / "avatar/brutos" / f"{nome}.png"
    bruto.parent.mkdir(parents=True, exist_ok=True)
    bruto.write_bytes(base64.b64decode(r["image"]))
    return bruto


def recortar(bruto, saida):
    im = np.array(Image.open(bruto).convert("RGB")).astype(int)
    h, w, _ = im.shape
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    verde = (g > 120) & (g > r + 50) & (g > b + 50)
    fundo = np.zeros((h, w), bool)
    q = deque([(y, x) for y in (0, h - 1) for x in range(w)] + [(y, x) for x in (0, w - 1) for y in range(h)])
    while q:
        y, x = q.popleft()
        if 0 <= y < h and 0 <= x < w and not fundo[y, x] and verde[y, x]:
            fundo[y, x] = True
            q.extend(((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)))
    fundo |= (g > 90) & (g > r + 45) & (g > b + 45)   # verde preso entre mãos/braços (não ligado à borda)
    alfa = Image.fromarray(np.where(fundo, 0, 255).astype("uint8")).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    rgb = im.copy()
    borda = (g > r) & (g > b)  # tira o verde que vaza na borda
    rgb[..., 1] = np.where(borda, np.maximum(r, b), g)
    out = Image.fromarray(rgb.astype("uint8")).convert("RGBA")
    out.putalpha(alfa)
    out = out.crop(out.getbbox())
    out.save(saida)


if __name__ == "__main__":
    alvo = sys.argv[1:] or list(POSES)
    for n in alvo:
        b = gerar(n, POSES[n])
        recortar(b, AQUI / "avatar" / f"{n}.png")
        print("OK", n, flush=True)
