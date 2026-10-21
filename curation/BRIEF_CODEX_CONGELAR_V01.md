# Codex: congelar la v0.1 de la base (tarea de cierre)

Este archivo manda para esta tarea. `RAIZ` = `C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence`. Contexto del proyecto: `curation\PUNTO_DE_REINICIO.md` y `equipo\PLAN_EQUIPO_FINAL.md`. Reglas de siempre: no abrir `curation\work\clave_modelo.csv` ni `curation\qc_codex\`; no hacer push a GitHub (Héctor lo hace); no modificar `curation\work\llm\E\` ni `E_v2\` (son las salidas de extracción, quedan como están); sin AAV ni virus.

## 0. Antes de empezar: dos respuestas que Héctor necesita (5 minutos)
Tu repaso de EX078–EX102 y EX128–EX160 fue muy bueno (1,80 descriptores y 2,20 espectros por artículo). Pero tu corrida anterior de EX128–EX160 duró 17 minutos para 33 lotes y extrajo muy poco (0,16–0,67 descriptores por artículo). Escribe `RAIZ\curation\work\ext\explicacion_corrida_rapida.md` con respuestas **honestas y concretas** (no hace falta justificarse; hace falta entender):
1. ¿Qué hiciste distinto en la corrida rápida frente al repaso riguroso? (¿leíste los paquetes completos o solo partes? ¿usaste algún atajo, muestreo o plantilla?)
2. ¿Qué parte de lo que pedía el protocolo riguroso (inventarios de descriptores y espectros, auditoría por artículo) cambió tu comportamiento?
3. ¿Qué instrucción habría evitado el problema en la primera corrida?
4. ¿Hay algo en los briefs que sea ambiguo y empuje a ir rápido?
Máximo una página. Esto se usará para mejorar las instrucciones, no para juzgar.

## 1. Tarea: congelar la v0.1
Objetivo: dejar una versión **estable, documentada y reproducible** de los 4 CSV `ext_*` que Bryan y Carlos usan desde el viernes. Fecha límite: **jueves 22 de octubre, 6 pm**. Las columnas actuales **no se cambian ni se reordenan**; solo se mejoran los datos.

Estado de partida (`python -m curation.extended apply`, ya corrido por Claude): 1.824 artículos (E1 1.130, E2 577, no 117), 2.726 paneles, 3.251 descriptores, 4.015 espectros; `apply` ya une `E` y `E_v2`.

### 1.1 Unir filas partidas de descriptores
Problema: a veces el tamaño y el zeta de una misma muestra están en filas distintas (cada fila con un campo vacío), o una misma muestra aparece repetida con citas distintas.
- **Dónde:** en `RAIZ\curation\extended.py`, función `apply`, justo antes de construir las tablas (después de verificar citas y números, sobre la lista `D` de cada artículo). **Haz un cambio mínimo** y no toques el resto de la lógica.
- **Regla de unión** (por artículo): dos filas se unen si tienen el mismo nombre de muestra normalizado (minúsculas, sin espacios dobles, sin paréntesis finales como «(B)» ni signos) **y** no se contradicen (si ambas tienen el mismo campo con valores distintos, NO se unen y quedan las dos). Al unir: se conservan los valores no vacíos, `medium` preferente el declarado (distinto de `not_declared`), y `quote` la de la fila principal (la que ya tenía tamaño; si no hay, la primera) — no concatenes citas.
- **Prohibido:** inventar valores, redondear o cambiar números, unir muestras diferentes (p. ej. «F1» con «F2»), o unir filas de artículos distintos.
- Registra cuántas uniones se hicieron en un archivo `curation\v0.1\CAMBIOS.md` y guarda una lista `curation\v0.1\filas_unidas.csv` (`pmcid, muestra, filas_antes, motivo`) para que Claude pueda auditarla.
- Antes y después del cambio, corre `python -m curation.extended apply` y anota las cifras (artículos, descriptores). El número de artículos y de espectros/paneles **no debe cambiar**; los descriptores deben bajar solo por uniones.

### 1.2 Validaciones de calidad de la v0.1 (solo reportar; no corregir a mano)
Escribe `RAIZ\curation\v0.1\VALIDACION.md` con estas comprobaciones sobre los 4 CSV (usa `utf-8-sig`):
1. Cada `pmcid` de paneles, descriptores y espectros existe en `ext_articulos.csv`.
2. Cada `image_file` de `ext_paneles.csv` (no vacío) coincide con un nombre de figura del artículo; cuántas filas tienen `image_file` vacío.
3. Rangos plausibles: tamaño 1–5.000 nm, PDI 0–1,5, zeta −150 a +150 mV. Lista los valores fuera de rango (máx. 50 filas) en `curation\v0.1\valores_extremos.csv` (`pmcid, campo, valor, quote`). **No los borres.**
4. Filas duplicadas exactas (mismo `pmcid`, muestra, valores) tras la unión.
5. Artículos con `tier` E1/E2 sin ninguna fila de panel, o E1 sin descriptor o sin espectro (debe ser 0).
6. Distribución: artículos por `family`/`carrier_type`, por `tier`, por `categoria_uso`, por año; micrografías por `variant`; descriptores por rango de tamaño; espectros por técnica.
7. Que `license_color` sea `verde` para todos y cuántos artículos tienen `quotes_rejected` > 0 o `numbers_not_found` > 0.

### 1.3 Documentación de la versión
Crea la carpeta `RAIZ\curation\v0.1\` con:
- `LEEME.md` (una página, en español): qué es la base, cómo se construyó (búsqueda en Europe PMC → extracción con IA → verificación de cada cita y cada número por código → control de calidad), qué contiene cada CSV, **diccionario de columnas** (nombre, tipo, ejemplo, significado, valores posibles), licencias (todos CC BY; imágenes con crédito DOI), limitaciones conocidas (datos extraídos por IA; figuras completas, no paneles recortados; precisión estimada en una muestra revisada: en 20 artículos, micrografías 19/19 comprobables, espectros 14 sí y 2 no, descriptores 9 sí y 1 no) y cómo reproducir (`python -m curation.extended apply`).
- `CAMBIOS.md`, `VALIDACION.md`, `filas_unidas.csv`, `valores_extremos.csv` (de arriba).
- `RESUMEN_NUMEROS.json` con los conteos finales (artículos, E1, E2, paneles, descriptores, espectros, familias, técnicas) para que Carlos los use en la portada de la web.
- `checksums.txt` con el SHA-256 de los 4 CSV (`Get-FileHash`).

### 1.4 Entrega
- No ejecutes `git`. Deja todo en disco; Héctor revisa con Claude y luego sube y crea la etiqueta `v0.1`.
- Reporte final corto en el chat: cifras antes y después de la unión, qué validaciones fallaron, cuántos valores extremos, y **qué no pudiste verificar**.
- Si algo del cambio en `extended.py` te parece arriesgado, no lo hagas: describe el problema en `CAMBIOS.md` y para.

## 2. Lo que Claude revisará después (para que lo sepas)
Claude abrirá `filas_unidas.csv` (muestra), comprobará que `apply` sigue dando los mismos artículos/espectros/paneles, repasará `VALIDACION.md` y recalculará `checksums.txt`. Si algo no coincide, se corrige antes de congelar.

## 3. Qué no hacer
No modificar las salidas de extracción, no reordenar ni renombrar columnas, no borrar filas por «limpieza», no abrir `clave_modelo.csv` ni `qc_codex\`, no hacer push, no inventar.
