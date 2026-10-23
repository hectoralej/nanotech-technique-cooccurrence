# Traspaso: Atlas Nano2Predict

**Actualizado:** 24 de octubre de 2026  
**Estado:** correcciones funcionales aplicadas; ZIP preliminar listo, falta revisión visual Chrome y tres capturas para completarlo.

## Enlaces

| Recurso | Ubicación |
|---|---|
| Sitio del Atlas | [`producto/web/index.html`](../../producto/web/index.html) |
| Progreso y pendientes | [`producto/web/PROGRESO.md`](../../producto/web/PROGRESO.md) |
| Informe completo para Héctor | [`equipo/REPORTE_ESTADO_ATLAS_PARA_HECTOR.md`](../REPORTE_ESTADO_ATLAS_PARA_HECTOR.md) |
| Ajuste 2 de Carlos | [`equipo/AJUSTE_2_CODEX_CARLOS.md`](../AJUSTE_2_CODEX_CARLOS.md) |
| Generador | [`producto/web/build_data.py`](../../producto/web/build_data.py) |
| Guion de demo | [`producto/web/GUION_DEMO.md`](../../producto/web/GUION_DEMO.md) |
| JSON generados | [`producto/web/data/`](../../producto/web/data/) |
| Lista provisional para revisar | [`producto/web/data/EXCLUIDOS_POR_TITULO_PROVISIONAL.csv`](../../producto/web/data/EXCLUIDOS_POR_TITULO_PROVISIONAL.csv) |
| Base congelada v0.1 | [`curation/v0.1/`](../../curation/v0.1/) |
| Tabla de etiquetas del modelo | [`curation/v0.1/tabla_modelo.csv`](../../curation/v0.1/tabla_modelo.csv) |
| Plan del equipo | [`equipo/PLAN_EQUIPO_FINAL.md`](../PLAN_EQUIPO_FINAL.md) |
| Carpeta de QC de Carlos | [`equipo/qc_carlos/`](.) |

## Hecho

- `main` se actualizó a `c137077`; `.gitattributes` conserva los bytes de CSV. Se restauraron los cuatro CSV y sus SHA-256 coinciden con `curation/v0.1/checksums.txt`.
- Se regeneraron los JSON desde `curation/` con lectura CSV `utf-8-sig`.
- Tras la decisión actualizada de Carlos, la web muestra solo E1/E2 (1.707 artículos) y excluye los 117 `tier=no`, incluidos PMC10239954 y PMC10535558. Se quitó el filtro por palabras AAV/virus.
- Según el dictamen de Claude del 22/10, ocho títulos no usan virus como portador y continúan en Atlas; los dos `tier=no` se mantienen fuera. El CSV incluye los diez casos con este estado.
- Se limpiaron entidades HTML, se simplificó el filtro a `carrier_type`, cada panel tiene `imagen_local`, y los JSON con `prueba: true` se muestran solo en local con aviso y se excluyen del ZIP.
- Las fichas muestran hasta cinco micrografías al inicio, control «Ver todas» y botón «Copiar cita/DOI».

## Conteos

| Tabla | Filas mostradas |
|---|---:|
| Artículos E1/E2 | 1.707 |
| Paneles/micrografías | 2.726 |
| Descriptores | 3.116 |
| Espectros | 4.015 |

La cifra anterior 3.122 era un conteo de líneas físicas del CSV de descriptores, no de registros CSV. Los hashes y conteos ya están resueltos.

## Siguiente

1. Revisar en Chrome consola, filtros, fichas con y sin imagen, ficha con muchos descriptores y móvil 375 px; tomar tres capturas.
2. Añadirlas a `entrega/Atlas_para_Hector_2026-10-24_sin_capturas.zip`, que excluye `.build_input`, imágenes y fixtures del modelo.
3. Integrar JSON reales de Bryan cuando estén disponibles y verificar predicciones, cinco vecinos distintos y matriz de confusión.
4. Ensayar dos veces la demo con `producto/web/GUION_DEMO.md`. No se ha hecho commit ni push.

La revisión QC de Carlos es asistida por IA, no una revisión humana. Los archivos de propuestas y evidencias permanecen en esta carpeta.
