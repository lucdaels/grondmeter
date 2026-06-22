# /// script
# requires-python = ">=3.11"
# dependencies = ["cryptography", "requests"]
# ///
"""
Deploy grondmeter naar Firebase Hosting via REST API (geen firebase login nodig).
Gebruik: uv run deploy.py
"""

import json, time, base64, hashlib, gzip, os, sys
import requests
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

SA_KEY   = r"C:\PMO apps lokaal\reisapp\serviceAccountKey.json"
SITE_ID  = "grondmeter-koksijde"
DEPLOY_FILES = ["index.html", "firebase-config.js", "manifest.json"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_token():
    with open(SA_KEY) as f:
        sa = json.load(f)

    header  = base64.urlsafe_b64encode(json.dumps({"alg":"RS256","typ":"JWT"}).encode()).rstrip(b"=")
    now     = int(time.time())
    claims  = {
        "iss": sa["client_email"], "sub": sa["client_email"],
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now, "exp": now + 3600,
        "scope": "https://www.googleapis.com/auth/firebase https://www.googleapis.com/auth/cloud-platform"
    }
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).rstrip(b"=")
    msg     = header + b"." + payload

    key = serialization.load_pem_private_key(sa["private_key"].encode(), password=None)
    sig = base64.urlsafe_b64encode(key.sign(msg, padding.PKCS1v15(), hashes.SHA256())).rstrip(b"=")
    jwt = (msg + b"." + sig).decode()

    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt
    })
    resp.raise_for_status()
    return resp.json()["access_token"]

def sha256_gz(path):
    with open(path, "rb") as f:
        content = f.read()
    gz = gzip.compress(content, compresslevel=9)
    return hashlib.sha256(gz).hexdigest(), gz

def deploy():
    print("🔑 Token ophalen via service account...")
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    base = "https://firebasehosting.googleapis.com/v1beta1"

    print("📦 Nieuwe versie aanmaken...")
    resp = requests.post(f"{base}/sites/{SITE_ID}/versions", headers=headers, json={
        "config": {"headers": [{"glob": "**", "headers": {"Cache-Control": "no-cache"}}]}
    })
    resp.raise_for_status()
    version_name = resp.json()["name"]
    print(f"   Versie: {version_name}")

    print("🗂️  Bestanden indexeren...")
    file_hashes = {}
    file_data   = {}
    for fname in DEPLOY_FILES:
        fpath = os.path.join(SCRIPT_DIR, fname)
        if not os.path.exists(fpath):
            print(f"   ⚠️  {fname} niet gevonden, overgeslagen")
            continue
        sha, gz = sha256_gz(fpath)
        file_hashes[f"/{fname}"] = sha
        file_data[sha] = gz
        print(f"   /{fname} → {sha[:12]}...")

    resp = requests.post(f"{base}/{version_name}:populateFiles",
        headers=headers, json={"files": file_hashes})
    resp.raise_for_status()
    to_upload = resp.json().get("uploadRequiredHashes", [])
    upload_url = resp.json().get("uploadUrl", "")
    print(f"   {len(to_upload)} bestand(en) moeten geüpload worden")

    for sha in to_upload:
        gz_data = file_data.get(sha)
        if not gz_data:
            continue
        fname_display = next((k for k,v in file_hashes.items() if v == sha), sha[:12])
        print(f"⬆️  Uploaden {fname_display}...")
        up = requests.post(
            f"{upload_url}/{sha}",
            headers={**headers, "Content-Type": "application/octet-stream"},
            data=gz_data
        )
        up.raise_for_status()

    print("✅ Versie afronden...")
    resp = requests.patch(
        f"{base}/{version_name}?update_mask=status",
        headers=headers, json={"status": "FINALIZED"}
    )
    resp.raise_for_status()

    print("🚀 Release aanmaken...")
    resp = requests.post(
        f"{base}/sites/{SITE_ID}/releases?versionName={version_name}",
        headers=headers, json={}
    )
    resp.raise_for_status()

    print()
    print("✅ Deploy geslaagd!")
    print(f"   🌐 https://{SITE_ID}.web.app")

if __name__ == "__main__":
    try:
        deploy()
    except Exception as e:
        print(f"❌ Fout: {e}")
        sys.exit(1)
