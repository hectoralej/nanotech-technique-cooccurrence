# ¿Presentación como página web o como app? Evaluación (versión 3, 24 de octubre)

**Decisión: página web estática (HTML + CSS + JS, sin servidor ni dependencias). Se descarta la app de escritorio.** Lo que cambió desde la primera evaluación (23 de octubre): la demo **«sube tu micrografía» ya no es trabajo futuro**: corre dentro de la página web, en el navegador, con ONNX.

## Por qué una web y no una app
1. **El jurado ve un video de 10 minutos.** Una página se abre en un clic; una app hay que instalarla.
2. **Todo corre en el navegador.** El modelo final exportado a ONNX se ejecuta en el navegador con ONNX Runtime Web: no hace falta PyTorch (≈ 506 MB medidos en este equipo), ni Python, ni servidor. Una app de escritorio no añadiría nada y pesaría más de 1 GB.
3. **Sin conexión y sin librerías externas** en la presentación; se puede alojar tal cual en un sitio estático (lo decide Héctor).

## La demo «sube tu micrografía» (hecha por Carlos)
Fuentes: `modelos/modelo_final/LEEME.md`, `02_onnx/modelo_card.json` y `03_verificacion/`.

| Pieza | Dato |
|---|---|
| Modelo | DINOv2 ViT-S/14 con ajuste fino completo, **ensamble de 3 semillas**, entrenado con 4.670 recortes de 1.114 artículos |
| Archivos | `ensamble3_int8.onnx` (67.151.951 bytes; el que usa la demo) y `semilla0_int8.onnx` (22.385.726 bytes), en la **Release `modelo-v1.0`** (no van en Git). Se comprueban con SHA-256 (`SHA256_onnx.txt`) |
| Entrada | `imagen` float32 `[N,3,256,256]`, 0–255, RGB; el recorte se rellena a cuadrado con blanco y se reduce a 256×256; sin normalizar |
| Salida | `probabilidades` `[N,4]` (media de las 3 redes) en el orden inorgánico, lipídico, nanomaterial, polimérico |
| Equivalencia entre formatos | ONNX fp32 contra PyTorch: diferencia máxima 3e-6 (misma clase 100 %). int8: diferencia media 0,008 y misma clase en el 98,5 % de 200 recortes. En la demo: 20 de 20 entradas, diferencia media 0,0051 |
| Desempeño de referencia | Validación cruzada por artículo, ensamble de 3 semillas, 1.114 artículos: **exactitud 0,561 y F1 macro 0,521**, frente a 0,442 de la clase mayoritaria. El modelo final se entrenó con todos los datos: no se puede evaluar; esa es la única estimación honesta |

**Advertencias que acompañan a la demo** (también en la presentación, en «Modelo final» y «Limitaciones»):
- Solo sirve para **micrografías de partículas** (TEM, SEM, AFM, cryo): con espectros, gráficas, células o tejido la salida no significa nada.
- Las **probabilidades no están calibradas** (`modelos/REVISION_CRITICA.md`, punto 8).
- La etiqueta es la **clase del artículo**, no la de la partícula ni la del recorte; «nanomaterial» es una categoría general.
- Resultado exploratorio, sin validación externa.

**Lo que esta evaluación no comprobó:** yo no abrí la demo (la web de Carlos con la demo y la vista «Figuras y paneles» no estaba en `main` cuando se redactó esto). Las cifras de verificación son las de la ficha del modelo. Antes de grabar hay que probar la demo en el navegador y revisar la narración contra ella.
