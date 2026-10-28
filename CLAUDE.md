# rtexjp — instruções do projeto

- Motor de reels 9:16 no **padrão rtexjp** (reel ilustrado roxo). Fluxo e comandos: `README.md` → "O processo, do início ao fim".
- **Exceção deliberada ao kit INEMA** (registrada em `~/projetos/inema-design/DECISOES.md`): paleta roxa/lilás, avatar ilustrado do Nei sem lip-sync e mascote robô. Não "corrigir" para amarelo/preto. O resto do kit vale (voz do Nei 0,6/0,6, `atempo` ≤ 1,15, ano por extenso, sem SFX no meio, zonas seguras, fonte escrita na tela).
- **Nunca citar referência externa do formato**: nenhum nome de criador/perfil/marca de terceiros que inspirou o formato, nenhuma URL de rede social de referência. Antes de todo commit: `python3 medir.py --grep` → `grep_fonte 0` (o padrão fica montado em partes dentro do `medir.py`, para não casar consigo mesmo).
- Tudo local e grátis: voz inemavox chatterbox (voz `nei`), Whisper local, imagens flux2-klein local (`http://localhost:8000`). Nenhuma API sem autorização explícita do Nei.
- Não publicar (YouTube, v3, Telegram) daqui — o orquestrador publica. Antes de publicar, o entregável prometido no CTA tem que existir no inema.club.
- Git: autor `inematds <inematds@gmail.com>`, repo público `inematds/rtexjp`, branch `main`. Versão em `VERSION` (semver do Nei: minor carrega o patch).
- Falha corrigida → uma linha em `FALHAS.md`.
