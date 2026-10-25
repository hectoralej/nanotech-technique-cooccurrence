"""Genera 06_preentrenamiento_nffa.ipynb: DINOv2 (LVD) -> NFFA-EUROPE SEM (etapa intermedia) -> nuestros recortes, frente a la linea base y a un control.
Misma receta de entrenamiento que el cuaderno 04 (AdamW por capas, OneCycleLR, AMP, pesos de clase suavizados, label smoothing, aumentos en GPU, punto de control por epoca).
Uso: python modelos/kabre/crear_cuaderno_06.py
"""
import ast
import json
from pathlib import Path

D = Path(__file__).resolve().parent
nb04 = json.loads((D / "04_recortes_ajuste_fino.ipynb").read_text(encoding="utf-8"))
celdas = []


def md(t):
    celdas.append(("markdown", t.strip("\n")))


def cod(t):
    celdas.append(("code", t.strip("\n")))


def cuadro(hace, espera, continuar, si_no):
    return ("| | |\n|---|---|\n" f"| **Qué hace** | {hace} |\n| **Qué esperar** | {espera} |\n| **Continuar si** | {continuar} |\n| **Si no** | {si_no} |")


# ------------------------------------------------------------------ portada
md("""
# 06 · Preentrenamiento intermedio con NFFA-EUROPE (SEM) → nuestros recortes · DINOv2

**Pregunta:** ¿aprender primero morfologías de nanomateriales en SEM (NFFA) mejora la predicción de la clase de portador con nuestros recortes, frente a partir solo del preentrenamiento general (LVD-142M)?

**Dónde correrlo:** Jupyter en `nukwa-l40s` (alternativa `nukwa-v100`), 1 nodo, 4 núcleos, 16 GB, **2 h** (hay margen para 3 h). Kernel `Python-ML-DL`. Es una sesión interactiva normal en un nodo de cómputo; no se corre nada en el nodo de acceso.

**Rutas (todas se calculan desde `BASE = ~/ondemand/Kabre_Nano2Predict`, o la variable de entorno `N2P_BASE`):**
| Qué | Dónde |
|---|---|
| Nuestros recortes (ya subidos para el 04) | `BASE/recortes_v02.zip` o `BASE/subir_a_kabre/` (se busca sola); ya descomprimido: `BASE/recortes/` y `BASE/datos/indice_recortes_entrenamiento.csv` |
| **Datos de NFFA (se descargan aquí, ≈ 0,5–1 GB)** | `BASE/datos_externos/nffa_sem/<clase>/*.jpg` (teselas de 256 px, sin banda de metadatos) |
| **Todos los resultados de este cuaderno** | `BASE/resultados/06_nffa_dinov2/` (una carpeta por etapa y por brazo; **no se mezcla con el 03 ni el 04**) |
| Para enviar a Claude | `BASE/resultados/06_nffa_dinov2/06_para_claude.zip` (solo archivos pequeños, sin pesos) |

**Estructura de resultados**
```
06_nffa_dinov2/
  00_diagnostico/        nodo, red, velocidad de descarga, disco
  01_nffa_datos/         indice_nffa.csv, ejemplos_teselas.jpg, log_descarga.json
  02_etapa1_nffa/        backbone_dinov2_nffa.pt (pesos), metricas_etapa1.json
  02b_etapa1_control/    backbone con etiquetas mezcladas (control)
  03_brazo_A_base/       semilla0/, semilla1/, semilla2/  (LVD → nuestros recortes)
  04_brazo_B_nffa/       semilla0/ ...                    (LVD → NFFA → nuestros recortes)
  05_brazo_C_control/    semilla0/ ...                    (LVD → NFFA con etiquetas mezcladas → nuestros recortes)
  99_analisis/           metricas_06.json, analisis_06.md, tabla_brazos.csv
  06_para_claude.zip
```

**Los 3 brazos (solo cambia el punto de partida del ajuste fino con nuestros recortes; misma receta, mismas particiones por artículo):**
- **A · línea base:** DINOv2 con su preentrenamiento general.
- **B · NFFA:** DINOv2 ajustado antes con 7 morfologías de NFFA.
- **C · control:** igual que B, pero con las etiquetas de NFFA **mezcladas al azar**. Si B gana a A pero C también, la mejora no viene de saber morfología sino de ver SEM en escala de grises. (No se usan épocas extra sobre nuestros datos: verían las particiones de prueba.)

**Criterio fijado antes de ver resultados:** métrica única = F1 macro por artículo (promedio de probabilidades de los recortes de cada artículo y de las 3 semillas). Éxito = B − A con IC 95 % por bootstrap de artículos que **excluye 0**, y B − C también. Cualquier otra cosa se reporta como «no concluyente / marginal». No se elige nada con datos de prueba.

**Tiempo (estimado; la celda de la etapa 2 lo mide):** descarga 10–25 min · etapa 1 ≈ 3–5 min (×2 con el control) · cada brazo-semilla ≈ 6 min · total ≈ 1,5 h.
""")

# ------------------------------------------------------------------ etapa 0
md("## ETAPA 0 · Diagnóstico (red, disco, velocidad de descarga)\n\n" + cuadro(
    "Comprueba GPU, disco, que el nodo alcance B2SHARE (NFFA) y Hugging Face, y mide la velocidad real de descarga con 50 MB.",
    "≈ 1 min. Imprime la velocidad (MB/s) y cuánto tardaría la descarga completa (≈ 6,7 GB).",
    "Hay GPU, B2SHARE responde y la velocidad es ≥ 4 MB/s (descarga completa ≤ 30 min).",
    "Sin B2SHARE: detente y avísale a Claude (se prepara el zip desde el PC). Velocidad < 4 MB/s: quita `Particles` o `Nanowires` de `CLASES_NFFA` más abajo (son los tars grandes)."))
