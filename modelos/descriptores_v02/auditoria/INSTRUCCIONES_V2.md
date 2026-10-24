# Auditoría de descriptores v2 (con contexto del artículo)

Cada fila de `lotes_v2/Exxx.json` trae los valores extraídos (`tamano_nm`, `pdi`, `zeta_mV`), la `muestra` (etiqueta), la `cita` guardada (**es solo un fragmento y puede estar truncada**) y `contexto_del_articulo`: la **tabla completa con encabezados** donde aparece la muestra, o el texto alrededor. **Decide con el contexto, no solo con la cita.** No uses conocimiento externo ni inventes valores.

## Decidir por fila
- Localiza en el contexto la fila/frase de **esa muestra** y lee los encabezados de columna (tamaño, PDI, zeta…, unidades).
- `veredicto`:
  - `"ok"`: los tres valores (los que no son null) corresponden a esa muestra y a la columna correcta. **Que la cita no los contenga no es un error** si el contexto sí los tiene.
  - `"corregir"`: el contexto muestra otro valor, una columna cambiada, una muestra equivocada, un radio en vez de diámetro, etc. Da `tamano_nm`, `pdi`, `zeta_mV` correctos (`null` solo si el contexto muestra que esa magnitud no existe para la muestra). **No anules un valor solo porque falta en la cita.**
  - `"descartar"`: el contexto no permite identificar la muestra o el valor, o es otra técnica (TEM/SEM/XRD/Scherrer) sin PDI ni zeta válidos, o es un duplicado exacto.
  - `"no_verificable"`: no hay contexto suficiente para decidir (texto completo no disponible o fila no localizable).
- `etiqueta_muestra`: etiqueta **corta tal como aparece en tablas y figuras** (p. ej. `"B1"`, `"NLC-PTX"`), o `null`.
- `metodo_tamano`: `"DLS"` (hidrodinámico, Z-average, PCS, Zetasizer), `"TEM"`, `"SEM"`, `"AFM"`, `"XRD"`, `"otro"` o `"desconocido"`. Solo lo que el contexto diga.

## Salida
`modelos/descriptores_v02/auditoria/resultados_v2/Exxx.jsonl`: una línea JSON por fila, mismo orden:
```
{"id": "DESC-0012", "veredicto": "ok", "tamano_nm": 114.56, "pdi": 0.21, "zeta_mV": -8.1, "etiqueta_muestra": "B1", "metodo_tamano": "DLS", "motivo": "fila de Tabla 2 coincide"}
```
`motivo`: ≤ 12 palabras. Guarda cada lote al terminarlo. Sin git; no modifiques nada más; no leas `resultados/` ni `resultados_v2/` de otros.
