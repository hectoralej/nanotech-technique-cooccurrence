# Ronda 2: mapa de entrega

- **A**: `figuras/figuras_para_el_video/INDICE.md`, PNG/SVG 1–10 a 1920×1080 y `datos/`; scripts individuales en `figuras/scripts/`. Figura 11 reservada a resultados reales. La figura 9 usa cifras del LEEME congelado: el resumen QC original no está en disco. Es revisión asistida por IA, no humana.
- **B1**: `modelos/formulacion/`: reglas, prevalencias, banderas por artículo, procedencia del texto, 30 citas y revisión explícita. 21 correctos/9 dudosos; todas las citas son literales. Las banderas son menciones ruidosas.
- **B2–B5**: `modelos/tabular_v2/REPORTE_TABULAR_V2.md`, código modular importando tabular_common de R1, dataset derivado y `resultados/`. 30 modelos reportados: cinco A compartidos/importados de R1, ocho regresores enriquecidos y 17 clasificadores (incluye un clasificador estricto solo-mediciones para C). Los 17 guardan probabilidades por clase y 85 comprobaciones de repetición de entrenamiento por fold.
- **C**: `modelos/comparacion/README.md`: manifiesto fijo, inventario de imágenes, fusión y seis pruebas. Los resultados sintéticos están explícitamente marcados y aislados. No existe resultado real ni figura 11 mientras falten predicciones Kabré.
- **D**: `modelos/REVISION_CRITICA.md`, con diagnósticos reproducibles en esta carpeta.

## Reproducción

Con `PYTHONDONTWRITEBYTECODE=1` (evita generar caches de importación dentro de R1/curation):

1. Python 3.13: `figuras/scripts/generar_video.py`; luego abrir cada PNG y revisar visualmente. Los scripts individuales son `figura_N.py`. El manifiesto automático queda con revisión visual pendiente al regenerar para exigir esa comprobación.
2. Extracción: ejecutar `modelos/formulacion/extraer_formulacion.py` con un Python que tenga lxml. En esta máquina se usó `C:/Users/Hector/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` (3.12); el script resuelve dependencias Python puras desde la instalación 3.13. No instala ni descarga nada. Si cambian los ejemplos se exige revisar los 30 antes de entrenar.
3. Python 3.13: `modelos/tabular_v2/run_models.py`, luego `modelos/tabular_v2/informe_v2.py`. Los caches por fold solo se reutilizan si datos/código/columnas coinciden. `PROGRESO_B.md` conserva el avance.
4. Python 3.13: `modelos/comparacion/conjunto_comparacion.py`; `fusion.py`; `validar_comparacion.py` (los dos últimos en esa carpeta). El modo real sin entradas termina con mensaje; el test sintético nunca escribe métricas reales.
5. Python 3.13: `modelos/ronda2/revision_critica.py`.

`CHECKPOINTS_RONDA2.md` contiene un cierre por letra. `fuentes_protegidas.json` guarda SHA-256 de ext_*, v0.1, R1 y su JSON de producto; se contrastan en cada cierre. No se usa Git ni se modifica producto/web o el clúster. Los resultados son exploratorios y los IC condicionales a predicciones OOF.