cod(r'''
# ETAPA 0: diagnóstico
import os, sys, json, time, math, random, socket, shutil, hashlib, io, tarfile, zipfile, subprocess
from pathlib import Path
T_INICIO = time.time()
SESION_HORAS = 2                              # horas pedidas a Slurm (2 o 3)
TIEMPO_MAX_MIN = SESION_HORAS * 60 - 15       # las celdas largas se detienen solas aquí; se puede volver a ejecutar y retoman

BASE = Path(os.environ.get("N2P_BASE", Path.home() / "ondemand" / "Kabre_Nano2Predict"))
assert BASE.exists(), f"No existe {BASE}. Define N2P_BASE o sube la carpeta Kabre_Nano2Predict a ~/ondemand/"
RES_RAIZ = next((p for p in (BASE / "resultados", BASE / "Resultados") if p.exists()), BASE / "resultados")   # mayúscula o minúscula
DATOS = BASE / "datos"
NFFA_DIR = BASE / "datos_externos" / "nffa_sem"
SAL = RES_RAIZ / "06_nffa_dinov2"
SUB = {k: SAL / v for k, v in {"diag": "00_diagnostico", "datos": "01_nffa_datos", "e1": "02_etapa1_nffa", "e1c": "02b_etapa1_control",
       "A": "03_brazo_A_base", "B": "04_brazo_B_nffa", "C": "05_brazo_C_control", "anal": "99_analisis"}.items()}
for p in [NFFA_DIR, *SUB.values()]:
    p.mkdir(parents=True, exist_ok=True)
print("BASE      :", BASE)
print("RESULTADOS:", SAL)
print("NFFA      :", NFFA_DIR)
print("contenido de BASE:", sorted(x.name for x in BASE.iterdir()))

import numpy as np, pandas as pd, requests
try:
    import torch, timm
    dev = "cuda"
    assert torch.cuda.is_available(), "No hay GPU: pide una cola nukwa-* y usa el kernel Python-ML-DL"
    gpu = torch.cuda.get_device_name(0)
except ImportError:
    gpu = None
asignados = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()
ram_gb = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1e9 if hasattr(os, "sysconf") else None
libre_gb = shutil.disk_usage(BASE).free / 1e9
print("nodo:", socket.gethostname(), "| GPU:", gpu, "| núcleos:", asignados, "| RAM total (nodo): %.0f GB" % (ram_gb or 0), "| disco libre en BASE: %.1f GB" % libre_gb)
try:
    print("cuota:", subprocess.run(["quota", "-s"], capture_output=True, text=True, timeout=20).stdout.strip() or "(sin salida)")
except Exception as e:
    print("cuota: no disponible (", type(e).__name__, ")")
uso = subprocess.run(["du", "-sh", str(BASE)], capture_output=True, text=True).stdout.split()[0]
print("espacio que ya ocupa BASE:", uso)

# --- clases de NFFA a usar: nombre -> (tar, tamaño aprox. en MB, md5 publicado en B2SHARE el 24-oct-2026)
URL_BASE = "https://b2share.eudat.eu/api/records/1nysp-05236/files"
NFFA = {
    "Particles": ("Particles.tar", 2533, "574dc286654f2ac5a5346cab3155cda2"),
    "Powder": ("Powder.tar", 881, "4cc608a22bb0cbe1fd6ac3450d22e773"),
    "Nanowires": ("Nanowires.tar", 2210, "8902e812f024a7fb0f35bac46347eccc"),
    "Fibres": ("Fibres.tar", 87, "e0e3fb9957efc2cf35c50680bc19d97a"),
    "Films_Coated_Surface": ("Films_Coated_Surface.tar", 207, "f8867e0f2f3c25ba50168c23506865e4"),
    "Porous_Sponge": ("Porous_Sponge.tar", 123, "a9c1c95421277514e12bc21bb424c9ae"),
    "Biological": ("Biological.tar", 710, "de3860deab60d6f61c90128674e200cf"),
}
CLASES_NFFA = list(NFFA)                      # edita esta lista para descargar menos
total_mb = sum(NFFA[c][1] for c in CLASES_NFFA)

diag = {"nodo": socket.gethostname(), "gpu": gpu, "nucleos": asignados, "disco_libre_gb": round(libre_gb, 1), "base": str(BASE)}
for nombre, url in (("b2share", "https://b2share.eudat.eu"), ("huggingface", "https://huggingface.co")):
    try:
        with requests.get(url, timeout=20, stream=True) as rr: diag[nombre] = rr.status_code
    except Exception as e:
        diag[nombre] = f"ERROR {type(e).__name__}"
print("red:", {k: diag[k] for k in ("b2share", "huggingface")})
try:                                                    # velocidad: 50 MB (o 25 s) del primer tar
    t0, n = time.time(), 0
    with requests.get(f"{URL_BASE}/Particles.tar/content", headers={"Range": "bytes=0-49999999"}, stream=True, timeout=(30, 60)) as r:
        for ch in r.iter_content(1 << 20):
            n += len(ch)
            if time.time() - t0 > 25: break
    diag["vel_mb_s"] = round(n / 1e6 / (time.time() - t0), 1)
    print(f"velocidad de descarga: {diag['vel_mb_s']} MB/s → descarga de {total_mb/1000:.1f} GB ≈ {total_mb / diag['vel_mb_s'] / 60:.0f} min")
except Exception as e:
    diag["vel_mb_s"] = None; print("prueba de velocidad falló:", type(e).__name__, e)
ok = bool(gpu) and diag["b2share"] == 200 and (diag["vel_mb_s"] or 0) >= 4 and libre_gb > 3
print("\nVEREDICTO ETAPA 0:", "OK, sigue con la etapa 1" if ok else "REVISA (mira el cuadro de arriba)")
(SUB["diag"] / "diagnostico.json").write_text(json.dumps(diag, indent=2), encoding="utf-8")
''')

