"""Contratos de troca de motor e do portão visual, sem rede/publicação."""
import copy, json, os, subprocess, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import yaml
import ia_motor as ia
import producao as p

class Teste(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
  self.out=Path(self.tmp.name); self.cfg=copy.deepcopy(ia.carregar())
  self.file=self.out/'ia.yaml'; self.save()
  self.env=patch.dict(os.environ,INEMA_IA_CONFIG=str(self.file)); self.env.start(); self.addCleanup(self.env.stop)
 def save(self): self.file.write_text(yaml.safe_dump(self.cfg))
 def test_modelo_esforco_imagem_e_sem_chaves(self):
  pic=self.out/'quadro.jpg'; pic.write_bytes(b'jpg')
  with patch.dict(os.environ,ANTHROPIC_API_KEY='segredo',OPENAI_API_KEY='segredo'):
   def run(cmd,**kw):
    self.assertIn('-i',cmd); self.assertIn(str(pic),cmd); self.assertIn('gpt-6.1-sol',cmd)
    self.assertIn('model_reasoning_effort="medium"',cmd); self.assertNotIn('OPENAI_API_KEY',kw['env'])
    self.assertNotIn('ANTHROPIC_API_KEY',kw['env']); self.assertIn('read-only',cmd)
    Path(cmd[cmd.index('-o')+1]).write_text('{"ok":true}')
    return subprocess.CompletedProcess(cmd,0,'','')
   with patch.object(ia.subprocess,'run',side_effect=run): self.assertEqual(json.loads(ia.executar('revisao_visual','confira',self.out,imagens=[pic])),{'ok':True})
 def test_api_bloqueada_antes_de_chave_ou_rede(self):
  self.cfg['etapas']['revisao_visual'].update(tipo='api',motor='anthropic',modelo='claude-opus-5-5'); self.save()
  with patch.object(ia,'ler_chave') as key, patch.object(ia.urllib.request,'urlopen') as net:
   with self.assertRaisesRegex(ValueError,'API desativada'): ia.executar('revisao_visual','x',self.out)
   key.assert_not_called(); net.assert_not_called()
 def test_comentarios_preservados(self):
  original=ia.CONFIG.read_text(); new=ia.alterar_com_comentarios(original,'revisao_visual',{'motor':'claude','modelo':'claude-opus-5-5','esforco':'high'})
  self.assertEqual([x for x in original.splitlines() if x.lstrip().startswith('#')],[x for x in new.splitlines() if x.lstrip().startswith('#')])
  self.assertEqual(yaml.safe_load(new)['etapas']['revisao_visual']['esforco'],'high')
 def test_claude_assinatura_modelo_e_esforco(self):
  c=dict(self.cfg['etapas']['revisao_visual'],motor='claude',modelo='claude-opus-5-5',esforco='high')
  cmd=ia.comando(c); self.assertEqual(cmd[cmd.index('--model')+1],c['modelo']); self.assertEqual(cmd[cmd.index('--effort')+1],'high')
 def test_sem_folha_nao_chama_modelo(self):
  with patch.object(p,'executar') as run:
   self.assertEqual(p.revisar(self.out)['veredito'],'erro'); run.assert_not_called()
 def test_resposta_invalida_nao_aprova(self):
  for f in ['build/folha.jpg','contact.jpg','ficha.yaml','roteiro.json']:
   q=self.out/f; q.parent.mkdir(parents=True,exist_ok=True); q.write_text('{}')
  with patch.object(p,'executar',return_value='{"veredito":"talvez"}'):
   self.assertEqual(p.revisar(self.out)['veredito'],'erro')
if __name__=='__main__': unittest.main()
