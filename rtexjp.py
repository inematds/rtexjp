#!/usr/bin/env python3
"""rtexjp — motor de reels 9:16 no padrão rtexjp (reel ilustrado roxo).

Uso:  python3 rtexjp.py <passo> <pasta-da-edicao>
Passos (em ordem):  checar · voz · cena · render · mix · qa · tudo
  checar  valida o roteiro.json pelas regras do formato (sem gosto)
  voz     um WAV por bloco (inemavox chatterbox, voz do Nei), apara, acelera até 1,15x, junta com respiros
          e o silêncio antes da máxima; Whisper local dá o tempo de cada palavra -> build/tempos.json
  cena    roteiro + tempos -> build/cena.json (o que o palco desenha)
  render  palco.html quadro a quadro (Playwright) -> build/video.mp4 (mudo)
  mix     voz + cama musical (para no silêncio da máxima) + loudnorm -14 LUFS -> final.mp4
  qa      medir.py -> build/qa.json + contact.jpg
"""
import json, re, subprocess, sys, difflib
from pathlib import Path

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / "motor"))
INEMAVOX = Path.home() / "projetos/inemavox"
VOZ_REF = Path.home() / "projetos/timesmkt3/media/voice-refs/nei.wav"
ALVO_WPM = 178
RESPIRO = 0.22

ORDEM = ["tese", "autoridade", "tese", "virada", "metodo", "ressalva", "maxima", "cta"]


def sh(*a, **k):
    return subprocess.run([str(x) for x in a], check=True, **k)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def ler(pasta):
    return json.loads((pasta / "roteiro.json").read_text())


# ---------------------------------------------------------------- checar
def checar(pasta):
    r = ler(pasta)
    erros, avisos = [], []
    bl = r["blocos"]
    tipos = [b["tipo"] for b in bl]
    if tipos[0] != "tese":
        erros.append("o 1º bloco tem que ser a tese (escrita no quadro 0)")
    if tipos[-1] != "cta":
        erros.append("o último bloco tem que ser o CTA (sem despedida)")
    if "maxima" not in tipos or tipos.index("maxima") != len(tipos) - 2:
        erros.append("a máxima vem imediatamente antes do CTA")
    if "ressalva" not in tipos or tipos.index("ressalva") > tipos.index("maxima"):
        erros.append("falta a ressalva honesta antes da máxima")
    if "virada" not in tipos or tipos.index("virada") > tipos.index("metodo"):
        erros.append("o índice (virada) vem antes da 1ª peça")
    met = [b for b in bl if b["tipo"] == "metodo"]
    if not 2 <= len(met) <= 5:
        erros.append(f"método com {len(met)} peças (2–5)")
    vir = next((b for b in bl if b["tipo"] == "virada"), None)
    if vir and len(vir["cena"]["params"]["itens"]) != len(met):
        erros.append("índice anunciado ≠ número de peças")
    for b in bl:
        f = b["fala"]
        if re.search(r"\d", f):
            erros.append(f"[{b['id']}] algarismo na fala (escreva por extenso): {f}")
        if "!" in f:
            erros.append(f"[{b['id']}] exclamação na fala")
        for fr in re.split(r"[.?:]", f):
            if len(fr.split()) > 16:
                avisos.append(f"[{b['id']}] frase longa ({len(fr.split())} palavras)")
        if b.get("fonte") and b["fonte"] not in {x["id"] for x in r["fontes"]}:
            erros.append(f"[{b['id']}] fonte '{b['fonte']}' não existe em fontes[]")
        for w in b.get("destaque_fala", []):
            if w.lower() not in f.lower():
                erros.append(f"[{b['id']}] destaque '{w}' não está na fala")
        for k, w in b.get("cena", {}).get("params", {}).get("gatilhos", {}).items():
            if w.lower() not in f.lower():
                erros.append(f"[{b['id']}] gatilho {k}='{w}' não está na fala")
    # números na tela só com fonte
    for b in bl:
        p = json.dumps(b.get("cena", {}), ensure_ascii=False) + json.dumps(b.get("tela", {}), ensure_ascii=False)
        if re.search(r"\d{2,}", re.sub(r"\b0\d\b", "", p)) and not b.get("fonte") and b["tipo"] not in ("cta", "virada", "tese"):
            erros.append(f"[{b['id']}] número na tela sem fonte")
    # isca = tese, plantada antes, presente no CTA
    isca = r["isca"]["palavra"]
    if isca not in bl[-1]["fala"]:
        erros.append("a palavra-isca não está na fala do CTA")
    antes = [b for b in bl[:-1] if isca.lower() in (b["fala"] + json.dumps(b.get("tela", {}))).lower()]
    if not antes:
        erros.append("a palavra-isca não foi plantada antes do CTA")
    elif bl.index(antes[0]) > 3:
        avisos.append("a palavra-isca aparece tarde (plante nos primeiros blocos)")
    if not isca.isascii() or not isca.isupper():
        erros.append("palavra-isca: caixa alta, sem acento")
    mx = bl[-2]
    if not 0.5 <= mx.get("silencio_antes_s", 0) <= 0.9:
        erros.append("a máxima precisa de 0,5–0,9 s de silêncio antes")
    if not 5 <= bl[-1].get("hold_s", 0) <= 9:
        avisos.append("hold depois da fala do CTA: 5–9 s (cartão final inteiro fica ~8–10 s)")
    pal = sum(len(b["fala"].split()) for b in bl)
    if not 160 <= pal <= 270:
        avisos.append(f"{pal} palavras (alvo 60–90 s ≈ 170–260)")
    print(f"{len(bl)} blocos · {len(met)} peças · {pal} palavras · isca {isca}")
    for a in avisos:
        print("AVISO", a)
    for e in erros:
        print("ERRO ", e)
    print("OK" if not erros else f"REPROVADO ({len(erros)} erros)")
    return not erros


