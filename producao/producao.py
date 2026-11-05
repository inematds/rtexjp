#!/usr/bin/env python3
"""Produção do rtexjp sem sessão aberta: monta, revisa e põe na fila do canal.

Nei, 05/11/2026: "no inemaccbot pode ter /rtex /rtexjp /r7ex". O /rtexjp do bot escreve o roteiro (fase ficha) e
entrega a edição aqui. Tudo é local (voz chatterbox, Whisper, palco Playwright): não há HeyGen para esperar, mas a
montagem leva minutos e divide a GPU, então quem anda é o timer `rtexjp-producao` (5 em 5 min, uma montagem por rodada),
não o processo do bot. O agente (claude -p, assinatura) só entra para REVISAR a folha de contato.

Estados (só andam para a frente):
  montar → revisao → publicar → na_fila
  qualquer erro → parado (motivo + aviso no v3); `--retomar <pasta>` tenta de novo do ponto certo.

Uso:
  producao.py --add <pasta>       entra na produção (precisa de roteiro.json com publicar.fila)
  producao.py --status            mostra as edições e o estado
  producao.py --retomar <pasta>   tira do 'parado' e recalcula o estado
  producao.py                     uma rodada (é o que o timer chama)

Travas: só entra edição adicionada com --add (nunca varre edicoes/); publicação só pela fila do canal (a fila com timer
do r7ex), nunca upload direto; nenhuma API (tudo local + claude -p pela assinatura).
"""
import fcntl, json, os, subprocess, sys, time
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
R = AQUI.parent
ESTADO = AQUI / "estado.json"
LOG = AQUI / "producao.log"
REVISOR = AQUI / "revisor.md"
FILA = Path.home() / "projetos/r7ex/fila/fila.json"          # a fila com timer é a do r7ex (1 a cada 2 h por canal)
FILA_PY = Path(os.environ.get("RTEXJP_FILA", Path.home() / "projetos/r7ex/fila/fila.py"))
ENVIAR_V3 = Path.home() / "projetos/refazvideo/ferramentas/enviar_bot_v3.mjs"
AVISA = Path.home() / "projetos/wifi/scripts/avisa-v3.sh"
RTEXJP = [sys.executable, str(R / "rtexjp.py")]
PASSAGEIRO = ("NV_ERR_NO_MEMORY", "out of memory", "CUDA error", "TimeoutError", "Timeout 30000ms", "tempo esgotado")
TENTATIVAS, ESPERA_S = 2, 600


def passageiro(out):
    return any(s.lower() in out.lower() for s in PASSAGEIRO)


def log(msg):
    with open(LOG, "a") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")
    print(msg, flush=True)


def tarja(sugestoes):
    """sugestão do revisor não para o vídeo; vai numa tarja vermelha e o Nei decide se refaz (regra de 21/10/2026)"""
    if not sugestoes:
        return ""
    return ("\n\n🟥🟥🟥 SUGESTÃO 🟥🟥🟥\n" + "\n".join(f"🔴 {x}" for x in sugestoes)
            + "\n🟥🟥🟥🟥🟥🟥🟥🟥🟥\n(o vídeo seguiu para a fila; se quiser refazer, é só pedir)")


def avisa(msg):
    h = datetime.now()
    if h.hour == 23 and 20 <= h.minute <= 55:            # janela proibida do Telegram
        time.sleep((56 - h.minute) * 60)
    subprocess.run(["bash", str(AVISA), msg], capture_output=True, timeout=60)
    log(f"aviso: {msg}")


class Estado:
    """estado.json com trava curta a cada leitura/escrita (o --add pode rodar no meio de uma rodada)"""
    def __enter__(self):
        self.lk = open(AQUI / ".estado.lock", "w"); fcntl.flock(self.lk, fcntl.LOCK_EX)
        self.d = json.loads(ESTADO.read_text()) if ESTADO.exists() else {}
        return self.d

    def __exit__(self, *a):
        if a[0] is None:
            tmp = ESTADO.with_suffix(".tmp"); tmp.write_text(json.dumps(self.d, ensure_ascii=False, indent=1)); tmp.replace(ESTADO)
        fcntl.flock(self.lk, fcntl.LOCK_UN); self.lk.close()


def muda(pasta, estado, **campos):
    with Estado() as d:
        it = d[pasta]; ant = it["estado"]
        it.update(estado=estado, desde=f"{datetime.now():%Y-%m-%d %H:%M}", **campos)
    log(f"{Path(pasta).name}: {ant} → {estado}" + (f" ({campos['motivo']})" if campos.get("motivo") else ""))


