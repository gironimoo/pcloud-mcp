# pCloud MCP Gateway

This project provides a minimal HTTP server acting as a "My Cloud Provider" (MCP)
proxy for [pCloud](https://www.pcloud.com/) using a single access token.

## Requirements

- Python 3.10 or newer (comes with the standard library only).
- A pCloud access token to authorize API calls.

## Configuration

The server expects the environment variable `PCLOUD_TOKEN` to contain your
pCloud access token. No API keys are required.

```
export PCLOUD_TOKEN="<your-token>"
python3 server.py
```

## API Usage

### List files

```
GET /files
```

Returns the contents of the root folder.

### Upload a file

```
POST /upload
Content-Type: multipart/form-data; boundary=...
Form field: file
```

### Download a file

```
GET /download?fileid=<ID>
```

### Delete a file

```
DELETE /delete?fileid=<ID>
```

All endpoints return JSON on success or an error status with a message.

## Example with `curl`

```
# Upload
curl -F "file=@local.txt" http://localhost:8000/upload

# List files
curl http://localhost:8000/files

# Download
curl -o out.txt "http://localhost:8000/download?fileid=12345"

# Delete
curl -X DELETE "http://localhost:8000/delete?fileid=12345"
```

The server does not persist the token; it is read from the environment at
startup to keep it out of source control.
