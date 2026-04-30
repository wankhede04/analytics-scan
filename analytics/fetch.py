"""Fetch raw inputs from the career-scan repo."""
from __future__ import annotations

import logging
import os
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

CAREER_SCAN_RAW = "https://raw.githubusercontent.com/wankhede04/career-scan/main"
CACHE_DIR = Path("_cache")


def _download(url: str, dest: Path, token: str | None = None) -> Path:
    headers = {"User-Agent": "analytics-scan/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    logger.info("downloading %s", url)
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(resp.content)
    return dest


def fetch_inputs(cache_dir: Path = CACHE_DIR) -> dict[str, Path]:
    """Download remote_jobs.xlsx and applications/_state.json. Returns paths."""
    token = os.environ.get("GITHUB_TOKEN")
    paths = {
        "excel": _download(f"{CAREER_SCAN_RAW}/remote_jobs.xlsx", cache_dir / "remote_jobs.xlsx", token),
        "state": _download(
            f"{CAREER_SCAN_RAW}/applications/_state.json",
            cache_dir / "_state.json",
            token,
        ),
    }
    return paths
