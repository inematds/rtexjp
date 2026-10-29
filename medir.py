#!/usr/bin/env python3
"""QA automático do rtexjp. Uso: python3 medir.py <pasta-da-edicao>
Mede no final.mp4: duração, wpm (fala e relógio), LUFS, trocas visuais/min (|Δluminância| médio ≥ 10 entre quadros a 1 fps,
108x192), isca (opinião: opções no CTA + plantadas antes, CTA sem promessa; legado: palavra), prova até 20 s, cartão final, silêncio antes da máxima, nada abaixo de 80% na tela (amostra),
grep de fonte proibida = 0. Grava build/qa.json + qa.md + contact.jpg."""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parent
# padrão montado em partes para o próprio arquivo não casar com ele
PROIBIDO = "|".join(["jp ?la" + "bs", "thejp" + "labs", "lobo fr" + "anco", "insta" + r"gram\.com/(reel|p)/", "rtex-an" + "alise"])


def run(*a):
    return subprocess.run([str(x) for x in a], capture_output=True, text=True)


def main(pasta):
    pasta = Path(pasta).resolve()
    mp4 = pasta / "final.mp4"
    rot = json.loads((pasta / "roteiro.json").read_text())
    cena = json.loads((pasta / "build/cena.json").read_text())
    q = {}
    # duração e formato
    pr = json.loads(run("ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,codec_type,r_frame_rate", "-of", "json", mp4).stdout)
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    q["duracao_s"] = round(float(pr["format"]["duration"]), 2)
    q["resolucao"] = f"{v['width']}x{v['height']}"
    q["fps"] = v["r_frame_rate"]
    # wpm
    pal = sum(len(b["fala"].split()) for b in rot["blocos"])
    fala = sum(b["fala_fim"] - b["fala_ini"] for b in cena["blocos"])
    rel = cena["blocos"][-1]["fala_fim"] - cena["blocos"][0]["fala_ini"]
    q["palavras"] = pal
    q["wpm_fala"] = round(pal / fala * 60)
    q["wpm_relogio"] = round(pal / rel * 60)
    # LUFS
    e = run("ffmpeg", "-nostats", "-i", mp4, "-filter_complex", "ebur128=peak=true", "-f", "null", "-").stderr
    q["lufs"] = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1])
    q["true_peak_dbfs"] = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)[-1])
    # trocas visuais/min
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(mp4), "-vf", "fps=1,scale=108:192,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 192, 108).astype(float)
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    mins = q["duracao_s"] / 60
    q["trocas_min_10"] = round(int((d >= 10).sum()) / mins, 1)
    q["trocas_min_20"] = round(int((d >= 20).sum()) / mins, 1)
    q["trocas_min_6"] = round(int((d >= 6).sum()) / mins, 1)
    # isca: opinião (pergunta + opções) ou legado (palavra + entregável)
    isca = rot["isca"]
    opiniao = isca.get("tipo") == "opiniao"
    quentes = isca["opcoes"] if opiniao else [isca["palavra"]]
    cta = cena["blocos"][-1]
    txt = lambda b: (b["fala"] + json.dumps(b.get("tela", {}), ensure_ascii=False)).lower()
    plant = next((b for b in cena["blocos"][:-1] if any(w.lower() in txt(b) for w in quentes)), None)
    q["isca"] = ("opinião: " + isca.get("pergunta", "") + " " + "/".join(quentes)) if opiniao else isca["palavra"] + " (legado)"
    q["isca_no_cta"] = all(w.lower() in cta["fala"].lower() for w in quentes)
    q["isca_plantada_s_antes_do_cta"] = round(cta["fala_ini"] - plant["fala_ini"], 1) if plant else None
    if opiniao:
        q["cta_sem_promessa"] = not re.search(r"te mando|eu mando|\bmando\b|envio|manda o link|comenta \w+ que|\bdm\b", cta["fala"] + json.dumps(cta.get("tela", {}), ensure_ascii=False), re.I)
    pv = next((b for b in cena["blocos"] if b["tipo"] == "autoridade"), None)
    q["prova_em_s"] = round(pv["fala_ini"], 1) if pv else None
    q["cartao_final_s"] = round(cta["fim"] - cta["ini"], 2)
    q["hold_depois_da_fala_s"] = round(cta["fim"] - cta["fala_fim"], 2)
    # silêncio antes da máxima (na mixagem final)
    mx = next(b for b in cena["blocos"] if b["tipo"] == "maxima")
    a0 = mx["fala_ini"] - 1.2
    s = run("ffmpeg", "-ss", f"{a0:.2f}", "-t", "1.6", "-i", mp4, "-af", "silencedetect=n=-45dB:d=0.3", "-f", "null", "-").stderr
    sd = re.findall(r"silence_duration: ([\d.]+)", s)
    q["silencio_antes_maxima_s"] = round(max(map(float, sd)), 2) if sd else 0.0
    # grep da fonte proibida
    g = run("grep", "-riIE", PROIBIDO, R, "--exclude-dir=node_modules")
    q["grep_fonte"] = len([l for l in g.stdout.splitlines() if l.strip()])
    # contact sheet: 1 quadro a cada 2,5 s
    n = int(q["duracao_s"] // 2.5) + 1
    cols = 7
    rows = (n + cols - 1) // cols
    run("ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf", f"fps=0.4,scale=216:384,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.6,tile={cols}x{rows}:padding=4:color=0x222222",
        "-frames:v", "1", "-q:v", "3", pasta / "contact.jpg")
    # critérios
    crit = {
        "duracao 60–90 s": 60 <= q["duracao_s"] <= 90,
        "1080x1920": q["resolucao"] == "1080x1920",
        "wpm fala 160–190": 160 <= q["wpm_fala"] <= 190,
        "LUFS −14 ±1": abs(q["lufs"] + 14) <= 1,
        "trocas/min ≥ 17 (Δ≥10)": q["trocas_min_10"] >= 17,
        "isca no CTA e plantada antes": q["isca_no_cta"] and bool(q["isca_plantada_s_antes_do_cta"]) and q["isca_plantada_s_antes_do_cta"] >= 10,
        "prova até 20 s": q["prova_em_s"] is not None and q["prova_em_s"] <= 20,
        "cartão final ≥ 8 s": q["cartao_final_s"] >= 8,
        "silêncio 0,5–0,9 s antes da máxima": 0.45 <= q["silencio_antes_maxima_s"] <= 1.0,
        "grep de fonte = 0": q["grep_fonte"] == 0,
    }
    if opiniao:
        crit["CTA sem promessa de entrega"] = q["cta_sem_promessa"]
    if str(rot.get("versao", "")).endswith("/3"):
        crit.update(beleza(pasta, cena, q))
    q["criterios"] = crit
    q["aprovado"] = all(crit.values())
    (pasta / "build/qa.json").write_text(json.dumps(q, ensure_ascii=False, indent=1))
    md = [f"# QA — {rot['id']}", "", "| medida | valor |", "|---|---|"] + [f"| {k} | {v} |" for k, v in q.items() if k not in ("criterios",)]
    md += ["", "| critério | ok |", "|---|---|"] + [f"| {k} | {'✅' if v else '❌'} |" for k, v in crit.items()]
    (pasta / "qa.md").write_text("\n".join(md) + "\n")
    for k, v in q.items():
        if k != "criterios":
            print(f"{k:32s} {v}")
    for k, v in crit.items():
        print(("OK  " if v else "FALHA ") + k)
    return q["aprovado"]


LIM = {"manchete_px": 96, "texto_px": 30, "area": 0.55, "contraste": 4.5, "avatar": 0.38}


def beleza(pasta, cena, q):
    """Portão de beleza (visual v1.2): amostra ini+0,6 s e o meio de cada bloco no palco e lê do DOM
    letra mínima, área ocupada no quadro útil (0–80 %), contraste WCAG do texto e altura do avatar."""
    ts = sorted({round(min(b["ini"] + 0.6, b["fim"] - 0.05), 2) for b in cena["blocos"]} |
                {round((b["ini"] + b["fim"]) / 2, 2) for b in cena["blocos"]})
    run("node", R / "motor/render.mjs", pasta / "build", "--quadros", ",".join(map(str, ts)))
    med = json.loads((pasta / "quadros/medidas.json").read_text())
    ruim = lambda f: [m["t"] for m in med if f(m)]
    falhas = {
        "manchete": ruim(lambda m: m["manchete_px_min"] is not None and m["manchete_px_min"] < LIM["manchete_px"]),
        "texto": ruim(lambda m: m["texto_px_min"] is not None and m["texto_px_min"] < LIM["texto_px"]),
        "area": ruim(lambda m: m["area_frac"] < LIM["area"]),
        "contraste": ruim(lambda m: m["contraste_min"] is not None and m["contraste_min"] < LIM["contraste"]),
        "avatar": ruim(lambda m: m["avatar_frac"] < LIM["avatar"]),
    }
    q["beleza_amostras"] = len(med)
    q["beleza_manchete_px_min"] = min((m["manchete_px_min"] for m in med if m["manchete_px_min"]), default=None)
    q["beleza_texto_px_min"] = min((m["texto_px_min"] for m in med if m["texto_px_min"]), default=None)
    q["beleza_area_min"] = min(m["area_frac"] for m in med)
    q["beleza_contraste_min"] = min((m["contraste_min"] for m in med if m["contraste_min"]), default=None)
    q["beleza_avatar_min"] = min(m["avatar_frac"] for m in med)
    q["beleza_falhas"] = {k: v for k, v in falhas.items() if v}
    return {"manchete ≥ 96 px": not falhas["manchete"], "rótulos/texto ≥ 30 px": not falhas["texto"],
            "área ocupada ≥ 55 % do quadro útil": not falhas["area"], "contraste do texto ≥ 4,5:1": not falhas["contraste"],
            "avatar ≥ 38 % da altura": not falhas["avatar"]}


def so_grep():
    g = run("grep", "-rniIE", PROIBIDO, R, "--exclude-dir=node_modules")
    linhas = [l for l in g.stdout.splitlines() if l.strip()]
    for l in linhas:
        print(l[:160])
    print("grep_fonte", len(linhas))
    return not linhas


if __name__ == "__main__":
    if sys.argv[1:] == ["--grep"]:
        sys.exit(0 if so_grep() else 1)
    sys.exit(0 if main(sys.argv[1]) else 1)
