# rtexjp — 9:16 illustrated reels engine

[![rtexjp](capa/capa.png)](https://inematds.github.io/rtexjp/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

rtexjp is an engine that assembles short vertical videos (reels) illustrated in navy blue, from a script written in a text file (`roteiro.json`). It’s the engine Nei uses for INEMA reels, open to anyone who wants to study or adapt it: no need to record yourself or pay for an avatar service. It generates the voice, draws each scene frame by frame, mixes the soundtrack, and checks on its own whether the video follows the format. It requires a computer with a graphics card (GPU), Python, Node, ffmpeg, and two local servers: voice ([inemavox](https://github.com/inematds/inemavox)) and image ([inemaimg](https://github.com/inematds/inemaimg), flux2-klein).

It comes configured with Nei’s voice and avatar. To use your own, point the environment variables `RTEXJP_VOZ_REF` (voice reference recording, `.wav`) and `RTEXJP_AVATAR_REF` (avatar photo) to your files, describe your character in `RTEXJP_AVATAR_DESC`, and regenerate the poses (`python3 motor/gerar_avatar.py`); these two files are not included in the repository. See **Paths and environment variables** below.

## 📖 User guide

Complete guide (landing page + walkthrough): **https://inematds.github.io/rtexjp/guia/** · 1st video (old, purple palette): https://www.youtube.com/watch?v=AZEZK1YgF98

**v1.2.0** · free, local engine that turns a `roteiro.json` into a vertical 1080×1920 reel in the **rtexjp style**: an illustrated reel in navy blue (with changes to ice blue paper), a **large** illustrated avatar of Nei (≈ 43% of the height, in 11 poses tied to the emotion of the speech, without lip-sync), one **hero illustration** per scene, a **real screenshot** as proof, centered Sora headline, karaoke captions, robot mascot, and a single **opinion** CTA (a question with a side to take, answered with one word: “comment DONO or REFÉM”).

## The format (rtexjp style)

Fixed structure, checked by the validator (`checar`) and QA (`qa`):

1. **Hook at frame 0** (`gancho.tipo` in the script), one of these: **contrarian** (tells people to stop doing something everyone does), **loss** (what if X disappeared?), **fear statistic** with an on-screen source, or **someone else’s story** with a number. Prohibited: lists (“5 things…”), “did you know…”, “I did…”.
2. **Frame 0 headline** of no more than ~6 words, uppercase, **one** word in yellow, more aggressive than the speech (the text catches people scrolling without sound; the voice softens it). It’s already in frame 0, which serves as the cover. A **damaged metaphor object** is drawn (crossed out in red, disappearing, broken), the avatar **reacts** in the first second, and something changes every ~1 s in the first 3 seconds.
3. **Proof by 20 s** — a number with a source (counter that lands on the number, monospaced source line below) or an authority.
4. **The viewer’s problem, with reassurance** (“it’s not your fault; no one gave you X”) — and here the **bait tension** is planted: the final question’s options appear on screen in yellow.
5. **One topic per video**; the method in 2–5 **parts**, announced with a visible index and a pill bar at the top throughout the parts.
6. **One part at a time, one visual object per sentence** — the object changes within the scene every ~2–3 s.
7. **An honest caveat spoken aloud**, in an alert card (red = problem, green = correct).
8. **A maxim in antithesis**, followed by **0.8 s of real silence** (voice and music stop).
9. **Opinion CTA**: a strong, emotional question that takes a side and is tied to the thesis; Nei states his side first (“I want to own mine”) and asks for a one-word answer (“comment DONO or REFÉM”). The card shows the question + options, the comment box types an option → Publish → confirmation, held for ~10 s, with no sign-off. **Promising a deliverable is prohibited** (“I’ll send it to you”, “I’ll send”, “comment X and…”): Nei doesn’t reply to comments. The link and source stay in the pinned comment/description (the script’s `publicar` block), never as a reward for commenting.

Visuals (v1.2, edits with `"versao": "rtexjp/3"`): every frame has the same shell, from top to bottom — mono label (≥ 30 px) · **headline in Sora ExtraBold, centered, 2–3 lines, ≥ 96 px**, white `#f4f7fc` with one word in light steel blue `#93c5fd` (yellow `#FACC15` only in frame 0) · **hero illustration** (an illustrated object in the same flat style as the avatar, from the `motor/assets/objetos/` library, or the **real screenshot** of the source page with the `fonte:` line below) · **karaoke caption** (Montserrat ExtraBold 74 px with a black outline, the spoken word in steel blue) in its own band · **large avatar**, at the bottom and centered (820 px, ≈ 43% of the height), in the pose for the block or beat. The background has a spotlight and light grain, alternating between navy `#07111f` and ice blue paper `#e8eef7` (`cena.tema: "claro"`, navy lettering, highlight on a `#1e3a8a` band). During the silence before the maxim, the last frame freezes with the avatar thinking: never an empty screen. Yellow is only for the hot word in frame 0 and the bait question/options (lettering `#1a1206` on the fill); green/red only for correct/incorrect. Reels safe zones: faces, text, and objects above 80% of the height (only the avatar’s torso below that).

**Beauty gate** (`medir.py`, only in `rtexjp/3`): the stage measures in its own DOM, in 2 samples per block, the headline (≥ 96 px), all text (≥ 30 px), the area occupied in the usable frame (≥ 55%), text contrast (WCAG ≥ 4.5:1), and avatar height (≥ 38%).

Older edits (`rtexjp/2`) retain the v1.1 visuals (Anton on the left, small avatar in the corner).

Audio: Nei’s voice (inemavox chatterbox, 0.6/0.6, `atempo` ≤ 1.15, internal pauses shortened), 160–190 words/min, low music bed with sidechain, master −14 LUFS.

> **Exception to the INEMA kit:** the illustrated avatar and robot mascot are project decisions (recorded in `inema-design/DECISOES.md`, D19). The palette follows the spirit of the kit: navy + blue, yellow `#FACC15` as the only warm color. The 1st edit (`2026-10-28-5-coisas`) uses the old format — purple palette, list hook, and bait with a deliverable — and stays as is because it has already been published.

## Paths and environment variables

| Variable | What it’s for | Default |
|---|---|---|
| `RTEXJP_INEMAVOX` | inemavox folder (chatterbox TTS in `venv` + Whisper large-v3) | `~/projetos/inemavox` |
| `RTEXJP_VOZ_REF` | voice reference recording (`.wav`) | `~/projetos/timesmkt3/media/voice-refs/nei.wav` |
| `RTEXJP_IMG_URL` | flux2-klein image server (`motor/gerar_avatar.py`, `motor/gerar_imagem.py`) | `http://localhost:8000/generate` |
| `RTEXJP_AVATAR_REF` | avatar reference photo | `~/projetos/inema-referencias/nei-avatar.jpg` |
| `RTEXJP_AVATAR_DESC` | character traits and clothing in the image prompt (in English); change it together with the photo | black cap, glasses, gray beard, steel blue T-shirt (Nei) |
| `RTEXJP_TRILHA` | mix music bed (for publishing, use music whose license you know) | `motor/assets/trilha.mp3` |
| `CS_WHISPER_PY` | Python from the environment with faster-whisper (Whisper server and fallback) | `~/miniconda3/envs/chatterbox/bin/python3` |
| `CHATTERBOX_PYTHON` | Python from the chatterbox environment, required by inemavox’s `tts_direct.py` | the one in the `chatterbox` environment |

Example: `RTEXJP_VOZ_REF=~/minha-voz.wav RTEXJP_INEMAVOX=~/inemavox python3 rtexjp.py voz edicoes/minha-edicao`.

## Structure

```
rtexjp.py              pipeline: checar · voz · cena · render · mix · qa · tudo
medir.py               QA automático (duração, wpm, LUFS, trocas/min, isca, cartão final, silêncio, grep de fonte) + contact.jpg
motor/palco.html       o palco: casca v1.2 (manchete, herói, avatar, legenda) desenhada por window.render(t) + window.medidas(t) (portão de beleza)
motor/render.mjs       Playwright quadro a quadro -> ffmpeg (30 fps)
motor/gerar_avatar.py  poses do avatar no flux2-klein local com a foto de referência (fundo verde recortado)
motor/capturar_prova.mjs print real da fonte para a prova (Playwright, tema escuro, 2x)
motor/gerar_objeto.py  desenho-herói no flux2-klein local -> motor/assets/objetos/<nome>.png + indice.json
motor/gerar_imagem.py  imagem de cena no flux2-klein local
motor/whisper.py       Whisper large-v3 local (inemavox) com tempo por palavra
motor/avatar/*.png     11 poses: bracos, queixo, apontando, segurando, surpreso, mostrando, explica, olha, polegar, duvida, susto
motor/assets/objetos/  biblioteca de desenhos-herói (terminal_quebrado, mapa_pinos, lupa_arquivos, dominos, chave_dono…) + indice.json
motor/assets/          trilha.mp3 (cama), grao.png (textura), carro.png
motor/fontes/          Sora, Anton, JetBrains Mono, Montserrat (OFL)
edicoes/<id>/          roteiro.json · final.mp4 · contact.jpg · qa.md · prova/ (prints reais) (voz/ e build/ ficam fora do git)
```

## The process, from beginning to end

🧠 session with Nei · ⚙️ script (zero tokens) · 🤖 `claude -p` / Codex via subscription (never API)

| # | Step | Command | Who |
|---|---|---|---|
| 1 | Topic: thesis, 2–5 parts, verified numbers (✅ with source and date) | — | 🧠 |
| 2 | Script: write `edicoes/<id>/roteiro.json` (`gancho`, opinion `isca`, full speech, `fala_tts` for pronunciation, word triggers, `publicar` block) | edit the JSON (or 🤖 from the topic) | 🤖 + 🧠 |
| 3 | Validate format rules | `python3 rtexjp.py checar edicoes/<id>` | ⚙️ |
| 4 | Approve the script (hook, bait question, numbers) | — | 🧠 |
| 5 | Avatar poses (once; redo only if the character changes) — inspect each one and redo any distorted poses | `python3 motor/gerar_avatar.py [pose …]` | ⚙️ |
| 6 | Any hero illustrations missing from the library (inspect and redo with another seed if distorted) | `python3 motor/gerar_objeto.py <nome> "<objeto em inglês>" [seed]` | ⚙️ |
| 6b | Real source screenshot (repository page, cropped around the name and counter) in `edicoes/<id>/prova/` | `node motor/capturar_prova.mjs <url> edicoes/<id>/prova/x.png [--clip x,y,w,h]` | ⚙️ |
| 7 | Voice per block + Whisper (timing per word) | `python3 rtexjp.py voz edicoes/<id> [bloco …]` (with names, redo only those TTS blocks) | ⚙️ |
| 8 | Scene (script + timings) | `python3 rtexjp.py cena edicoes/<id>` | ⚙️ |
| 9 | Frame preview (+ `quadros/medidas.json` from the beauty gate) | `node motor/render.mjs edicoes/<id>/build --quadros 0,10,20` → `edicoes/<id>/quadros/` | ⚙️ |
| 10 | Render 1080×1920 30 fps | `python3 rtexjp.py render edicoes/<id>` | ⚙️ |
| 11 | Mix (music stops during the maxim’s silence, −14 LUFS) | `python3 rtexjp.py mix edicoes/<id>` | ⚙️ |
| 12 | Automated QA + beauty gate + contact sheet | `python3 rtexjp.py qa edicoes/<id>` → `qa.md`, `contact.jpg` | ⚙️ |
| 13 | Inspect `contact.jpg` and the video; independent reviewer (`claude -p`, fixed list in `CLAUDE.md`, score 0–10 for “would this stop the scroll?” on key frames) | — | 🧠 / 🤖 |
| 14 | Publish (channel queue / v3 / Telegram) using the script’s `publicar` block | outside this repo | orchestrator |

Shortcut: `python3 rtexjp.py tudo edicoes/<id>` runs 3 → 7 → 8 → 10 → 11 → 12.

## Requirements

- inemavox (chatterbox TTS in `venv`, Whisper large-v3) and the voice reference recording — `RTEXJP_INEMAVOX`, `RTEXJP_VOZ_REF`
- local flux2-klein image server and the avatar photo — `RTEXJP_IMG_URL`, `RTEXJP_AVATAR_REF`
- Node + `npm i` (Playwright 1.64), ffmpeg, Python 3 with Pillow and numpy

## Editions

### 2026-10-28-mapa-v2 — “Claude disappeared. Now what?” (v1.2 visuals)

`edicoes/2026-10-28-mapa-v2/final.mp4` — the same script, loss hook, and DONO/REFÉM bait as the edition below, rebuilt with v1.2 visuals: large avatar in 9 of the 11 poses, one hero illustration per beat, real GitHub screenshot (88.8 thousand stars on 28/10/2026), ice blue paper in two scenes. `comparativo.jpg` places 4 frames from v1 above and v2 below.

### 2026-10-28-mapa — “Claude disappeared. Now what?” (v1.1 visuals)

`edicoes/2026-10-28-mapa/final.mp4` — kept for comparison. One topic (Understand Anything), **loss** hook, 3 parts (the map, the explanation, the impact), **DONO or REFÉM** opinion bait. Title, description, and pinned comment are in the `publicar` block of `roteiro.json`.

### 2026-10-28-5-coisas — “5 AI things this month that almost nobody noticed” (old format)

`edicoes/2026-10-28-5-coisas/final.mp4` — published at https://www.youtube.com/watch?v=AZEZK1YgF98. Purple palette, list hook, and bait with a deliverable (SETUP): rules the current format prohibits. It remains in the repository as a record; `checar` still accepts this script, with a LEGACY warning.
