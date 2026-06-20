"""Encrypted database backups (admin-only).

``pg_dump`` -> AES-256-GCM (crypto_utils) -> timestamped file in BACKUP_DIR.
Restore is guarded: only runs when ALLOW_DB_RESTORE=true AND the caller passes a
matching confirm token, so it can never wipe the dev DB by accident.

Routes
------
POST /api/v1/admin/backup     Super Admin  -> create encrypted backup
GET  /api/v1/admin/backups    Super Admin  -> list backups
POST /api/v1/admin/restore    Super Admin  -> decrypt + restore (guarded)
"""
import asyncio
import hashlib
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

import crypto_utils
from .deps import TokenData, require_roles

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/admin", tags=["backup"])

BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "/app/backups"))
# The live edu_demo_new DB lives in the host's PostgreSQL (the Odoo server runs on
# the Windows host), reachable from the container via host.docker.internal.
PG_HOST = os.getenv("BACKUP_PG_HOST", "host.docker.internal")
PG_PORT = os.getenv("BACKUP_PG_PORT", "5432")
PG_USER = os.getenv("BACKUP_PG_USER", "odoo")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "Admin123")
PG_DB = os.getenv("ODOO_DB", "edu_demo_new")
ALLOW_DB_RESTORE = os.getenv("ALLOW_DB_RESTORE", "false").lower() in ("1", "true", "yes")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


async def _run(cmd: list, env: dict, stdin: bytes = None):
    proc = await asyncio.create_subprocess_exec(
        *cmd, env=env,
        stdin=asyncio.subprocess.PIPE if stdin is not None else None,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate(input=stdin)
    return proc.returncode, out, err


class RestoreBody(BaseModel):
    filename: str
    confirm_token: str


@router.post("/backup", summary="Create an AES-256-GCM encrypted pg_dump")
async def create_backup(token: TokenData = Depends(require_roles("super_admin"))):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"backup_{PG_DB}_{ts}.dump.enc"
    target = BACKUP_DIR / filename

    env = dict(os.environ, PGPASSWORD=PG_PASSWORD)
    cmd = ["pg_dump", "-h", PG_HOST, "-p", str(PG_PORT), "-U", PG_USER,
           "-d", PG_DB, "-F", "c", "--no-owner"]
    rc, dump, err = await _run(cmd, env)
    if rc != 0:
        logger.error("pg_dump failed: %s", err.decode("utf-8", "replace")[:500])
        raise HTTPException(status_code=502, detail="pg_dump failed")

    try:
        blob = crypto_utils.backup_encrypt(dump)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    target.write_bytes(blob)

    meta = {
        "filename": filename,
        "size": target.stat().st_size,
        "sha256": _sha256_file(target),
        "timestamp": ts,
    }
    try:
        from routers import audit as audit_router
        await audit_router.record_audit_event(
            "backup_created", "info", user_id=token.user_id, actor_login=token.username,
            detail=f"{filename} ({meta['size']} bytes)")
    except Exception:
        pass
    return meta


@router.get("/backups", summary="List encrypted backups")
async def list_backups(token: TokenData = Depends(require_roles("super_admin"))):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for p in sorted(BACKUP_DIR.glob("*.dump.enc"), reverse=True):
        st = p.stat()
        items.append({
            "filename": p.name,
            "size": st.st_size,
            "sha256": _sha256_file(p),
            "timestamp": datetime.fromtimestamp(st.st_mtime, timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        })
    return {"backups": items, "restore_enabled": ALLOW_DB_RESTORE}


@router.post("/restore", summary="Decrypt + restore a backup (guarded)")
async def restore_backup(body: RestoreBody,
                         token: TokenData = Depends(require_roles("super_admin"))):
    if not ALLOW_DB_RESTORE:
        raise HTTPException(status_code=400,
                            detail="Restore is disabled. Set ALLOW_DB_RESTORE=true to enable.")
    if body.confirm_token != f"RESTORE-{body.filename}":
        raise HTTPException(status_code=400, detail="Invalid confirm token")

    path = (BACKUP_DIR / body.filename).resolve()
    if path.parent != BACKUP_DIR.resolve() or not path.exists():
        raise HTTPException(status_code=404, detail="Backup not found")

    try:
        plain = crypto_utils.backup_decrypt(path.read_bytes())
    except Exception:
        raise HTTPException(status_code=400, detail="Decryption failed (bad key or corrupt file)")

    env = dict(os.environ, PGPASSWORD=PG_PASSWORD)
    cmd = ["pg_restore", "-h", PG_HOST, "-p", str(PG_PORT), "-U", PG_USER,
           "-d", PG_DB, "--clean", "--if-exists", "--no-owner"]
    rc, out, err = await _run(cmd, env, stdin=plain)
    if rc != 0:
        logger.error("pg_restore failed: %s", err.decode("utf-8", "replace")[:500])
        raise HTTPException(status_code=502, detail="pg_restore failed")

    try:
        from routers import audit as audit_router
        await audit_router.record_audit_event(
            "backup_restored", "critical", user_id=token.user_id,
            actor_login=token.username, detail=f"restored {body.filename}")
    except Exception:
        pass
    return {"success": True, "restored": body.filename}
