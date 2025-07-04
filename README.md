# pCloud MCP Gateway

This project provides a lightweight REST server acting as a Model Context Protocol (MCP) gateway for [pCloud](https://www.pcloud.com/). It allows listing, uploading, downloading and deleting files from a pCloud account using only an **access token**.

## Requirements

- Node.js 20+
- A valid `PCLOUD_TOKEN` from pCloud

## Configuration

Set the environment variable `PCLOUD_TOKEN` with your pCloud access token. Optionally, set `PORT` to change the listening port (default is `3000`).

```
export PCLOUD_TOKEN=your_token_here
node server.js
```

## Endpoints

### `GET /files`
List files in the root folder of your pCloud storage.

### `POST /files`
Upload a file. The request body must be JSON:

```json
{
  "path": "/folder/name.txt",
  "content": "base64-encoded content"
}
```

### `GET /download?path=/folder/name.txt`
Download a file. Returns the raw file bytes.

### `DELETE /files?path=/folder/name.txt`
Delete a file from pCloud.

Each operation uses the `PCLOUD_TOKEN` for authentication when calling the pCloud API.

## Example

```
# List files
curl http://localhost:3000/files

# Upload a text file
curl -X POST http://localhost:3000/files \
  -H "Content-Type: application/json" \
  -d '{"path":"/hello.txt","content":"SGVsbG8gd29ybGQh"}'

# Download a file
curl "http://localhost:3000/download?path=/hello.txt" -o hello.txt

# Delete a file
curl -X DELETE "http://localhost:3000/files?path=/hello.txt"
```

## Notes on Security

The server expects the access token through an environment variable and never stores it on disk. Ensure the token is kept secret and the server runs in a trusted environment.
