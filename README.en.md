# rtexjp — 9:16 illustrated reels engine

[![rtexjp](capa/capa.png)](https://inematds.github.io/rtexjp/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

rtexjp is an engine that assembles short vertical illustrated videos (reels), in purple, from a script written in a text file (`roteiro.json`). It’s the engine Nei uses for INEMA reels, open to anyone who wants to study or adapt it: no need to record yourself or pay for an avatar service. It generates the voice, draws each scene frame by frame, mixes the soundtrack, and automatically checks whether the video follows the format. It requires a computer with a graphics card (GPU), Python, Node, ffmpeg, and two local servers: one for voice ([inemavox](https://github.com/inematds/inemavox)) and one for images ([inemaimg](https://github.com/inematds/inemaimg), flux2-klein).

It comes configured with Nei’s voice and avatar. To use your own, replace the voice reference recording (`VOZ_REF` in `rtexjp.py`) and the avatar photo (`REF` in `motor/gerar_avatar.py`), then regenerate the poses; those two files are not included in the repository.

## 📖 User guide

Full guide (landing page + walkthrough): **https://inematds.github.io/rtexjp/guia/en/** · example video: https://www.youtube.com/watch?v=AZEZK1YgF98

**v1.0.0** · free local engine that turns a `roteiro.json` into a 1080×1920 vertical reel in the **rtexjp format**: an illustrated reel with an almost-black background and a purple beam of light, an illustrated avatar of Nei (no lip sync, in poses), a robot mascot, a 2–3 word headline caption, and a single CTA: “comment WORD.”

## The format (rtexjp format)

Fixed structure, checked by the validator:

1. **Thesis written in frame 0** — uppercase, one word in lilac; serves as the cover (viewers scrolling with the sound off can read the thesis).
2. **Social proof with a number on screen** — counter lands on the number, with a source line in monospace underneath.
3. **The hook word is the thesis and is introduced early** (here: SETUP, ~65 s before the prompt), always in the video’s only warm color.
4. **“N items” announced with a visible index** (folder 01…05) and a 01–05 pill bar at the top throughout the items.
5. **One item at a time, one visual object per sentence** — the object changes within the scene every ~2–3 s (robots, a snapping wire, folder, repository card, stamp, a map being drawn, terminal).
6. **Proof with an on-screen source** — every number has `source: …` written out.
7. **An honest caveat spoken aloud**, in an alert card (red = problem, green = correct).
8. **A maxim in antithesis**, followed by **0.8 s of actual silence** (voice and music bed stop).
9. **CTA “comment WORD”** with the comment box typing the word → Publish → confirmation; card held for ~9–10 s, no sign-off, final section without captions.

Visuals: background `#05040f`, purple `#6b51d2`/`#7e58eb`, lilac `#a080ef`/`#9974f8`, white; orange `#f59f0c` **only** for the hook word; green/red only for correct/incorrect. Titles in Anton (condensed uppercase), labels and sources in JetBrains Mono, captions in Montserrat ExtraBold at ~77% of the height. Reels safe zones: nothing important below 80% of the height or in the right-side icon strip (except the terminal deliberately cropped at the edge — the deliverable sits behind the comment).

Audio: Nei’s voice (inemavox chatterbox, 0.6/0.6, `atempo` ≤ 1.15, shortened internal pauses), 160–190 words/min, low music bed with sidechain, master −14 LUFS.

> **Exception to the INEMA kit:** the purple/lilac palette, illustrated avatar, and mascot are project decisions (recorded in `inema-design/DECISOES.md`). The rest of the kit applies.

## Structure

```
rtexjp.py              pipeline: check · voice · scene · render · mix · qa · all
medir.py               automatic QA (duration, wpm, LUFS, cuts/min, hook, final card, silence, source grep) + contact.jpg
motor/palco.html       the stage: scene components drawn by window.render(t) (deterministic)
motor/render.mjs       frame-by-frame Playwright -> ffmpeg (30 fps)
motor/gerar_avatar.py  avatar poses with local flux2-klein using the reference photo (green background removed)
motor/gerar_imagem.py  scene image with local flux2-klein
motor/whisper.py       local Whisper large-v3 (inemavox) with word-level timing
motor/avatar/*.png     poses: arms, chin, pointing, holding, surprised, showing
motor/assets/          trilha.mp3 (music bed), carro.png
edicoes/<id>/          roteiro.json · final.mp4 · contact.jpg · qa.md (voz/ and build/ stay out of git)
```

## The process, from start to finish

🧠 session with Nei · ⚙️ script (zero tokens) · 🤖 `claude -p` / Codex by subscription (never API)

| # | Step | Command | Who |
|---|---|---|---|
| 1 | Topic: thesis, 2–5 items, verified numbers (✅ with source and date) | — | 🧠 |
| 2 | Script: write `edicoes/<id>/roteiro.json` (spoken text written out, `fala_tts` for pronunciation, word triggers, hook = thesis) | edit the JSON (or 🤖 from the topic) | 🤖 + 🧠 |
| 3 | Validate format rules | `python3 rtexjp.py checar edicoes/<id>` | ⚙️ |
| 4 | Approve the script (hook, deliverable, numbers) | — | 🧠 |
| 5 | Avatar poses (once; regenerate only if the character changes) | `python3 motor/gerar_avatar.py` | ⚙️ |
| 6 | Scene images, if the item calls for them | `python3 motor/gerar_imagem.py motor/assets/x.png "<prompt>"` | ⚙️ |
| 7 | Voice by block + Whisper (word-level timing) | `python3 rtexjp.py voz edicoes/<id> [bloco …]` (with names, only those TTS blocks are regenerated) | ⚙️ |
| 8 | Scene (script + timings) | `python3 rtexjp.py cena edicoes/<id>` | ⚙️ |
| 9 | Frame preview | `node motor/render.mjs edicoes/<id>/build --quadros 0,10,20` → `edicoes/<id>/quadros/` | ⚙️ |
| 10 | Render 1080×1920 30 fps | `python3 rtexjp.py render edicoes/<id>` | ⚙️ |
| 11 | Mix (music bed stops during the maxim’s silence, −14 LUFS) | `python3 rtexjp.py mix edicoes/<id>` | ⚙️ |
| 12 | Automatic QA + contact sheet | `python3 rtexjp.py qa edicoes/<id>` → `qa.md`, `contact.jpg` | ⚙️ |
| 13 | Review `contact.jpg` and the video; independent reviewer if publishing | — | 🧠 / 🤖 |
| 14 | **CTA deliverable live** (page on inema.club with what the CTA promises) | — | orchestrator |
| 15 | Publish (channel queue / v3 / Telegram) | outside this repo | orchestrator |

Shortcut: `python3 rtexjp.py tudo edicoes/<id>` runs 3 → 7 → 8 → 10 → 11 → 12.

## Requirements

- `~/projetos/inemavox` (chatterbox TTS in `venv`, Whisper large-v3), voice `~/projetos/timesmkt3/media/voice-refs/nei.wav`
- local image server `http://localhost:8000` (flux2-klein), photo `~/projetos/inema-referencias/nei-avatar.jpg`
- Node + `npm i` (Playwright 1.64), ffmpeg, Python 3 with Pillow and numpy

## Edit 2026-10-28 — “5 AI things this month that almost nobody noticed”

`edicoes/2026-10-28-5-coisas/final.mp4` — 5 items (one folder per task, ponytail, Roadster, Understand Anything, ECC), hook **SETUP**.

> ⚠️ **Before publishing:** the CTA promises “the five links and the commands.” That package **must exist** on inema.club/guia (a page with the 5 links and installation commands) before the video goes live. Responsible: orchestrator.