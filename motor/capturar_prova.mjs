// Print real da fonte para a prova (navegador sem janela, tema escuro, 2x).
// node motor/capturar_prova.mjs <url> <saida.png> [--clip x,y,w,h] [--largura 1280]
//   sem --clip: a primeira tela da página (1280x900 px CSS); com --clip: só esse retângulo (px CSS), ex. o nome do repo + o contador.
// Guarde em edicoes/<id>/prova/ e cite no campo "print" da batida; confira o número no print e atualize fontes[] com a data.
import { chromium } from 'playwright';

const [, , url, saida, ...resto] = process.argv;
if (!url || !saida) { console.error('uso: node motor/capturar_prova.mjs <url> <saida.png> [--clip x,y,w,h] [--largura 1280]'); process.exit(1); }
const opt = k => { const i = resto.indexOf(k); return i >= 0 ? resto[i + 1] : null; };
const largura = Number(opt('--largura') || 1280);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: largura, height: 900 }, deviceScaleFactor: 2, colorScheme: 'dark', locale: 'en-US' });
await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
await p.waitForTimeout(3000);
const c = opt('--clip');
const clip = c ? (([x, y, width, height]) => ({ x, y, width, height }))(c.split(',').map(Number)) : undefined;
await p.screenshot({ path: saida, clip });
await b.close();
console.log('OK', saida);
