# Atlas: revisión del paquete del 24/10 y siguientes pasos para Carlos

Claude abrió el zip `Atlas_traspaso_2026-10-24_sin_capturas.zip`, lo sirvió con las imágenes en un navegador y lo probó (laptop y móvil de 375 px). **Resultado: aprobado. Está mucho mejor.** Ya está subido a `main` (`producto/web/`, `equipo/qc_carlos/`, `equipo/carlos_traspaso/`): **no necesitas la rama `web-carlos` ni resolver el error 403 de GitHub**. Haz `git pull origin main` para tener lo mismo que todos. Los cambios futuros se siguen enviando como zip a Héctor.

## Lo que Claude comprobó (todo pasó)
- Portada: 1.707 / 2.726 / 3.116 / 4.015, sin errores en la consola.
- 0 títulos con etiquetas HTML (antes eran 364).
- El filtro de portador está en español con conteos (Liposoma 119, SLN 69, Polimérica 311, Nanomaterial 733…).
- Flujo de la demo: Liposoma + cryoTEM → 15 artículos; la ficha muestra imagen, descriptores, cita desplegable y «Copiar cita/DOI».
- Fichas sin imagen: marcador «No está en la copia local; consulta el DOI», sin errores 404 en la consola.
- Móvil (375 px): no se desborda nada.
- Nota: las 44 imágenes que faltan son archivos `.webp` (revistas como RSC) que Europe PMC no incluye en su paquete. Es normal; el marcador las cubre.

## Cambio importante: el modelo ya tiene resultados reales
- **Quién hace el modelo cambió:** lo lleva Héctor (con Claude y Codex), no Bryan. Bryan se encarga del video y de las validaciones científicas. Cambia en el guion el nombre de quien entrega el modelo.
- Claude **ya generó los tres JSON reales** y los dejó en `producto/modelo/` (`metricas.json`, `predicciones.json`, `similares.json`). Tras `python web/build_data.py` (desde `producto/`), el panel del modelo aparece: «Predicción del modelo: … (confianza)» separada de «Clase del artículo (base de datos)», con cinco micrografías parecidas y las métricas. Verificado en el navegador: predicciones, 10 vecinos con imagen y 0 errores.
- **Qué es ese modelo:** vectores de imagen (DINOv2 y ResNet50, calculados en el clúster Kabré) con un clasificador no lineal; cada predicción es **fuera de muestra** (el artículo no estaba en el entrenamiento). Exactitud 52,6 %, exactitud balanceada 43,2 %, F1 macro 0,44, frente a 45,4 % de la clase mayoritaria (que da F1 ~0,16). Es un resultado **exploratorio**: solo con la imagen la tarea es difícil, y la fusión con las medidas rinde más (F1 0,55). En la demo no se vende como «el modelo acierta»; se dice «un primer modelo de imágenes, evaluado por artículo, ya supera al azar y se compara con la base».

## Qué hacer ahora, en orden
1. **`git pull origin main`**, ejecutar `python web/build_data.py` desde `producto/` y abrir `http://localhost:8000/web/` (servidor desde `producto/`). Comprobar que aparece el panel del modelo.
2. **Guion de demo** (`producto/web/GUION_DEMO.md`):
   - Quita «de Bryan» y las condiciones que dicen que faltan resultados.
   - Segmento del modelo (1:10–1:40): abre una ficha con predicción acertada **y una con predicción errada** y di la frase de honestidad: «la etiqueta de la base y la predicción del modelo se muestran por separado; aquí el modelo acierta/falla». Mostrar un fallo da credibilidad.
   - Dura 2:20: déjalo en 2:30 como máximo.
3. **Pequeños detalles de interfaz:**
   - El filtro «Categoría» muestra `nanomaterial` y `nanoportador` en minúscula y sin formato: pásalos a «Nanomaterial» y «Nanoportador».
   - En el bloque de métricas muestra también el **F1 macro** y la **exactitud balanceada** si el JSON las trae, y el texto de `nota` (aviso de resultado exploratorio).
   - En móvil, al abrir el explorador tras hacer clic en una ficha, en una captura de Claude aparecía un hueco en blanco bajo el buscador. **Comprueba en tu Chrome móvil que los filtros y la lista se ven** y arréglalo si pasa.
4. **QA propio con capturas** en tu Chrome: portada, una ficha con imagen y predicción, una ficha sin imagen y una de móvil. Guárdalas en `producto/web/capturas/` y mándalas a Héctor en el próximo zip (sin imágenes de artículos).
5. **Dos ensayos cronometrados** de la demo (2–3 minutos) y grabación **el sábado con la web congelada a las 5 pm**. Ensaya con la grabación de pantalla a 1920×1080.

## Decisiones que no son tuyas (Héctor)
- **Vista en la nube del Atlas:** un enlace privado para que el equipo lo abra sin instalar nada. Héctor decide si se hace.
- **Publicación pública:** se decide después de congelar la web; publicaría datos e imágenes.
- **Imágenes:** Héctor comparte el zip de 260 MB por Drive; se descomprime en `producto/imagenes/`.

## Para el video
La demo del Atlas es el bloque de 2–3 minutos. Las figuras del video las genera el Codex de Héctor en `figuras/figuras_para_el_video/` (cuando estén revisadas, te avisamos). Bryan ayuda con el guion y el montaje.