# ------------------------------------------------------------------ funciones comunes
md("### Funciones comunes (no hace nada visible; define aumentos, modelo, entrenamiento y descarga)")
cod(r'''
# FUNCIONES COMUNES
import torch, timm
import torch.nn as nn, torch.nn.functional as F
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
torch.backends.cudnn.benchmark = True
TAM, LADO, DROP_PATH = 224, 256, 0.1
MODELO = "vit_small_patch14_dinov2.lvd142m"
os.environ.setdefault("HF_HOME", str(BASE / "hf_cache"))
MEDIA = torch.tensor([0.485, 0.456, 0.406], device=dev).view(1, 3, 1, 1) * 255
DESV = torch.tensor([0.229, 0.224, 0.225], device=dev).view(1, 3, 1, 1) * 255

def lote_train(X, idx):                                        # aumentos en GPU: recorte aleatorio 70-100 % + espejo
    xb, out = X[idx], []
    for i in range(xb.shape[0]):
        s = random.uniform(0.7, 1.0); c = int(LADO * math.sqrt(s))
        x0, y0 = random.randint(0, LADO - c), random.randint(0, LADO - c)
        im = F.interpolate(xb[i:i + 1, :, y0:y0 + c, x0:x0 + c].float(), size=(TAM, TAM), mode="bilinear", align_corners=False)
        out.append(im.flip(3) if random.random() < 0.5 else im)
    return (torch.cat(out) - MEDIA) / DESV

def lote_eval(X, idx):
    return (F.interpolate(X[idx].float(), size=(TAM, TAM), mode="bilinear", align_corners=False) - MEDIA) / DESV

def crear(n_clases, backbone=None):
    m = timm.create_model(MODELO, pretrained=True, num_classes=n_clases, img_size=TAM, drop_path_rate=DROP_PATH).to(dev)
    if backbone is not None:                                    # pesos de la etapa 1 (sin la cabeza)
        falta, extra = m.load_state_dict(torch.load(backbone, map_location=dev), strict=False)
        assert not extra and all(k.startswith("head") for k in falta), f"pesos incompatibles: {falta[:3]} {extra[:3]}"
    return m

def ajustar(m, X, y, tr, epocas, lr, ckpt, semilla, n_clases, bs=32, nombre=""):
    """Misma receta que el 04. y: tensor de etiquetas en GPU alineado con X. Punto de control por época (reanudable)."""
    random.seed(semilla); np.random.seed(semilla); torch.manual_seed(semilla)
    ids_cab = {id(p) for p in m.get_classifier().parameters()}
    bb = [p for p in m.parameters() if id(p) not in ids_cab]; cab = [p for p in m.parameters() if id(p) in ids_cab]
    opt = torch.optim.AdamW([{"params": bb, "lr": lr}, {"params": cab, "lr": lr * 10}], weight_decay=0.05)
    pasos_ep = len(tr) // bs
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=[lr, lr * 10], total_steps=epocas * pasos_ep, pct_start=0.15)
    frec = np.bincount(y[tr].cpu().numpy(), minlength=n_clases).clip(min=1)
    w = torch.tensor((frec.sum() / (n_clases * frec)) ** 0.5, dtype=torch.float32, device=dev)     # pesos suavizados
    crit = nn.CrossEntropyLoss(weight=w, label_smoothing=0.1)
    scaler = torch.cuda.amp.GradScaler(); ep0 = 0
    if ckpt.exists():
        s = torch.load(ckpt, map_location=dev)
        m.load_state_dict(s["m"]); opt.load_state_dict(s["opt"]); sched.load_state_dict(s["sched"]); scaler.load_state_dict(s["scaler"]); ep0 = s["ep"] + 1
        print(f"  reanudando {nombre} desde la época {ep0}")
    for ep in range(ep0, epocas):
        m.train(); perm = np.random.permutation(tr); perd = ok = n = 0
        for i in range(pasos_ep):
            idx = torch.tensor(perm[i * bs:(i + 1) * bs], device=dev)
            with torch.autocast("cuda", dtype=torch.float16):
                lo = m(lote_train(X, idx)); loss = crit(lo, y[idx])
            opt.zero_grad(set_to_none=True); scaler.scale(loss).backward(); scaler.step(opt); scaler.update(); sched.step()
            perd += float(loss) * len(idx); ok += int((lo.argmax(1) == y[idx]).sum()); n += len(idx)
        print(f"  {nombre} época {ep+1}/{epocas}: pérdida {perd/n:.3f} | acierto entrenamiento {ok/n:.3f} | {(time.time()-T_INICIO)/60:.1f} min desde el inicio", flush=True)
        torch.save({"m": m.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(), "scaler": scaler.state_dict(), "ep": ep}, ckpt)
    return m

def predecir(m, X, idx):
    m.eval(); P = []
    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.float16):
        for i in range(0, len(idx), 128):
            P.append(torch.softmax(m(lote_eval(X, torch.tensor(idx[i:i + 128], device=dev))).float(), 1).cpu().numpy())
    return np.concatenate(P)

def cargar_jpg(ruta):                                           # teselas NFFA y recortes ya cuadrados o no: se rellena a cuadrado y se reduce a LADO
    im = Image.open(ruta).convert("RGB"); w, h = im.size; l = max(w, h)
    lienzo = Image.new("RGB", (l, l), (255, 255, 255)); lienzo.paste(im, ((l - w) // 2, (l - h) // 2))
    return np.asarray(lienzo.resize((LADO, LADO), Image.BICUBIC), dtype=np.uint8)

def a_gpu(rutas):
    with ThreadPoolExecutor(max_workers=max(2, asignados)) as ex:
        X = np.stack(list(ex.map(cargar_jpg, [str(p) for p in rutas])))
    return torch.from_numpy(X).permute(0, 3, 1, 2).contiguous().to(dev)

# --- descarga de NFFA en streaming (sin guardar el .tar), recorte de la banda de metadatos y teselas cuadradas
EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
class LectorMD5:
    def __init__(s, r): s.r, s.h, s.n = r, hashlib.md5(), 0
    def read(s, n=-1):
        b = s.r.read(n); s.h.update(b); s.n += len(b); return b

def corte_banda(im):
    """Fila donde empieza la banda blanca de metadatos del SEM (abajo). Devuelve (corte_y, método)."""
    g = np.asarray(im.convert("L")); h, w = g.shape
    filas = np.where((g[int(h * 0.6):] > 235).mean(1) > 0.8)[0] + int(h * 0.6)
    if len(filas) >= 20:
        y0 = int(filas[0])
        if y0 > h * 0.5: return max(y0 - 3, 1), "detectada"
    if (w, h) == (1024, 768): return 630, "tamaño_conocido"
    return h, "sin_banda"

def teselas(im):
    """Dos teselas cuadradas (extremos de la imagen sin banda) reducidas a LADO px."""
    c, met = corte_banda(im); im2 = im.crop((0, 0, im.width, c)); w, h = im2.size; s = min(w, h)
    cajas = [(0, 0, s, s), (w - s, h - s, w, h)] if w >= h else [(0, 0, s, s), (0, h - s, s, h)]
    return [im2.crop(b).resize((LADO, LADO), Image.BICUBIC) for b in cajas], c, met

def descargar_clase(clase, n_img, semilla=20261025):
    fichero, mb, md5 = NFFA[clase]; url = f"{URL_BASE}/{fichero}/content"
    for intento in range(1, 4):
        try:
            rng = random.Random(semilla); res = []; vistos = 0; t0 = time.time()
            with requests.get(url, stream=True, timeout=(30, 120)) as r:
                r.raise_for_status()
                lec = LectorMD5(r.raw)
                with tarfile.open(fileobj=lec, mode="r|") as tf:
                    for mi in tf:
                        if not mi.isfile() or not mi.name.lower().endswith(EXT) or os.path.basename(mi.name).startswith("._"): continue
                        i = vistos; vistos += 1
                        if i < n_img: slot = i
                        else:
                            j = rng.randint(0, i); slot = j if j < n_img else None
                        if slot is None: continue
                        datos = tf.extractfile(mi).read()
                        if slot < len(res): res[slot] = (mi.name, datos)
                        else: res.append((mi.name, datos))
                while lec.read(1 << 20): pass            # drena el resto para que el md5 sea del archivo completo
            coincide = lec.h.hexdigest() == md5
            if not coincide and intento < 3:
                print(f"  md5 no coincide en {clase} (intento {intento}); reintento"); continue
            return res, vistos, lec.n, coincide, time.time() - t0
        except Exception as e:
            print(f"  fallo en {clase} (intento {intento}/3): {type(e).__name__}: {e}"); time.sleep(5)
    raise RuntimeError(f"No se pudo descargar {clase}")

def metr(real, P, clases):
    pred = np.array(clases)[P.argmax(1)]; real = np.asarray(real); f1 = []; rec = []
    for c in clases:
        tp = float(((pred == c) & (real == c)).sum()); pr = tp / max(1, (pred == c).sum()); re = tp / max(1, (real == c).sum())
        f1.append(0.0 if pr + re == 0 else 2 * pr * re / (pr + re)); rec.append(re)
    return {"acc": float((pred == real).mean()), "acc_bal": float(np.mean(rec)), "f1": float(np.mean(f1))}
print("OK funciones comunes")
''')

