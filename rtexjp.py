#!/usr/bin/env python3
"""rtexjp — motor de reels 9:16 no padrão rtexjp (reel ilustrado azul-marinho, isca de opinião).

Uso:  python3 rtexjp.py <passo> <pasta-da-edicao>
Passos (em ordem):  checar · voz · cena · render · mix · qa · tudo
  checar  valida o roteiro.json pelas regras do formato (sem gosto)
  voz     um WAV por bloco (inemavox chatterbox, voz do Nei), apara, acelera até 1,15x, junta com respiros
          e o silêncio antes da máxima; Whisper local dá o tempo de cada palavra -> build/tempos.json
  cena    roteiro + tempos -> build/cena.json (o que o palco desenha)
  render  palco.html quadro a quadro (Playwright) -> build/video.mp4 (mudo)
  mix     voz + cama musical (para no silêncio da máxima) + loudnorm -14 LUFS -> final.mp4
  qa      medir.py -> build/qa.json + contact.jpg

Caminhos (variáveis de ambiente, com o padrão da máquina do Nei):
  RTEXJP_INEMAVOX  pasta do inemavox (TTS chatterbox + Whisper)   ~/projetos/inemavox
  RTEXJP_VOZ_REF   gravação de referência da voz (wav)            ~/projetos/timesmkt3/media/voice-refs/nei.wav
  RTEXJP_IMG_URL   servidor de imagem flux2-klein (motor/gerar_*) http://localhost:8000/generate
  RTEXJP_AVATAR_REF foto de referência do avatar (gerar_avatar)    ~/projetos/inema-referencias/nei-avatar.jpg
  RTEXJP_AVATAR_DESC traços e roupa do personagem no prompt (gerar_avatar)   boné preto, óculos, barba grisalha, camiseta azul-aço
  RTEXJP_TRILHA    cama musical do mix                            motor/assets/trilha.mp3
"""
import json, os, re, subprocess, sys, difflib
from pathlib import Path

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / "motor"))
INEMAVOX = Path(os.environ.get("RTEXJP_INEMAVOX", os.environ.get("CS_INEMAVOX", Path.home() / "projetos/inemavox"))).expanduser()
os.environ.setdefault("CS_INEMAVOX", str(INEMAVOX))   # o motor/whisper.py lê esta
TRILHA = Path(os.environ.get("RTEXJP_TRILHA", R / "motor/assets/trilha.mp3")).expanduser()
VOZ_REF = Path(os.environ.get("RTEXJP_VOZ_REF", Path.home() / "projetos/timesmkt3/media/voice-refs/nei.wav")).expanduser()
ALVO_WPM = 178
RESPIRO = 0.22

ORDEM = ["tese", "autoridade", "tese", "virada", "metodo", "ressalva", "maxima", "cta"]
# gancho do quadro 0 (Nei, 28/10/2026): um destes tipos; lista, "você sabia" e "eu fiz" são proibidos
GANCHOS = ["contrario", "perda", "estatistica", "historia"]
GANCHO_PROIBIDO = [(r"\b(\d+|duas|três|tres|quatro|cinco|seis|sete|oito|nove|dez)\s+(coisas|peças|pecas|dicas|ferramentas|jeitos|formas)\b", "lista"),
                   (r"voc[êe] sabia", "você sabia"), (r"\beu fiz\b", "eu fiz")]
# isca de opinião: o CTA pede opinião, nunca promete entrega (Nei não responde comentários)
PROMESSA = [r"te mando", r"eu mando", r"\bmando\b", r"eu envio", r"te envio", r"manda o link", r"comenta \w+ que", r"link na dm", r"\bdm\b"]


def sh(*a, **k):
    return subprocess.run([str(x) for x in a], check=True, **k)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def ler(pasta):
    return json.loads((pasta / "roteiro.json").read_text())


# ---------------------------------------------------------------- checar
def poses_disponiveis():
    return sorted(p.stem for p in (R / "motor/avatar").glob("*.png"))


def objetos_disponiveis():
    return sorted(p.stem for p in (R / "motor/assets/objetos").glob("*.png"))


