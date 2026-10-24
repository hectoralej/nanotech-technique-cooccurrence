# Atlas Nano2Predict: cierre de la actualización y siguientes pasos

**Para:** Héctor y Carlos  
**Corte:** 24 de octubre de 2026  
**Fuente sincronizada:** `main` / `origin/main`, commit `de48aa7`  
**Estado:** cambios locales sin commit ni push; ZIP actualizado con capturas de QA automatizado.

## Resumen ejecutivo

Se sincronizó la copia local con `origin/main` y se reconstruyeron los datos web usando los datos canónicos del repositorio. Se completaron los arreglos solicitados al Atlas, se añadieron las páginas «Cómo se construyó» y «Modelos y limitaciones», se incorporaron los créditos y se actualizó el guion de demo. El QA automatizado en Chrome para escritorio y un viewport móvil de 375 px terminó sin errores de consola ni respuestas HTTP fallidas. El ZIP de traspaso incluye código, datos web, métricas y capturas, pero no incluye las 2.149 imágenes JPG (273,7 MB); se deben transferir aparte mediante `imagenes_v0.1.zip`.

## Cambios realizados

- `main` quedó sincronizada en `de48aa7`. No hice commit ni push.
- Se ejecutó `python web/build_data.py` desde `producto/`; el Atlas conserva los datos E1/E2: **1.707 artículos, 2.726 paneles, 3.116 descriptores y 4.015 espectros**.
- Se dejaron los nombres visibles de las categorías como «Nanomaterial» y «Nanoportador».
- El panel de modelo muestra exactitud, exactitud balanceada, F1 macro, línea base y la nota de limitaciones desde los JSON reales de `main`.
- La página «Modelos y limitaciones» presenta los resultados tabulares y de imagen, con las líneas base identificadas. Se corrigió el vínculo de las tres filas base para que las tres aparezcan resaltadas.
- La página «Cómo se construyó» organiza las decisiones D1–D8 y enlaza la evidencia. Bryan no había dejado los textos editoriales en `producto/web_contenido/`; la página queda como esqueleto factual hasta recibirlos.
- El pie acredita Europe PMC, enlaza las imágenes al DOI conforme a la licencia y añade el crédito obligatorio a Kabré (CeNAT/CNCA).
- Se añadió favicon para evitar una solicitud 404 en el navegador.
- El guion queda limitado a 2:30 y presenta un caso coincidente y uno discrepante como resultados exploratorios; no dice que el modelo esté validado ni que «acierta» en general.

## Verificación y evidencia

- Chrome ejecutado con Playwright en 1365×900 y 375×812. Se recorrieron portada, una ficha con imágenes, el caso de predicción distinta, una ficha con imagen no descargada, modelos y construcción.
- Resultado: cero errores de consola, cero solicitudes fallidas/HTTP ≥400 en esas rutas, cero imágenes cargadas rotas y cero archivos JPG ausentes entre los 2.669 paneles marcados como disponibles localmente.
- La ficha PMC12703698 muestra el marcador «No está en la copia local» y conserva el enlace DOI. Las 44 figuras ausentes (30 PMCID) no se solicitaron como archivos locales.
- Se verificaron las etiquetas de categoría (`Nanomaterial`, `Nanoportador`), las tres filas de línea base y ausencia de desbordamiento horizontal en 375 px (documento = viewport = 375 px). El espacio entre el campo de búsqueda y el siguiente control corresponde al rótulo del buscador y la separación normal de la cuadrícula; no se detecta un hueco grande.
- Pasaron `node --check` para `app.js` y `modelos.js`, y `python -m py_compile producto/web/build_data.py`.
- Capturas: [portada laptop](../producto/web/capturas/01-portada-laptop.png), [ficha con imagen](../producto/web/capturas/02-ficha-imagen-prediccion.png), [predicción distinta](../producto/web/capturas/03-ficha-prediccion-diferente.png), [ficha sin imagen](../producto/web/capturas/03b-ficha-sin-imagen.png), [móvil 375 px](../producto/web/capturas/04-movil-375.png), [modelos](../producto/web/capturas/05-modelos-laptop.png) y [construcción](../producto/web/capturas/06-construccion-laptop.png).

> La revisión es automatizada y visual sobre Chrome headless; no sustituye una comprobación humana en el equipo de presentación. Las capturas no son una grabación de ensayo.

## No completado y motivo

| Pendiente | Motivo | Próxima acción |
|---|---|---|
| Texto editorial de Bryan para ambas páginas | No se encontró `producto/web_contenido/` ni los textos allí. | Recibirlos e integrarlos, respetando las fuentes de Bryan. |
| Dos ensayos cronometrados de la demo | Requieren que el presentador practique la narración en voz alta; no los puedo hacer ni afirmar como realizados. | Carlos/Héctor hacen dos ensayos con cronómetro y ajustan el guion si excede 2:30. |
| Congelar la web y grabar a 1920×1080 | Requiere decisión del equipo, equipo de grabación y grabación humana. | Después del ensayo, congelar esta versión y grabar; reflejar cualquier cambio posterior en el paquete. |
| Transferencia del ZIP a Héctor | No hay una conexión de mensajería/Drive autorizada en esta tarea. | Compartir manualmente el ZIP local por el canal acordado. |
| Incluir las JPG en el ZIP de código | Las 2.149 JPG ocupan aproximadamente 273,7 MB y ya existe un archivo separado `imagenes_v0.1.zip`. | Pasar ese archivo por separado y extraerlo en `producto/imagenes/<pmcid>/`. |

## Entrega y vista previa

- ZIP actualizado: [Atlas_traspaso_2026-10-24_QA.zip](Atlas_traspaso_2026-10-24_QA.zip).
- [Instrucciones del paquete](LEEME_PAQUETE_ATLAS.md).
- [Progreso técnico](../producto/web/PROGRESO.md).
- [Guion](../producto/web/GUION_DEMO.md).
- [Web del Atlas](../producto/web/index.html).
- Vista local si el servidor sigue activo: [http://localhost:8000/web/](http://localhost:8000/web/). Para iniciarlo desde `producto/`: `python -m http.server 8000`.
- Repositorio: [GitHub, rama main](https://github.com/hectoralej/nanotech-technique-cooccurrence/tree/main).

El checkout sincronizado no publica automáticamente los cambios nuevos: permanecen locales en `main`, sin commit ni push. El paquete ZIP es el medio preparado para revisión y traspaso.