# ------------------------------------------------------------------ etapa 1 descarga
md("## ETAPA 1 · Descarga y preparación de NFFA\n\n" + cuadro(
    "Descarga **en streaming** (sin guardar el .tar) las 7 carpetas de NFFA-EUROPE Majority SEM (CC BY 4.0), verifica el md5, toma hasta `N_IMG` imágenes al azar por clase, **recorta la banda blanca de metadatos** del instrumento y guarda 2 teselas cuadradas de 256 px por imagen en `BASE/datos_externos/nffa_sem/<clase>/`. Es reanudable por clase.",
    "10–25 min según la velocidad medida. Disco final ≈ 0,5–1 GB. Al terminar imprime imágenes vistas/guardadas por clase, md5 y un montaje `ejemplos_teselas.jpg` para que veas que la banda desapareció.",
    "Todos los md5 coinciden (`ok`), hay ≥ 5 clases con ≥ 80 imágenes y el montaje no muestra banda ni texto.",
    "md5 distinto: se reintentó 3 veces; si persiste, se marca en el log y esa clase se descarta de `CLASES_NFFA`. Banda visible en el montaje: avisa a Claude antes de la etapa 2."))
cod(r'''
# ETAPA 1: descarga NFFA (reanudable por clase)
N_IMG = 1000                                    # imágenes por clase como máximo (2 teselas cada una)
log_ruta = SUB["datos"] / "log_descarga.json"
log = json.loads(log_ruta.read_text()) if log_ruta.exists() else {}
for clase in CLASES_NFFA:
    marca = NFFA_DIR / clase / "_listo.json"
    if marca.exists():
        print(f"{clase}: ya descargada ({json.loads(marca.read_text())['guardadas']} imágenes)"); continue
    if (time.time() - T_INICIO) / 60 > TIEMPO_MAX_MIN:
        print("Límite de tiempo; vuelve a ejecutar esta celda."); break
    print(f"{clase}: descargando ≈ {NFFA[clase][1]} MB ...", flush=True)
    res, vistos, nbytes, md5_ok, seg = descargar_clase(clase, N_IMG)
    carpeta = NFFA_DIR / clase; carpeta.mkdir(exist_ok=True); met_cuenta = {}
    for i, (nombre, datos) in enumerate(res):
        im = Image.open(io.BytesIO(datos)).convert("RGB")
        ts, c, met = teselas(im); met_cuenta[met] = met_cuenta.get(met, 0) + 1
        for suf, t in zip("ab", ts):
            t.save(carpeta / f"{clase[:4]}_{i:04d}_{hashlib.md5(nombre.encode()).hexdigest()[:6]}_{suf}.jpg", quality=92)
    info = {"vistas": vistos, "guardadas": len(res), "bytes": nbytes, "md5_ok": md5_ok, "segundos": round(seg), "banda": met_cuenta}
    marca.write_text(json.dumps(info)); log[clase] = info
    print(f"  {clase}: vistas {vistos} | guardadas {len(res)} | {nbytes/1e6:.0f} MB en {seg:.0f}s ({nbytes/1e6/seg:.1f} MB/s) | md5 {'ok' if md5_ok else 'NO COINCIDE'} | banda: {met_cuenta}", flush=True)
    log_ruta.write_text(json.dumps(log, indent=1))

# índice y montaje de control
filas = [{"clase": c, "imagen": f"{c}/" + p.stem[:-2], "tesela": p.stem[-1], "ruta": str(p)} for c in CLASES_NFFA if (NFFA_DIR / c).exists() for p in sorted((NFFA_DIR / c).glob("*.jpg"))]
idx_nffa = pd.DataFrame(filas); idx_nffa.to_csv(SUB["datos"] / "indice_nffa.csv", index=False)
print("\nteselas por clase:", idx_nffa.groupby("clase").size().to_dict(), "| imágenes:", idx_nffa.imagen.nunique())
rng = random.Random(1); tiles = []
for c in CLASES_NFFA:
    sub = idx_nffa[idx_nffa.clase == c]
    if len(sub): tiles.append([Image.open(r).resize((160, 160)) for r in sub.ruta.sample(min(6, len(sub)), random_state=1)])
mont = Image.new("RGB", (160 * 6, 160 * len(tiles)), "white")
for j, fila in enumerate(tiles):
    for i, t in enumerate(fila): mont.paste(t, (i * 160, j * 160))
mont.save(SUB["datos"] / "ejemplos_teselas.jpg", quality=85)
print("montaje:", SUB["datos"] / "ejemplos_teselas.jpg", "(filas = clases en el orden de CLASES_NFFA:", CLASES_NFFA, ")")
print("disco usado por NFFA: %.2f GB" % (sum(p.stat().st_size for p in NFFA_DIR.rglob("*.jpg")) / 1e9))
print("md5:", {c: log[c]["md5_ok"] for c in log})
''')

