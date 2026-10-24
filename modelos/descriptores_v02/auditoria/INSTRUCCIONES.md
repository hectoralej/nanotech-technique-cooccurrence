# Auditoría de descriptores (solo texto; sin imágenes)

Para cada fila de `lotes/Dxxx.json` tienes la **cita textual** del artículo y los valores extraídos (`tamano_nm`, `pdi`, `zeta_mV`), la `muestra` (etiqueta), el `medio` y una `alerta` que explica por qué la fila es dudosa. Decide con **la cita**; no uses conocimiento externo ni inventes valores.

## Qué decidir por fila
1. ¿Cada valor extraído está respaldado por la cita **para esa muestra**? Comprueba cifra, signo (zeta: `−`, `–` y `-` son el mismo signo), unidades y que no sea el valor de otra muestra de la tabla.
2. `veredicto`:
   - `"ok"`: los valores son correctos (la alerta era un falso positivo: formato, signo, redondeo, valor derivado explícito).
   - `"corregir"`: la cita respalda otro valor o un campo está mal asignado (tamaño por zeta, PDI en lugar de otra cosa, columna cambiada, radio en vez de diámetro); da los valores correctos en `tamano_nm`, `pdi`, `zeta_mV` (`null` si la cita no los da).
   - `"descartar"`: la cita no permite sostener ningún valor para esa muestra, o es otra técnica (tamaño por TEM/SEM/XRD, no DLS) y no hay zeta ni PDI válidos, o es un duplicado.
3. `etiqueta_muestra`: la etiqueta **corta tal como aparece en las figuras y tablas** (p. ej. `"B1"`, `"F7"`, `"NLC-PTX"`, `"AuNPs 20 nm"`), para poder enlazar la fila con paneles y espectros; si la `muestra` dada ya es esa etiqueta, repítela. Si no se puede determinar, `null`.
4. `metodo_tamano`: `"DLS"` si la cita lo dice o es inequívocamente hidrodinámico/Z-average/PCS; `"TEM"`, `"SEM"`, `"AFM"`, `"XRD"`, `"otro"`; `"desconocido"` si no se puede saber. No supongas.

## Salida
Escribe `modelos/descriptores_v02/auditoria/resultados/Dxxx.jsonl`: **una línea JSON por fila**, mismo orden:
```
{"id": "DESC-0012", "veredicto": "ok", "tamano_nm": 114.56, "pdi": 0.21, "zeta_mV": -8.1, "etiqueta_muestra": "B1", "metodo_tamano": "DLS", "motivo": "zeta con signo unicode"}
```
`motivo`: máximo 12 palabras. Guarda cada lote al terminarlo. Sin git; no modifiques nada más; no leas `resultados/` de otros lotes.
