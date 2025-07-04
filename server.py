import os
import json
import cgi
import http.server
import urllib.parse
import urllib.request
import uuid

TOKEN = os.environ.get('PCLOUD_TOKEN')
API_BASE = 'https://api.pcloud.com'

if not TOKEN:
    raise RuntimeError('PCLOUD_TOKEN environment variable not set')

def api_call(endpoint, params=None, method='GET', data=None, headers=None):
    """Helper to call the pCloud API."""
    params = params or {}
    params['auth'] = TOKEN
    url = f"{API_BASE}/{endpoint}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read()
            return resp.getcode(), body
    except urllib.error.HTTPError as e:
        return e.code, e.read()

def list_files():
    code, body = api_call('listfolder', {'folderid': 0})
    return code, json.loads(body)

def delete_file(file_id):
    code, body = api_call('deletefile', {'fileid': file_id})
    return code, json.loads(body)

def get_file_link(file_id):
    code, body = api_call('getfilelink', {'fileid': file_id})
    if code == 200:
        info = json.loads(body)
        return 200, info.get('hosts')[0] + info.get('path')
    return code, None

def upload_file(file_data, filename, folder_id=0):
    boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
    parts = []
    parts.append(f'--{boundary}\r\n'.encode())
    parts.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode())
    parts.append(b'Content-Type: application/octet-stream\r\n\r\n')
    parts.append(file_data)
    parts.append(f'\r\n--{boundary}--\r\n'.encode())
    body = b''.join(parts)
    headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}
    endpoint = f'uploadfile'
    params = {'folderid': folder_id, 'filename': filename}
    code, resp_body = api_call(endpoint, params=params, method='POST', data=body, headers=headers)
    return code, json.loads(resp_body)

class Handler(http.server.BaseHTTPRequestHandler):
    def _json_response(self, code, payload):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/files':
            code, info = list_files()
            self._json_response(code, info)
        elif parsed.path == '/download':
            query = urllib.parse.parse_qs(parsed.query)
            file_id = query.get('fileid', [None])[0]
            if not file_id:
                self._json_response(400, {'error': 'fileid required'})
                return
            code, link = get_file_link(file_id)
            if code != 200 or not link:
                self._json_response(code, {'error': 'unable to get file'})
                return
            try:
                with urllib.request.urlopen(link) as resp:
                    data = resp.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.end_headers()
                    self.wfile.write(data)
            except Exception as e:
                self._json_response(502, {'error': str(e)})
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != '/upload':
            self.send_error(404)
            return
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={
            'REQUEST_METHOD': 'POST'
        })
        if 'file' not in form:
            self._json_response(400, {'error': 'file field required'})
            return
        file_item = form['file']
        file_data = file_item.file.read()
        filename = file_item.filename
        code, info = upload_file(file_data, filename)
        self._json_response(code, info)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != '/delete':
            self.send_error(404)
            return
        query = urllib.parse.parse_qs(parsed.query)
        file_id = query.get('fileid', [None])[0]
        if not file_id:
            self._json_response(400, {'error': 'fileid required'})
            return
        code, info = delete_file(file_id)
        self._json_response(code, info)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    server = http.server.HTTPServer(('', port), Handler)
    print(f'Serving on port {port}')
    server.serve_forever()
