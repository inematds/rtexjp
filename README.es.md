# rtexjp — motor de reels ilustrados 9:16

[![rtexjp](capa/capa.png)](https://inematds.github.io/rtexjp/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

rtexjp es un motor que crea videos cortos verticales (reels) ilustrados en azul marino a partir de un guion escrito en un archivo de texto (`roteiro.json`). Es el motor que Nei usa en los reels de INEMA, abierto para quien quiera estudiarlo o adaptarlo: sin grabarse a sí mismo y sin pagar por un servicio de avatar. Genera la voz, dibuja cada escena fotograma a fotograma, mezcla la música y comprueba por sí solo que el video siga el formato. Necesita una computadora con tarjeta gráfica (GPU), Python, Node, ffmpeg y dos servidores locales: el de voz ([inemavox](https://github.com/inematds/inemavox)) y el de imagen ([inemaimg](https://github.com/inematds/inemaimg), flux2-klein).

Viene configurado con la voz y el avatar de Nei. Para usar los tuyos, apunta las variables de entorno `RTEXJP_VOZ_REF` (grabación de referencia de voz, `.wav`) y `RTEXJP_AVATAR_REF` (foto del avatar) a tus archivos, describe tu personaje en `RTEXJP_AVATAR_DESC` y vuelve a generar las poses (`python3 motor/gerar_avatar.py`); esos dos archivos no están incluidos en el repositorio. Consulta **Rutas y variables de entorno** más abajo.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/rtexjp/guia/** · 1.er video (paleta antigua, morada): https://www.youtube.com/watch?v=AZEZK1YgF98

**v1.2.0** · motor local y gratuito que transforma un `roteiro.json` en un reel vertical 1080×1920 con el **estándar rtexjp**: un reel ilustrado en azul marino (con cambios a papel azul hielo), avatar ilustrado de Nei **grande** (≈ 43 % de la altura, en 11 poses vinculadas a la emoción del habla, sin sincronización labial), un **dibujo protagonista** por escena, **captura real** como prueba, titular Sora centrado, subtítulos karaoke, mascota robot y una única CTA de **opinión** (una pregunta con postura, respondida con una palabra: "comenta DONO o REFÉM").

## El formato (estándar rtexjp)

Estructura fija, comprobada por el validador (`checar`) y el QA (`qa`):

1. **Gancho en el fotograma 0** (`gancho.tipo` en el guion), uno de estos: **contrario** (manda parar algo que todo el mundo hace), **pérdida** (¿y si X desapareciera?), **estadística de miedo** con fuente en pantalla o **historia de un tercero** con número. Prohibido: listas ("5 cosas…"), "¿sabías que…?", "yo hice…".
2. **Titular del fotograma 0** con unas 6 palabras como máximo, en mayúsculas, **una** palabra en amarillo, más agresivo que el habla (el texto atrae a quien se desplaza sin sonido, la voz suaviza el tono). Ya está listo en el fotograma 0, que sirve de portada. Un **objeto-metáfora con daño** dibujado (tachado en rojo, desapareciendo, roto), el avatar **reacciona** en el primer segundo y algo cambia cada ~1 s durante los primeros 3 segundos.
3. **Prueba antes de los 20 s**: cifra con fuente (contador que aterriza en la cifra, línea de fuente en monoespaciado debajo) o autoridad.
4. **El problema de quien mira, con absolución** ("no es culpa tuya, nadie te enseñó X"); aquí se plantea la **tensión del anzuelo**: las opciones de la pregunta final aparecen en pantalla, en amarillo.
5. **Un tema por video**; el método en 2–5 **partes** anunciadas con un índice visible y una barra de píldoras en la parte superior durante las partes.
6. **Una parte a la vez, un objeto visual por frase**: el objeto cambia dentro de la escena cada ~2–3 s.
7. **Salvedad honesta en voz alta**, en una tarjeta de alerta (rojo = problema, verde = correcto).
8. **Máxima en antítesis**, después de **0,8 s de silencio real** (la voz y la música se detienen).
9. **CTA de opinión**: pregunta fuerte, emocional y con postura, vinculada a la tesis; Nei dice su postura antes ("yo quiero ser dueño de lo mío") y pide una respuesta de una palabra ("comenta DONO o REFÉM"). La tarjeta muestra la pregunta + las opciones; el cuadro de comentarios escribe una opción → Publicar → confirmación, que permanece ~10 s, sin despedida. **Prohibido prometer una entrega** ("te lo mando", "te lo envío", "comenta X y…"): Nei no responde comentarios. El enlace y la fuente quedan fijos en el comentario fijado/la descripción (bloque `publicar` del guion), nunca como recompensa por comentar.

Visual (v1.2, ediciones con `"versao": "rtexjp/3"`): cada fotograma tiene la misma estructura, de arriba abajo: etiqueta en mono (≥ 30 px) · **titular en Sora ExtraBold, centrado, 2–3 líneas, ≥ 96 px**, blanco `#f4f7fc` con una palabra en azul acero claro `#93c5fd` (amarilla `#FACC15` solo en el fotograma 0) · **dibujo protagonista** (objeto ilustrado con el mismo estilo flat del avatar, de la biblioteca `motor/assets/objetos/`, o la **captura real** de la página de la fuente con la línea `fonte:` debajo) · **subtítulo karaoke** (Montserrat ExtraBold 74 px con contorno negro, la palabra pronunciada en azul acero) en una franja propia · **avatar grande**, abajo y centrado (820 px, ≈ 43 % de la altura), en la pose del bloque o del momento. El fondo tiene un foco de luz y grano ligero, y alterna entre azul marino `#07111f` y papel azul hielo `#e8eef7` (`cena.tema: "claro"`, letras azul marino, destacado en una franja `#1e3a8a`). Durante el silencio previo a la máxima, el último fotograma queda congelado con el avatar pensativo: nunca una pantalla vacía. El amarillo se usa solo en la palabra clave del fotograma 0 y en la pregunta/opciones del anzuelo (texto `#1a1206` sobre el relleno); verde/rojo solo para correcto/incorrecto. Zonas seguras de Reels: rostro, texto y objetos por encima del 80 % de la altura (por debajo, solo el torso del avatar).

**Control de calidad visual** (`medir.py`, solo en `rtexjp/3`): el escenario mide en su propio DOM, con 2 muestras por bloque, el titular (≥ 96 px), todo el texto (≥ 30 px), el área ocupada en el cuadro útil (≥ 55 %), el contraste del texto (WCAG ≥ 4,5:1) y la altura del avatar (≥ 38 %).

Las ediciones antiguas (`rtexjp/2`) conservan el aspecto de la v1.1 (Anton a la izquierda, avatar pequeño en una esquina).

Audio: voz de Nei (inemavox chatterbox, 0,6/0,6, `atempo` ≤ 1,15, pausas internas acortadas), 160–190 palabras/min, música de fondo baja con sidechain, master −14 LUFS.

> **Excepción al kit INEMA:** el avatar ilustrado y la mascota robot son decisiones del proyecto (registradas en `inema-design/DECISOES.md`, D19). La paleta sigue el espíritu del kit: azul marino + azul, amarillo `#FACC15` como único color cálido. La primera edición (`2026-10-28-5-coisas`) es del formato antiguo —paleta morada, gancho de lista y anzuelo con material entregable— y se queda como está porque ya se publicó.

## Rutas y variables de entorno

| Variable | Para qué | Predeterminado |
|---|---|---|
| `RTEXJP_INEMAVOX` | carpeta de inemavox (TTS chatterbox en `venv` + Whisper large-v3) | `~/projetos/inemavox` |
| `RTEXJP_VOZ_REF` | grabación de referencia de voz (`.wav`) | `~/projetos/timesmkt3/media/voice-refs/nei.wav` |
| `RTEXJP_IMG_URL` | servidor de imagen flux2-klein (`motor/gerar_avatar.py`, `motor/gerar_imagem.py`) | `http://localhost:8000/generate` |
| `RTEXJP_AVATAR_REF` | foto de referencia del avatar | `~/projetos/inema-referencias/nei-avatar.jpg` |
| `RTEXJP_AVATAR_DESC` | rasgos y ropa del personaje en la solicitud de imagen (en inglés); cambiar junto con la foto | gorra negra, gafas, barba canosa, camiseta azul acero (Nei) |
| `RTEXJP_TRILHA` | música de fondo de la mezcla (para publicar, usa música cuya licencia conozcas) | `motor/assets/trilha.mp3` |
| `CS_WHISPER_PY` | Python del entorno con faster-whisper (servidor de Whisper y plan B) | `~/miniconda3/envs/chatterbox/bin/python3` |
| `CHATTERBOX_PYTHON` | Python del entorno de chatterbox, requerido por `tts_direct.py` de inemavox | el del entorno `chatterbox` |

Ejemplo: `RTEXJP_VOZ_REF=~/minha-voz.wav RTEXJP_INEMAVOX=~/inemavox python3 rtexjp.py voz edicoes/minha-edicao`.

## Estructura

```
rtexjp.py              pipeline: checar · voz · cena · render · mix · qa · tudo
medir.py               QA automático (duración, wpm, LUFS, cambios/min, anzuelo, tarjeta final, silencio, búsqueda de fuente) + contact.jpg
motor/palco.html       el escenario: estructura v1.2 (titular, protagonista, avatar, subtítulo) dibujada por window.render(t) + window.medidas(t) (control de calidad visual)
motor/render.mjs       Playwright fotograma a fotograma -> ffmpeg (30 fps)
motor/gerar_avatar.py  poses del avatar en flux2-klein local con la foto de referencia (fondo verde recortado)
motor/capturar_prova.mjs print real da fonte para a prova (Playwright, tema escuro, 2x)
motor/gerar_objeto.py  dibujo protagonista en flux2-klein local -> motor/assets/objetos/<nome>.png + indice.json
motor/gerar_imagem.py  imagen de escena en flux2-klein local
motor/whisper.py       Whisper large-v3 local (inemavox) con tiempo por palabra
motor/avatar/*.png     11 poses: bracos, queixo, apontando, segurando, surpreso, mostrando, explica, olha, polegar, duvida, susto
motor/assets/objetos/  biblioteca de dibujos protagonistas (terminal_quebrado, mapa_pinos, lupa_arquivos, dominos, chave_dono…) + indice.json
motor/assets/          trilha.mp3 (música), grao.png (textura), carro.png
motor/fontes/          Sora, Anton, JetBrains Mono, Montserrat (OFL)
edicoes/<id>/          roteiro.json · final.mp4 · contact.jpg · qa.md · prova/ (capturas reales) (voz/ y build/ quedan fuera de git)
```

## El proceso, de principio a fin

🧠 sesión con Nei · ⚙️ script (cero tokens) · 🤖 `claude -p` / Codex con suscripción (nunca API)

| # | Paso | Comando | Quién |
|---|---|---|---|
| 1 | Tema: tesis, 2–5 partes, cifras verificadas (✅ con fuente y fecha) | — | 🧠 |
| 2 | Guion: escribir `edicoes/<id>/roteiro.json` (`gancho`, `isca` de opinión, texto completo, `fala_tts` para la pronunciación, activadores por palabra, bloque `publicar`) | editar el JSON (o 🤖 a partir del tema) | 🤖 + 🧠 |
| 3 | Validar las reglas del formato | `python3 rtexjp.py checar edicoes/<id>` | ⚙️ |
| 4 | Aprobar el guion (gancho, pregunta del anzuelo, cifras) | — | 🧠 |
| 5 | Poses del avatar (una vez; volver a generarlas solo si cambia el personaje): revisar cada una y rehacer las deformadas | `python3 motor/gerar_avatar.py [pose …]` | ⚙️ |
| 6 | Dibujo protagonista que falte en la biblioteca (revisar y volver a generarlo con otra seed si sale torcido) | `python3 motor/gerar_objeto.py <nome> "<objeto em inglês>" [seed]` | ⚙️ |
| 6b | Captura real de la fuente (página del repositorio, recortada para mostrar el nombre y el contador) en `edicoes/<id>/prova/` | `node motor/capturar_prova.mjs <url> edicoes/<id>/prova/x.png [--clip x,y,w,h]` | ⚙️ |
| 7 | Voz por bloque + Whisper (tiempo por palabra) | `python3 rtexjp.py voz edicoes/<id> [bloco …]` (con nombres, vuelve a generar solo esos TTS) | ⚙️ |
| 8 | Escena (guion + tiempos) | `python3 rtexjp.py cena edicoes/<id>` | ⚙️ |
| 9 | Vista previa de fotogramas (+ `quadros/medidas.json` del control de calidad visual) | `node motor/render.mjs edicoes/<id>/build --quadros 0,10,20` → `edicoes/<id>/quadros/` | ⚙️ |
| 10 | Render 1080×1920 30 fps | `python3 rtexjp.py render edicoes/<id>` | ⚙️ |
| 11 | Mezcla (la música se detiene durante el silencio de la máxima, −14 LUFS) | `python3 rtexjp.py mix edicoes/<id>` | ⚙️ |
| 12 | QA automático + control de calidad visual + hoja de contactos | `python3 rtexjp.py qa edicoes/<id>` → `qa.md`, `contact.jpg` | ⚙️ |
| 13 | Revisar `contact.jpg` y el video; revisor independiente (`claude -p`, lista fija en `CLAUDE.md`, nota de 0–10 sobre "¿dejaría de desplazarse?" por fotograma clave) | — | 🧠 / 🤖 |
| 14 | Publicar (cola del canal / v3 / Telegram) con el bloque `publicar` del guion | fuera de este repositorio | orquestador |

Atajo: `python3 rtexjp.py tudo edicoes/<id>` ejecuta 3 → 7 → 8 → 10 → 11 → 12.

## Requisitos

- inemavox (TTS chatterbox en `venv`, Whisper large-v3) y la grabación de referencia de voz — `RTEXJP_INEMAVOX`, `RTEXJP_VOZ_REF`
- servidor de imagen local flux2-klein y foto del avatar — `RTEXJP_IMG_URL`, `RTEXJP_AVATAR_REF`
- Node + `npm i` (Playwright 1.64), ffmpeg, Python 3 con Pillow y numpy

## Ediciones

### 2026-10-28-mapa-v2 — "O Claude sumiu. E agora?" (visual v1.2)

`edicoes/2026-10-28-mapa-v2/final.mp4` — el mismo guion, gancho de pérdida y anzuelo DONO/REFÉM de la edición de abajo, rehecho con el visual v1.2: avatar grande en 9 de las 11 poses, un dibujo protagonista por momento, captura real de GitHub (88,8 mil estrellas el 28/10/2026), papel azul hielo en dos escenas. `comparativo.jpg` pone 4 fotogramas de la v1 arriba y de la v2 abajo.

### 2026-10-28-mapa — "O Claude sumiu. E agora?" (visual v1.1)

`edicoes/2026-10-28-mapa/final.mp4` — se conserva para comparar. Un tema (Understand Anything), gancho de **pérdida**, 3 partes (el mapa, la explicación, el impacto), anzuelo de opinión **DONO o REFÉM**. Título, descripción y comentario fijado en el bloque `publicar` de `roteiro.json`.

### 2026-10-28-5-coisas — "5 coisas de IA deste mês que quase ninguém percebeu" (formato antiguo)

`edicoes/2026-10-28-5-coisas/final.mp4` — publicado en https://www.youtube.com/watch?v=AZEZK1YgF98. Paleta morada, gancho de lista y anzuelo con material entregable (SETUP): reglas que el formato actual prohíbe. Se conserva en el repositorio como registro; `checar` todavía acepta ese guion, con aviso de LEGADO.