# ------------------------------------------------------------------ etapa 2
md("## ETAPA 2 · Etapa 1 del modelo: DINOv2 aprende morfologías de NFFA (y su control)\n\n" + cuadro(
    "Mide primero la velocidad (≈ 1 min); luego ajusta DINOv2-S/14 con las clases de NFFA (8 épocas, 90 % de las imágenes para entrenar y 10 % para comprobar que aprende). Guarda el backbone sin cabeza. Después repite con las **etiquetas mezcladas** (control C).",
    "≈ 3–5 min cada una. Imprime el acierto de validación por clase (solo informativo; no se elige nada con él) y la estimación de tiempo de todo el plan.",
    "Acierto de validación NFFA claramente sobre el azar (1/7 ≈ 0,14; esperable > 0,6) y la estimación total cabe en la sesión.",
    "Acierto ≈ azar: algo falló con las teselas; avisa a Claude. Estimación > sesión: pon `HACER_CONTROL = False` o `SEMILLAS = [0]`."))
cod(r'''
# ETAPA 2: etapa 1 de DINOv2 en NFFA (+ control con etiquetas mezcladas)
EPOCAS_E1, LR_E1, HACER_CONTROL = 8, 3e-5, True
idx_nffa = pd.read_csv(SUB["datos"] / "indice_nffa.csv")
cl_n = sorted(idx_nffa.clase.unique()); ci = {c: i for i, c in enumerate(cl_n)}
yn = np.array([ci[c] for c in idx_nffa.clase])
t0 = time.time(); Xn = a_gpu(idx_nffa.ruta); print(f"teselas NFFA en GPU: {tuple(Xn.shape)} ({time.time()-t0:.0f}s) | memoria GPU {torch.cuda.memory_allocated()/1e9:.1f} GB")

# partición por IMAGEN (las 2 teselas de una imagen van juntas): 10 % para validar
rng = np.random.default_rng(7); imgs = idx_nffa.drop_duplicates("imagen")[["imagen", "clase"]]; val_imgs = set()
for c, g in imgs.groupby("clase"):
    n = max(1, int(round(0.1 * len(g)))); val_imgs |= set(rng.choice(g.imagen.values, n, replace=False))
es_val = idx_nffa.imagen.isin(val_imgs).values; tr_n, va_n = np.where(~es_val)[0], np.where(es_val)[0]
print("entrenamiento:", len(tr_n), "teselas | validación:", len(va_n), "| clases:", cl_n)

# prueba mínima de velocidad
m = crear(len(cl_n)); m.train(); opt = torch.optim.AdamW(m.parameters(), lr=1e-5); sc = torch.cuda.amp.GradScaler(); yg = torch.tensor(yn, device=dev); tiempos = []
for i in range(6):
    idx = torch.randint(0, len(yn), (32,), device=dev); torch.cuda.synchronize(); t1 = time.time()
    with torch.autocast("cuda", dtype=torch.float16): loss = F.cross_entropy(m(lote_train(Xn, idx)), yg[idx])
    opt.zero_grad(set_to_none=True); sc.scale(loss).backward(); sc.step(opt); sc.update(); torch.cuda.synchronize(); tiempos.append(time.time() - t1)
seg = float(np.median(tiempos[2:])); del m, opt; torch.cuda.empty_cache()
e1_min = seg * (len(tr_n) // 32) * EPOCAS_E1 / 60; fold_min = seg * (4670 * 0.8 / 32) * 10 / 60
print(f"{seg*1000:.0f} ms por lote | etapa 1 ≈ {e1_min:.1f} min | una partición con nuestros recortes ≈ {fold_min:.1f} min | plan completo "
      f"(2 etapas 1 + 3 brazos × 3 semillas × 5 particiones) ≈ {2*e1_min + 45*fold_min:.0f} min (estimación)")

def etapa1(nombre, y_vec, salida, validar=True):
    bb = salida / "backbone_dinov2.pt"
    if bb.exists(): print(nombre, ": ya hecho"); return
    yg = torch.tensor(y_vec, device=dev); m = crear(len(cl_n))
    m = ajustar(m, Xn, yg, tr_n, EPOCAS_E1, LR_E1, salida / "ckpt.pt", 0, len(cl_n), nombre=nombre)
    info = {"epocas": EPOCAS_E1, "lr": LR_E1, "clases": cl_n, "teselas_entrenamiento": int(len(tr_n)), "teselas_validacion": int(len(va_n))}
    if validar:
        P = predecir(m, Xn, va_n); r = metr(np.array(cl_n)[yn[va_n]], P, cl_n); info["validacion_interna"] = r
        por_clase = {c: round(float((P.argmax(1)[yn[va_n] == i] == i).mean()), 3) for i, c in enumerate(cl_n)}; info["acierto_por_clase"] = por_clase
        print(f"  validación interna NFFA: exactitud {r['acc']:.3f} | F1 macro {r['f1']:.3f} | por clase {por_clase}")
    torch.save({k: v for k, v in m.state_dict().items() if not k.startswith("head")}, bb)
    (salida / "metricas_etapa1.json").write_text(json.dumps(info, indent=1)); (salida / "ckpt.pt").unlink(missing_ok=True)
    del m; torch.cuda.empty_cache()

etapa1("etapa1 NFFA", yn, SUB["e1"])
if HACER_CONTROL:                                         # etiquetas mezcladas ENTRE IMÁGENES (las dos teselas de una imagen conservan la misma etiqueta)
    r2 = np.random.default_rng(11); ids = idx_nffa.drop_duplicates("imagen"); perm = dict(zip(ids.imagen, r2.permutation(np.array([ci[c] for c in ids.clase]))))
    y_mezcla = np.array([perm[i] for i in idx_nffa.imagen])
    etapa1("etapa1 control (etiquetas mezcladas)", y_mezcla, SUB["e1c"], validar=False)
del Xn; torch.cuda.empty_cache()
print("pesos:", [str(p) for p in SAL.rglob("backbone_dinov2.pt")])
''')