def _checar_visual(r, pasta, erros, avisos):
    """visual v1.2 (versao rtexjp/3): pose por bloco/batida, objeto da biblioteca, print existente, manchete curta."""
    poses, objs = set(poses_disponiveis()), set(objetos_disponiveis())
    for b in r["blocos"]:
        bts = b.get("cena", {}).get("params", {}).get("beats", [])
        if b["tipo"] not in ("cta",) and b.get("cena", {}).get("comp") in ("quadro", "maxima") and not bts:
            erros.append(f"[{b['id']}] sem beats (manchete/objeto/pose por batida)")
        for p in [b.get("pose")] + [x.get("pose") for x in bts] + [b.get("pose_silencio")]:
            if p and p not in poses:
                erros.append(f"[{b['id']}] pose '{p}' não existe em motor/avatar ({', '.join(sorted(poses))})")
        if not b.get("pose") and not any(x.get("pose") for x in bts):
            erros.append(f"[{b['id']}] sem pose (o avatar reage à emoção do bloco)")
        for x in bts:
            for o in ([x["objeto"]] if x.get("objeto") else []) + x.get("objetos", []):
                if o not in objs:
                    erros.append(f"[{b['id']}] objeto '{o}' não está na biblioteca (motor/gerar_objeto.py)")
            if x.get("print") and not (pasta / x["print"]).exists():
                erros.append(f"[{b['id']}] print '{x['print']}' não existe na edição")
            if x.get("em") and x["em"].lower() not in b["fala"].lower():
                erros.append(f"[{b['id']}] batida em='{x['em']}' não está na fala")
            m = x.get("manchete") or []
            if len(m) > 3:
                erros.append(f"[{b['id']}] manchete com {len(m)} linhas (2–3)")
            if any(len(l) > 16 for l in m):
                avisos.append(f"[{b['id']}] linha de manchete longa (> 16 letras) encolhe a letra: {m}")


