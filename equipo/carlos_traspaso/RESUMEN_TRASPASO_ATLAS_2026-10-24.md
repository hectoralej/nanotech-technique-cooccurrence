# Atlas Nano2Predict: resumen de trabajo y siguientes pasos

**Actualizado:** 24 de octubre de 2026  
**Alcance:** cambios locales preparados para traspaso; este informe no significa que estén publicados en GitHub.

## Resumen

Se preparó una versión local de la web del Atlas a partir de los datos canónicos v0.1, un paquete de transferencia sin imágenes y un tablero Excel con tareas y referencias. La publicación de la rama quedó bloqueada por un error de permisos de la integración de GitHub. El trabajo se puede revisar en el checkout local y se puede compartir mediante el ZIP.

## Qué se hizo

### Datos y alcance

- La selección del Atlas se basa en artículos E1/E2; se quitó el filtro por palabras del título, incluidas AAV/virus.
- Se generaron los datos web con **1.707 artículos, 2.726 paneles, 3.116 descriptores y 4.015 espectros**. El conteo correcto de descriptores es 3.116 registros, no 3.122 líneas físicas.
- Los 117 artículos `tier=no` quedan fuera del Atlas y de las tablas de evidencia, de acuerdo con la decisión de incluir solo E1/E2.
- Se limpiaron etiquetas y entidades HTML en títulos y citas; el filtro de portador usa `carrier_type` y sus categorías suman 1.707 artículos.

### Interfaz e imágenes

- Las fichas muestran hasta cinco micrografías inicialmente, permiten desplegar el resto y copiar cita, DOI y PMCID.
- Se añadió el indicador `imagen_local`; cuando la imagen falta, la ficha presenta un marcador y un enlace al DOI.
- El panel del modelo separa datos observados de predicciones y el paquete distribuido mantiene `available:false` para no presentar fixtures como resultados reales.
- Se integraron localmente 2.149 JPG y se compararon con `producto/imagenes/descargas.csv`. El inventario mantiene 44 archivos no disponibles de 30 PMCID; no se incluyeron JPG en Git ni en el ZIP.

### Documentación y transferencia

- Se actualizaron los informes de estado y progreso y se preparó el guion de demo.
- Se creó el paquete ZIP con la web y documentos de QC/traspaso, excluyendo imágenes, fixtures del modelo y capturas.
- Se creó el tablero Excel con el estado de diez frentes de trabajo y una pestaña de referencias.

## Qué falta y por qué

| Pendiente | Estado y motivo | Qué se necesita para cerrarlo |
|---|---|---|
| QA visual en Chrome, laptop y móvil | Pendiente. El vistazo anterior correspondía a una versión previa; no valida esta actualización. | Probar portada, filtros, búsqueda, consola, fichas con imagen y sin imagen, y una ficha extensa en móvil de 375 px. Guardar capturas de portada y dos fichas. |
| JSON finales del modelo | En espera de Bryan. Los archivos disponibles son fixtures `prueba:true`. | Recibir los archivos finales, validar esquema, predicciones, confianza, vecinos y matriz de confusión; regenerar los datos web. |
| Ensayo y grabación de la demo | Pendiente; debe hacerse después de cerrar QA y congelar la web. | Hacer dos ensayos de 2–3 minutos y grabar. Omitir el modelo si siguen faltando resultados reales. |
| Rama remota y PR | Bloqueado: GitHub devolvió HTTP 403 (`Resource not accessible by integration`) al crear la rama. | Habilitar el permiso de escritura necesario o pedir a una sesión autorizada que publique el commit en `web-carlos`. No subir directamente a `main` sin revisión. |
| Publicación privada o pública | Sin publicar. Las instrucciones reservan la decisión de nube a Héctor; el hosting público expone los datos. | Héctor debe decidir si autoriza vista privada y, por separado, si autoriza hosting público. |
| Compartir las imágenes | Pendiente. Los JPG no están incluidos en el ZIP. | Compartir `imagenes_v0.1.zip` por Drive u otro canal acordado; cada equipo debe extraerlo en `producto/imagenes/<pmcid>/`. |
| Compartir el paquete | Aún no transferido fuera del equipo local. | Enviar el ZIP y este informe por el canal acordado. No hay una sesión conectada de Drive o WhatsApp en esta tarea. |

## Verificaciones completadas

