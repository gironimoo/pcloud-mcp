import os
import requests
from typing import List

API_BASE = "https://api.pcloud.com"

def get_token() -> str:
    token = os.getenv("PCLOUD_TOKEN")
    if not token:
        raise RuntimeError("PCLOUD_TOKEN environment variable not set")
    return token

def list_files(path: str) -> dict:
    token = get_token()
    params = {"path": path, "access_token": token}
    resp = requests.get(f"{API_BASE}/listfolder", params=params)
    resp.raise_for_status()
    return resp.json()

def upload_file(path: str, file_path: str) -> dict:
    token = get_token()
    params = {"path": path, "access_token": token}
    files = {"file": open(file_path, "rb")}
    resp = requests.post(f"{API_BASE}/uploadfile", params=params, files=files)
    resp.raise_for_status()
    return resp.json()

def download_file(path: str) -> bytes:
    token = get_token()
    params = {"path": path, "access_token": token}
    resp = requests.get(f"{API_BASE}/getfile", params=params, stream=True)
    resp.raise_for_status()
    return resp.content

def delete_file(path: str) -> dict:
    token = get_token()
    params = {"path": path, "access_token": token}
    resp = requests.post(f"{API_BASE}/deletefile", params=params)
    resp.raise_for_status()
    return resp.json()
