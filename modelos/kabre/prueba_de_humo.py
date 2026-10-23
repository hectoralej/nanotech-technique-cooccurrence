"""Prueba de humo para Kabre: que hay en el nodo donde se ejecuta. Solo biblioteca estandar (+ torch si existe).

Uso (en el nodo, por ejemplo desde una terminal de Jupyter de OnDemand en la cola nukwa-debug):
    python prueba_de_humo.py
Escribe `humo_<nodo>.json` junto al script. Pegar ese JSON (sin contrasenas, no contiene ninguna) a Claude.
"""
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import urllib.request


def run(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as exc:  # noqa: BLE001
        return f"no disponible: {exc}"


def internet(url: str) -> str:
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "nano2predict-humo"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return f"ok {r.status}"
    except Exception as exc:  # noqa: BLE001
        return f"sin acceso: {str(exc)[:80]}"


def main() -> None:
    home = os.path.expanduser("~")
    total, usado, libre = shutil.disk_usage(home)
    info = {
        "nodo": socket.gethostname(),
        "python": sys.version.split()[0],
        "sistema": platform.platform(),
        "cpus": os.cpu_count(),
        "memoria_MB": next((int(l.split()[1]) // 1024 for l in open("/proc/meminfo") if l.startswith("MemTotal")), None) if os.path.exists("/proc/meminfo") else None,
        "disco_home_GB": {"total": round(total / 1e9, 1), "libre": round(libre / 1e9, 1)},
        "slurm_job": os.environ.get("SLURM_JOB_ID"),
        "slurm_particion": os.environ.get("SLURM_JOB_PARTITION"),
        "gpu_nvidia_smi": run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"]),
        "internet": {u: internet(u) for u in ("https://pypi.org", "https://github.com", "https://download.pytorch.org")},
        "modulos_ml": {},
    }
    for mod in ("numpy", "pandas", "sklearn", "torch", "torchvision", "timm", "PIL", "matplotlib"):
        try:
            m = __import__(mod)
            info["modulos_ml"][mod] = getattr(m, "__version__", "ok")
        except Exception:  # noqa: BLE001
            info["modulos_ml"][mod] = "no instalado"
    try:
        import torch  # noqa: PLC0415

        info["torch_cuda"] = bool(torch.cuda.is_available())
        if torch.cuda.is_available():
            p = torch.cuda.get_device_properties(0)
            info["torch_gpu"] = {"nombre": p.name, "memoria_GB": round(p.total_memory / 1e9, 1)}
    except Exception:  # noqa: BLE001
        pass
    salida = f"humo_{info['nodo']}.json"
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(json.dumps(info, ensure_ascii=False, indent=2))
    print("\nEscrito:", os.path.abspath(salida))


if __name__ == "__main__":
    main()
