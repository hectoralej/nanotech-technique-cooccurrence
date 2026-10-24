# Estado del flujo de figuras — checkpoint 24-oct (noche) · cómo reanudar

## Qué se hizo (todo en GitHub)
- **Tipología por pie** (`modelos/tipologia_figuras/`) y **clasificación visual por lotes** (`modelos/flujo_figuras/`): 4.429 de 5.539 figuras clasificadas (80 %). Solo ~17 % son figuras de un único panel; ~63 % tienen 3 o más.
- **Auditoría a ciegas** de la clasificación: 47/48 (97,9 %) en número de paneles. **Cajas humanas de referencia** (Héctor, 22 figuras, 120 paneles) en `segmentacion/anotador/`; Haiku vs humano: IoU 0,89 (100 % ≥ 0,7) en las figuras con el mismo criterio.
- **Reglas v2** (`INSTRUCCIONES_REVISOR.md`, `segmentacion/INSTRUCCIONES_CAJAS.md`): insets = cajas hijas; curvas en cascada = una caja por curva; curvas solapadas = un panel; fluorescencia/histología/TEM-SEM biológicos = «otro» con `tecnica` y `contenido` (opción C). EXSCLAIM!/FigEx2 **descartados** (licencias de pesos sin declarar; FigEx2 sin licencia).
- **Cajas de paneles** (Haiku, rejilla 0,1): 815 figuras con cajas válidas (3.774 recortes), 125 en cola. Recortes en `producto/imagenes_recortes/paneles_v02/` (no van a Git).

## Cómo reanudar (cualquier sesión)
1. `python modelos/flujo_figuras/consolidar.py` → `figuras_vision.csv`, `bases/*.csv`, `cola_desacuerdos.csv`, `PROGRESO.md` (lee lotes L, R y A; A > R > L).
2. `python modelos/flujo_figuras/segmentacion/consolidar_cajas.py` → `cajas/paneles.csv`, `cajas/cola_cajas.csv`, hojas de revisión `cajas/revision/R###.jpg`.
3. Pendientes de Claude: `python modelos/flujo_figuras/siguiente_lote.py claude 20` (lotes A de arbitraje, Sonnet; ver `INSTRUCCIONES_ARBITRO.md`) y `python modelos/flujo_figuras/segmentacion/siguiente_lote_cajas.py claude 20` (cajas: C107–C113 sin hacer; C187–C193 pueden estar en curso). Un lote está hecho si existe su archivo en `resultados/claude/` o `cajas/resultados/claude/`.
4. Pendientes de Codex (texto en `equipo/encargos/CODEX_RONDA_FIGURAS_4.md` y `modelos/flujo_figuras/INSTRUCCIONES_BIO.md`): lotes **B** (contenido biológico, 69 lotes, prioridad), luego L, R y C. Consolidar B: aún no hay script (`consolidar_bio.py` por escribir: leer `resultados/codex/B*.jsonl` + `bio_plan.csv`).
5. Límite de agentes en paralelo: 20. Haiku ≈ 40 k tokens por lote de clasificación y ≈ 40 k por lote de 10 figuras de cajas.

## Pendiente (en orden)
1. Terminar lotes A (árbitros) y cajas C107–C113, C187–C193; consolidar y subir.
2. Escribir `consolidar_bio.py` y cruzar `contenido` con `elegible_morfologia` de `paneles.csv`.
3. **Excel con muestra de la cola** (≈ 100–200 figuras) para medir la exactitud real; auditoría humana de 200 paneles recortados (IC de Wilson).
4. Segunda ronda de cajas sobre la cola y las figuras de Codex (lotes C pares).
5. Cuaderno 04 en Kabré: clasificador de clase con recortes `elegible_morfologia` frente a figura completa, mismos folds por artículo; con/sin contenido biológico.
6. Entregables: congelado de resultados sáb 3 pm; web sáb 5 pm; vídeo domingo antes de 2 pm; entrega dom 5:45 pm (Costa Rica).

## Decisiones vigentes (resumen)
Ver mensajes de esta sesión: reglas de cajas v2; contenido biológico (opción C); precisión antes que recall; no redistribuir pesos de terceros; `figuras_vision.csv` es la base maestra (una fila por figura).
