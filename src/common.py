"""Utilidades compartidas: rutas, configuracion, cliente HTTP con limite de tasa y reintentos."""
from __future__ import annotations

import json
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
if sys.platform == "win32" and not str(ROOT).startswith("\\\\?\\"):
    # rutas > 260 caracteres (el espacio de trabajo vive en una ruta virtualizada muy larga)
    ROOT = Path("\\\\?\\" + str(ROOT))
CONFIG = ROOT / "config"
DATA = ROOT / "data"
CACHE = DATA / "cache"
FIGS = ROOT / "figures"
LOGS = ROOT / "logs"

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"


def load_yaml(name: str) -> dict:
    with open(CONFIG / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_event(kind: str, **fields) -> None:
    """Registro append-only (JSON lines) de consultas y descargas, con fecha."""
    LOGS.mkdir(exist_ok=True)
    rec = {"ts": now_iso(), "kind": kind, **fields}
    with open(LOGS / "queries.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


class Client:
    """requests con User-Agent identificable, <= N solicitudes/s y espera exponencial ante 429/5xx."""

    def __init__(self, user_agent: str, max_rps: float = 3.0, max_retries: int = 6):
        self.s = requests.Session()
        self.s.headers["User-Agent"] = user_agent
        self.min_gap = 1.0 / max_rps
        self._last = 0.0
        self.max_retries = max_retries
        self._lock = threading.Lock()

    def _throttle(self) -> None:
        with self._lock:                      # tasa global compartida entre hilos
            wait = self.min_gap - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()

    def get(self, url: str, **kw) -> requests.Response:
        delay = 2.0
        timeout = kw.pop("timeout", 60)
        for attempt in range(self.max_retries):
            self._throttle()
            try:
                r = self.s.get(url, timeout=timeout, **kw)
            except requests.RequestException as exc:  # red caida / timeout
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(delay)
                delay *= 2
                continue
            if r.status_code in (429, 500, 502, 503, 504):
                if attempt == self.max_retries - 1:
                    r.raise_for_status()
                retry_after = r.headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after and retry_after.isdigit() else delay)
                delay *= 2
                continue
            return r
        raise RuntimeError("unreachable")


def make_client() -> Client:
    cfg = load_yaml("families.yaml")["search"]
    return Client(cfg["user_agent"], cfg["max_requests_per_second"])
