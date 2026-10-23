# Carlos: cierre del Atlas, páginas nuevas y demo

**Para:** Carlos y su Codex. **Fecha:** viernes 23 de octubre, tarde. **Entrega: domingo 25, 5:45 pm.** El Atlas se **congela el sábado a las 5 pm** y se graba la demo.

## 0. Respuesta a lo que preguntó tu Codex (léela primero)
Tu Codex dijo que no sabe si GitHub `main` tiene la actualización y que tu copia está en la rama `web-carlos` (`534096a`). **Sí: está en `main`** (commit `faf1a43`, «Atlas revisado…»): es **tu web, ya revisada**, más los tres JSON reales del modelo en `producto/modelo/`. Esos JSON **no son prueba**: son predicciones reales fuera de muestra (exactitud 52,6 %, F1 macro 0,44; resultado exploratorio). Haz esto en tu terminal, desde la carpeta del repositorio:
```
git fetch origin
git checkout main
git pull origin main
cd producto
python web/build_data.py
python -m http.server 8000
```
y abre `http://localhost:8000/web/`. Tu rama `web-carlos` ya no hace falta; **no intentes subir nada a GitHub**: sigue entregando zips a Héctor.

## 1. Decisión de equipo: Bryan te ayuda
Bryan deja el modelo y pasa a presentación interactiva, guion del video y apoyo al sitio. **Reparto de archivos para no pisarse:**
- **Tuyo:** `producto/web/` completo (`app.js`, `styles.css`, `index.html`, `build_data.py`, `data/`).
- **De Bryan:** `producto/presentacion/` (presentación), `video/` y `producto/web_contenido/*.md` (textos que tú integras).
- **De Héctor:** `curation/`, `modelos/`, `producto/modelo/`.
No edites los archivos del otro; pídelo por WhatsApp.

## 2. Tus tareas, en orden
1. **Sincronizar** (sección 0) y comprobar que aparece el panel del modelo.
2. **Pequeños arreglos del Atlas** (de `equipo/SIGUIENTES_PASOS_CARLOS_2.md`): formato del filtro «Categoría» (Nanomaterial/Nanoportador), métricas completas en el panel del modelo (F1 macro, exactitud balanceada y la `nota`), y el hueco en blanco en móvil bajo el buscador (confírmalo en tu Chrome móvil).
3. **Dos páginas nuevas** (con el texto que escribe Bryan en `producto/web_contenido/`; mientras llega, deja el esqueleto):
   - **«Cómo se construyó»**: el flujo y las decisiones de `equipo/DECISIONES.md` (D1–D8: licencia CC BY, cita verificada por código, exclusión de vectores virales, E1/E2, QC asistido por IA). Un enlace por decisión a su evidencia.
   - **«Modelos y limitaciones»**: la escalera de modelos con las cifras de `producto/modelo_tabular/metricas_tabular.json` y `producto/modelo/metricas.json`, con la línea base visible en cada una y el aviso de que es exploratorio.
4. **Créditos y licencia** al pie de la web: Europe PMC; imágenes de artículos de acceso abierto con enlace al DOI de cada uno; y **«Cálculo realizado en el supercomputador Kabré (CeNAT/CNCA)»** (lo exigen los términos de uso de Kabré).
5. **QA con capturas** en tu Chrome: portada, ficha con imagen y predicción, ficha sin imagen, móvil. Consola con 0 errores en rojo. Guárdalas en `producto/web/capturas/`.
6. **Guion de la demo** (`producto/web/GUION_DEMO.md`): quita lo de «Bryan entrega el modelo»; en el segmento del modelo muestra **un acierto y un fallo** y di la frase de honestidad; 2:30 como máximo. **Dos ensayos cronometrados.**
7. **Sábado 5 pm: congelar y grabar** a 1920×1080. Entrega el zip final a Héctor ese mismo día.

## 3. Cómo usar tu Codex (qué delegar)
Delega lo repetitivo: dar formato a filtros, generar las páginas con el texto de Bryan, revisar rutas y enlaces, regenerar datos. **Que valide cada paso** (conteos de la portada = `summary.json` = 1.707 / 2.726 / 3.116 / 4.015). No le pidas modelos: eso es de Héctor.

## 4. Lo que NO hay que decir en el Atlas
Nada de «el modelo acierta» ni «validado por humanos». El QC es **asistido por IA en una muestra de 20 artículos**; la predicción es **exploratoria**.

## 5. Calendario
- **Hoy:** secciones 0 y 2.1–2.2.
- **Sábado 12 m:** páginas nuevas integradas (con el texto de Bryan, o esqueleto). **3 pm:** guion y ensayos. **5 pm:** web congelada y grabación.
- **Domingo:** nada nuevo en la web; solo apoyo al montaje.
