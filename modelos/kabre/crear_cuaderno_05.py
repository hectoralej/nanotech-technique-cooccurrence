"""Genera 05_modelo_final_onnx.ipynb: entrena el modelo final (DINOv2 ViT-S/14 desde LVD, 3 semillas, TODOS los recortes), lo exporta a ONNX (ensamble de 3 modelos, fp32 e int8)
y comprueba que ONNX da lo mismo que PyTorch. Misma receta que los cuadernos 04 y 06 (brazo A del 06: sin NFFA, que no mejoro).
Uso: python modelos/kabre/crear_cuaderno_05.py
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


md("""
# 05 · Modelo final (DINOv2, ensamble de 3 semillas) y exportación a ONNX para el navegador

**Qué produce:** el modelo que usará la web: clasifica un recorte de micrografía de partículas en 4 clases de portador (inorgánico, lipídico, nanomaterial, polimérico). Se entrena con **todos** los recortes (4.670), se exporta a **ONNX** (opset 17) en fp32 e int8, y se comprueba que ONNX coincide con PyTorch.

**Decisión de diseño (cuaderno 06):** DINOv2 desde su preentrenamiento general (LVD-142M), **sin NFFA** (no mejoró: B − A = −0,019 de F1 macro, IC [−0,042, +0,005]) y con **ensamble de 3 semillas** (+0,013 de exactitud y +0,016 de F1 macro frente a una sola semilla, en validación cruzada por artículo). Referencia de validación cruzada por artículo del brazo A (1.114 artículos): exactitud 0,561, F1 macro 0,521 con el ensamble. **El modelo final no se puede evaluar** (usa todos los datos): esa referencia es la única estimación honesta de su desempeño.

**Dónde correrlo:** Jupyter en `nukwa-l40s` (o `nukwa-v100`), 1 nodo, 4 núcleos, 16 GB, **1 h** bastan (entrenamiento ≈ 6–10 min; exportación y verificación ≈ 5–10 min: estimaciones). Kernel `Python-ML-DL`. La exportación y la verificación corren en CPU.

**Rutas (desde `BASE = ~/ondemand/Kabre_Nano2Predict`, o la variable `N2P_BASE`):**
| Qué | Dónde |
|---|---|
| Recortes (ya subidos para el 04/06) | `BASE/recortes/` y `BASE/datos/indice_recortes_entrenamiento.csv` (si falta, se descomprime `recortes_v02.zip`) |
| **Todo lo que produce este cuaderno** | `BASE/resultados/05_modelo_final/` |
| Para la web | `BASE/resultados/05_modelo_final/05_para_web.zip` (ONNX int8 + JSON + entradas de prueba, ≈ 90 MB) |
| Para enviar a Claude | `BASE/resultados/05_modelo_final/05_para_claude.zip` (sin pesos ni ONNX, pocos MB) |

**Estructura de resultados**
```
05_modelo_final/
  00_diagnostico/     nodo, GPU, versiones, disco
  01_entrenamiento/   metricas_entrenamiento.json (una entrada por semilla)
  pesos/              modelo_semilla0.pt, modelo_semilla1.pt, modelo_semilla2.pt  (PyTorch)
  02_onnx/            ensamble3_fp32.onnx, ensamble3_int8.onnx, semilla0_int8.onnx, clases.json, preprocesado.json, modelo_card.json
  03_verificacion/    entradas/*.png (20 recortes ya preprocesados), verificacion_onnx.csv, resumen_verificacion.json
  05_para_web.zip     05_para_claude.zip
```

