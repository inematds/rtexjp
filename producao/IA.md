# Modelo do revisor automático

O cron usa `producao/ia.yaml`, uma configuração exclusiva deste projeto. Edite os quatro campos da etapa `revisao_visual`: tipo, motor, modelo e esforco. As cinco combinações estão comentadas com `#` no próprio arquivo. Texto/visão aceitam assinatura Claude/Codex ou APIs Anthropic/OpenAI/OpenRouter. APIs estão desativadas e exigem autorização específica para este sistema.

```bash
python3 producao/ia_motor.py ver
python3 producao/ia_motor.py validar
python3 producao/ia_motor.py configurar revisao_visual --tipo assinatura --motor claude --modelo claude-opus-5-5 --esforco medium
python3 producao/ia_motor.py configurar revisao_visual --tipo assinatura --motor codex --modelo gpt-6.1-sol --esforco medium
```

Alterar a configuração preserva os comentários. O cron lê o arquivo a cada revisão; não precisa reiniciar o timer. Modelo e esforço são passados explicitamente ao CLI. Chaves herdadas de APIs são removidas na assinatura. Não existe fallback automático pago.

O executor anexa roteiro, medições disponíveis e os bytes da folha de quadros (Codex usa `-i`; APIs recebem imagem). Falta de imagem, JSON inválido ou falha do motor retorna erro e mantém o tratamento de tentativas/parada do produtor. O parecer continua sujeito às mesmas regras: defeito reprova; melhoria vira sugestão. Registro local em `ia-execucoes.jsonl` na edição, sem conteúdo de credenciais. A revisão não publica nem altera a edição.

Imagens geradas continuam na assinatura Codex; este arquivo troca o revisor, não o gerador.

Validação em 15/11/2026: seis contratos locais e teste existente da produção passaram; revisão real pela assinatura Codex devolveu parecer aprovado em folha de edição existente, sem publicar. Evidência local em `~/projetos/output/crons-multiprovedor-2026-11-15/rtexjp/resultado.json`.


## Trava de cota (17/11/2026)

Na primeira recusa ESTRUTURADA de cota do Claude Code (JSON `is_error` + `api_error: usage_limit_reached` ou 429), o executor grava o horário de volta em `~/.local/state/enginebridge/state.sqlite` (tabela `pools` do EngineBridge; `INEMA_COTA_DB` muda o caminho). Até lá a etapa falha na hora, sem abrir o programa; o revisor devolve `espera` (não conta como erro, uma linha de log por bloqueio). Codex ainda não trava sozinho (sem recusa real registrada). `python3 producao/ia_motor.py cota ver` mostra as travas; `cota liberar --motor claude` tira antes do horário. Reserva (`alternativa`) só entre assinaturas, texto/visão, com o principal recusando por cota. `claude -p` automático roda com `--no-session-persistence`. Mesmo executor do r7ex v1.7.6.
