# pCloud MCP Gateway

This project provides a simple REST API to interact with [pCloud](https://www.pcloud.com/) using only an access token. It exposes endpoints to list, upload, download and delete files through a minimal server acting as a My Cloud Provider (MCP).

## Architecture

- **FastAPI** web framework (Python)
- **Requests** library for HTTP calls to pCloud
- Access token provided via the `PCLOUD_TOKEN` environment variable
- No persistent storage of credentials

## Installation

1. Clone ce dépôt puis créez éventuellement un environnement virtuel :
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Exportez votre jeton d'accès pCloud :
   ```bash
   export PCLOUD_TOKEN="<votre_token>"
   ```
4. Lancez le serveur :
   ```bash
   uvicorn app.main:app --reload
   ```

## Endpoints

### `GET /files`
List files in a pCloud path.
- **Query:** `path` (default: `/`)
- **Response:** JSON listing from pCloud

### `POST /upload`
Upload a file.
- **Query:** `path` target folder (default: `/`)
- **Body:** multipart form field `upload` with file content
- **Response:** JSON from pCloud

### `GET /download`
Download a file.
- **Query:** `path` file path
- **Response:** file stream

### `DELETE /delete`
Delete a file.
- **Query:** `path` file path
- **Response:** JSON from pCloud

## Example API Call

```bash
curl -X GET "http://localhost:8000/files?path=/" -H "accept: application/json"
```

## Notes

Ensure the `PCLOUD_TOKEN` variable is kept secure (for example, load it from a safe store or environment configuration tool). The server does not persist the token on disk.