# ------------------------------------------------------------------ etapa 3 datos
md("## ETAPA 3 · Nuestros recortes (datos del 04)\n\n" + cuadro(
    "Carga los 4.670 recortes de micrografía de partículas (descomprime `recortes_v02.zip` solo la primera vez si hace falta) y los pasa a la GPU; define los brazos A, B y C.",
    "≈ 1 min. Imprime recortes, artículos, clases y línea base (clase mayoritaria).",
    "≈ 4.670 recortes, ≈ 1.114 artículos, 4 clases y ningún artículo en dos particiones.",
    "Faltan recortes: sube/descomprime `recortes_v02.zip` en `BASE` (como en el 04)."))
cod(r'''
# ETAPA 3: datos propios
ZIP = next((z for z in (BASE / "recortes_v02.zip", DATOS / "recortes_v02.zip", BASE / "subir_a_kabre" / "recortes_v02.zip") if z.exists()), None) or next(iter(sorted(BASE.rglob("recortes_v02.zip"))), None)
REC = BASE / "recortes"
if not REC.exists() and ZIP is not None:
    DATOS.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP) as z: z.extractall(BASE)
    (BASE / "indice_recortes_entrenamiento.csv").replace(DATOS / "indice_recortes_entrenamiento.csv"); print("recortes descomprimidos en", REC)
t = pd.read_csv(DATOS / "indice_recortes_entrenamiento.csv", encoding="utf-8-sig", dtype=str)
t["ruta"] = t.apply(lambda r: REC / str(r["pmcid"]) / str(r["image_file"]), axis=1)
d = t[t.ruta.map(lambda p: p.exists()) & t.clase_modelo.notna()].reset_index(drop=True); d["fold"] = d.fold.astype(int)
assert len(d) > 1000, "faltan recortes: sube y descomprime recortes_v02.zip"
assert (d.groupby("pmcid").fold.nunique() == 1).all(), "un artículo está en dos particiones"
clases = sorted(set(d.clase_modelo)); cidx = {c: i for i, c in enumerate(clases)}
yi = np.array([cidx[c] for c in d.clase_modelo]); folds = d.fold.values; yg_ours = torch.tensor(yi, device=dev)
print(f"recortes: {len(d)} | artículos: {d.pmcid.nunique()} | clases: {clases} | línea base mayoritaria (recortes): {pd.Series(d.clase_modelo).value_counts(normalize=True).max():.3f}")
t0 = time.time(); Xg = a_gpu(d.ruta); print(f"recortes en la GPU: {tuple(Xg.shape)} ({time.time()-t0:.0f}s)")

EPOCAS, LR, SEMILLAS = 10, 3e-5, [0, 1, 2]
RUTAS = {"A": (SUB["A"], None), "B": (SUB["B"], SUB["e1"] / "backbone_dinov2.pt"), "C": (SUB["C"], SUB["e1c"] / "backbone_dinov2.pt")}

def por_art(o):
    pc = ["p_" + c for c in clases]
    g = o.groupby("pmcid").agg({**{c: "mean" for c in pc}, "real": "first", "fold": "first"}); return g, pc

def correr(brazo, semillas):
    carpeta, bb = RUTAS[brazo]
    if bb is not None: assert bb.exists(), f"falta {bb}: ejecuta la etapa 2 (y comprueba que no se detuvo por tiempo)"
    for s in semillas:
        out = carpeta / f"semilla{s}"; out.mkdir(exist_ok=True)
        if (out / "predicciones_semilla.csv").exists(): print(f"{brazo} semilla {s}: ya hecha"); continue
        for k in range(5):
            f = out / f"ft_dinov2_vits14_fold{k}.csv"
            if f.exists(): continue
            if (time.time() - T_INICIO) / 60 > TIEMPO_MAX_MIN:
                print(f"\nLímite de tiempo ({TIEMPO_MAX_MIN} min). Vuelve a ejecutar esta celda en otra sesión: retoma donde quedó."); return False
            t1 = time.time(); tr, te = np.where(folds != k)[0], np.where(folds == k)[0]
            m = crear(len(clases), bb)
            m = ajustar(m, Xg, yg_ours, tr, EPOCAS, LR, out / f"ckpt_f{k}.pt", s * 100 + k, len(clases), nombre=f"{brazo} s{s} fold {k}")
            P = predecir(m, Xg, te)
            df = pd.DataFrame({"pmcid": d.pmcid.values[te], "image_file": d.image_file.values[te], "real": d.clase_modelo.values[te], "prediccion": [clases[j] for j in P.argmax(1)], "fold": k})
            for j, c in enumerate(clases): df["p_" + c] = P[:, j].round(5)
            df.to_csv(f, index=False); (out / f"ckpt_f{k}.pt").unlink(missing_ok=True); del m; torch.cuda.empty_cache()
            print(f"== {brazo} semilla {s} fold {k} listo en {time.time()-t1:.0f}s | exactitud por recorte {(df.real == df.prediccion).mean():.3f}\n", flush=True)
        o = pd.concat([pd.read_csv(out / f"ft_dinov2_vits14_fold{k}.csv", dtype={"pmcid": str}) for k in range(5)]); o.to_csv(out / "predicciones_semilla.csv", index=False)
        g, pc = por_art(o); r = metr(g.real.values, g[pc].values, clases)
        (out / "metricas_semilla.json").write_text(json.dumps({"brazo": brazo, "semilla": s, "por_articulo": r, "n_articulos": int(len(g)), "epocas": EPOCAS, "lr": LR}, indent=1))
        print(f"### {brazo} semilla {s}: por artículo exactitud {r['acc']:.3f} | balanceada {r['acc_bal']:.3f} | F1 macro {r['f1']:.3f}\n")
    return True

def lee_brazo(brazo, s):
    f = RUTAS[brazo][0] / f"semilla{s}" / "predicciones_semilla.csv"
    return pd.read_csv(f, dtype={"pmcid": str}) if f.exists() else None
print("OK etapa 3")
''')

