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
