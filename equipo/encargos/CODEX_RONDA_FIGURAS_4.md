# Codex: ronda 4 de figuras (24-oct) — reglas nuevas, re-revisión y cajas de paneles

Gracias por el informe de EXSCLAIM!: aplicaste bien la regla de parada (licencia sin aclarar) y detectaste un defecto real en `comparar_cajas.py` (tipo fijado a 100 % y fallo con menos cajas); **ya está corregido**. Decisión: **EXSCLAIM! y FigEx2 se descartan por ahora** (licencia de pesos sin declarar; FigEx2 sin ninguna licencia). No hagas más trabajo sobre ellos.

Reglas de siempre: sin git; no tocar `curation\`, `producto\`, `modelos\imagenes_v02\`; escribe solo en tus carpetas `resultados\codex\` y `cajas\resultados\codex\`; no mires `resultados\claude\` ni `cajas\resultados\claude\`; no inventes; baja la confianza si no se ve.

## 0. Reglas nuevas (verificación humana de Héctor, 24-oct)
Relee los casos frecuentes de `modelos\flujo_figuras\INSTRUCCIONES_REVISOR.md` y completa `modelos\flujo_figuras\segmentacion\INSTRUCCIONES_CAJAS.md` (v2). Cambios:
1. **Fluorescencia, confocal, histología (H&E), citometría y fotos de células/animales → `n_otro`**, no `n_micro`. Solo TEM, SEM, STEM, AFM, cryo-EM y microscopía óptica/DIC de partículas o muestras son `micro`.
2. **Espectros en cascada** (curvas de muestras **distintas**, desplazadas verticalmente sin solaparse, eje x compartido): **un panel `n_espectro` por curva**, `curvas_superpuestas: "no"`, campo opcional `"cascada": true`. Curvas que **se cruzan o solapan sobre los mismos ejes** → **un solo panel** con `curvas_superpuestas: "si"`.
3. **Gráficos con ejes propios** bajo una misma letra → un panel por gráfico.
4. **Insets** (recuadros ampliados): no cuentan como panel; en las cajas se registran como **hijas** (`"padre": k, "rel": "inset"`).

## 1. Re-revisión con las reglas nuevas (primero; son pocas)
`python modelos\flujo_figuras\siguiente_lote.py codex 10` → te saldrán los lotes **R002, R004, …** (8 lotes, 30 figuras cada uno: figuras ya clasificadas con posible fluorescencia/histología o curvas superpuestas). Mismo procedimiento y formato que los lotes L (un `.jsonl` por lote en `resultados\codex\Rxxx.jsonl`, checkpoint por lote). Estas filas **reemplazan** a las anteriores de esas figuras; juzga la imagen desde cero con las reglas nuevas.

## 2. Lotes de clasificación L que te quedan
Después de los R, el mismo comando te seguirá dando los L pendientes (≈ 27). Tandas de 15 lotes, validación aislada cada 5, igual que hasta ahora.

## 3. Cajas de paneles (nuevo)
`python modelos\flujo_figuras\segmentacion\siguiente_lote_cajas.py codex 10`. Cada lote `Cxxx` (10 figuras) está en `segmentacion\cajas\lotes\Cxxx.json`: por figura trae una imagen con **cuadrícula roja cada 0,1** (campo `grid`) y el nº de paneles esperado (estimación). Marca una caja por panel según `INSTRUCCIONES_CAJAS.md` v2 (coordenadas 0–1, orden de lectura; hijas para insets; una caja por curva en cascada) y escribe `segmentacion\cajas\resultados\codex\Cxxx.json`. Cada 5 lotes corre `python modelos\flujo_figuras\segmentacion\consolidar_cajas.py`: valida (estructura, solapes, hijas dentro de su padre, nº de paneles útiles) y manda a la cola lo dudoso.
Referencia de calidad: Haiku obtuvo IoU 0,89 frente a las cajas humanas de Héctor; apunta a lo mismo. Prefiere cajas algo holgadas (≈ 1 %) a cajas que corten un panel.

## Entrega
Al terminar cada tanda responde solo con: lotes terminados (R / L / C), nº de figuras dudosas y problemas. Prioridad de orden: **1 (R) → 2 (L) → 3 (C)**.
