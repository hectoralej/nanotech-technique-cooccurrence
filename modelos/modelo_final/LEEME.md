# Modelo final de Nano2Predict (v1.0, hackatón 2026)

Clasifica un **recorte de micrografía de partículas** en 4 clases de portador (inorgánico, lipídico, nanomaterial, polimérico). **DINOv2 ViT-S/14** (LVD-142M) con ajuste fino completo; **ensamble de 3 semillas** entrenado con los 4.670 recortes. Cuaderno: `modelos/kabre/05_modelo_final_onnx.ipynb` (se genera con `crear_cuaderno_05.py`). Sin preentrenamiento NFFA (no mejoró, ver `modelos/comparacion/ANALISIS_06_NFFA.md`).

## Qué hay aquí y qué no
| Ruta | Contenido |
|---|---|
| `02_onnx/clases.json`, `preprocesado.json`, `modelo_card.json` | Orden de las clases, contrato de entrada/salida y ficha del modelo |
| `03_verificacion/` | 20 entradas ya preprocesadas (PNG), `verificacion_onnx.csv` (salida esperada de PyTorch, ONNX fp32 e int8) y `resumen_verificacion.json` |
| `01_entrenamiento/` | Métricas de entrenamiento por semilla y diagnóstico del nodo de Kabré |
| `SHA256_onnx.txt` | Huellas de los ONNX, para comprobar la descarga |
| **Los archivos `.onnx` NO están en Git** | Van como *asset* de la release **`modelo-v1.0`** del repositorio (67 MB el ensamble, 22 MB la semilla sola) |

Para usarlos: descarga `ensamble3_int8.onnx` de la release, compara su SHA-256 con `SHA256_onnx.txt` y cópialo a `producto/modelo_onnx/02_onnx/`.

## Contrato
Entrada `imagen` float32 `[N,3,256,256]`, valores 0–255, RGB (NCHW): recorte rellenado a cuadrado con blanco, centrado, y reducido a 256×256 (suavizado alto); sin normalizar. El modelo reduce a 224 y normaliza por dentro. Salida `probabilidades` `[N,4]` (media de las 3 redes) en el orden de `clases.json`.

## Verificación (200 recortes, solo equivalencia entre formatos)
ONNX fp32 contra PyTorch: diferencia máxima 3e-6, misma clase en el 100 %. ONNX int8 (ensamble): diferencia media 0,008, máxima 0,060, misma clase en el 98,5 %. Los recortes eran de entrenamiento: **no miden desempeño**.

## Desempeño de referencia (la única estimación honesta)
Validación cruzada por artículo del brazo A del cuaderno 06 (1.114 artículos, 5 particiones, ensamble de 3 semillas): **exactitud 0,561 y F1 macro 0,521**, frente a 0,442 de exactitud de la clase mayoritaria. Resultados exploratorios; las probabilidades no están calibradas.

## Limitaciones
Solo micrografías de partículas (TEM/SEM/AFM/cryo): con espectros, gráficas, células o tejido la salida no significa nada. La etiqueta de entrenamiento es la clase del **artículo**, no la del recorte. La clase «nanomaterial» es una categoría general. Sin validación externa.
