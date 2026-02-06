# app/services/policy.py
"""Policy document management — upload, list, delete."""

import hashlib
import os
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Policy

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "policies")


def _ensure_upload_dir():
    """Create the upload directory if it doesn't exist."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_all_policies(db: Session) -> list[Policy]:
    """Return all policies ordered by upload date descending."""
    return db.query(Policy).order_by(Policy.uploaded_at.desc()).all()


def get_policy_by_id(db: Session, policy_id: int) -> Optional[Policy]:
    """Fetch a single policy by ID."""
    return db.query(Policy).filter(Policy.id == policy_id).first()


def save_policy(db: Session, title: str, filename: str, file_content: bytes) -> Policy:
    """
    Save a policy PDF to disk and create a database record.
    """
    _ensure_upload_dir()

    # Content hash for deduplication
    content_hash = hashlib.sha256(file_content).hexdigest()

    # Save file to disk
    safe_filename = filename.replace(" ", "_")
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Avoid overwriting: append hash fragment if file exists
    if os.path.exists(file_path):
        name, ext = os.path.splitext(safe_filename)
        safe_filename = f"{name}_{content_hash[:8]}{ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as f:
        f.write(file_content)

    policy = Policy(
        title=title,
        filename=safe_filename,
        file_path=file_path,
        content_hash=content_hash,
        file_size=len(file_content),
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def delete_policy(db: Session, policy_id: int) -> bool:
    """Delete a policy record and its file from disk."""
    policy = get_policy_by_id(db, policy_id)
    if not policy:
        return False

    # Remove file from disk
    if os.path.exists(policy.file_path):
        os.remove(policy.file_path)

    db.delete(policy)
    db.commit()
    return True
