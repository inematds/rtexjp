#!/usr/bin/env python3
"""Imagem de cena no flux2-klein LOCAL (inemaimg :8000). Uso: python3 motor/gerar_imagem.py <saida.png> "<prompt>" [LxA] [seed]"""
import base64, json, sys, urllib.request
out, prompt = sys.argv[1], sys.argv[2]
w, h = map(int, (sys.argv[3] if len(sys.argv) > 3 else "1152x784").split("x"))
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 11
body = {"model": "flux2-klein", "prompt": prompt, "width": w, "height": h, "steps": 4, "seed": seed}
req = urllib.request.Request("http://localhost:8000/generate", data=json.dumps(body).encode(), headers={"content-type": "application/json"})
open(out, "wb").write(base64.b64decode(json.loads(urllib.request.urlopen(req, timeout=900).read())["image"]))
print("OK", out)
