# rtexjp — motor de reels ilustrados 9:16

[![rtexjp](capa/capa.png)](https://inematds.github.io/rtexjp/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

rtexjp es un motor que crea videos cortos verticales (reels) ilustrados, en azul marino, a partir de un guion escrito en un archivo de texto (`roteiro.json`). Es el motor que Nei usa en los reels de INEMA, abierto para quien quiera estudiarlo o adaptarlo: sin grabarse a sí mismo y sin pagar por un servicio de avatar. Genera la voz, dibuja cada escena fotograma a fotograma, mezcla la música y comprueba automáticamente si el video sigue el formato. Necesita una computadora con tarjeta gráfica (GPU), Python, Node, ffmpeg y dos servidores locales: el de voz ([inemavox](https://github.com/inematds/inemavox)) y el de imágenes ([inemaimg](https://github.com/inematds/inemaimg), flux2-klein).

Viene configurado con la voz y el avatar de Nei. Para usar los tuyos, apunta las variables de entorno `RTEXJP_VOZ_REF` (grabación de referencia de la voz, `.wav`) y `RTEXJP_AVATAR_REF` (foto del avatar) a tus archivos y vuelve a generar las poses (`python3 motor/gerar_avatar.py`); esos dos archivos no están incluidos en el repositorio. Consulta **Rutas y variables de entorno** más abajo.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/rtexjp/guia/es/** · 1.er video (paleta antigua, morada): https://www.youtube.com/watch?v=AZEZK1YgF98

**v1.1.0** · motor local y gratis que transforma un `roteiro.json` en un reel vertical de 1080×1920 con el **estándar rtexjp**: un reel ilustrado, fondo azul marino casi negro con un haz de luz azul, avatar ilustrado de Nei (sin lip-sync, en poses), mascota robot, subtítulo tipo titular de 2–3 palabras y un único CTA de **opinión** (una pregunta con dos lados, que se responde con una palabra: «comenta DONO (DUEÑO) o REFÉM (REHÉN)»).

## El formato (estándar rtexjp)

Estructura fija, comprobada por el validador (`checar`) y por el QA (`qa`):

1. **Gancho en el fotograma 0** (`gancho.tipo` en el guion), uno de estos: **contrario** (manda dejar de hacer algo que todo el mundo hace), **pérdida** (¿y si X desapareciera?), **estadística que da miedo** con la fuente en pantalla, o **historia de otra persona** con una cifra. Prohibido: listas («5 cosas…»), «¿sabías que…?», «yo hice…».
2. **Titular del fotograma 0** de unas 6 palabras como máximo, en mayúsculas, **una** palabra en amarillo, más agresivo que lo que se dice (el texto atrae a quien desliza sin sonido, la voz suaviza el mensaje). Ya aparece en el fotograma 0, que sirve de portada. Un **objeto metáfora dañado** dibujado (tachado en rojo, desapareciendo, roto), el avatar **reacciona** en el primer segundo y algo cambia cada ~1 s durante los 3 primeros segundos.
3. **Prueba antes de los 20 s**: cifra con fuente (contador que llega al número, línea de fuente en monoespaciada debajo) o autoridad.
4. **El problema de quien mira, con absolución** («no es culpa tuya, nadie te enseñó X»); aquí se plantea la **tensión de la carnada**: las opciones de la pregunta final aparecen en pantalla, en amarillo.
5. **Un tema por video**; el método, dividido en 2–5 **piezas**, se anuncia con un índice visible y una barra de cápsulas en la parte superior durante las piezas.
6. **Una pieza a la vez, un objeto visual por frase**: el objeto cambia dentro de la escena cada ~2–3 s.
7. **Advertencia honesta en voz alta**, en una tarjeta de alerta (rojo = problema, verde = correcto).
8. **Frase máxima en antítesis**, seguida de **0,8 s de silencio real** (se detienen la voz y la música de fondo).
9. **CTA de opinión**: pregunta fuerte, emocional y con dos lados, vinculada a la tesis; Nei dice cuál es su lado («yo quiero ser dueño de lo mío») y pide una respuesta de una palabra («comenta DONO (DUEÑO) o REFÉM (REHÉN)»). La tarjeta muestra la pregunta y las opciones; el cuadro de comentarios escribe una opción → Publicar → confirmación, que se mantiene unos 10 s, sin despedida. **Prohibido prometer algo a cambio** («te lo mando», «te lo envío», «comenta X y…»): Nei no responde a los comentarios. El enlace y la fuente quedan visibles en el comentario fijado o en la descripción (bloque `publicar` del guion), nunca como recompensa por comentar.

Visual: fondo azul marino `#07111f` (tarjetas `#0b1a30`/`#12284a`), azul real `#1e3a8a`/`#2563eb`, azul acero `#7aa7e0`/`#93c5fd`, texto `#e6edf7`/blanco; amarillo INEMA `#FACC15` **solo** en la palabra destacada del titular del fotograma 0 y en la pregunta/opciones de la carnada (texto oscuro `#1a1206` cuando se usa como relleno); verde/rojo solo para correcto/incorrecto. Títulos en Anton (condensada en mayúsculas), etiquetas y fuentes en JetBrains Mono, subtítulo en Montserrat ExtraBold al ~77 % de la altura. Zonas seguras de Reels: nada importante por debajo del 80 % de la altura ni en la franja derecha de los iconos.

Audio: voz de Nei (inemavox chatterbox, 0,6/0,6, `atempo` ≤ 1,15, pausas internas acortadas), 160–190 palabras/min, música de fondo baja con sidechain, master −14 LUFS.

> **Excepción al kit INEMA:** el avatar ilustrado y la mascota robot son decisiones del proyecto (registradas en `inema-design/DECISOES.md`, D19). La paleta sigue el espíritu del kit: azul marino + azul, amarillo `#FACC15` como único color cálido. La primera edición (`2026-10-28-5-coisas`) pertenece al formato antiguo —paleta morada, gancho de lista y carnada con algo prometido— y se queda como está porque ya fue publicada.

## Rutas y variables de entorno

| Variable | Para qué | Valor predeterminado |
|---|---|---|
| `RTEXJP_INEMAVOX` | carpeta de inemavox (TTS chatterbox en `venv` + Whisper large-v3) | `~/projetos/inemavox` |
| `RTEXJP_VOZ_REF` | grabación de referencia de la voz (`.wav`) | `~/projetos/timesmkt3/media/voice-refs/nei.wav` |
| `RTEXJP_IMG_URL` | servidor de imágenes flux2-klein (`motor/gerar_avatar.py`, `motor/gerar_imagem.py`) | `http://localhost:8000/generate` |
| `RTEXJP_AVATAR_REF` | foto de referencia del avatar | `~/projetos/inema-referencias/nei-avatar.jpg` |

Ejemplo: `RTEXJP_VOZ_REF=~/minha-voz.wav RTEXJP_INEMAVOX=~/inemavox python3 rtexjp.py voz edicoes/minha-edicao`.

## Estructura

```
rtexjp.py              pipeline: checar · voz · cena · render · mix · qa · tudo
medir.py               QA automático (duración, wpm, LUFS, cambios/min, carnada, tarjeta final, silencio, grep de fuente) + contact.jpg
motor/palco.html       el escenario: componentes de escena dibujados por window.render(t) (determinista)
motor/render.mjs       Playwright fotograma a fotograma -> ffmpeg (30 fps)
motor/gerar_avatar.py  poses del avatar con flux2-klein local y la foto de referencia (fondo verde recortado)
motor/gerar_imagem.py  imagen de escena con flux2-klein local
motor/whisper.py       Whisper large-v3 local (inemavox) con tiempo por palabra
motor/avatar/*.png     poses: bracos, queixo, apontando, segurando, surpreso, mostrando
motor/assets/          trilha.mp3 (música de fondo), carro.png
edicoes/<id>/          roteiro.json · final.mp4 · contact.jpg · qa.md (voz/ y build/ quedan fuera de git)
```

## El proceso de principio a fin

🧠 sesión con Nei · ⚙️ script (cero tokens) · 🤖 `claude -p` / Codex por suscripción (nunca API)

| # | Paso | Comando | Quién |
|---|---|---|---|
| 1 | Tema: tesis, 2–5 piezas, cifras comprobadas (✅ con fuente y fecha) | — | 🧠 |
| 2 | Guion: escribir `edicoes/<id>/roteiro.json` (`gancho`, `isca` de opinión, texto hablado completo, `fala_tts` para pronunciación, activadores por palabra, bloque `publicar`) | editar el JSON (o 🤖 a partir del tema) | 🤖 + 🧠 |
| 3 | Validar las reglas del formato | `python3 rtexjp.py checar edicoes/<id>` | ⚙️ |
| 4 | Aprobar el guion (gancho, pregunta de la carnada, cifras) | — | 🧠 |
| 5 | Poses del avatar (una vez; volver a generarlas solo si cambia el personaje) | `python3 motor/gerar_avatar.py` | ⚙️ |
| 6 | Imágenes de escena, si la pieza las requiere | `python3 motor/gerar_imagem.py motor/assets/x.png "<prompt>"` | ⚙️ |
| 7 | Voz por bloque + Whisper (tiempo por palabra) | `python3 rtexjp.py voz edicoes/<id> [bloco …]` (con nombres, vuelve a generar solo esos TTS) | ⚙️ |
| 8 | Escena (guion + tiempos) | `python3 rtexjp.py cena edicoes/<id>` | ⚙️ |
| 9 | Vista previa de fotogramas | `node motor/render.mjs edicoes/<id>/build --quadros 0,10,20` → `edicoes/<id>/quadros/` | ⚙️ |
| 10 | Render 1080×1920 a 30 fps | `python3 rtexjp.py render edicoes/<id>` | ⚙️ |
| 11 | Mezcla (la música se detiene durante el silencio de la frase máxima, −14 LUFS) | `python3 rtexjp.py mix edicoes/<id>` | ⚙️ |
| 12 | QA automático + hoja de contacto | `python3 rtexjp.py qa edicoes/<id>` → `qa.md`, `contact.jpg` | ⚙️ |
| 13 | Revisar `contact.jpg` y el video; usar un revisor independiente si se va a publicar | — | 🧠 / 🤖 |
| 14 | Publicar (cola del canal / v3 / Telegram) con el bloque `publicar` del guion | fuera de este repo | orquestador |

Atajo: `python3 rtexjp.py tudo edicoes/<id>` ejecuta 3 → 7 → 8 → 10 → 11 → 12.

## Requisitos

- inemavox (TTS chatterbox en `venv`, Whisper large-v3) y la grabación de referencia de la voz — `RTEXJP_INEMAVOX`, `RTEXJP_VOZ_REF`
- servidor local de imágenes flux2-klein y foto del avatar — `RTEXJP_IMG_URL`, `RTEXJP_AVATAR_REF`
- Node + `npm i` (Playwright 1.64), ffmpeg, Python 3 con Pillow y numpy

## Ediciones

### 2026-10-28-mapa — «O Claude sumiu. E agora?» (formato actual)

`edicoes/2026-10-28-mapa/final.mp4` — un tema (Understand Anything), gancho de **pérdida**, 3 piezas (el mapa, la explicación, el impacto), carnada de opinión **DONO (DUEÑO) o REFÉM (REHÉN)**. El título, la descripción y el comentario fijado están en el bloque `publicar` de `roteiro.json`.

### 2026-10-28-5-coisas — «5 coisas de IA deste mês que quase ninguém percebeu» (formato antiguo)

`edicoes/2026-10-28-5-coisas/final.mp4` — publicado en https://www.youtube.com/watch?v=AZEZK1YgF98. Paleta morada, gancho de lista y carnada con algo prometido (SETUP): reglas que el formato actual prohíbe. Se conserva en el repositorio como registro; `checar` todavía acepta ese guion, con aviso de LEGADO.
