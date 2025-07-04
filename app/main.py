from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
import tempfile
import os
from . import pcloud_client

app = FastAPI(title="pCloud MCP Gateway")

@app.get("/files")
def list_files(path: str = "/"):
    """List files at a given pCloud path."""
    try:
        return pcloud_client.list_files(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
def upload_file(path: str = "/", upload: UploadFile = File(...)):
    """Upload a file to pCloud."""
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(upload.file.read())
            tmp_path = tmp.name
        res = pcloud_client.upload_file(path, tmp_path)
        os.remove(tmp_path)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download")
def download_file(path: str):
    """Download a file from pCloud."""
    try:
        content = pcloud_client.download_file(path)
        return StreamingResponse(iter([content]), media_type="application/octet-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete")
def delete_file(path: str):
    """Delete a file from pCloud."""
    try:
        return pcloud_client.delete_file(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
