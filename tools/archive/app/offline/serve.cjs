// Static server for dist/ that behaves like Vercel for static files
// (cache-control: public, max-age=0, must-revalidate + ETag/304) and logs every request.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const zlib = require('node:zlib');
const root = process.argv[2];
// one shared link for every request (the page's and the service worker's):
// THROTTLE_MBPS of bandwidth, RTT_MS before each response starts
const MBPS = Number(process.env.THROTTLE_MBPS || 0);
const RTT = Number(process.env.RTT_MS || 0);
let linkFree = 0;
function send(res, buf) {
  if (!MBPS) return res.end(buf);
  const perMs = (MBPS * 1e6) / 8 / 1000;
  let off = 0;
  const step = () => {
    if (off >= buf.length) return res.end();
    const chunk = buf.subarray(off, off + 16384);
    off += chunk.length;
    const now = Date.now();
    linkFree = Math.max(now, linkFree) + chunk.length / perMs;
    setTimeout(() => { res.write(chunk); step(); }, linkFree - now);
  };
  setTimeout(step, RTT);
}
const port = Number(process.argv[3] || 4300);
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.jpg': 'image/jpeg', '.png': 'image/png', '.webmanifest': 'application/manifest+json', '.json': 'application/json' };
http.createServer((req, res) => {
  const u = new URL(req.url, 'http://x');
  if (u.pathname.startsWith('/api/')) { res.writeHead(503, { 'content-type': 'application/json' }); res.end('{}'); console.log(`${req.method} ${u.pathname} 503 0`); return; }
  let file = path.join(root, decodeURIComponent(u.pathname));
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) file = path.join(root, 'index.html');
  const body = fs.readFileSync(file);
  const etag = '"' + crypto.createHash('sha1').update(body).digest('hex') + '"';
  const headers = { vary: 'Origin', 'content-type': types[path.extname(file)] || 'application/octet-stream', etag, 'cache-control': 'public, max-age=0, must-revalidate' };
  if (req.headers['if-none-match'] === etag) { res.writeHead(304, headers); res.end(); console.log(`${req.method} ${u.pathname} 304 0`); return; }
  // compress text like Vercel does (it serves brotli; gzip is close enough)
  if (/^(text|application\/(json|manifest))/.test(headers['content-type']) && /gzip/.test(req.headers['accept-encoding'] ?? '')) {
    const gz = zlib.gzipSync(body);
    res.writeHead(200, { ...headers, 'content-encoding': 'gzip' }); send(res, gz); console.log(`${req.method} ${u.pathname} 200 ${gz.length}`);
    return;
  }
  res.writeHead(200, headers); send(res, body); console.log(`${req.method} ${u.pathname} 200 ${body.length}`);
}).listen(port, () => console.log(`listening ${port}`));
