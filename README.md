# rtexjp — motor de reels ilustrados 9:16

[![rtexjp](capa/capa.png)](https://inematds.github.io/rtexjp/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

O rtexjp é um motor que monta vídeos curtos verticais (reels) ilustrados, em azul-marinho, a partir de um roteiro escrito num arquivo de texto (`roteiro.json`). É o motor que o Nei usa nos reels do INEMA, aberto para quem quiser estudar ou adaptar: sem gravar a si mesmo e sem pagar serviço de avatar. Ele gera a voz, desenha cada cena quadro a quadro, mistura a trilha e confere sozinho se o vídeo segue o formato. Precisa de um computador com placa de vídeo (GPU), Python, Node, ffmpeg e dois servidores locais: o de voz ([inemavox](https://github.com/inematds/inemavox)) e o de imagem ([inemaimg](https://github.com/inematds/inemaimg), flux2-klein).

Vem configurado com a voz e o avatar do Nei. Para usar os seus, aponte as variáveis de ambiente `RTEXJP_VOZ_REF` (gravação de referência da voz, `.wav`) e `RTEXJP_AVATAR_REF` (foto do avatar) para os seus arquivos, descreva o seu personagem em `RTEXJP_AVATAR_DESC` e gere as poses de novo (`python3 motor/gerar_avatar.py`); esses dois arquivos não vêm no repositório. Veja **Caminhos e variáveis de ambiente** abaixo.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/rtexjp/guia/** · 1º vídeo (paleta antiga, roxa): https://www.youtube.com/watch?v=AZEZK1YgF98

**v1.1.0** · motor local e grátis que transforma um `roteiro.json` num reel vertical 1080×1920 no **padrão rtexjp**: um reel ilustrado, fundo azul-marinho quase preto com feixe de luz azul, avatar ilustrado do Nei (sem lip-sync, em poses), mascote robô, legenda-manchete de 2–3 palavras e um único CTA de **opinião** (uma pergunta com lado, respondida com uma palavra: "comenta DONO ou REFÉM").

## O formato (padrão rtexjp)

Esqueleto fixo, conferido pelo validador (`checar`) e pelo QA (`qa`):

1. **Gancho no quadro 0** (`gancho.tipo` no roteiro), um destes: **contrário** (manda parar algo que todo mundo faz), **perda** (e se X sumisse?), **estatística de medo** com fonte na tela, ou **história de terceiro** com número. Proibido: lista ("5 coisas…"), "você sabia que…", "eu fiz…".
2. **Manchete do quadro 0** com no máximo ~6 palavras, caixa alta, **uma** palavra em amarelo, mais agressiva que a fala (o texto puxa quem rola sem som, a voz suaviza). Já está pronta no quadro 0, que serve de capa. Um **objeto-metáfora com dano** desenhado (riscado de vermelho, sumindo, quebrado), o avatar **reage** no 1º segundo e algo muda a cada ~1 s nos 3 primeiros segundos.
3. **Prova até 20 s** — número com fonte (contador que pousa no número, linha de fonte em monoespaçada embaixo) ou autoridade.
4. **O problema de quem assiste, com absolvição** ("não é culpa sua, ninguém te deu X") — e aqui a **tensão da isca** é plantada: as opções da pergunta final aparecem na tela, em amarelo.
5. **Um tema por vídeo**; o método em 2–5 **peças** anunciadas com índice visível e barra de pílulas no topo durante as peças.
6. **Uma peça por vez, um objeto visual por frase** — o objeto muda dentro da cena a cada ~2–3 s.
7. **Ressalva honesta falada**, em cartão de alerta (vermelho = problema, verde = certo).
8. **Máxima em antítese**, depois de **0,8 s de silêncio real** (voz e cama param).
9. **CTA de opinião**: pergunta forte, emocional e com lado, ligada à tese; o Nei diz o lado dele antes ("eu quero ser dono do meu") e pede a resposta em uma palavra ("comenta DONO ou REFÉM"). O cartão mostra a pergunta + as opções, a caixa de comentário digita uma opção → Publicar → confirmação, segurado ~10 s, sem despedida. **Proibido prometer entrega** ("te mando", "eu envio", "comenta X que…"): o Nei não responde comentários. Link e fonte ficam parados no comentário fixado/descrição (bloco `publicar` do roteiro), nunca como recompensa por comentar.

Visual: fundo azul-marinho `#07111f` (cartões `#0b1a30`/`#12284a`), azul royal `#1e3a8a`/`#2563eb`, azul-aço `#7aa7e0`/`#93c5fd`, texto `#e6edf7`/branco; amarelo INEMA `#FACC15` **só** na palavra quente da manchete do quadro 0 e na pergunta/opções da isca (letra escura `#1a1206` quando é preenchimento); verde/vermelho só para certo/errado. Títulos em Anton (condensada caixa alta), rótulos e fontes em JetBrains Mono, legenda em Montserrat ExtraBold a ~77 % da altura. Zonas seguras do Reels: nada útil abaixo de 80 % da altura nem na faixa direita dos ícones.

Áudio: voz do Nei (inemavox chatterbox, 0,6/0,6, `atempo` ≤ 1,15, pausas internas encurtadas), 160–190 palavras/min, cama musical baixa com sidechain, master −14 LUFS.

> **Exceção ao kit INEMA:** avatar ilustrado e mascote robô são decisão de projeto (registrada em `inema-design/DECISOES.md`, D19). A paleta segue o kit em espírito: marinho + azul, amarelo `#FACC15` como única cor quente. A 1ª edição (`2026-10-28-5-coisas`) é do formato antigo — paleta roxa, gancho de lista e isca com entregável — e fica como está, porque já foi publicada.

## Caminhos e variáveis de ambiente

| Variável | Para quê | Padrão |
|---|---|---|
| `RTEXJP_INEMAVOX` | pasta do inemavox (TTS chatterbox no `venv` + Whisper large-v3) | `~/projetos/inemavox` |
| `RTEXJP_VOZ_REF` | gravação de referência da voz (`.wav`) | `~/projetos/timesmkt3/media/voice-refs/nei.wav` |
| `RTEXJP_IMG_URL` | servidor de imagem flux2-klein (`motor/gerar_avatar.py`, `motor/gerar_imagem.py`) | `http://localhost:8000/generate` |
| `RTEXJP_AVATAR_REF` | foto de referência do avatar | `~/projetos/inema-referencias/nei-avatar.jpg` |
| `RTEXJP_AVATAR_DESC` | traços e roupa do personagem no pedido de imagem (em inglês); troque junto com a foto | boné preto, óculos, barba grisalha, camiseta azul-aço (o Nei) |
| `RTEXJP_TRILHA` | cama musical do mix (para publicar, use uma música cuja licença você conheça) | `motor/assets/trilha.mp3` |
| `CS_WHISPER_PY` | Python do ambiente com faster-whisper (servidor do Whisper e plano B) | `~/miniconda3/envs/chatterbox/bin/python3` |

Exemplo: `RTEXJP_VOZ_REF=~/minha-voz.wav RTEXJP_INEMAVOX=~/inemavox python3 rtexjp.py voz edicoes/minha-edicao`.

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
| 2 | Roteiro: escrever `edicoes/<id>/roteiro.json` (`gancho`, `isca` de opinião, fala por extenso, `fala_tts` para pronúncia, gatilhos por palavra, bloco `publicar`) | editar o JSON (ou 🤖 a partir da pauta) | 🤖 + 🧠 |
| 3 | Validar regras do formato | `python3 rtexjp.py checar edicoes/<id>` | ⚙️ |
| 4 | Aprovar o roteiro (gancho, pergunta da isca, números) | — | 🧠 |
| 5 | Poses do avatar (uma vez; refazer só se mudar o personagem) | `python3 motor/gerar_avatar.py` | ⚙️ |
| 6 | Imagens de cena, se a peça pedir | `python3 motor/gerar_imagem.py motor/assets/x.png "<prompt>"` | ⚙️ |
| 7 | Voz por bloco + Whisper (tempo por palavra) | `python3 rtexjp.py voz edicoes/<id> [bloco …]` (com nomes, refaz só esses TTS) | ⚙️ |
| 8 | Cena (roteiro + tempos) | `python3 rtexjp.py cena edicoes/<id>` | ⚙️ |
| 9 | Prévia de quadros | `node motor/render.mjs edicoes/<id>/build --quadros 0,10,20` → `edicoes/<id>/quadros/` | ⚙️ |
| 10 | Render 1080×1920 30 fps | `python3 rtexjp.py render edicoes/<id>` | ⚙️ |
| 11 | Mixagem (cama para no silêncio da máxima, −14 LUFS) | `python3 rtexjp.py mix edicoes/<id>` | ⚙️ |
| 12 | QA automático + contact sheet | `python3 rtexjp.py qa edicoes/<id>` → `qa.md`, `contact.jpg` | ⚙️ |
| 13 | Olhar o `contact.jpg` e o vídeo; revisor independente se for publicar | — | 🧠 / 🤖 |
| 14 | Publicar (fila do canal / v3 / Telegram) com o bloco `publicar` do roteiro | fora deste repo | orquestrador |

Atalho: `python3 rtexjp.py tudo edicoes/<id>` roda 3 → 7 → 8 → 10 → 11 → 12.

## Requisitos

- inemavox (TTS chatterbox no `venv`, Whisper large-v3) e a gravação de referência da voz — `RTEXJP_INEMAVOX`, `RTEXJP_VOZ_REF`
- servidor de imagem local flux2-klein e a foto do avatar — `RTEXJP_IMG_URL`, `RTEXJP_AVATAR_REF`
- Node + `npm i` (Playwright 1.64), ffmpeg, Python 3 com Pillow e numpy

## Edições

### 2026-10-28-mapa — "O Claude sumiu. E agora?" (formato atual)

`edicoes/2026-10-28-mapa/final.mp4` — um tema (Understand Anything), gancho de **perda**, 3 peças (o mapa, a explicação, o impacto), isca de opinião **DONO ou REFÉM**. Título, descrição e comentário fixado no bloco `publicar` do `roteiro.json`.

### 2026-10-28-5-coisas — "5 coisas de IA deste mês que quase ninguém percebeu" (formato antigo)

`edicoes/2026-10-28-5-coisas/final.mp4` — publicado em https://www.youtube.com/watch?v=AZEZK1YgF98. Paleta roxa, gancho de lista e isca com entregável (SETUP): regras que o formato atual proíbe. Fica no repositório como registro; o `checar` ainda aceita esse roteiro, com aviso de LEGADO.