# ------------------------------------------------------------------ brazos A y B semilla 0
md("## ETAPA 4 · Brazos A (línea base) y B (NFFA), semilla 0\n\n" + cuadro(
    "Ajuste fino de DINOv2 con nuestros recortes, 5 particiones por artículo, 10 épocas: primero **A** (partiendo del preentrenamiento general) y luego **B** (partiendo del backbone de NFFA). Al final compara ambos por artículo.",
    "≈ 6 min por brazo (30–40 s por época con 4.670 recortes: estimación). A semilla 0 debería reproducir el 04 con DINOv2 (≈ acc 0,50–0,54 por artículo; no será idéntico).",
    "A se parece al 04 (confirma que la receta es la misma). Si B − A (F1 macro, semilla 0) ≥ ≈ +0,02 → sigue con las semillas 1 y 2 (etapa 5) y con el control.",
    "B − A ≤ 0: sigue igual con la etapa 5 (una semilla no basta para decidir), pero el control C pierde prioridad."))
cod(r'''
# ETAPA 4: A y B, semilla 0
ok_a = correr("A", [0]); ok_b = correr("B", [0]) if ok_a else False
a0, b0 = lee_brazo("A", 0), lee_brazo("B", 0)
if a0 is not None and b0 is not None:
    (ga, pc), (gb, _) = por_art(a0), por_art(b0); com = ga.index.intersection(gb.index)
    ra, rb = metr(ga.loc[com].real.values, ga.loc[com, pc].values, clases), metr(gb.loc[com].real.values, gb.loc[com, pc].values, clases)
    print(f"\nPor artículo ({len(com)} artículos), semilla 0:  A: acc {ra['acc']:.3f} F1 {ra['f1']:.3f}  |  B: acc {rb['acc']:.3f} F1 {rb['f1']:.3f}  |  B − A: acc {rb['acc']-ra['acc']:+.3f}, F1 {rb['f1']-ra['f1']:+.3f}")
    print("(una sola semilla: la diferencia puede ser solo ruido; la decisión se toma en la etapa 6 con 3 semillas e IC)")
''')

# ------------------------------------------------------------------ semillas 1 y 2
md("## ETAPA 5 · Semillas 1 y 2 de A y B\n\n" + cuadro(
    "Repite A y B con otras 2 semillas (otra inicialización de la cabeza, otro orden y otros aumentos) para saber cuánto varía el resultado por azar.",
    "≈ 24 min en total (4 brazos-semilla × 6 min: estimación).",
    "Terminan las 4 corridas antes del límite de tiempo.",
    "Se corta por tiempo: vuelve a ejecutar la celda (retoma). Si no queda sesión, el análisis (etapa 7) funciona con las semillas que haya."))
cod(r'''
# ETAPA 5: semillas 1 y 2
for s in SEMILLAS[1:]:
    if not correr("A", [s]): break
    if not correr("B", [s]): break
''')

# ------------------------------------------------------------------ control
md("## ETAPA 6 · Brazo C (control: NFFA con etiquetas mezcladas)\n\n" + cuadro(
    "Ajuste fino con nuestros recortes partiendo del backbone entrenado con **etiquetas de NFFA mezcladas al azar**: mismo cómputo y mismas imágenes que B, pero sin información morfológica.",
    "≈ 18 min con 3 semillas (estimación). Debería ser igual o peor que A.",
    "Termina, para que el análisis distinga «ayuda NFFA» de «ayuda ver SEM».",
    "Sin tiempo: usa `SEMILLAS_C = [0]` o sáltala; el análisis lo indica como «sin control»."))
cod(r'''
# ETAPA 6: control C
SEMILLAS_C = [0, 1, 2]
if (RUTAS["C"][1]).exists():
    for s in SEMILLAS_C:
        if not correr("C", [s]): break
else:
    print("No existe el backbone del control: ejecuta la etapa 2 con HACER_CONTROL = True")
''')

# ------------------------------------------------------------------ analisis
md("## ETAPA 7 · Análisis y paquete de resultados\n\n" + cuadro(
    "Por artículo y con las semillas disponibles: F1 macro, exactitud y exactitud balanceada de cada brazo (promedio ± desviación entre semillas); diferencias B − A y B − C con IC 95 % por bootstrap de artículos (2.000) sobre las probabilidades promediadas entre semillas. Escribe `99_analisis/` y `06_para_claude.zip`.",
    "≈ 1 min. Imprime el veredicto automático según el criterio de la portada.",
    "Hay al menos A y B con 3 semillas (y C si se corrió).",
    "Faltan semillas: el veredicto lo dice (poca potencia). Envía a Claude `06_para_claude.zip`."))
