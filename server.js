const http = require('http');
const { URL } = require('url');

const PCLOUD_TOKEN = process.env.PCLOUD_TOKEN;
if (!PCLOUD_TOKEN) {
  console.error('Missing PCLOUD_TOKEN environment variable');
  process.exit(1);
}

const API_BASE = 'https://api.pcloud.com';

async function pcloudRequest(endpoint, options = {}) {
  const url = endpoint.includes('http') ? endpoint : `${API_BASE}${endpoint}`;
  const res = await fetch(url, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status} - ${text}`);
  }
  return res;
}

async function listFiles() {
  const res = await pcloudRequest(`/listfolder?path=%2F&access_token=${PCLOUD_TOKEN}`);
  return res.json();
}

async function uploadFile(path, buffer) {
  const form = new FormData();
  const blob = new Blob([buffer]);
  const filename = path.split('/').pop();
  form.append('file', blob, filename);
  const url = `/uploadfile?path=${encodeURIComponent(path)}&access_token=${PCLOUD_TOKEN}`;
  const res = await pcloudRequest(url, { method: 'POST', body: form });
  return res.json();
}

async function getDownloadLink(path) {
  const res = await pcloudRequest(`/getfilelink?path=${encodeURIComponent(path)}&access_token=${PCLOUD_TOKEN}`);
  const data = await res.json();
  if (data.result !== 0) throw new Error(data.error);
  const host = data.hosts[0];
  return `https://${host}${data.path}`;
}

async function downloadFile(path) {
  const link = await getDownloadLink(path);
  const res = await pcloudRequest(link);
  const arrayBuffer = await res.arrayBuffer();
  return Buffer.from(arrayBuffer);
}

async function deleteFile(path) {
  const res = await pcloudRequest(`/deletefile?path=${encodeURIComponent(path)}&access_token=${PCLOUD_TOKEN}`);
  return res.json();
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  // enable CORS for convenience
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  try {
    if (req.method === 'GET' && url.pathname === '/files') {
      const data = await listFiles();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(data));
    } else if (req.method === 'POST' && url.pathname === '/files') {
      let body = '';
      req.on('data', chunk => body += chunk);
      req.on('end', async () => {
        try {
          const { path, content } = JSON.parse(body);
          if (!path || !content) {
            res.writeHead(400);
            res.end('Missing path or content');
            return;
          }
          const buffer = Buffer.from(content, 'base64');
          const data = await uploadFile(path, buffer);
          res.writeHead(201, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify(data));
        } catch (err) {
          res.writeHead(500);
          res.end(err.toString());
        }
      });
    } else if (req.method === 'GET' && url.pathname === '/download') {
      const path = url.searchParams.get('path');
      if (!path) {
        res.writeHead(400);
        res.end('Missing path');
        return;
      }
      const fileBuffer = await downloadFile(path);
      res.writeHead(200, { 'Content-Type': 'application/octet-stream' });
      res.end(fileBuffer);
    } else if (req.method === 'DELETE' && url.pathname === '/files') {
      const path = url.searchParams.get('path');
      if (!path) {
        res.writeHead(400);
        res.end('Missing path');
        return;
      }
      const data = await deleteFile(path);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(data));
    } else {
      res.writeHead(404);
      res.end('Not Found');
    }
  } catch (err) {
    res.writeHead(500);
    res.end(err.toString());
  }
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