- Los cuatro CSV fuente coinciden con los SHA-256 de `curation/v0.1/checksums.txt`.
- Los conteos de los CSV y los JSON generados coinciden: 1.707 artículos, 2.726 paneles, 3.116 descriptores y 4.015 espectros.
- Los 117 artículos `tier=no` no aparecen en el Atlas ni en las tablas de evidencia.
- Se revisó que los títulos generados no conservaran etiquetas o entidades HTML sin limpiar.
- Cada panel tiene un indicador booleano de disponibilidad local. Hay 2.669 paneles con imagen descargada y 57 paneles sin archivo local; estos representan 44 nombres de imagen faltantes.
- Los archivos JPG disponibles se verificaron por tamaño y firma JPEG; los faltantes tienen DOI asociado a sus fichas.
- Pasaron `node --check producto/web/app.js` y `python -m py_compile producto/web/build_data.py`.
- El ZIP preliminar pasó la comprobación de integridad y excluye imágenes, `.build_input` y fixtures del modelo.

Estas pruebas cubren datos, sintaxis y contenido del paquete. No equivalen a la inspección visual en Chrome ni a una nueva revisión humana artículo por artículo.

## Siguiente secuencia recomendada

1. Abrir la web local y completar QA visual en laptop y móvil; registrar errores de consola y corregirlos.
2. Tomar las tres capturas nuevas (portada, ficha con imagen, ficha sin imagen) y actualizar el paquete.
3. Incorporar los JSON finales de Bryan si llegan; si no, mantener desactivado el panel de resultados del modelo para la demo.
4. Rehacer el ZIP tras las correcciones y revisar que siga excluyendo imágenes y fixtures.
5. Ensayar dos veces y grabar la demo.
6. Resolver el acceso de GitHub, revisar el diff de `web-carlos` y publicar la rama/PR. Mantener `main` intacta hasta la revisión.
7. Acordar la decisión de publicación en nube y compartir por un canal autorizado el ZIP de código y, por separado, el paquete de imágenes.

## Archivos y enlaces

### Entrega

- [Tablero Excel de tareas y referencias](../outputs/atlas_traspaso_2026-10-24/Traspaso_Atlas.xlsx)
- [ZIP de transferencia, sin capturas](Atlas_traspaso_2026-10-24_sin_capturas.zip)
- [Instrucciones para abrir el paquete](LEEME_PAQUETE_ATLAS.md)

### Web y registro de progreso

- [Web del Atlas](../producto/web/index.html)
- [Progreso y verificaciones de la web](../producto/web/PROGRESO.md)
- [Guion de demo](../producto/web/GUION_DEMO.md)
- [Resumen de conteos web](../producto/web/data/summary.json)
- [Indicador del modelo distribuido](../producto/web/data/model-status.json)
- [Registro de imágenes disponibles y faltantes](../producto/imagenes/descargas.csv)

### Datos fuente

- [Artículos](../curation/ext_articulos.csv)
- [Paneles](../curation/ext_paneles.csv)
- [Descriptores](../curation/ext_descriptores.csv)
- [Espectros](../curation/ext_espectros.csv)
- [Resumen numérico v0.1](../curation/v0.1/RESUMEN_NUMEROS.json)
- [Checksums v0.1](../curation/v0.1/checksums.txt)
- [Repositorio en GitHub, rama main](https://github.com/hectoralej/nanotech-technique-cooccurrence/tree/main)

### Informes de apoyo

- [Actualización resumida](../equipo/ACTUALIZACION_ATLAS_PARA_HECTOR.md)
- [Informe detallado de estado](../equipo/REPORTE_ESTADO_ATLAS_PARA_HECTOR.md)
- [QC y traspaso](../equipo/qc_carlos/RESUMEN_TRASPASO_ATLAS.md)

## Estado de publicación y vista previa

- Rama local: `web-carlos`, basada en `origin/main` `739576a`.
- Commit local: `534096a` (`Atlas: publica web y datos v0.1`). La creación de la rama remota fue rechazada por HTTP 403; no existe push ni PR de esta actualización.
- [Vista previa local](../producto/web/index.html) o [servidor local](http://localhost:8000/web/) si se ejecuta desde `producto/`. `localhost` solo es accesible en el equipo que sirve la web.
- No se publicó una vista en nube. El ZIP sigue siendo preliminar y sin capturas.
