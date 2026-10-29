# FALHAS — rtexjp

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 2026-10-28 | pose `surpreso` com verde do fundo preso entre as mãos (o flood fill só tira o verde ligado à borda) | `recortar` também zera verde forte isolado | infra |
| 2026-10-28 | `checar` acusou "número na tela sem fonte" na máxima por causa de tamanho/posição (`tam: 140`, `y: 620`) | conferir só os textos de `cena`/`tela`, não números de layout | prompt |
| 2026-10-28 | Mono e sans saíram em serifa no palco (woff2 do JetBrains com 11 KB = subconjunto sem os glifos) | trocar por TTF completo (JetBrains Mono, Montserrat) | infra |
| 2026-10-28 | `mix` parou: rótulo `[v]` usado duas vezes no filtergraph | `asplit=2[vz][vsc]` | prompt |
| 2026-10-28 | loudnorm de uma passada deu −15,0 LUFS | loudnorm em duas passadas (medida + `linear=true`) | infra |
| 2026-10-28 | grep da fonte proibida casava com o próprio padrão (medir.py, CLAUDE.md) | padrão montado em partes + `medir.py --grep` | prompt |
| 2026-10-28 | trocas visuais 10,3/min (< 17): mudanças pequenas demais no fundo escuro | flash tipográfico (stinger) por peça + cartões mais claros → 18,5/min | prompt |
| 2026-10-28 | voz a 86–106 wpm em blocos do chatterbox (pausas internas longas) | encurtar pausas internas para ≤ 0,16 s + refazer o TTS do bloco | infra |
