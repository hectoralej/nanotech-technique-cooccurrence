# Progreso del Atlas Nano2Predict

**24 de octubre de 2026 · corte local en `main`**

## Fuente y datos

El checkout se sincronizó con `origin/main` en `de48aa7`. Se ejecutó `python web/build_data.py` desde `producto/`. La selección contiene solo E1/E2: **1.707 artículos, 2.726 paneles, 3.116 descriptores y 4.015 espectros**. No se subieron cambios: el trabajo de esta sesión sigue local, sin commit ni push.

## Cambios cerrados

- Categorías visibles `Nanomaterial` y `Nanoportador`.
- Panel del modelo con exactitud, exactitud balanceada, F1 macro, línea base y nota del JSON real.
- Página `modelos.html` con escalera tabular y métricas de imagen. Las tres líneas base están correctamente resaltadas.
- Página `construccion.html` con D1–D8 y enlaces a evidencias. El texto editorial de Bryan no estaba en `producto/web_contenido/`; queda pendiente sustituir el esqueleto cuando lo entregue.
- Créditos a Europe PMC, licencia/DOI por imagen y Kabré (CeNAT/CNCA) en el pie.
- Favicon agregado; evita el 404 que apareció en la primera ejecución de QA.
- Guion en 2:30 con un ejemplo coincidente y uno discrepante. Ambos se presentan como exploratorios.
- Las imágenes locales no se subieron a Git. `descargas.csv` registra las 44 figuras no disponibles de 30 PMCID.

## QA automatizado en Chrome

Se ejecutó Chrome mediante Playwright en 1365×900 y 375×812. Se recorrieron la portada, una ficha con imágenes y predicción, el ejemplo con predicción distinta, una ficha sin imagen, la página de modelos y la de construcción.

- Cero errores de consola y cero respuestas fallidas/HTTP ≥400 al final del QA.
- Cero imágenes rotas en la ficha probada; los 2.669 paneles marcados `imagen_local=true` apuntan a archivos existentes.
- PMC12703698 muestra el marcador de imagen no descargada y conserva el enlace DOI.
- Categorías correctas y tres filas de línea base visibles.
- En viewport móvil, el documento mide 375 px, igual que el viewport: no hay desbordamiento horizontal. El espacio bajo el buscador se limita al rótulo y a la separación de cuadrícula; no se observó el hueco grande reportado.
- Capturas guardadas en `producto/web/capturas/`: portada laptop, dos fichas con imagen/predicción, una ficha sin imagen, móvil 375 px, modelos y construcción.
- `node --check` pasa para `app.js` y `modelos.js`; `python -m py_compile producto/web/build_data.py` pasa.

La revisión fue automatizada y visual sobre Chrome headless; no equivale a inspección humana en el equipo final ni a un ensayo de presentación.

## Pendientes

1. Recibir e integrar los textos editoriales de Bryan.
2. Hacer dos ensayos humanos cronometrados; ajustar el guion si supera 2:30.
3. Congelar la web después del ensayo y grabar la demo en 1920×1080.
4. Transferir el ZIP preparado a Héctor. No hay envío remoto realizado.
5. Pasar aparte `imagenes_v0.1.zip` (2.149 JPG, 273,7 MB) para que la copia del receptor pueda mostrar las figuras locales.

El ZIP actualizado está en `entrega/Atlas_traspaso_2026-10-24_QA.zip`. Contiene el código web, datos generados, JSON reales del modelo, métricas tabulares, informe y capturas; omite los JPG.