def _textos(x):
    if isinstance(x, str):
        return [x]
    if isinstance(x, dict):
        return [t for k, v in x.items() if k not in ("gatilhos", "comp") for t in _textos(v)]
    if isinstance(x, list):
        return [t for v in x for t in _textos(v)]
    return []


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
    itens = vir and (vir["cena"]["params"].get("itens") or next((x["itens"] for x in vir["cena"]["params"].get("beats", []) if x.get("itens")), []))
    if vir and len(itens) != len(met):
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
        p = " ".join(_textos(b.get("cena", {})) + _textos(b.get("tela", {})))   # só texto que vai à tela (não tamanhos/posições)
        if re.search(r"\d{2,}", re.sub(r"\b0\d\b", "", p)) and not b.get("fonte") and b["tipo"] not in ("cta", "virada", "tese"):
            erros.append(f"[{b['id']}] número na tela sem fonte")
    # gancho (quadro 0 + 3 primeiros segundos)
    tese0 = bl[0]
    tela0 = tese0.get("tela", {})
    g = r.get("gancho")
    if not g:
        avisos.append("LEGADO: sem gancho.tipo (formato antigo; edição nova precisa de gancho)")
    else:
        if g.get("tipo") not in GANCHOS:
            erros.append(f"gancho.tipo '{g.get('tipo')}' (use {', '.join(GANCHOS)})")
        txt0 = (tela0.get("texto", "") + " " + tese0["fala"]).lower()
        for pat, nome in GANCHO_PROIBIDO:
            if re.search(pat, txt0):
                erros.append(f"gancho proibido ({nome}) no quadro 0: {tela0.get('texto') or tese0['fala']}")
        nm = len(tela0.get("texto", "").split())
        if not tela0.get("texto"):
            erros.append("quadro 0 sem manchete (tela.texto)")
        elif nm > 7:
            erros.append(f"manchete do quadro 0 com {nm} palavras (máx. ~6)")
        elif nm > 6:
            avisos.append(f"manchete do quadro 0 com {nm} palavras (alvo ≤ 6)")
        if tela0.get("texto") and tela0["texto"] != tela0["texto"].upper():
            erros.append("manchete do quadro 0 em caixa alta")
        if not tela0.get("destaque") or tela0["destaque"] not in tela0.get("texto", ""):
            erros.append("manchete do quadro 0 precisa de UMA palavra na cor quente (tela.destaque)")
        if not g.get("objeto"):
            erros.append("gancho.objeto: o objeto-metáfora com dano desenhado no quadro 0")
        if tese0.get("pose") not in ("surpreso", "susto", "queixo"):
            avisos.append("no gancho o avatar reage (pose susto ou surpreso)")
    pv = next((b for b in bl if b["tipo"] == "autoridade"), None)
    if not pv:
        erros.append("falta a prova (bloco autoridade, até ~20 s)")
    elif bl.index(pv) > 2:
        erros.append("a prova (autoridade) vem no 2º ou 3º bloco (até ~20 s)")
    # isca
    isca = r["isca"]
    cta = bl[-1]
    cta_txt = cta["fala"] + " " + json.dumps(cta.get("tela", {}), ensure_ascii=False) + " " + json.dumps(cta.get("cena", {}), ensure_ascii=False)
    if isca.get("tipo") == "opiniao":
        ops = isca.get("opcoes", [])
        if not isca.get("pergunta", "").strip().endswith("?"):
            erros.append("isca.pergunta tem que ser uma pergunta (termina em ?)")
        if not 2 <= len(ops) <= 3 or any(len(o.split()) != 1 or o != o.upper() for o in ops):
            erros.append("isca.opcoes: 2–3 opções de UMA palavra em caixa alta")
        for o in ops:
            if o.lower() not in cta["fala"].lower():
                erros.append(f"a opção {o} não está na fala do CTA")
        antes = [b for b in bl[:-1] if any(o.lower() in (b["fala"] + json.dumps(b.get("tela", {}), ensure_ascii=False)).lower() for o in ops)]
        if not antes:
            erros.append("a tensão (opções) não foi plantada antes do CTA")
        elif bl.index(antes[0]) > 3:
            avisos.append("as opções aparecem tarde (plante nos primeiros blocos)")
        lado = isca.get("lado", "")
        fala_ate = " ".join(b["fala"] for b in bl[:-1]) + " " + cta["fala"].split("?")[0]
        if not lado:
            erros.append("isca.lado: a posição do Nei, dita antes da pergunta")
        elif lado.lower().rstrip(".") not in fala_ate.lower():
            erros.append("o lado do Nei (isca.lado) não é dito antes da pergunta")
        if r.get("entregavel") or isca.get("entregavel"):
            erros.append("isca de opinião não tem entregável (o Nei não responde comentários)")
        if not tela0.get("texto", "").strip().endswith("?") and not (g and g.get("tipo") in ("contrario", "estatistica")):
            avisos.append("a tensão do quadro 0 costuma ser pergunta (termine a manchete em ?)")
    else:
        avisos.append("LEGADO: isca de palavra + entregável (formato antigo; edição nova usa isca de opinião)")
        palavra = isca["palavra"]
        if palavra not in cta["fala"]:
            erros.append("a palavra-isca não está na fala do CTA")
        antes = [b for b in bl[:-1] if palavra.lower() in (b["fala"] + json.dumps(b.get("tela", {}))).lower()]
        if not antes:
            erros.append("a palavra-isca não foi plantada antes do CTA")
    if isca.get("tipo") == "opiniao":
        for pat in PROMESSA:
            if re.search(pat, cta_txt, re.I):
                erros.append(f"CTA promete entrega ('{pat}'): o pedido é de opinião, sem recompensa")
    mx = bl[-2]
    if not 0.5 <= mx.get("silencio_antes_s", 0) <= 0.9:
        erros.append("a máxima precisa de 0,5–0,9 s de silêncio antes")
    if not 5 <= bl[-1].get("hold_s", 0) <= 9:
        avisos.append("hold depois da fala do CTA: 5–9 s (cartão final inteiro fica ~8–10 s)")
    if str(r.get("versao", "")).endswith("/3"):
        _checar_visual(r, pasta, erros, avisos)
    pal = sum(len(b["fala"].split()) for b in bl)
    if not 160 <= pal <= 270:
        avisos.append(f"{pal} palavras (alvo 60–90 s ≈ 170–260)")
    rot_isca = "/".join(isca.get("opcoes", [])) if isca.get("tipo") == "opiniao" else isca.get("palavra")
    print(f"{len(bl)} blocos · {len(met)} peças · {pal} palavras · isca {rot_isca} · gancho {(g or {}).get('tipo', '—')}")
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
        # batidas (visual v1.2): cada uma troca manchete/objeto/pose na palavra "em" (a 1ª entra no início do bloco)
        ult = ini[i]
        for k, bt in enumerate(b.get("cena", {}).get("params", {}).get("beats", [])):
            if k == 0 and not bt.get("em"):
                bt["t"] = round(ini[i], 3)
                continue
            hit = next((p for p in t["palavras"] if p["ini"] >= ult - 0.01 and re.sub(r"\W", "", p["w"]).lower().startswith(bt["em"].lower())), None)
            bt["t"] = round((hit["ini"] if hit else t["ini"]) - 0.08, 3)
            ult = bt["t"]
            for chave in ("carimbo_em", "chips_em", "opcoes_em"):
                if isinstance(bt.get(chave), str):
                    h2 = next((p for p in t["palavras"] if re.sub(r"\W", "", p["w"]).lower().startswith(bt[chave].lower())), None)
                    bt[chave] = h2["ini"] if h2 else bt["t"]
        blocos.append({**b, "ini": round(ini[i], 3), "fala_ini": t["ini"], "fala_fim": t["fim"], "fim": round(fim_vis, 3),
                       "palavras": t["palavras"], "g": g})
    fontes = {f["id"]: f for f in r["fontes"]}
    isca = r["isca"]
    quentes = [o.upper() for o in isca["opcoes"]] if isca.get("tipo") == "opiniao" else [isca["palavra"].upper()]
    bts = [bt for b in blocos for bt in b.get("cena", {}).get("params", {}).get("beats", [])]
    objs = sorted({o for bt in bts for o in ([bt["objeto"]] if bt.get("objeto") else []) + bt.get("objetos", [])})
    prints = sorted({bt["print"] for bt in bts if bt.get("print")})
    c = {"duracao": round(blocos[-1]["fim"], 3), "versao": r.get("versao", ""), "poses": poses_disponiveis(),
         "objetos_usados": objs, "prints_usados": prints, "isca": quentes, "isca_obj": isca, "fontes": fontes, "blocos": blocos}
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
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", pasta / "build/voz.wav", "-i", TRILHA, "-filter_complex", f,
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