**Contrato del modelo ONNX (lo que necesita Carlos):** entrada `imagen` float32 `[N,3,256,256]`, valores 0–255, RGB; el recorte se rellena a cuadrado con blanco, centrado, y se reduce a 256×256. **Dentro del modelo** se reduce a 224 (bilineal) y se normaliza. Salida `probabilidades` `[N,4]` (media de las 3 semillas) en el orden de `clases.json`. Los 20 PNG de `03_verificacion/entradas/` son entradas ya preprocesadas con su salida esperada en `verificacion_onnx.csv`: sirven para comprobar el preprocesado en JavaScript.
""")

# ------------------------------------------------------------------ etapa 0
md("## ETAPA 0 · Diagnóstico y dependencias\n\n" + cuadro(
    "Comprueba GPU, disco y versiones; instala `onnx` y `onnxruntime` en tu usuario si faltan (los nodos alcanzan pypi.org); crea las carpetas de resultados.",
    "≈ 1 min (hasta 3 si instala paquetes). Imprime versiones de torch, timm, onnx y onnxruntime.",
    "Hay GPU, ambas librerías ONNX importan y hay > 2 GB libres.",
    "Si `pip` falla, avisa a Claude con el mensaje; sin ONNX solo se puede entrenar (etapas 1–2) y exportar después."))
cod(r'''
# ETAPA 0: diagnóstico y dependencias
import os, sys, json, time, math, random, socket, shutil, zipfile, subprocess, importlib
from pathlib import Path
T_INICIO = time.time()
SESION_HORAS = 1                              # horas pedidas a Slurm
TIEMPO_MAX_MIN = SESION_HORAS * 60 - 10       # el entrenamiento se detiene solo aquí; se puede volver a ejecutar y retoma

BASE = Path(os.environ.get("N2P_BASE", Path.home() / "ondemand" / "Kabre_Nano2Predict"))
assert BASE.exists(), f"No existe {BASE}. Define N2P_BASE o sube la carpeta Kabre_Nano2Predict a ~/ondemand/"
RES_RAIZ = next((p for p in (BASE / "resultados", BASE / "Resultados") if p.exists()), BASE / "resultados")
DATOS = BASE / "datos"
SAL = RES_RAIZ / "05_modelo_final"
SUB = {k: SAL / v for k, v in {"diag": "00_diagnostico", "entr": "01_entrenamiento", "pesos": "pesos", "onnx": "02_onnx", "ver": "03_verificacion"}.items()}
for p in SUB.values(): p.mkdir(parents=True, exist_ok=True)
(SUB["ver"] / "entradas").mkdir(exist_ok=True)
print("BASE      :", BASE); print("RESULTADOS:", SAL)

def asegurar(modulo, paquete):
    try:
        return importlib.import_module(modulo)
    except ImportError:
        print(f"instalando {paquete} ...", flush=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", "-q", paquete], check=True)
        importlib.invalidate_caches(); return importlib.import_module(modulo)

import numpy as np, pandas as pd, torch, timm
assert torch.cuda.is_available(), "No hay GPU: pide una cola nukwa-* y usa el kernel Python-ML-DL"
dev = "cuda"
onnx = asegurar("onnx", "onnx"); ort = asegurar("onnxruntime", "onnxruntime")
asignados = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()
libre_gb = shutil.disk_usage(BASE).free / 1e9
diag = {"nodo": socket.gethostname(), "gpu": torch.cuda.get_device_name(0), "nucleos": asignados, "disco_libre_gb": round(libre_gb, 1),
        "torch": torch.__version__, "timm": timm.__version__, "onnx": onnx.__version__, "onnxruntime": ort.__version__}
print(diag)
print("\nVEREDICTO ETAPA 0:", "OK, sigue" if libre_gb > 2 else "REVISA el disco")
(SUB["diag"] / "diagnostico.json").write_text(json.dumps(diag, indent=2), encoding="utf-8")
''')

# ------------------------------------------------------------------ funciones comunes
md("### Funciones comunes (no hace nada visible; define aumentos, modelo y entrenamiento: la misma receta del 04/06)")
cod(r'''
# FUNCIONES COMUNES
import torch.nn as nn, torch.nn.functional as F
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
torch.backends.cudnn.benchmark = True
TAM, LADO, DROP_PATH = 224, 256, 0.1
MODELO = "vit_small_patch14_dinov2.lvd142m"
os.environ.setdefault("HF_HOME", str(BASE / "hf_cache"))
MEDIA = torch.tensor([0.485, 0.456, 0.406], device=dev).view(1, 3, 1, 1) * 255
DESV = torch.tensor([0.229, 0.224, 0.225], device=dev).view(1, 3, 1, 1) * 255

def lote_train(X, idx):                                        # recorte aleatorio 70-100 % + espejo, en GPU
    xb, out = X[idx], []
    for i in range(xb.shape[0]):
        s = random.uniform(0.7, 1.0); c = int(LADO * math.sqrt(s))
        x0, y0 = random.randint(0, LADO - c), random.randint(0, LADO - c)
        im = F.interpolate(xb[i:i + 1, :, y0:y0 + c, x0:x0 + c].float(), size=(TAM, TAM), mode="bilinear", align_corners=False)
        out.append(im.flip(3) if random.random() < 0.5 else im)
    return (torch.cat(out) - MEDIA) / DESV

def crear(n_clases):
    return timm.create_model(MODELO, pretrained=True, num_classes=n_clases, img_size=TAM, drop_path_rate=DROP_PATH).to(dev)

def ajustar(m, X, y, tr, epocas, lr, ckpt, semilla, n_clases, bs=32, nombre=""):
    random.seed(semilla); np.random.seed(semilla); torch.manual_seed(semilla)
    ids_cab = {id(p) for p in m.get_classifier().parameters()}
    bb = [p for p in m.parameters() if id(p) not in ids_cab]; cab = [p for p in m.parameters() if id(p) in ids_cab]
    opt = torch.optim.AdamW([{"params": bb, "lr": lr}, {"params": cab, "lr": lr * 10}], weight_decay=0.05)
    pasos_ep = len(tr) // bs
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=[lr, lr * 10], total_steps=epocas * pasos_ep, pct_start=0.15)
    frec = np.bincount(y[tr].cpu().numpy(), minlength=n_clases).clip(min=1)
    w = torch.tensor((frec.sum() / (n_clases * frec)) ** 0.5, dtype=torch.float32, device=dev)
    crit = nn.CrossEntropyLoss(weight=w, label_smoothing=0.1)
    scaler = torch.cuda.amp.GradScaler(); ep0 = 0; ult = {}
    if ckpt.exists():
        try:
            s = torch.load(ckpt, map_location=dev)
            m.load_state_dict(s["m"]); opt.load_state_dict(s["opt"]); sched.load_state_dict(s["sched"]); scaler.load_state_dict(s["scaler"]); ep0 = s["ep"] + 1
            print(f"  reanudando {nombre} desde la época {ep0}")
        except Exception as e:                         # punto de control corrupto (una corrida anterior se cortó al guardarlo): se descarta y se empieza de cero
            print(f"  punto de control corrupto ({type(e).__name__}); se borra y se empieza {nombre} desde la época 0"); ckpt.unlink(missing_ok=True)
            random.seed(semilla); np.random.seed(semilla); torch.manual_seed(semilla)
    for ep in range(ep0, epocas):
        m.train(); perm = np.random.permutation(tr); perd = ok = n = 0
        for i in range(pasos_ep):
            idx = torch.tensor(perm[i * bs:(i + 1) * bs], device=dev)
            with torch.autocast("cuda", dtype=torch.float16):
                lo = m(lote_train(X, idx)); loss = crit(lo, y[idx])
            opt.zero_grad(set_to_none=True); scaler.scale(loss).backward(); scaler.step(opt); scaler.update(); sched.step()
            perd += float(loss) * len(idx); ok += int((lo.argmax(1) == y[idx]).sum()); n += len(idx)
        ult = {"epoca": ep + 1, "perdida": round(perd / n, 4), "acierto_entrenamiento": round(ok / n, 4)}
        print(f"  {nombre} época {ep+1}/{epocas}: pérdida {perd/n:.3f} | acierto de entrenamiento {ok/n:.3f} | {(time.time()-T_INICIO)/60:.1f} min desde el inicio", flush=True)
        tmp = ckpt.with_suffix(".tmp")                 # guardado atómico: si se corta a mitad, el punto de control anterior sigue intacto
        torch.save({"m": m.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(), "scaler": scaler.state_dict(), "ep": ep}, tmp); os.replace(tmp, ckpt)
    return m, ult

def cargar_jpg(ruta):                       # el MISMO preprocesado que debe hacer la web: rellenar a cuadrado (blanco), centrado, y reducir a 256x256 (bicúbico)
    im = Image.open(ruta).convert("RGB"); w, h = im.size; l = max(w, h)
    lienzo = Image.new("RGB", (l, l), (255, 255, 255)); lienzo.paste(im, ((l - w) // 2, (l - h) // 2))
    return np.asarray(lienzo.resize((LADO, LADO), Image.BICUBIC), dtype=np.uint8)
print("OK funciones comunes")
''')

# ------------------------------------------------------------------ etapa 1 datos
md("## ETAPA 1 · Datos: todos los recortes\n\n" + cuadro(
    "Carga los 4.670 recortes de micrografía de partículas con clase de portador (descomprime `recortes_v02.zip` solo si hace falta) y los pasa a la GPU. **Se usan todos para entrenar** (sin partición de prueba).",
    "≈ 1 min. Imprime recortes, artículos, clases y su distribución.",
    "≈ 4.670 recortes, ≈ 1.114 artículos y 4 clases.",
    "Faltan recortes: sube/descomprime `recortes_v02.zip` en `BASE` (como en el 04)."))
cod(r'''
# ETAPA 1: datos
ZIP = next((z for z in (BASE / "recortes_v02.zip", DATOS / "recortes_v02.zip", BASE / "subir_a_kabre" / "recortes_v02.zip") if z.exists()), None) or next(iter(sorted(BASE.rglob("recortes_v02.zip"))), None)
REC = BASE / "recortes"
if not REC.exists() and ZIP is not None:
    DATOS.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP) as z: z.extractall(BASE)
    (BASE / "indice_recortes_entrenamiento.csv").replace(DATOS / "indice_recortes_entrenamiento.csv"); print("recortes descomprimidos en", REC)
t = pd.read_csv(DATOS / "indice_recortes_entrenamiento.csv", encoding="utf-8-sig", dtype=str)
t["ruta"] = t.apply(lambda r: REC / str(r["pmcid"]) / str(r["image_file"]), axis=1)
d = t[t.ruta.map(lambda p: p.exists()) & t.clase_modelo.notna()].reset_index(drop=True)
assert len(d) > 1000, "faltan recortes: sube y descomprime recortes_v02.zip"
clases = sorted(set(d.clase_modelo)); cidx = {c: i for i, c in enumerate(clases)}
yi = np.array([cidx[c] for c in d.clase_modelo]); yg = torch.tensor(yi, device=dev)
print(f"recortes: {len(d)} | artículos: {d.pmcid.nunique()} | clases: {clases} | por clase: {d.clase_modelo.value_counts().to_dict()}")
t0 = time.time()
with ThreadPoolExecutor(max_workers=max(2, asignados)) as ex:
    Xcpu = np.stack(list(ex.map(cargar_jpg, [str(p) for p in d.ruta])))          # [N,256,256,3] uint8: se conserva para la verificación
Xg = torch.from_numpy(Xcpu).permute(0, 3, 1, 2).contiguous().to(dev)
print(f"recortes en la GPU: {tuple(Xg.shape)} ({time.time()-t0:.0f}s)")
''')

# ------------------------------------------------------------------ etapa 2 entrenamiento
md("## ETAPA 2 · Entrenar 3 modelos (semillas 0, 1, 2) con todos los recortes\n\n" + cuadro(
    "Ajuste fino de DINOv2 ViT-S/14 (desde LVD) con todos los recortes, 10 épocas, la receta del 04/06; guarda los pesos de cada semilla. Es reanudable por época y por semilla.",
    "≈ 2–3 min por semilla (estimación: 4.670 recortes en vez de 3.700 por partición). El acierto de **entrenamiento** subirá mucho (el 04 mostraba sobreajuste); eso NO mide el desempeño real.",
    "Las 3 semillas terminan y las pérdidas bajan sin `nan`.",
    "Se corta por tiempo: vuelve a ejecutar la celda (retoma). Pérdida `nan`: avisa a Claude."))
cod(r'''
# ETAPA 2: entrenar las 3 semillas
EPOCAS, LR, SEMILLAS = 10, 3e-5, [0, 1, 2]
mret = SUB["entr"] / "metricas_entrenamiento.json"
registro = json.loads(mret.read_text()) if mret.exists() else {}
todos = np.arange(len(d))
for s in SEMILLAS:
    peso = SUB["pesos"] / f"modelo_semilla{s}.pt"
    if peso.exists(): print(f"semilla {s}: ya entrenada"); continue
    if (time.time() - T_INICIO) / 60 > TIEMPO_MAX_MIN:
        print(f"\nLímite de tiempo ({TIEMPO_MAX_MIN} min). Vuelve a ejecutar esta celda: retoma donde quedó."); break
    t1 = time.time(); m = crear(len(clases))
    m, ult = ajustar(m, Xg, yg, todos, EPOCAS, LR, SUB["pesos"] / f"ckpt_s{s}.pt", s * 100, len(clases), nombre=f"semilla {s}")
    torch.save({k: v.cpu() for k, v in m.state_dict().items()}, peso)
    (SUB["pesos"] / f"ckpt_s{s}.pt").unlink(missing_ok=True)
    registro[str(s)] = {**ult, "segundos": round(time.time() - t1), "recortes": int(len(d)), "epocas": EPOCAS, "lr": LR, "peso_mb": round(peso.stat().st_size / 1e6, 1)}
    mret.write_text(json.dumps(registro, indent=1)); print(f"== semilla {s} lista en {time.time()-t1:.0f}s | {registro[str(s)]}\n", flush=True)
    del m; torch.cuda.empty_cache()
print("pesos:", sorted(p.name for p in SUB["pesos"].glob("modelo_semilla*.pt")))
''')

# ------------------------------------------------------------------ etapa 3 export
md("## ETAPA 3 · Exportar a ONNX (fp32 e int8)\n\n" + cuadro(
    "Junta las 3 semillas en **un solo modelo** que reduce a 224, normaliza, promedia las probabilidades de las 3 redes y devuelve `[N,4]`; lo exporta a ONNX (opset 17, lote variable) y lo cuantiza a int8 (dinámico, UInt8). También exporta la semilla 0 sola en int8, como versión ligera.",
    "≈ 2–5 min en CPU. Tamaños aproximados (estimación): fp32 ≈ 260 MB el ensamble; int8 ≈ 65 MB el ensamble y ≈ 22 MB la semilla sola.",
    "Se crean los 3 archivos `.onnx` y `onnx.checker` no da errores.",
    "Falla el exportador: se prueba solo la ruta alternativa (dynamo); si también falla, copia el mensaje completo a Claude. La cuantización puede avisar de formas (`shape inference`): son avisos."))
cod(r'''
# ETAPA 3: exportar a ONNX
from onnxruntime.quantization import quantize_dynamic, QuantType
pesos_ok = [SUB["pesos"] / f"modelo_semilla{s}.pt" for s in SEMILLAS]
assert all(p.exists() for p in pesos_ok), "faltan pesos: ejecuta la etapa 2 completa"
torch.cuda.empty_cache()

class Envoltorio(nn.Module):
    """entrada: float32 [N,3,256,256] en 0-255 (RGB, ya rellenada a cuadrado). Reduce a 224, normaliza, promedia softmax de los modelos."""
    def __init__(self, modelos):
        super().__init__(); self.ms = nn.ModuleList(modelos)
        self.register_buffer("media", torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1) * 255)
        self.register_buffer("desv", torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1) * 255)
    def forward(self, x):
        x = F.interpolate(x, size=(TAM, TAM), mode="bilinear", align_corners=False)
        x = (x - self.media) / self.desv
        return torch.stack([torch.softmax(m(x), dim=1) for m in self.ms]).mean(0)

def cargar_cpu(ruta):
    m = timm.create_model(MODELO, pretrained=False, num_classes=len(clases), img_size=TAM)
    m.load_state_dict(torch.load(ruta, map_location="cpu")); return m.float().eval()

def exportar(modelos, ruta):
    env = Envoltorio(modelos).eval(); x = torch.zeros(2, 3, LADO, LADO)
    kw = dict(opset_version=17, input_names=["imagen"], output_names=["probabilidades"], dynamic_axes={"imagen": {0: "lote"}, "probabilidades": {0: "lote"}})
    with torch.no_grad():
        try:
            torch.onnx.export(env, x, str(ruta), dynamo=False, **kw)         # exportador clásico (torch >= 2.5)
        except TypeError:
            torch.onnx.export(env, x, str(ruta), **kw)                        # torch más antiguo
    onnx.checker.check_model(onnx.load(str(ruta)))
    return env

def cuantizar(fp32, int8):
    try:
        from onnxruntime.quantization.shape_inference import quant_pre_process
        pre = fp32.with_name(fp32.stem + "_pre.onnx"); quant_pre_process(str(fp32), str(pre)); origen = pre
    except Exception as e:
        print("  (sin preprocesado de cuantización:", type(e).__name__, ")"); origen = fp32
    quantize_dynamic(str(origen), str(int8), weight_type=QuantType.QUInt8)
    if origen != fp32: origen.unlink(missing_ok=True)

mods = [cargar_cpu(p) for p in pesos_ok]
t0 = time.time()
env3 = exportar(mods, SUB["onnx"] / "ensamble3_fp32.onnx"); print(f"ensamble fp32 exportado ({time.time()-t0:.0f}s)")
cuantizar(SUB["onnx"] / "ensamble3_fp32.onnx", SUB["onnx"] / "ensamble3_int8.onnx"); print(f"ensamble int8 listo ({time.time()-t0:.0f}s)")
exportar(mods[:1], SUB["onnx"] / "semilla0_fp32.onnx")
cuantizar(SUB["onnx"] / "semilla0_fp32.onnx", SUB["onnx"] / "semilla0_int8.onnx"); (SUB["onnx"] / "semilla0_fp32.onnx").unlink(missing_ok=True)
(SUB["onnx"] / "clases.json").write_text(json.dumps(clases, ensure_ascii=False), encoding="utf-8")
(SUB["onnx"] / "preprocesado.json").write_text(json.dumps({
    "entrada": {"nombre": "imagen", "tipo": "float32", "forma": ["N", 3, LADO, LADO], "rango": "0-255", "canales": "RGB, orden NCHW"},
    "preprocesado_en_el_navegador": "dibujar el recorte centrado sobre un lienzo cuadrado BLANCO (lado = max(ancho, alto)) y reducir a 256x256 con suavizado alto (imageSmoothingQuality='high'); NO normalizar",
    "dentro_del_modelo": ["reduccion bilineal a 224x224", "normalizacion media=[0.485,0.456,0.406]*255, desv=[0.229,0.224,0.225]*255", "softmax y media de las redes"],
    "salida": {"nombre": "probabilidades", "forma": ["N", len(clases)], "clases": clases}}, indent=2, ensure_ascii=False), encoding="utf-8")
for p in sorted(SUB["onnx"].glob("*.onnx")): print(f"  {p.name}: {p.stat().st_size/1e6:.1f} MB")
''')

# ------------------------------------------------------------------ etapa 4 verificacion
md("## ETAPA 4 · Verificar que ONNX = PyTorch\n\n" + cuadro(
    "Toma 200 recortes (50 por clase, semilla fija) y compara las probabilidades del ensamble en **PyTorch (CPU)**, **ONNX fp32** y **ONNX int8**; guarda 20 entradas ya preprocesadas (PNG) con su salida esperada para probar el preprocesado en JavaScript, y mide el tiempo por imagen en CPU.",
    "≈ 2–4 min. Imprime diferencia máxima, coincidencia de la clase predicha y tiempo por imagen. Estos recortes son de **entrenamiento**: la exactitud contra la etiqueta no vale como desempeño; solo se comprueba equivalencia.",
    "fp32: diferencia máxima < 1e-3 y 100 % de coincidencia. int8: ≥ 95 % de coincidencia y diferencia media < 0,03.",
    "Si fp32 falla: no usar ese ONNX y avisa a Claude. Si solo falla int8: usar fp32 (≈ 260 MB, fuera de Git) o la semilla sola; la web debe decir qué versión usa."))
cod(r'''
# ETAPA 4: verificación
rng = np.random.default_rng(5)
sel = np.concatenate([rng.choice(np.where(yi == j)[0], min(50, int((yi == j).sum())), replace=False) for j in range(len(clases))])
primeras = np.concatenate([sel[yi[sel] == j][:5] for j in range(len(clases))])           # 5 por clase = 20 entradas guardadas
X = Xcpu[sel].astype(np.float32).transpose(0, 3, 1, 2)                                 # [n,3,256,256] 0-255

def por_lotes(f, X, bs=16): return np.concatenate([f(X[i:i + bs]) for i in range(0, len(X), bs)])
with torch.no_grad(): P_t = por_lotes(lambda b: env3(torch.from_numpy(b)).numpy(), X)
def sesion(nombre):
    so = ort.SessionOptions(); so.intra_op_num_threads = max(1, asignados)
    return ort.InferenceSession(str(SUB["onnx"] / nombre), so, providers=["CPUExecutionProvider"])
res = {"n_recortes": int(len(sel)), "nota": "recortes de entrenamiento: solo se mide equivalencia entre formatos, no desempeño"}
sal_onnx = {}
for nombre in ("ensamble3_fp32.onnx", "ensamble3_int8.onnx", "semilla0_int8.onnx"):
    s = sesion(nombre); t0 = time.time(); P = por_lotes(lambda b: s.run(None, {"imagen": b})[0], X); seg = (time.time() - t0) / len(X); sal_onnx[nombre] = P
    ref = P_t if "ensamble" in nombre else None
    if ref is None:                                                                      # la semilla sola se compara con su propia salida PyTorch
        m0 = Envoltorio(mods[:1]).eval()
        with torch.no_grad(): ref = por_lotes(lambda b: m0(torch.from_numpy(b)).numpy(), X)
    res[nombre] = {"dif_max": round(float(np.abs(P - ref).max()), 6), "dif_media": round(float(np.abs(P - ref).mean()), 6),
                   "coincide_clase": round(float((P.argmax(1) == ref.argmax(1)).mean()), 4), "segundos_por_imagen_cpu": round(seg, 3),
                   "tamano_mb": round((SUB["onnx"] / nombre).stat().st_size / 1e6, 1)}
    print(nombre, res[nombre])
res["acierto_ensamble_pytorch_sobre_estos_recortes_de_entrenamiento"] = round(float((P_t.argmax(1) == yi[sel]).mean()), 4)
ok32 = res["ensamble3_fp32.onnx"]["dif_max"] < 1e-3 and res["ensamble3_fp32.onnx"]["coincide_clase"] == 1.0
ok8 = res["ensamble3_int8.onnx"]["coincide_clase"] >= 0.95 and res["ensamble3_int8.onnx"]["dif_media"] < 0.03
res["veredicto"] = {"fp32_ok": bool(ok32), "int8_ok": bool(ok8)}
print("\nVEREDICTO ETAPA 4: fp32", "OK" if ok32 else "FALLA", "| int8", "OK" if ok8 else "NO CUMPLE (usa fp32 o la semilla sola)")
# entradas de prueba para JavaScript
filas = []; pos = {int(i): k for k, i in enumerate(sel)}
for i in primeras:
    k = pos[int(i)]; nom = f"entrada_{len(filas):02d}_{d.clase_modelo[i]}.png"
    Image.fromarray(Xcpu[i]).save(SUB["ver"] / "entradas" / nom)
    filas.append({"archivo": nom, "recorte_original": f"{d.pmcid[i]}/{d.image_file[i]}", "clase_base": d.clase_modelo[i],
                  **{f"torch_{c}": round(float(P_t[k, j]), 5) for j, c in enumerate(clases)},
                  **{f"onnx_fp32_{c}": round(float(sal_onnx['ensamble3_fp32.onnx'][k, j]), 5) for j, c in enumerate(clases)},
                  **{f"onnx_int8_{c}": round(float(sal_onnx['ensamble3_int8.onnx'][k, j]), 5) for j, c in enumerate(clases)}})
pd.DataFrame(filas).to_csv(SUB["ver"] / "verificacion_onnx.csv", index=False)
(SUB["ver"] / "resumen_verificacion.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print("guardado:", SUB["ver"])
''')

# ------------------------------------------------------------------ etapa 5 paquetes
md("## ETAPA 5 · Ficha del modelo y paquetes\n\n" + cuadro(
    "Escribe `modelo_card.json` (qué es, cómo se entrenó, desempeño de referencia y limitaciones) y arma dos zips: `05_para_web.zip` (ONNX int8, JSON, entradas de prueba) y `05_para_claude.zip` (todo lo pequeño, sin pesos ni ONNX).",
    "≈ 1 min. `05_para_web.zip` ≈ 90 MB.",
    "Los dos zips existen y el veredicto de la etapa 4 fue OK.",
    "Si int8 no cumplió, el zip web trae solo lo que sí cumple y lo indica en `LEEME_WEB.txt`."))
cod(r'''
# ETAPA 5: ficha y paquetes
ref_06 = next(iter(RES_RAIZ.glob("06_nffa_dinov2/99_analisis/metricas_06.json")), None)
referencia = {}
if ref_06 is not None:
    j = json.loads(ref_06.read_text()); a = next(x for x in j["tabla"] if x["brazo"] == "A")
    referencia = {"fuente": "resultados/06_nffa_dinov2/99_analisis/metricas_06.json (brazo A)", "articulos": j["articulos_comunes"], "validacion": "5 particiones por artículo, ensamble de 3 semillas",
                  "exactitud": a["acc_ensamble"], "exactitud_balanceada": a["acc_bal_ensamble"], "f1_macro": a["f1_ensamble"], "linea_base_clase_mayoritaria_exactitud": "ver ANALISIS_04_RECORTES.md"}
card = {"nombre": "Nano2Predict · clase de portador desde un recorte de micrografía", "version": "1.0 (hackatón 2026)",
        "modelo": f"{MODELO} (DINOv2 ViT-S/14, LVD-142M) con ajuste fino completo; ensamble de {len(SEMILLAS)} semillas", "clases": clases,
        "entrenamiento": {"datos": f"{len(d)} recortes de panel de micrografía de partículas de {d.pmcid.nunique()} artículos CC BY (Europe PMC); la etiqueta es la clase del ARTÍCULO, no del recorte",
                          "epocas": EPOCAS, "lr_backbone": LR, "receta": "AdamW por capas, OneCycleLR, AMP, pesos de clase suavizados, label smoothing 0,1, drop_path 0,1, aumentos recorte 70-100 % y espejo",
                          "sin_NFFA": "el preentrenamiento intermedio con NFFA-EUROPE no mejoró (cuaderno 06)"},
        "desempeno_de_referencia_validacion_cruzada": referencia,
        "limitaciones": ["El modelo final se entrenó con todos los recortes: su desempeño real solo se estima con la validación cruzada de referencia (por artículo).",
                         "Resultados modestos y exploratorios; las probabilidades NO están calibradas.",
                         "Solo tiene sentido con micrografías de partículas (TEM/SEM/AFM/cryo): con espectros, gráficas, células o tejido la salida no significa nada.",
                         "La etiqueta de entrenamiento es la clase del artículo; una micrografía de otro estilo de laboratorio puede predecirse mal.",
                         "La clase «nanomaterial» es una categoría general (no nanoportador), la más frecuente."],
        "entrada_salida": json.loads((SUB["onnx"] / "preprocesado.json").read_text()), "onnx_opset": 17, "verificacion": res}
(SUB["onnx"] / "modelo_card.json").write_text(json.dumps(card, indent=2, ensure_ascii=False), encoding="utf-8")

web = ["ensamble3_int8.onnx", "semilla0_int8.onnx"] if ok8 else []
(SAL / "LEEME_WEB.txt").write_text("Contenido: ONNX int8 (" + (", ".join(web) or "ninguno: int8 no cumplió la verificación") + "), clases.json, preprocesado.json, modelo_card.json, entradas de prueba y verificacion_onnx.csv.\n"
    "Cargar con onnxruntime-web (WASM). Entrada 'imagen' float32 [N,3,256,256] 0-255; salida 'probabilidades' [N,4] (orden de clases.json). Comprobar el preprocesado con las PNG de 03_verificacion/entradas y las columnas onnx_int8_* de verificacion_onnx.csv.\n", encoding="utf-8")
with zipfile.ZipFile(SAL / "05_para_web.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for n in web: z.write(SUB["onnx"] / n, f"02_onnx/{n}")
    for n in ("clases.json", "preprocesado.json", "modelo_card.json"): z.write(SUB["onnx"] / n, f"02_onnx/{n}")
    for p in sorted(SUB["ver"].rglob("*")):
        if p.is_file(): z.write(p, p.relative_to(SAL))
    z.write(SAL / "LEEME_WEB.txt", "LEEME_WEB.txt")
with zipfile.ZipFile(SAL / "05_para_claude.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(SAL.rglob("*")):
        if p.is_file() and p.suffix in (".json", ".csv", ".txt", ".png") and p.stat().st_size < 30e6: z.write(p, p.relative_to(SAL))
for n in ("05_para_web.zip", "05_para_claude.zip"): print(f"{n}: {(SAL / n).stat().st_size/1e6:.1f} MB")
print("pesos PyTorch (no se envían, quedan en Kabré):", [str(p.relative_to(BASE)) for p in SUB["pesos"].glob("modelo_semilla*.pt")])
print("tiempo total de sesión: %.0f min" % ((time.time() - T_INICIO) / 60))
''')

for tipo, tx in celdas:
    if tipo == "code":
        ast.parse(tx)
nuevo = {"cells": [], "metadata": nb04["metadata"], "nbformat": nb04["nbformat"], "nbformat_minor": nb04["nbformat_minor"]}
for tipo, tx in celdas:
    c = {"cell_type": tipo, "metadata": {}, "source": tx.splitlines(keepends=True)}
    if tipo == "code":
        c["outputs"] = []; c["execution_count"] = None
    nuevo["cells"].append(c)
ruta = D / "05_modelo_final_onnx.ipynb"
ruta.write_text(json.dumps(nuevo, ensure_ascii=False, indent=1), encoding="utf-8")
print("cuaderno 05 escrito:", len(celdas), "celdas;", sum(t == "code" for t, _ in celdas), "de código con sintaxis OK ->", ruta)
