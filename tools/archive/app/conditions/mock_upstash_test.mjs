import http from 'node:http';
const hashes = new Map();
const seen = [];
const server = http.createServer((req, res) => {
  let body = '';
  req.on('data', (c) => (body += c));
  req.on('end', () => {
    if (req.headers.authorization !== 'Bearer test-token') { res.writeHead(401); return res.end('{"error":"unauthorized"}'); }
    const [cmd, key, ...args] = JSON.parse(body);
    seen.push(cmd + ' ' + key);
    const h = hashes.get(key) ?? new Map(); hashes.set(key, h);
    let result = null;
    if (cmd === 'HGETALL') result = [...h].flat();
    else if (cmd === 'HSET') { h.set(args[0], args[1]); result = 1; }
    else if (cmd === 'HDEL') { args.forEach((f) => h.delete(f)); result = args.length; }
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ result }));
  });
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
process.env.KV_REST_API_URL = `http://127.0.0.1:${server.address().port}`;
process.env.KV_REST_API_TOKEN = 'test-token';
const m = await import(process.argv[2]);
const post = (resort, body) => m.POST(new Request(`https://x/api/conditions?resort=${resort}`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) }));
let r = await post('okemo', { trailId: 'sunset-strip', deviceId: 'device-aaaa-1111', vote: 1, tags: ['groomed', 'powder'] });
console.log('POST okemo vote ->', r.status, await r.text());
r = await post('okemo', { trailId: 'sunset-strip', deviceId: 'device-bbbb-2222', vote: -1, tags: ['icy'] });
console.log('POST okemo 2nd device ->', r.status, await r.text());
r = await m.GET(new Request('https://x/api/conditions?resort=okemo'));
console.log('GET okemo ->', r.status, await r.text());
r = await m.GET(new Request('https://x/api/conditions'));
console.log('GET killington (default) ->', r.status, await r.text());
r = await post('okemo', { trailId: 'sunset-strip', deviceId: 'device-aaaa-1111', vote: 0, tags: [] });
console.log('POST okemo take back ->', r.status, await r.text());
console.log('redis hashes used:', [...hashes.keys()].join(', '), '| commands:', seen.join('; '));
server.close();
