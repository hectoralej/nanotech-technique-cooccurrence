"""Descarga las figuras de ext_paneles.csv a producto/imagenes/<pmcid>/<image_file>.

Metodo: por cada pmcid se baja el zip de Europe PMC (supplementaryFiles), se extraen solo las figuras pedidas y se borra el zip.
Reanudable. Cada peticion tarda ~10 s, asi que se usan pocos hilos (por defecto 4; cada uno espera entre peticiones). Uso:
    python modelos/descargar_imagenes.py            # todo
    python modelos/descargar_imagenes.py 40         # prueba con los primeros 40 articulos
    python modelos/descargar_imagenes.py 0 6        # todo, con 6 hilos
"""
import csv
import sys
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[1]
PANELES = RAIZ / "curation" / "ext_paneles.csv"
SALIDA = RAIZ / "producto" / "imagenes"
LOG = SALIDA / "descargas.csv"
UA = {"User-Agent": "nano2predict-hackathon (mailto:hector.rojas.valdez@est.una.ac.cr)"}
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pm}/supplementaryFiles"
EXT_OK = {".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff"}
lock = threading.Lock()
cont = {"ok": 0, "fallo": 0, "hechos": 0}


def bajar(pm: str, pedidas: set[str], w, lf, total: int) -> None:
    faltan = [n for n in sorted(pedidas) if not (SALIDA / pm / n).exists()]
    if not faltan:
        return
    zpath = SALIDA / f"_{pm}.zip"
    filas = []
    try:
        ses = requests.Session()
        ses.headers.update(UA)
        for intento in range(3):
            r = ses.get(URL.format(pm=pm), timeout=120)
            if r.status_code == 200:
                zpath.write_bytes(r.content)
                break
            time.sleep(3 * (intento + 1))
        else:
            raise RuntimeError(f"http {r.status_code}")
        with zipfile.ZipFile(zpath) as z:
            nombres = {Path(n).name: n for n in z.namelist()}
            (SALIDA / pm).mkdir(exist_ok=True)
            for n in faltan:
                # solo por nombre exacto y solo imagenes: nada de rutas del zip ni ejecutables
                if n in nombres and Path(n).suffix.lower() in EXT_OK and Path(n).name == n:
                    datos = z.read(nombres[n])
                    (SALIDA / pm / n).write_bytes(datos)
                    filas.append([pm, n, 1, len(datos), ""])
                else:
                    filas.append([pm, n, 0, 0, "no esta en el zip"])
    except Exception as exc:  # noqa: BLE001
        filas = [[pm, n, 0, 0, str(exc)[:80]] for n in faltan]
    finally:
        if zpath.exists():
            zpath.unlink()
    with lock:
        for f in filas:
            w.writerow(f)
            cont["ok" if f[2] else "fallo"] += 1
        cont["hechos"] += 1
        lf.flush()
        if cont["hechos"] % 25 == 0:
            print(f"{cont['hechos']}/{total} articulos | figuras ok {cont['ok']} | fallos {cont['fallo']}", flush=True)
    time.sleep(0.5)


def main() -> None:
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    hilos = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    SALIDA.mkdir(parents=True, exist_ok=True)
    pedidas: dict[str, set[str]] = {}
    with PANELES.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r["image_file"]:
                pedidas.setdefault(r["pmcid"], set()).add(r["image_file"])
    pmcs = sorted(pedidas)[:limite] if limite else sorted(pedidas)
    nuevo = not LOG.exists()
    with LOG.open("a", encoding="utf-8-sig", newline="") as lf:
        w = csv.writer(lf)
        if nuevo:
            w.writerow(["pmcid", "image_file", "ok", "bytes", "motivo"])
        with ThreadPoolExecutor(max_workers=hilos) as ex:
            for pm in pmcs:
                ex.submit(bajar, pm, pedidas[pm], w, lf, len(pmcs))
    print(f"listo: figuras ok {cont['ok']} | fallos {cont['fallo']}")


if __name__ == "__main__":
    main()
