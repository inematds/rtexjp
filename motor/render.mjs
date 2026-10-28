// node motor/render.mjs <pasta-build-com-cena.js> <saida.mp4 | --quadros t1,t2,...> [--fps 30]
// Palco = motor/palco.html + build/cena.js. Cada quadro: window.render(t) -> screenshot -> ffmpeg (image2pipe).
// Laço de quadros no mesmo espírito do ~/projetos/r7ex/motor/render.mjs.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const aqui = path.dirname(fileURLToPath(import.meta.url));
const [, , pasta, saida, ...resto] = process.argv;
const opt = k => { const i = resto.indexOf(k); return i >= 0 ? resto[i + 1] : null; };
const fps = Number(opt('--fps') || 30);

const html = fs.readFileSync(path.join(aqui, 'palco.html'), 'utf8')
  .replaceAll('src="cena.js"', `src="file://${path.resolve(pasta, 'cena.js')}"`)
  .replaceAll('url(fontes/', `url(file://${aqui}/fontes/`)
  .replaceAll('"avatar/', `"file://${aqui}/avatar/`)
  .replaceAll('"assets/', `"file://${aqui}/assets/`);
const tmp = path.resolve(pasta, '.palco.html');
fs.writeFileSync(tmp, html);

const browser = await chromium.launch({ args: ['--allow-file-access-from-files', '--disable-web-security'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('pageerror', e => console.error('pageerror', e.message));
page.on('console', m => { if (m.type() === 'error') console.error('console', m.text()); });
await page.goto('file://' + tmp);
await page.waitForFunction(() => window.pronto === true, null, { timeout: 60000 });
const dur = Number(opt('--dur') || await page.evaluate(() => window.CENA.duracao));

if (saida === '--quadros') {
  const ts = (opt('--quadros') || resto[0]).split(',').map(Number);
  const dir = path.resolve(pasta, '..', 'quadros');
  fs.mkdirSync(dir, { recursive: true });
  for (const t of ts) {
    await page.evaluate(t => window.render(t), t);
    const f = path.join(dir, `q_${t.toFixed(2).replace('.', '_')}.jpg`);
    await page.screenshot({ path: f, type: 'jpeg', quality: 88 });
    console.log(f);
  }
  await browser.close();
  process.exit(0);
}

const n = Math.round(dur * fps);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(fps), saida], { stdio: ['pipe', 'inherit', 'inherit'] });
const t0 = Date.now();
for (let i = 0; i < n; i++) {
  await page.evaluate(t => window.render(t), i / fps);
  const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 150 === 0) console.log(`quadro ${i}/${n} (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();
console.log(`render -> ${saida} (${n} quadros, ${((Date.now() - t0) / 1000).toFixed(0)} s)`);
