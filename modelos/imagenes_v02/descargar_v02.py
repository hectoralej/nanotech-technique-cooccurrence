"""Descarga las figuras NUEVAS del inventario (modelos/imagenes_v02/inventario_figuras.csv) a producto/imagenes_v02/<pmcid>/.

Usa el zip de Europe PMC (supplementaryFiles) con `requests` (la descarga con urllib dio timeouts en la sesión de Codex).
Si el inventario lista un .gif, se busca primero el .jpg del mismo nombre (el .gif del zip suele ser una miniatura).
Reanudable; salta lo que ya está en producto/imagenes/ o en producto/imagenes_v02/. Registro: modelos/imagenes_v02/descargas_v02_requests.csv
Uso: python modelos/imagenes_v02/descargar_v02.py [hilos]
"""
import csv
import sys
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[2]
INV = RAIZ / "modelos/imagenes_v02/inventario_figuras.csv"
ORIG = RAIZ / "producto/imagenes"
DEST = RAIZ / "producto/imagenes_v02"
LOG = RAIZ / "modelos/imagenes_v02/descargas_v02_requests.csv"
UA = {"User-Agent": "nano2predict-hackathon (mailto:hector.rojas.valdez@est.una.ac.cr)"}
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pm}/supplementaryFiles"
EXT = (".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".webp")
lock = threading.Lock()
cont = {"ok": 0, "fallo": 0, "hechos": 0}


def bajar(pm, nombres, w, lf, total):
    pendientes = [n for n in nombres if not (ORIG / pm / n).exists() and not (DEST / pm / n).exists()]
    filas = []
    if pendientes:
        zpath = DEST / f"_{pm}.zip"
        try:
            DEST.mkdir(parents=True, exist_ok=True)
            for intento in range(3):
                r = requests.get(URL.format(pm=pm), headers=UA, timeout=120)
                if r.status_code == 200:
                    zpath.write_bytes(r.content)
                    break
                time.sleep(3 * (intento + 1))
            else:
                raise RuntimeError(f"http {r.status_code}")
            with zipfile.ZipFile(zpath) as z:
                en_zip = {Path(n.replace("\\", "/")).name.lower(): n for n in z.namelist()}
                for n in pendientes:
                    stem = Path(n).stem.lower()
                    hallado = next((en_zip[c] for c in (stem + ".jpg", stem + ".jpeg", stem + ".png", n.lower()) if c in en_zip), None)
                    if hallado is None or Path(hallado).suffix.lower() not in EXT:
                        filas.append([pm, n, 0, 0, "no esta en el zip"]); continue
                    nombre = Path(hallado.replace("\\", "/")).name
                    (DEST / pm).mkdir(parents=True, exist_ok=True)
                    datos = z.read(hallado)
                    (DEST / pm / nombre).write_bytes(datos)
                    filas.append([pm, n, 1, len(datos), f"guardado como {nombre}"])
        except Exception as exc:  # noqa: BLE001
            filas = [[pm, n, 0, 0, "fallo: " + str(exc)[:80]] for n in pendientes]
        finally:
            if zpath.exists():
                zpath.unlink()
    with lock:
        for f in filas:
            w.writerow(f); cont["ok" if f[2] else "fallo"] += 1
        cont["hechos"] += 1; lf.flush()
        if cont["hechos"] % 25 == 0:
            print(f"{cont['hechos']}/{total} articulos | ok {cont['ok']} | fallos {cont['fallo']}", flush=True)
    time.sleep(0.4)


def main():
    hilos = int(next((a for a in sys.argv[1:] if a.isdigit()), 4))
    inv = pd.read_csv(INV, encoding="utf-8-sig")
    if "--todo" not in sys.argv and "ya_en_base" in inv.columns:    # con --todo se baja también lo marcado ya_en_base (p. ej. espectros que nunca se descargaron)
        inv = inv[inv.ya_en_base == 0]
    grupos = {pm: sorted(set(g.archivo_grafico.dropna().astype(str))) for pm, g in inv.groupby("pmcid")}
    nuevo = not LOG.exists()
    with LOG.open("a", encoding="utf-8-sig", newline="") as lf:
        w = csv.writer(lf)
        if nuevo:
            w.writerow(["pmcid", "archivo_inventario", "ok", "bytes", "motivo"])
        with ThreadPoolExecutor(max_workers=hilos) as ex:
            for pm, nombres in grupos.items():
                ex.submit(bajar, pm, nombres, w, lf, len(grupos))
    print(f"listo: ok {cont['ok']} | fallos {cont['fallo']} | articulos {len(grupos)}")


if __name__ == "__main__":
    main()
