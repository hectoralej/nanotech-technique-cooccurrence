# Presentación interactiva de Nano2Predict

Página estática (sin servidor ni librerías externas) que acompaña al video. Una sección por bloque del guion (`video/GUION.md`).

## Cómo abrirla
```bash
python producto/presentacion/servir.py
```
Abre `http://localhost:8000/presentacion/` en el navegador. `servir.py` es un servidor sin caché: siempre se ve la versión actual. Si usas `python -m http.server 8000` desde `producto/`, el navegador puede guardar copias viejas de `app.js` y `estilo.css` y la página se ve rota o incompleta tras una actualización: en ese caso recarga con `Ctrl+F5` (o `Ctrl+Mayús+R`). También funciona abriendo `index.html` con doble clic (los datos van en `datos.js`); solo la vista previa del Atlas necesita el servidor.

**Teclas:** `←` `→` cambian de sección · `Inicio`/`Fin` · `P` modo presentar (letra más grande) · `F` pantalla completa.

## Secciones y bloques del guion
| # | Sección | Bloque del guion |
|---|---|---|
| 1 | Portada (con descriptores utilizables) | 0:00 |
| 2 | El problema (Figura 1) | Bloque 1 · 0:00–1:00 |
| 3 | Cómo se construyó: línea de proceso animada y **ejemplo real con verificación de la cita en vivo** | Bloque 2 · 1:00–2:30 |
| 4–10 | **De la figura al recorte** (7 pantallas): el problema · cinco destinos · tres pasos · **el flujo (ig_hero_flujo)** · qué entra · muestra al azar · calidad y diagrama | Bloque 3 · 2:30–4:00 |
| 11 | Línea de tiempo (pulsar cada hito) | apoyo |
| 12 | La base en figuras (galería de las figuras 1–8 y 10) | apoyo |
| 13 | El Atlas (enlace, vista previa y la demo «sube tu micrografía») | Bloque 4 · 4:00–6:30 |
| 14 | Modelos: tamaño · clase · imagen · **recortes de panel (ig_modelos_2)** · **modelo final** · **NFFA (ig_modelos_3)** | Bloque 5 · 6:30–8:30 |
| 15 | Decisiones: tabla filtrable de 34 decisiones en 4 grupos (D25–D34 son propuestas) | Bloque 5 |
| 16 | Limitaciones | Bloque 6 · 8:30–9:50 |
| 17 | Siguientes pasos y créditos | Bloque 6 |

## Cómo actualizarla
Los datos salen de archivos congelados del repositorio: `curation/v0.1/RESUMEN_NUMEROS.json`, `curation/ext_*.csv`, `equipo/DECISIONES.md`, `figuras/figuras_para_el_video/` y `producto/imagenes/` (solo las 4 figuras de los ejemplos, con su DOI). Para regenerar `datos.js` y las imágenes de `assets/`:
```bash
python producto/presentacion/construir_datos.py
```
**Cifras del modelo de imagen:** viven en un solo sitio, el bloque «ÚNICO SITIO» al inicio de la función `imagen()` de `construir_datos.py` (valor e IC 95 %, copiados de `modelos/comparacion/METRICAS_CON_IC.md`). Los textos de la pestaña «¿Y con la imagen?» se generan desde ahí. Cuando Héctor entregue las cifras finales del ajuste fino (sábado 24, 3 pm): cambiar esas constantes, ejecutar el script y actualizar **a mano** estos cuatro sitios, que no se generan: `video/GUION.md`, `video/GUION_EN.md`, `producto/web_contenido/modelos_y_limitaciones.md` y la Figura 11. Al ejecutar, el script avisa si `equipo/DECISIONES.md` (D17) cita cifras distintas.

## Notas
- Las imágenes de `assets/ejemplos/` son de artículos CC BY y se muestran con su crédito y DOI. `producto/imagenes/` sigue fuera de Git; `assets/` sí puede ir.
- Mensaje obligatorio visible en todas las pantallas: «Datos extraídos por IA y verificados por código. Precisión estimada en una muestra revisada.»
- Evaluación de página web frente a app: `EVALUACION_APP_VS_WEB.md`.
- Hecho para `producto/presentacion/`, que es de Bryan; no toca `producto/web/` (de Carlos).
