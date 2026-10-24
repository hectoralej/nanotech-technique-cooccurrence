# Tipología de figuras (a partir del pie)

Clasifica las 6.524 figuras lógicas del inventario sin mirar la imagen: nº de paneles declarado en el pie, clase de cada panel (micrografía, espectro, DLS/zeta, contenido no útil) y tipología.

| Archivo | Qué es |
|---|---|
| `clasificar_figuras.py` | Reglas (léxico de técnicas, etiquetas de subpanel `(a)`, `A)`, rangos `(a–d)`, plurales, indicios de superposición). Reproducible. |
| `tipologia_figuras.csv` | Una fila por figura con tipología, destino, nº de paneles y contraste con la segmentación de Codex. |
| `figuras_simples.csv`, `figuras_pareja.csv`, `figuras_compuestas.csv`, `espectros_superpuestos.csv`, `figuras_multiples_sin_etiquetas.csv` | Bases separadas por destino de depurado. |
| `impacto_en_modelo.py` → `IMPACTO_EN_MODELO.md` | Exactitud del modelo de clase por tipo de figura (IC por bootstrap de artículos). |
| `generar_verificacion.py` → `Verificar_tipologia.xlsx` | 78 figuras (6 por tipología) para comprobar a mano la tipología. |

Límites: es una estimación solo con texto. Los plurales sin lista («FTIR spectra of X») pueden ser una curva o varias; «superpuesto» es probable, no seguro. No sustituye la validación humana: usar `Verificar_tipologia.xlsx` para medir su exactitud real.
