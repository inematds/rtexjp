# rtexjp — illustrated 9:16 reels engine

[![rtexjp](capa/capa.png)](https://inematds.github.io/rtexjp/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

rtexjp is an engine that assembles short vertical videos (reels), illustrated in navy blue, from a script written in a text file (`roteiro.json`). It’s the engine Nei uses for INEMA reels, open for anyone who wants to study or adapt it: no need to film yourself or pay for an avatar service. It generates the voice, draws each scene frame by frame, mixes the soundtrack, and checks on its own whether the video follows the format. It requires a computer with a graphics card (GPU), Python, Node, ffmpeg, and two local servers: one for voice ([inemavox](https://github.com/inematds/inemavox)) and one for images ([inemaimg](https://github.com/inematds/inemaimg), flux2-klein).

It comes configured with Nei’s voice and avatar. To use your own, point the `RTEXJP_VOZ_REF` (voice reference recording, `.wav`) and `RTEXJP_AVATAR_REF` (avatar photo) environment variables to your files, describe your character in `RTEXJP_AVATAR_DESC`, and regenerate the poses (`python3 motor/gerar_avatar.py`); those two files are not included in the repository. See **Paths and environment variables** below.

## 📖 User guide

Complete guide (landing page + walkthrough): **https://inematds.github.io/rtexjp/guia/en/** · 1st video (old purple palette): https://www.youtube.com/watch?v=AZEZK1YgF98

**v1.1.0** · a free local engine that turns a `roteiro.json` into a vertical 1080×1920 reel in the **rtexjp format**: an illustrated reel with an almost black navy background and a blue beam of light, an illustrated avatar of Nei (no lip sync, in poses), a robot mascot, a 2–3 word headline caption, and a single **opinion** CTA (a question with a side to choose, answered with one word: "comenta DONO (OWNER) ou REFÉM (HOSTAGE)").

## The format (rtexjp standard)

Fixed structure, checked by the validator (`checar`) and QA (`qa`):

1. **Hook in frame 0** (`gancho.tipo` in the script), one of these: **contrary** (tells people to stop doing something everyone does), **loss** (what if X disappeared?), a **fear statistic** with its source on screen, or a **third-party story** with a number. Forbidden: lists (“5 things…”), “did you know that…”, “I did…”.
2. **Frame 0 headline** with about 6 words maximum, uppercase, **one** word in yellow, more aggressive than the spoken line (the text catches people scrolling without sound; the voice softens it). It’s already in frame 0, which serves as the cover. A **metaphorical object showing damage** is drawn (crossed out in red, disappearing, broken); the avatar **reacts** in the first second, and something changes about every second during the first three seconds.
3. **Proof by 20 seconds** — a number with a source (a counter that lands on the number, with a monospaced source line underneath) or an authority.
4. **The viewer’s problem, with absolution** (“it’s not your fault; no one gave you X”) — and this is where the **bait tension** is planted: the final question’s options appear on screen in yellow.
5. **One topic per video**; the method is presented in 2–5 **parts**, announced with a visible index and a pill bar at the top while the parts play.
6. **One part at a time, one visual object per sentence** — the object changes within the scene every 2–3 seconds.
7. **An honest caveat spoken aloud**, in a warning card (red = problem, green = correct).
8. **A maxim in antithesis**, followed by **0.8 seconds of actual silence** (voice and music stop).
9. **Opinion CTA**: a strong, emotional question with a side to choose, tied to the thesis; Nei states his side first (“eu quero ser dono do meu” [“I want to own mine”]) and asks for a one-word answer (“comenta DONO ou REFÉM” [“comment OWNER or HOSTAGE”]). The card shows the question + options; the comment box types an option → Publish → confirmation, held for about 10 seconds, with no sign-off. **Promising a deliverable is forbidden** (“I’ll send it to you”, “I’ll send it”, “comment X and…”): Nei doesn’t reply to comments. Links and sources stay in the pinned comment/description (the script’s `publicar` block), never as a reward for commenting.

Visuals: navy background `#07111f` (cards `#0b1a30`/`#12284a`), royal blue `#1e3a8a`/`#2563eb`, steel blue `#7aa7e0`/`#93c5fd`, text `#e6edf7`/white; INEMA yellow `#FACC15` **only** for the hot word in the frame 0 headline and for the bait question/options (dark lettering `#1a1206` when used as a fill); green/red only for correct/incorrect. Titles in Anton (condensed uppercase), labels and sources in JetBrains Mono, captions in Montserrat ExtraBold at about 77% of the height. Reels safe zones: nothing useful below 80% of the height or in the right-side icon strip.

Audio: Nei’s voice (inemavox chatterbox, 0.6/0.6, `atempo` ≤ 1.15, internal pauses shortened), 160–190 words/minute, quiet music bed with sidechain, master −14 LUFS.

> **Exception to the INEMA kit:** The illustrated avatar and robot mascot are project decisions (recorded in `inema-design/DECISOES.md`, D19). The palette follows the spirit of the kit: navy + blue, yellow `#FACC15` as the only warm color. The 1st edition (`2026-10-28-5-coisas`) uses the old format — purple palette, list hook, and bait with a deliverable — and stays as is because it has already been published.

## Paths and environment variables

| Variable | Purpose | Default |
|---|---|---|
| `RTEXJP_INEMAVOX` | inemavox folder (chatterbox TTS in `venv` + Whisper large-v3) | `~/projetos/inemavox` |
| `RTEXJP_VOZ_REF` | voice reference recording (`.wav`) | `~/projetos/timesmkt3/media/voice-refs/nei.wav` |
| `RTEXJP_IMG_URL` | flux2-klein image server (`motor/gerar_avatar.py`, `motor/gerar_imagem.py`) | `http://localhost:8000/generate` |
| `RTEXJP_AVATAR_REF` | avatar reference photo | `~/projetos/inema-referencias/nei-avatar.jpg` |
| `RTEXJP_AVATAR_DESC` | character features and clothing in the image prompt (in English); change along with the photo | black cap, glasses, gray beard, steel blue T-shirt (Nei) |
| `RTEXJP_TRILHA` | mix music bed (for publishing, use music with a license you know) | `motor/assets/trilha.mp3` |
| `CS_WHISPER_PY` | Python for the environment with faster-whisper (Whisper server and fallback) | `~/miniconda3/envs/chatterbox/bin/python3` |

Example: `RTEXJP_VOZ_REF=~/minha-voz.wav RTEXJP_INEMAVOX=~/inemavox python3 rtexjp.py voz edicoes/minha-edicao`.

## Structure

```
rtexjp.py              pipeline: checar · voz · cena · render · mix · qa · tudo
medir.py               automatic QA (duration, wpm, LUFS, changes/min, bait, final card, silence, source grep) + contact.jpg
motor/palco.html       the stage: scene components drawn by window.render(t) (deterministic)
motor/render.mjs       frame-by-frame Playwright -> ffmpeg (30 fps)
motor/gerar_avatar.py  avatar poses with local flux2-klein and reference photo (green screen cutout)
motor/gerar_imagem.py  scene image with local flux2-klein
motor/whisper.py       local large-v3 Whisper (inemavox) with word-level timing
motor/avatar/*.png     poses: bracos, queixo, apontando, segurando, surpreso, mostrando
motor/assets/          trilha.mp3 (music bed), carro.png
edicoes/<id>/          roteiro.json · final.mp4 · contact.jpg · qa.md (voz/ and build/ are outside git)
```

## The process, start to finish

🧠 session with Nei · ⚙️ script (zero tokens) · 🤖 `claude -p` / Codex by subscription (never API)

| # | Step | Command | Who |
|---|---|---|---|
| 1 | Topic: thesis, 2–5 parts, verified numbers (✅ with source and date) | — | 🧠 |
| 2 | Script: write `edicoes/<id>/roteiro.json` (`gancho`, opinion `isca`, full spoken text, `fala_tts` for pronunciation, word triggers, `publicar` block) | edit the JSON (or 🤖 from the topic) | 🤖 + 🧠 |
| 3 | Validate format rules | `python3 rtexjp.py checar edicoes/<id>` | ⚙️ |
| 4 | Approve the script (hook, bait question, numbers) | — | 🧠 |
| 5 | Avatar poses (once; redo only if the character changes) | `python3 motor/gerar_avatar.py` | ⚙️ |
| 6 | Scene images, if the part calls for them | `python3 motor/gerar_imagem.py motor/assets/x.png "<prompt>"` | ⚙️ |
| 7 | Voice by block + Whisper (word-level timing) | `python3 rtexjp.py voz edicoes/<id> [bloco …]` (with names, redoes only those TTS clips) | ⚙️ |
| 8 | Scene (script + timings) | `python3 rtexjp.py cena edicoes/<id>` | ⚙️ |
| 9 | Frame preview | `node motor/render.mjs edicoes/<id>/build --quadros 0,10,20` → `edicoes/<id>/quadros/` | ⚙️ |
| 10 | Render 1080×1920 30 fps | `python3 rtexjp.py render edicoes/<id>` | ⚙️ |
| 11 | Mix (music bed stops during the maxim’s silence, −14 LUFS) | `python3 rtexjp.py mix edicoes/<id>` | ⚙️ |
| 12 | Automatic QA + contact sheet | `python3 rtexjp.py qa edicoes/<id>` → `qa.md`, `contact.jpg` | ⚙️ |
| 13 | Review `contact.jpg` and the video; use an independent reviewer if publishing | — | 🧠 / 🤖 |
| 14 | Publish (channel queue / v3 / Telegram) with the script’s `publicar` block | outside this repo | orchestrator |

Shortcut: `python3 rtexjp.py tudo edicoes/<id>` runs 3 → 7 → 8 → 10 → 11 → 12.

## Requirements

- inemavox (chatterbox TTS in `venv`, Whisper large-v3) and the voice reference recording — `RTEXJP_INEMAVOX`, `RTEXJP_VOZ_REF`
- local flux2-klein image server and avatar photo — `RTEXJP_IMG_URL`, `RTEXJP_AVATAR_REF`
- Node + `npm i` (Playwright 1.64), ffmpeg, Python 3 with Pillow and numpy

## Editions

### 2026-10-28-mapa — "O Claude sumiu. E agora?" (“Claude disappeared. Now what?”) (current format)

`edicoes/2026-10-28-mapa/final.mp4` — one topic (Understand Anything), **loss** hook, 3 parts (the map, the explanation, the impact), **DONO or REFÉM (OWNER or HOSTAGE)** opinion bait. Title, description, and pinned comment are in the `publicar` block of `roteiro.json`.

### 2026-10-28-5-coisas — "5 coisas de IA deste mês que quase ninguém percebeu" (“5 AI things this month that almost no one noticed”) (old format)

`edicoes/2026-10-28-5-coisas/final.mp4` — published at https://www.youtube.com/watch?v=AZEZK1YgF98. Purple palette, list hook, and bait with a deliverable (SETUP): rules forbidden by the current format. It remains in the repository as a record; `checar` still accepts this script, with a LEGADO warning.
