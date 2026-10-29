# rtexjp — instruções do projeto

- Motor de reels 9:16 no **padrão rtexjp** (reel ilustrado azul-marinho, isca de opinião). Fluxo e comandos: `README.md` → "O processo, do início ao fim".
- **Paleta azul-marinho** (Nei, 28/10/2026: "não quero ele roxo, quero uma cor profissional" — `~/projetos/inema-design/DECISOES.md` D19): fundo `#07111f`, azul royal `#1e3a8a`/`#2563eb`, azul-aço `#7aa7e0`/`#93c5fd`; amarelo `#FACC15` é a única cor quente (palavra da manchete do quadro 0 e pergunta/opções da isca). Nada de roxo/lilás. **Exceção ao kit:** avatar ilustrado do Nei sem lip-sync e mascote robô. O resto do kit vale (voz do Nei 0,6/0,6, `atempo` ≤ 1,15, ano por extenso, sem SFX no meio, zonas seguras, fonte escrita na tela).
- **Nunca citar referência externa do formato**: nenhum nome de criador/perfil/marca de terceiros que inspirou o formato, nenhuma URL de rede social de referência. Antes de todo commit: `python3 medir.py --grep` → `grep_fonte 0` (o padrão fica montado em partes dentro do `medir.py`, para não casar consigo mesmo).
- Caminhos por variável de ambiente (`RTEXJP_INEMAVOX`, `RTEXJP_VOZ_REF`, `RTEXJP_IMG_URL`, `RTEXJP_AVATAR_REF`; padrões no `README.md`).
- Tudo local e grátis: voz inemavox chatterbox (voz `nei`), Whisper local, imagens flux2-klein local (`http://localhost:8000`). Nenhuma API sem autorização explícita do Nei.
- **Gancho** (Nei, 28/10/2026): `gancho.tipo` = contrario | perda | estatistica | historia; manchete do quadro 0 ≤ ~6 palavras, caixa alta, 1 palavra amarela, mais agressiva que a fala; objeto-metáfora com dano no quadro 0, avatar reage no 1º s; prova até 20 s; problema + absolvição logo depois. Proibido gancho de lista, "você sabia", "eu fiz".
- **Isca de opinião** (Nei, 28/10/2026): CTA = pergunta forte com lado (`isca.tipo: opiniao`, `pergunta`, `opcoes` de 1 palavra, `lado` dito antes). **Proibido prometer entrega** ("te mando", "eu envio", "comenta X que…") e não existe entregável: o Nei não responde comentários. Link/fonte só parados no `publicar.comentario_fixado`/descrição.
- A edição `2026-10-28-5-coisas` é do formato antigo (roxa, lista, entregável), já publicada: não re-renderizar nem "corrigir".
- Não publicar (YouTube, v3, Telegram) daqui — o orquestrador publica com o bloco `publicar` do roteiro.
- Git: autor `inematds <inematds@gmail.com>`, repo público `inematds/rtexjp`, branch `main`. Versão em `VERSION` (semver do Nei: minor carrega o patch).
- Falha corrigida → uma linha em `FALHAS.md`.
