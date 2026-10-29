# FALHAS — rtexjp

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 2026-10-29 | `rm edicoes/2026-10-28-*/prova/pagina-2026-10-28.png` apagou o print do mapa-v2 (mesmo nome de arquivo) | apagar só por caminho explícito da própria edição; restaurado com git checkout | prompt |
| 2026-10-29 | contador da prova parado no meio ("US$ 1 MIL") na amostra do QA/revisor; print largo saiu pequeno ou cortado | número fixo na manchete em vez de contador de 0 a 5; print recortado no trecho e com margem branca de 50 px | prompt |
| 2026-10-28 | sombra do objeto sobre o verde virou oliva escuro e escapou do recorte (mapa_pinos) | `tirar_sombra` no `gerar_objeto.py` + prompt sem sombra projetada | infra |
| 2026-10-28 | legenda branca de contorno preto pesada no papel azul-gelo (revisor) | no tema claro, legenda marinho com contorno branco | prompt |
| 2026-10-28 | v1.1 com ~1 s de tela vazia antes da máxima (o bloco `maxima` herda o silêncio e o `flash` não desenhava nada) | no silêncio, congelar o último quadro do bloco anterior com o avatar pensativo | prompt |
| 2026-10-28 | legenda da casca v1.2 caiu sobre a boca do avatar grande (y 1420) e depois sobre o pé do herói | faixa própria da legenda (y 985) entre o herói (até 975) e o boné (1100) | prompt |
| 2026-10-28 | objetos-herói `chave_dono`/`pasta_unica` com manchas vermelhas ("vermelho só para dano" virou respingo) | prompt com "no red, no damage, no stains" + outra seed | prompt |
| 2026-10-28 | guia reprovado pelo revisor (7/10): 2º vídeo sem player e troca de avatar exigindo editar o prompt fixo do Nei | `<video>` apontando para o final.mp4 do repo + `RTEXJP_AVATAR_DESC` (e `RTEXJP_TRILHA`, `CS_WHISPER_PY` no plano B do Whisper) | prompt |
| 2026-10-28 | pose `surpreso` com verde do fundo preso entre as mãos (o flood fill só tira o verde ligado à borda) | `recortar` também zera verde forte isolado | infra |
| 2026-10-28 | `checar` acusou "número na tela sem fonte" na máxima por causa de tamanho/posição (`tam: 140`, `y: 620`) | conferir só os textos de `cena`/`tela`, não números de layout | prompt |
| 2026-10-28 | Mono e sans saíram em serifa no palco (woff2 do JetBrains com 11 KB = subconjunto sem os glifos) | trocar por TTF completo (JetBrains Mono, Montserrat) | infra |
| 2026-10-28 | `mix` parou: rótulo `[v]` usado duas vezes no filtergraph | `asplit=2[vz][vsc]` | prompt |
| 2026-10-28 | loudnorm de uma passada deu −15,0 LUFS | loudnorm em duas passadas (medida + `linear=true`) | infra |
| 2026-10-28 | grep da fonte proibida casava com o próprio padrão (medir.py, CLAUDE.md) | padrão montado em partes + `medir.py --grep` | prompt |
| 2026-10-28 | trocas visuais 10,3/min (< 17): mudanças pequenas demais no fundo escuro | flash tipográfico (stinger) por peça + cartões mais claros → 18,5/min | prompt |
| 2026-10-28 | voz a 86–106 wpm em blocos do chatterbox (pausas internas longas) | encurtar pausas internas para ≤ 0,16 s + refazer o TTS do bloco | infra |