cod(r'''
# ETAPA 7: análisis
rng_b = np.random.default_rng(20261026); pcs = ["p_" + c for c in clases]
brazos = {}
for b in "ABC":
    ss = [s for s in SEMILLAS if lee_brazo(b, s) is not None]
    if ss: brazos[b] = ss
assert "A" in brazos and "B" in brazos, "faltan los brazos A y B"
ens, filas, ref = {}, [], None
for b, ss in brazos.items():
    gs = [por_art(lee_brazo(b, s))[0] for s in ss]; com = gs[0].index
    for g in gs[1:]: com = com.intersection(g.index)
    ref = com if ref is None else ref.intersection(com)
for b, ss in brazos.items():
    gs = [por_art(lee_brazo(b, s))[0].loc[ref] for s in ss]; real = gs[0].real.values
    por_sem = [metr(real, g[pcs].values, clases) for g in gs]
    ens[b] = np.mean([g[pcs].values for g in gs], axis=0); e = metr(real, ens[b], clases)
    filas.append({"brazo": b, "semillas": len(ss), **{f"{k}_media": round(float(np.mean([r[k] for r in por_sem])), 4) for k in ("acc", "acc_bal", "f1")},
                  **{f"{k}_sd": round(float(np.std([r[k] for r in por_sem])), 4) for k in ("acc", "acc_bal", "f1")}, **{f"{k}_ensamble": round(e[k], 4) for k in ("acc", "acc_bal", "f1")}})
real = por_art(lee_brazo("A", brazos["A"][0]))[0].loc[ref].real.values
tabla = pd.DataFrame(filas); tabla.to_csv(SUB["anal"] / "tabla_brazos.csv", index=False)
print(f"{len(ref)} artículos comunes | línea base mayoritaria: {pd.Series(real).value_counts(normalize=True).max():.3f}\n"); print(tabla.to_string(index=False))

def boot(Pa, Pb, n=2000):
    N = len(real); dd = []
    for _ in range(n):
        i = rng_b.integers(0, N, N); a, b2 = metr(real[i], Pa[i], clases), metr(real[i], Pb[i], clases); dd.append([a["acc"] - b2["acc"], a["f1"] - b2["f1"]])
    dd = np.array(dd); return {"acc": [float(np.percentile(dd[:, 0], 2.5)), float(np.percentile(dd[:, 0], 97.5))], "f1": [float(np.percentile(dd[:, 1], 2.5)), float(np.percentile(dd[:, 1], 97.5))]}
difs = {}
for a, b in (("B", "A"), ("B", "C"), ("C", "A")):
    if a in ens and b in ens:
        ra, rb = metr(real, ens[a], clases), metr(real, ens[b], clases)
        difs[f"{a} - {b}"] = {"acc": ra["acc"] - rb["acc"], "f1": ra["f1"] - rb["f1"], "IC95": boot(ens[a], ens[b])}
        print(f"{a} − {b}: Δ exactitud {difs[f'{a} - {b}']['acc']:+.3f} [{difs[f'{a} - {b}']['IC95']['acc'][0]:+.3f}, {difs[f'{a} - {b}']['IC95']['acc'][1]:+.3f}] | Δ F1 macro {difs[f'{a} - {b}']['f1']:+.3f} [{difs[f'{a} - {b}']['IC95']['f1'][0]:+.3f}, {difs[f'{a} - {b}']['IC95']['f1'][1]:+.3f}]")
# diferencia por semilla (cuánto varía por azar)
if len(brazos["A"]) == len(brazos["B"]):
    pares = [metr(por_art(lee_brazo("B", s))[0].loc[ref].real.values, por_art(lee_brazo("B", s))[0].loc[ref][pcs].values, clases)["f1"] - metr(real, por_art(lee_brazo("A", s))[0].loc[ref][pcs].values, clases)["f1"] for s in brazos["A"]]
    print("ΔF1 B − A por semilla:", [round(x, 3) for x in pares])
ba = difs["B - A"]["IC95"]["f1"]; bc = difs.get("B - C", {}).get("IC95", {}).get("f1")
if ba[0] > 0 and (bc is None or bc[0] > 0): veredicto = "B supera a A" + (" y al control C" if bc else " (sin control C)") + ": la mejora es distinguible del azar. Se informa con su magnitud."
elif ba[0] > 0: veredicto = "B supera a A pero NO al control C: la mejora no se atribuye a la información morfológica de NFFA."
else: veredicto = "NO CONCLUYENTE/MARGINAL: el IC de B − A incluye 0. Se informa como resultado nulo (el preentrenamiento morfológico externo no mejora de forma detectable con esta muestra)."
print("\nVEREDICTO:", veredicto)
(SUB["anal"] / "metricas_06.json").write_text(json.dumps({"articulos_comunes": int(len(ref)), "semillas": brazos, "tabla": filas, "diferencias": difs, "veredicto": veredicto, "criterio": "F1 macro por articulo, ensamble de semillas, IC95 bootstrap de articulos (2000); exito si B-A y B-C excluyen 0"}, indent=1))
filas_md = ["| " + " | ".join(map(str, r)) + " |" for r in [list(tabla.columns)] + tabla.values.tolist()]
(SUB["anal"] / "analisis_06.md").write_text("# Análisis 06\n\n" + "\n".join(filas_md) + "\n\n" + "\n".join(f"- {k}: ΔF1 {v['f1']:+.3f} IC95 {v['IC95']['f1']}" for k, v in difs.items()) + f"\n\n**Veredicto:** {veredicto}\n", encoding="utf-8")

# paquete pequeño para enviar a Claude (sin pesos ni puntos de control)
zp = SAL / "06_para_claude.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(SAL.rglob("*")):
        if p.is_file() and p.suffix in (".csv", ".json", ".md", ".jpg", ".txt") and p.stat().st_size < 30e6: z.write(p, p.relative_to(SAL))
print(f"\nPara enviar a Claude: {zp} ({zp.stat().st_size/1e6:.1f} MB). Los pesos quedan en:", [str(p.relative_to(BASE)) for p in SAL.rglob('backbone_dinov2.pt')])
print("tiempo total de sesión: %.0f min" % ((time.time() - T_INICIO) / 60))
''')

# ------------------------------------------------------------------ escribir
for tipo, tx in celdas:
    if tipo == "code":
        ast.parse(tx)                                             # sintaxis valida
nuevo = {"cells": [], "metadata": nb04["metadata"], "nbformat": nb04["nbformat"], "nbformat_minor": nb04["nbformat_minor"]}
for tipo, tx in celdas:
    c = {"cell_type": tipo, "metadata": {}, "source": tx.splitlines(keepends=True)}
    if tipo == "code":
        c["outputs"] = []; c["execution_count"] = None
    nuevo["cells"].append(c)
ruta = D / "06_preentrenamiento_nffa.ipynb"
ruta.write_text(json.dumps(nuevo, ensure_ascii=False, indent=1), encoding="utf-8")
print("cuaderno 06 escrito:", len(celdas), "celdas;", sum(t == "code" for t, _ in celdas), "de código con sintaxis OK ->", ruta)
