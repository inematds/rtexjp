# rtexjp — motor de reels ilustrados 9:16

[![rtexjp](capa/capa.png)](https://inematds.github.io/rtexjp/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

O rtexjp é um motor que monta vídeos curtos verticais (reels) ilustrados, em roxo, a partir de um roteiro escrito num arquivo de texto (`roteiro.json`). É o motor que o Nei usa nos reels do INEMA, aberto para quem quiser estudar ou adaptar: sem gravar a si mesmo e sem pagar serviço de avatar. Ele gera a voz, desenha cada cena quadro a quadro, mistura a trilha e confere sozinho se o vídeo segue o formato. Precisa de um computador com placa de vídeo (GPU), Python, Node, ffmpeg e dois servidores locais: o de voz ([inemavox](https://github.com/inematds/inemavox)) e o de imagem ([inemaimg](https://github.com/inematds/inemaimg), flux2-klein).

Vem configurado com a voz e o avatar do Nei. Para usar os seus, troque a gravação de referência da voz (`VOZ_REF` no `rtexjp.py`) e a foto do avatar (`REF` no `motor/gerar_avatar.py`) e gere as poses de novo; esses dois arquivos não vêm no repositório.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/rtexjp/guia/** · vídeo exemplo: https://www.youtube.com/watch?v=AZEZK1YgF98

**v1.0.0** · motor local e grátis que transforma um `roteiro.json` num reel vertical 1080×1920 no **padrão rtexjp**: um reel ilustrado, fundo quase preto com feixe de luz roxa, avatar ilustrado do Nei (sem lip-sync, em poses), mascote robô, legenda-manchete de 2–3 palavras e um único CTA "comenta PALAVRA".

## O formato (padrão rtexjp)

Esqueleto fixo, conferido pelo validador:

1. **Tese escrita no quadro 0** — caixa alta, uma palavra em lilás; serve de capa (quem rola sem som lê a tese).
2. **Prova social com número na tela** — contador que pousa no número, linha de fonte em monoespaçada embaixo.
3. **A palavra-isca é a tese e é plantada cedo** (aqui: SETUP, ~65 s antes do pedido), sempre na única cor quente do vídeo.
4. **"N peças" anunciadas com índice visível** (pasta 01…05) e barra de pílulas 01–05 no topo durante as peças.
5. **Uma peça por vez, um objeto visual por frase** — o objeto muda dentro da cena a cada ~2–3 s (robôs, fio que arrebenta, pasta, card de repositório, carimbo, mapa que se desenha, terminal).
6. **Prova com fonte na tela** — todo número tem `fonte: …` escrito.
7. **Ressalva honesta falada**, em cartão de alerta (vermelho = problema, verde = certo).
8. **Máxima em antítese**, depois de **0,8 s de silêncio real** (voz e cama param).
9. **CTA "comenta PALAVRA"** com a caixa de comentário digitando a palavra → Publicar → confirmação; cartão segurado ~9–10 s, sem despedida, último trecho sem legenda.

Visual: fundo `#05040f`, roxo `#6b51d2`/`#7e58eb`, lilás `#a080ef`/`#9974f8`, branco; laranja `#f59f0c` **só** na palavra-isca; verde/vermelho só para certo/errado. Títulos em Anton (condensada caixa alta), rótulos e fontes em JetBrains Mono, legenda em Montserrat ExtraBold a ~77 % da altura. Zonas seguras do Reels: nada útil abaixo de 80 % da altura nem na faixa direita dos ícones (exceto o terminal de propósito cortado na borda — o entregável fica atrás do comentário).

Áudio: voz do Nei (inemavox chatterbox, 0,6/0,6, `atempo` ≤ 1,15, pausas internas encurtadas), 160–190 palavras/min, cama musical baixa com sidechain, master −14 LUFS.

> **Exceção ao kit INEMA:** paleta roxa/lilás, avatar ilustrado e mascote são decisão de projeto (registrada em `inema-design/DECISOES.md`). O resto do kit vale.

## Estrutura

```
rtexjp.py              pipeline: checar · voz · cena · render · mix · qa · tudo
medir.py               QA automático (duração, wpm, LUFS, trocas/min, isca, cartão final, silêncio, grep de fonte) + contact.jpg
motor/palco.html       o palco: componentes de cena desenhados por window.render(t) (determinístico)
motor/render.mjs       Playwright quadro a quadro -> ffmpeg (30 fps)
motor/gerar_avatar.py  poses do avatar no flux2-klein local com a foto de referência (fundo verde recortado)
motor/gerar_imagem.py  imagem de cena no flux2-klein local
motor/whisper.py       Whisper large-v3 local (inemavox) com tempo por palavra
motor/avatar/*.png     poses: bracos, queixo, apontando, segurando, surpreso, mostrando
motor/assets/          trilha.mp3 (cama), carro.png
edicoes/<id>/          roteiro.json · final.mp4 · contact.jpg · qa.md (voz/ e build/ ficam fora do git)
```

## O processo, do início ao fim

🧠 sessão com o Nei · ⚙️ script (zero token) · 🤖 `claude -p` / Codex pela assinatura (nunca API)

| # | Passo | Comando | Quem |
|---|---|---|---|
| 1 | Pauta: tese, 2–5 peças, números conferidos (✅ com fonte e data) | — | 🧠 |
| 2 | Roteiro: escrever `edicoes/<id>/roteiro.json` (fala por extenso, `fala_tts` para pronúncia, gatilhos por palavra, isca = tese) | editar o JSON (ou 🤖 a partir da pauta) | 🤖 + 🧠 |
| 3 | Validar regras do formato | `python3 rtexjp.py checar edicoes/<id>` | ⚙️ |
| 4 | Aprovar o roteiro (isca, entregável, números) | — | 🧠 |
| 5 | Poses do avatar (uma vez; refazer só se mudar o personagem) | `python3 motor/gerar_avatar.py` | ⚙️ |
| 6 | Imagens de cena, se a peça pedir | `python3 motor/gerar_imagem.py motor/assets/x.png "<prompt>"` | ⚙️ |
| 7 | Voz por bloco + Whisper (tempo por palavra) | `python3 rtexjp.py voz edicoes/<id> [bloco …]` (com nomes, refaz só esses TTS) | ⚙️ |
| 8 | Cena (roteiro + tempos) | `python3 rtexjp.py cena edicoes/<id>` | ⚙️ |
| 9 | Prévia de quadros | `node motor/render.mjs edicoes/<id>/build --quadros 0,10,20` → `edicoes/<id>/quadros/` | ⚙️ |
| 10 | Render 1080×1920 30 fps | `python3 rtexjp.py render edicoes/<id>` | ⚙️ |
| 11 | Mixagem (cama para no silêncio da máxima, −14 LUFS) | `python3 rtexjp.py mix edicoes/<id>` | ⚙️ |
| 12 | QA automático + contact sheet | `python3 rtexjp.py qa edicoes/<id>` → `qa.md`, `contact.jpg` | ⚙️ |
| 13 | Olhar o `contact.jpg` e o vídeo; revisor independente se for publicar | — | 🧠 / 🤖 |
| 14 | **Entregável do CTA no ar** (página no inema.club com o que o CTA promete) | — | orquestrador |
| 15 | Publicar (fila do canal / v3 / Telegram) | fora deste repo | orquestrador |

Atalho: `python3 rtexjp.py tudo edicoes/<id>` roda 3 → 7 → 8 → 10 → 11 → 12.

## Requisitos

- `~/projetos/inemavox` (TTS chatterbox no `venv`, Whisper large-v3), voz `~/projetos/timesmkt3/media/voice-refs/nei.wav`
- servidor de imagem local `http://localhost:8000` (flux2-klein), foto `~/projetos/inema-referencias/nei-avatar.jpg`
- Node + `npm i` (Playwright 1.64), ffmpeg, Python 3 com Pillow e numpy

## Edição 2026-10-28 — "5 coisas de IA deste mês que quase ninguém percebeu"

`edicoes/2026-10-28-5-coisas/final.mp4` — 5 peças (uma pasta por tarefa, ponytail, Roadster, Understand Anything, ECC), isca **SETUP**.

> ⚠️ **Antes de publicar:** o CTA promete "os cinco links e os comandos". Esse pacote **precisa existir** no inema.club/guia (página com os 5 links e os comandos de instalação) antes do vídeo ir ao ar. Responsável: orquestrador.
