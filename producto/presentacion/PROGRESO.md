# Progreso de la presentación (24 de octubre, versión 4)

Encargos: `BRYAN_PRESENTACION_FINAL.md` y `BRYAN_FINAL.md` (este último manda en lo que contradice al primero). Reglas: toda cifra sale de un archivo del repositorio y se cita; **cada cifra va con su n y no se mezclan muestras distintas**; las imágenes de artículos llevan su crédito (artículo, DOI y licencia); el repositorio es público: no se suben credenciales.

## Qué se hizo
1. **Figuras de Héctor integradas** (`figuras/modelos/`, con botón ES/EN y visor para ampliar; las de fondo blanco van sobre una tarjeta clara también en modo oscuro, la de flujo sobre una oscura):
   - `fig_hero_flujo` en una pantalla propia («Del artículo al recorte: qué entra al modelo»);
   - `fig_modelos_2` (figura completa → recortes) en la pestaña «Con recortes de panel (preliminar)»;
   - `fig_modelos_3` (NFFA) en «Lo que no funcionó: NFFA».
   (`fig_modelos_1` no se usó: ya hay una escalera interactiva.)
2. **Sección «De la figura al recorte» (7 pantallas)** con los ejemplos reales de Héctor (`entrega/ejemplos_presentacion/`: 10 figuras con cajas, 2 por destino, incluido «superpuesto») y su crédito desde `creditos.csv`; la muestra al azar es su `recortes_por_clase.jpg` con los 12 créditos. La demostración «original → cajas → recortes» usa una figura compuesta que está en este equipo (cajas aplicadas a la figura original).
3. **Modelos con todas las cifras, cada una con su n:**
   - tabla v0.1 (2.100 figuras de 1.641 artículos) como línea base;
   - recortes de panel, preliminar: tabla A (n = 1.112) y tabla B (n = 786), sin mezclarlas, con el control de «mismo número de vistas» (+0,006 de exactitud en ResNet50 y +0,008 en DINOv2) y el IC de «fusión 04 − fusión 03», que incluye el cero;
   - modelo final: exactitud 0,561 y F1 macro 0,521 (validación cruzada por artículo, n = 1.114) frente a 0,442 de la clase mayoritaria; entrenado con todos los datos, no se puede evaluar;
   - NFFA: no mejora (B − A = −0,019 [−0,042, +0,005]); el control con etiquetas mezcladas empeora.
4. **Decisiones:** 34, en cuatro grupos filtrables (Datos, Figuras, Evaluación estadística, Modelos). D25–D34 son **propuestas** y están también en `equipo/DECISIONES.md` (sección E). D33 (NFFA) y D34 (ensamble de 3 semillas) se añadieron ahora que `ANALISIS_06_NFFA.md` existe.
5. **Demo «sube tu micrografía»:** descrita como lo que es (corre en el navegador con ONNX; la hizo Carlos), con sus advertencias, en «Modelo final», «Limitaciones», el Atlas y `EVALUACION_APP_VS_WEB.md`.
6. **Textos para la web de Carlos** (`producto/web_contenido/`): `como_se_construyo.md` (5.539 → 1.702 → 8.108 → 4.670, reglas, 47/48, IoU 0,89, registro D1–D8) y `modelos_y_limitaciones.md` (todas las cifras con su n y su fuente).
7. **Guiones** `video/GUION.md` y `GUION_EN.md` v3: presupuesto 9:50, el flujo y las figuras de modelos con su tiempo en pantalla (≥ 8 s), la demo dentro del bloque del Atlas.

## Qué quedó pendiente
- **Verificar contra la web real de Carlos:** la vista «Figuras y paneles» y la demo **no estaban en `main`** (el `producto/web/` de `main` es la versión anterior: sin ONNX ni esa vista). La narración del Bloque 4 del guion se escribió desde las descripciones de los encargos.
- **No abrí la demo ONNX:** las cifras de verificación (20 de 20; diferencia media 0,0051) son las de la ficha del modelo y del encargo. No descargué la Release `modelo-v1.0` (no hace falta para la presentación).
- **La rama `presentacion-bryan` no se pudo crear desde esta computadora:** no hay `git` ni `gh` instalados. Se entrega un zip y los pasos para subirla (ver abajo).
- Verificación visual en Chrome real y en un proyector (se probó en el navegador integrado de la app: 1920×1080, 375 px, modo claro y oscuro, visor con Esc).
- Decidir el idioma del video (inglés frente a español con subtítulos).

## Qué espera a Héctor
Confirmar D25–D34 (propuestas); revisar los créditos de las 22 imágenes; decidir el alojamiento (no se publicó nada); la cifra «0,442 de clase mayoritaria» del modelo final viene de `ANALISIS_04_RECORTES.md` (n = 1.112 artículos), no de los 1.114 del modelo final: se dice con ese n.

## Cómo subir la rama (desde una computadora con git)
```bash
git pull origin main
git switch -c presentacion-bryan
# copiar producto/presentacion/, video/ y producto/web_contenido/ y equipo/DECISIONES.md del zip sobre el repositorio
git add producto/presentacion video producto/web_contenido equipo/DECISIONES.md
git commit -m "Presentación v4: figuras y recortes, modelos, NFFA, modelo final, decisiones D25–D34, guiones v3"
git push -u origin presentacion-bryan
```
`producto/presentacion/assets/` pesa ≈ 7 MB; son imágenes CC BY con crédito en pantalla. No se sube `producto/imagenes/`.

## Cómo regenerar y abrir
```bash
python producto/presentacion/construir_datos.py   # datos.js, assets, versiones de los enlaces (lee los archivos del repositorio y falla si falta una cifra)
python producto/presentacion/servir.py            # abre http://localhost:8000/presentacion/ (servidor sin caché)
```
`figuras_recortes.py` necesita `producto/imagenes/` (figuras originales, fuera de Git) solo para la demostración de tres pasos; el resto sale de `entrega/ejemplos_presentacion/`.