# ---------------------------------------------------------------- voz
def _trim(src, dst):
    # apara silêncio das pontas (o chatterbox deixa 0,3–0,5 s)
    # pontas fora; pausas internas encurtadas para no máximo ~0,16 s (respiros cortados, ritmo do formato)
    f = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,"
         "silenceremove=stop_periods=-1:stop_duration=0.16:stop_threshold=-42dB:stop_silence=0.16,"
         "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse")
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", f, "-ar", "44100", "-ac", "1", dst)


def _volume(p):
    o = subprocess.run(["ffmpeg", "-i", str(p), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.search(r"mean_volume: (-?[\d.]+)", o).group(1))


def voz(pasta, so=None):
    from whisper import transcrever, norm
    r = ler(pasta)
    vd = pasta / "voz"
    vd.mkdir(exist_ok=True)
    for i, b in enumerate(r["blocos"]):
        bruto = vd / f"{i:02d}-{b['id']}.raw.wav"
        out = vd / f"{i:02d}-{b['id']}"
        if bruto.exists() and not (so and b["id"] in so):
            pass  # reaproveita o TTS já gerado; só refaz o tratamento
        else:
          sh(INEMAVOX / "venv/bin/python", "tts_direct.py", "--text", b.get("fala_tts", b["fala"]), "--lang", "pt", "--engine", "chatterbox",
           "--ref", VOZ_REF, "--outdir", out, "--exaggeration", "0.6", "--cfg-weight", "0.6", cwd=INEMAVOX, stdout=subprocess.DEVNULL)
          (out / "generated.wav").rename(bruto)
        if _volume(bruto) < -50:
            raise SystemExit(f"voz muda no bloco {b['id']} (chatterbox gravou silêncio)")
        aparado = vd / f"{i:02d}-{b['id']}.trim.wav"
        _trim(bruto, aparado)
        n = len(b["fala"].split())
        wpm = n / dur(aparado) * 60
        alvo = ALVO_WPM + (12 if b["tipo"] == "cta" else 0) - (14 if b["tipo"] == "maxima" else 0)
        fator = max(1.0, min(1.15, alvo / wpm))
        sh("ffmpeg", "-y", "-loglevel", "error", "-i", aparado, "-af", f"atempo={fator:.3f}", vd / f"{i:02d}-{b['id']}.wav")
        print(f"voz {b['id']:9s} {n:3d} pal  {wpm:5.0f} wpm cru  x{fator:.2f}", flush=True)
    # junta: respiro entre blocos; silêncio real antes da máxima
    build = pasta / "build"
    build.mkdir(exist_ok=True)
    partes, t, blocos = [], 0.0, []
    lst = build / "voz.txt"
    linhas = []
    sil = lambda s: build / f"sil_{int(s*1000)}.wav"
    for i, b in enumerate(r["blocos"]):
        gap = b.get("silencio_antes_s", RESPIRO if i else 0.0)
        if gap:
            if not sil(gap).exists():
                sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono", "-t", f"{gap}", sil(gap))
            linhas.append(f"file '{sil(gap)}'")
            t += gap
        w = vd / f"{i:02d}-{b['id']}.wav"
        d = dur(w)
        blocos.append({"id": b["id"], "ini": round(t, 3), "fim": round(t + d, 3), "wav": str(w)})
        linhas.append(f"file '{w}'")
        t += d
    lst.write_text("\n".join(linhas) + "\n")
    sh("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-ar", "44100", "-ac", "1", build / "voz.wav")
    # tempo por palavra: Whisper por bloco, alinhado à fala escrita
    out = []
    for b, info in zip(r["blocos"], blocos):
        ws = transcrever(info["wav"], build / "wh" / b["id"], palavras=True)
        orig = b["fala"].split()
        alvo_n = [(norm(w) or [""])[0] for w in orig]
        wh = [(norm(w["word"]) or [""])[0] for w in ws]
        m = difflib.SequenceMatcher(None, alvo_n, wh, autojunk=False)
        tempos = [None] * len(orig)
        for a, bb, sz in m.get_matching_blocks():
            for k in range(sz):
                tempos[a + k] = (ws[bb + k]["start"], ws[bb + k]["end"])
        d = info["fim"] - info["ini"]
        # interpola o que o Whisper não casou
        idx = [k for k, x in enumerate(tempos) if x]
        for k in range(len(orig)):
            if tempos[k]:
                continue
            ant = max([j for j in idx if j < k], default=None)
            pro = min([j for j in idx if j > k], default=None)
            t0 = tempos[ant][1] if ant is not None else 0.0
            t1 = tempos[pro][0] if pro is not None else d
            na = (pro if pro is not None else len(orig)) - (ant if ant is not None else -1) - 1
            pos = k - (ant if ant is not None else -1) - 1
            s = t0 + (t1 - t0) * pos / max(na, 1)
            tempos[k] = (s, s + (t1 - t0) / max(na, 1))
        casou = len(idx) / len(orig)
        info["palavras"] = [{"w": w, "ini": round(info["ini"] + a, 3), "fim": round(info["ini"] + z, 3)} for w, (a, z) in zip(orig, tempos)]
        info["casou"] = round(casou, 2)
        info["whisper"] = " ".join(x["word"].strip() for x in ws)
        print(f"whisper {b['id']:9s} casou {casou:4.0%} | {info['whisper'][:90]}")
        out.append(info)
    (build / "tempos.json").write_text(json.dumps({"duracao_voz": round(t, 3), "blocos": out}, ensure_ascii=False, indent=1))
    print(f"voz total {t:.1f} s -> {build/'tempos.json'}")


# ---------------------------------------------------------------- cena
def cena(pasta):
    r = ler(pasta)
    tp = json.loads((pasta / "build/tempos.json").read_text())
    tb = {b["id"]: b for b in tp["blocos"]}
    blocos = []
    # início visual de cada bloco: metade do respiro antes da fala; com silêncio (máxima), o silêncio inteiro já é do bloco (tela vazia)
    ini = []
    for i, b in enumerate(r["blocos"]):
        t = tb[b["id"]]
        if i == 0:
            ini.append(0.0)
        elif b.get("silencio_antes_s"):
            ini.append(t["ini"] - b["silencio_antes_s"])
        else:
            ini.append(t["ini"] - (t["ini"] - tb[r["blocos"][i - 1]["id"]]["fim"]) / 2)
    for i, b in enumerate(r["blocos"]):
        t = tb[b["id"]]
        fim_vis = ini[i + 1] if i + 1 < len(r["blocos"]) else t["fim"] + b.get("hold_s", 0)
        g = {}
        for k, w in b.get("cena", {}).get("params", {}).get("gatilhos", {}).items():
            hit = next((p for p in t["palavras"] if re.sub(r"\W", "", p["w"]).lower().startswith(w.lower())), None)
            g[k] = hit["ini"] if hit else t["ini"]
        for k in ("gatilho_l2",):
            w = b.get("cena", {}).get("params", {}).get(k)
            if w:
                hits = [p for p in t["palavras"] if re.sub(r"\W", "", p["w"]).lower() == w.lower()]
                g["l2"] = hits[-1]["ini"] if hits else t["ini"]
        for st in b.get("cena", {}).get("params", {}).get("stingers", []):
            hit = next((p for p in t["palavras"] if re.sub(r"\W", "", p["w"]).lower().startswith(st["em"].lower())), None)
            st["t"] = round((hit["ini"] if hit else t["ini"]) - 0.05, 3)
        blocos.append({**b, "ini": round(ini[i], 3), "fala_ini": t["ini"], "fala_fim": t["fim"], "fim": round(fim_vis, 3),
                       "palavras": t["palavras"], "g": g})
    fontes = {f["id"]: f for f in r["fontes"]}
    c = {"duracao": round(blocos[-1]["fim"], 3), "isca": r["isca"]["palavra"], "fontes": fontes, "blocos": blocos}
    (pasta / "build/cena.json").write_text(json.dumps(c, ensure_ascii=False, indent=1))
    (pasta / "build/cena.js").write_text("window.CENA = " + json.dumps(c, ensure_ascii=False) + ";\n")
    print(f"cena {c['duracao']:.1f} s, {len(blocos)} blocos -> build/cena.js")


# ---------------------------------------------------------------- render / mix / qa
def render(pasta, *extra):
    sh("node", R / "motor/render.mjs", pasta / "build", pasta / "build/video.mp4", *extra)


def mix(pasta):
    c = json.loads((pasta / "build/cena.json").read_text())
    mx = next(b for b in c["blocos"] if b["tipo"] == "maxima")
    cta = c["blocos"][-1]
    a = mx["fala_ini"] - mx.get("silencio_antes_s", 0.8) - 0.15   # a cama some junto com a voz
    z = cta["fala_ini"]                                            # e volta no CTA
    D = c["duracao"]
    bed = (f"[1:a]aloop=loop=-1:size=2e9,atrim=0:{D},volume=0.16,"
           f"volume=enable='between(t,{a:.2f},{z:.2f})':volume=0,afade=t=in:st=0:d=0.4,afade=t=out:st={D-1.2:.2f}:d=1.2[bed]")
    f = (f"[0:a]apad=whole_dur={D},highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,asplit=2[vz][vsc];{bed};"
         f"[bed][vsc]sidechaincompress=threshold=0.04:ratio=6:attack=20:release=300[bd];"
         f"[vz][bd]amix=inputs=2:duration=first:normalize=0[a]")
    bruto = pasta / "build/mix_bruto.wav"
    pre = pasta / "build/mix_pre.wav"
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", pasta / "build/voz.wav", "-i", R / "motor/assets/trilha.mp3", "-filter_complex", f,
       "-map", "[a]", "-ar", "48000", "-ac", "2", bruto)
    # loudnorm em duas passadas (uma passada fica ~1 LU abaixo)
    ln = "loudnorm=I=-14:TP=-1.5:LRA=7"
    o = subprocess.run(["ffmpeg", "-i", str(bruto), "-af", ln + ":print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(o[o.rindex("{"):o.rindex("}") + 1])
    ln2 = (f"{ln}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
           f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", bruto, "-af", ln2, "-ar", "48000", "-ac", "2", pre)
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", pasta / "build/video.mp4", "-i", pre, "-map", "0:v", "-map", "1:a",
       "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{D}", "-movflags", "+faststart", pasta / "final.mp4")
    print(f"mix -> {pasta/'final.mp4'} (cama muda de {a:.2f} a {z:.2f} s)")


def qa(pasta):
    sh(sys.executable, R / "medir.py", pasta)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    passo, pasta = sys.argv[1], Path(sys.argv[2]).resolve()
    extra = sys.argv[3:]
    if passo == "checar":
        sys.exit(0 if checar(pasta) else 1)
    elif passo == "voz":
        voz(pasta, extra or None)
    elif passo == "cena":
        cena(pasta)
    elif passo == "render":
        render(pasta, *extra)
    elif passo == "mix":
        mix(pasta)
    elif passo == "qa":
        qa(pasta)
    elif passo == "tudo":
        if not checar(pasta):
            sys.exit(1)
        voz(pasta); cena(pasta); render(pasta); mix(pasta); qa(pasta)
    else:
        print(__doc__)
        sys.exit(1)