def para(pasta, motivo):
    muda(pasta, "parado", motivo=motivo[-400:])
    avisa(f"Falhou: rtexjp {Path(pasta).name} — {motivo[-300:]}\n(depois de corrigir: producao.py --retomar {Path(pasta).name})")


def roda(cmd, timeout, saida=None, cwd=None):
    """roda um comando; devolve (rc, últimas linhas)"""
    try:
        r = subprocess.run([str(x) for x in cmd], cwd=cwd or R, capture_output=True, text=True, timeout=timeout,
                           stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return 124, f"tempo esgotado ({timeout} s) em {Path(str(cmd[1])).name if len(cmd) > 1 else cmd[0]}"
    out = r.stdout + r.stderr
    if saida:
        with open(saida, "a") as f:
            f.write(f"\n=== {datetime.now():%Y-%m-%d %H:%M:%S} {' '.join(str(x) for x in cmd)[:200]} (rc {r.returncode})\n{out}")
    return r.returncode, out.strip()[-600:]


def roteiro(p):
    return json.loads((p / "roteiro.json").read_text())


def na_fila(p):
    return FILA.exists() and str(p / "final.mp4") in FILA.read_text()


def revisar(p):
    """agente (claude -p, assinatura) lê roteiro + folha de contato + qa e devolve {veredito, motivo}"""
    try:
        r = subprocess.run(["claude", "-p", "--output-format", "json", "--allowedTools", "Read", "--", REVISOR.read_text()],
                           cwd=p, capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
        res = json.loads(r.stdout)["result"].strip()
        v = json.loads(res[res.index("{"): res.rindex("}") + 1])
        assert v.get("veredito") in ("aprovado", "reprovado")
        v["sugestoes"] = [str(x) for x in (v.get("sugestoes") or []) if str(x).strip()]
        if int(v.get("impacto", 10)) < 7 and not any("impacto" in x.lower() for x in v["sugestoes"]):
            v["sugestoes"].append(f"impacto {v['impacto']}/10")
        return v
    except Exception as e:
        return {"veredito": "erro", "motivo": f"revisor não respondeu direito: {str(e)[:200]}"}


def nota_revisor(p, v):
    """grava o parecer no registro único (wifi/scripts/revisor-nota.py); nunca para a produção"""
    if v.get("veredito") not in ("aprovado", "reprovado"):
        return
    cmd = [sys.executable, str(Path.home() / "projetos/wifi/scripts/revisor-nota.py"), "registra", "--fluxo", "rtexjp",
           "--item", p.name, "--quem", "revisor", "--veredito", v["veredito"], "--motivo", str(v.get("motivo", ""))]
    if str(v.get("impacto", "")).replace(".", "", 1).isdigit():
        cmd += ["--nota", str(v["impacto"])]
    try:
        subprocess.run(cmd, capture_output=True, timeout=30)
    except Exception:
        pass


def passo(pasta, it, feito):
    """avança uma edição um passo; uma montagem por rodada (GPU). Devolve True se andou."""
    p = Path(pasta); st = it["estado"]; logp = p / "producao.log"
    if st == "montar":
        if feito.get("montar") or time.time() < it.get("tentar_apos", 0):
            return False
        feito["montar"] = True
        rc, out = roda(RTEXJP + ["tudo", pasta], 7200, logp)
        if rc and passageiro(out) and it.get("tentativas", 0) < TENTATIVAS:
            n = it.get("tentativas", 0) + 1
            with Estado() as d:
                d[pasta].update(tentativas=n, tentar_apos=time.time() + ESPERA_S * n)
            log(f"{p.name}: falha passageira na montagem (tentativa {n}/{TENTATIVAS}, de novo em {ESPERA_S * n // 60} min)")
            return False
        if rc:
            para(pasta, f"montagem/QA: {out}"); return False
        muda(pasta, "revisao"); return True
    if st == "revisao":
        v = revisar(p)
        with open(logp, "a") as f:
            f.write(f"\n=== {datetime.now():%Y-%m-%d %H:%M:%S} revisor: {json.dumps(v, ensure_ascii=False)}\n")
        if v["veredito"] == "erro" and it.get("erros_revisor", 0) < 3:
            with Estado() as d:
                d[pasta]["erros_revisor"] = it.get("erros_revisor", 0) + 1
            return False
        nota_revisor(p, v)
        if v["veredito"] != "aprovado":
            para(pasta, f"revisão reprovou: {v['motivo']}"); return False
        muda(pasta, "publicar", revisao=v["motivo"][:300], sugestoes=(v.get("sugestoes") or [])[:5]); return True
    if st == "publicar":
        r = roteiro(p); pub = r.get("publicar") or {}
        canal = pub.get("fila", "lives11")
        tema = r.get("tema") or pub.get("titulo") or r.get("titulo") or p.name
        if not it.get("enviado_v3"):
            rc, out = roda(["node", ENVIAR_V3, p / "final.mp4", f"rtexjp · {tema}"], 900, logp)
            if rc:
                para(pasta, f"envio ao v3: {out}"); return False
            with Estado() as d:
                d[pasta]["enviado_v3"] = True
        lugar = "já estava na fila"
        if pub.get("so_v3"):                              # teste: só no v3, sem fila nem YouTube
            lugar = "mandado só ao v3 (teste, sem fila)"
        elif not na_fila(p):                              # nunca entra duas vezes na fila
            contexto = pub.get("contexto") or pub.get("descricao") or tema
            rc, out = roda([sys.executable, FILA_PY, "--add", p / "final.mp4", "--nome", tema, "--titulo", pub.get("titulo", tema),
                            "--contexto", contexto, "--canal", canal], 300, logp)
            if rc:
                para(pasta, f"entrada na fila: {out}"); return False
            lugar = next((l for l in out.splitlines() if "na fila" in l), f"na fila do {canal}")
        muda(pasta, "na_fila")
        avisa(f"Terminei: rtexjp {p.name} revisado e {lugar}" + tarja(it.get("sugestoes")))
        return True
    return False


def rodada():
    lk = open(AQUI / ".rodada.lock", "w")
    try:
        fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return                                            # rodada anterior ainda trabalhando
    feito = {}
    for _ in range(20):
        with Estado() as d:
            itens = {k: dict(v) for k, v in d.items() if v["estado"] not in ("na_fila", "parado")}
        andou = False
        for pasta, it in sorted(itens.items(), key=lambda kv: kv[1]["entrou"]):
            try:
                andou |= passo(pasta, it, feito)
            except Exception as e:                        # erro do próprio script: para a edição, não a produção
                para(pasta, f"erro na produção: {e!r}")
        if not andou:
            break


def estado_inicial(p):
    return "na_fila" if na_fila(p) else "montar"


def add(pasta):
    p = Path(pasta).resolve()
    if not (p / "roteiro.json").exists():
        sys.exit(f"sem roteiro.json em {p}")
    if not (roteiro(p).get("publicar") or {}).get("fila"):
        sys.exit("falta publicar.fila (o canal) no roteiro.json")
    st = estado_inicial(p)
    with Estado() as d:
        if str(p) in d and d[str(p)]["estado"] not in ("parado",):
            sys.exit(f"já está na produção: {d[str(p)]['estado']}")
        d[str(p)] = {"estado": st, "entrou": f"{datetime.now():%Y-%m-%d %H:%M:%S}", "desde": f"{datetime.now():%Y-%m-%d %H:%M}"}
    log(f"{p.name}: entrou na produção ({st})")


def retomar(pasta):
    p = Path(pasta).resolve()
    with Estado() as d:
        if str(p) not in d:
            sys.exit("não está na produção (use --add)")
        it = d[str(p)]
        it.update(estado=estado_inicial(p), desde=f"{datetime.now():%Y-%m-%d %H:%M}")
        for k in ("motivo", "tentativas", "tentar_apos", "erros_revisor"):
            it.pop(k, None)
    log(f"{p.name}: retomada ({it['estado']})")


def status():
    with Estado() as d:
        itens = dict(d)
    if not itens:
        print("produção vazia"); return
    for k, v in sorted(itens.items(), key=lambda kv: kv[1]["entrou"]):
        print(f"{v['estado']:<10} {v['desde']}  {Path(k).name}" + (f"\n{'':<11}motivo: {v['motivo'][:160]}" if v.get("motivo") else ""))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        rodada()
    elif a[0] == "--add" and len(a) == 2:
        add(a[1])
    elif a[0] == "--retomar" and len(a) == 2:
        retomar(a[1])
    elif a[0] == "--status":
        status()
    else:
        sys.exit(__doc__)
