# Codex: flujo de revisión visual de figuras (por lotes, reanudable)

**Contexto.** La revisión humana mostró que el problema de calidad está en las **figuras**: la mayoría son compuestas (2 o más paneles), mezclan micrografías con espectros, histogramas o esquemas, y varios espectros traen curvas superpuestas. Claude preparó un flujo para clasificar cada figura **mirando la imagen** (no el pie) con hojas de contacto reducidas (6 figuras por hoja, 30 por lote), repartido entre Claude y tú. Todo se guarda por lote; si la sesión se corta, se reanuda donde quedó.

**Reglas de siempre:** no tocar `curation\`, `producto\`, `modelos\imagenes_v02\` ni nada fuera de `modelos\flujo_figuras\resultados\codex\`; no git; no inventar; si una hoja no deja ver, `confianza: 1`.

## Qué hacer
1. Lee **completo** `modelos\flujo_figuras\INSTRUCCIONES_REVISOR.md` (campos, reglas de conteo de paneles y casos frecuentes).
2. `python modelos\flujo_figuras\siguiente_lote.py codex 3` → te dice los próximos lotes pendientes.
3. Para cada lote: abre `lotes\Lxxx.json`, mira las 5 hojas `miniaturas\Lxxx_hN.jpg` con tu herramienta de imágenes y escribe `resultados\codex\Lxxx.jsonl` (30 líneas, una por figura, en orden). **Guarda cada lote al terminarlo.**
4. Cada 3 lotes corre `python modelos\flujo_figuras\consolidar.py`: valida el formato y muestra el progreso. Corrige lo que marque.
5. Trabaja en tandas de **10 lotes** y entrega solo: lotes terminados, nº de figuras con confianza 1 y problemas. Sin resúmenes largos. Tus lotes son los `asignado = codex` o `ambos` (los «ambos» también los hace Claude para medir el acuerdo entre modelos; no los saltes, pero **no mires** `resultados\claude\`).

## Después (cuando Claude lo pida; no antes)
- **T-seg:** con el número de paneles de `figuras_vision.csv` (columna `paneles`) segmentar las figuras `compuesta` y `pareja` en exactamente ese número de recortes (tu segmentador por huecos/componentes; verifica `n_recortes == paneles`) y registrar las que no coincidan para revisión humana. Las `superpuesto` y `excluir` no entran a la tabla del modelo.
- **Espectros:** `tabla_espectros_v02.csv` solo debe incluir paneles de figuras `simple` o paneles espectrales de figuras separadas con `espectro_limpio = si`; nada de `curvas_superpuestas = si`.

## Precisión
- Prioridad 1 de los lotes = imágenes que ya usa el modelo de clase (lotes L001–L069 aprox.); prioridad 2 = el resto útil. Se procesan en ese orden.
- Calidad esperada: Claude y tú se compararán en los lotes «ambos» (conteo exacto de paneles y mismo destino). Si el acuerdo es bajo, se revisa la instrucción, no se culpa a nadie.
