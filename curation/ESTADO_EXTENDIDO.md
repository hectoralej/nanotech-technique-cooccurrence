# Estado del conjunto ampliado (2026-10-21, madrugada)

## Dónde estamos
- **Texto descargado:** 4.385 archivos en disco; la descarga (`work/ext/fetch.log`) iba en 1.400 de 2.691. Si el proceso se detuvo, se reanuda con `python -m curation.extended fetch`. Después hay que bajar 10 artículos que se agregaron al incluir Raman (el mismo comando).
- **Revisados por código:** 1.690 artículos: E1 1.263, E2 317, no 110.
- **Lotes asignados:** EX001 a EX140 (10 artículos cada uno; EX054 tiene 3). `work/ext/exportados.csv` es la fuente de verdad de qué artículo va en qué lote. EX001–EX054 y EX068–EX140 son E1; EX055–EX067 son E2.
- **Leídos y verificados:** 193 artículos (`python -m curation.extended apply`): E1 120, E2 64, sin categoría 9. 2 citas rechazadas, 0 números no hallados.

## Reparto de lotes
| Rango | Quién | Estado |
|---|---|---|
| EX001–EX016 | Codex | hecho y verificado |
| EX017–EX036 | Codex (corrida de la noche del 20 al 21) | en curso; instrucciones en `BRIEF_CODEX_CORRIDA_FINAL.md` |
| EX052–EX054 | Claude (Haiku) | **hecho** (23 artículos, 0 citas rechazadas) |
| EX037–EX051 | Claude | mañana, con el uso reiniciado |
| EX068–EX140 (E1 nuevos, 730 artículos) | Codex primero, luego Claude lo que quede | mañana |
| EX055–EX067 (E2) | Claude | al final |

## Lo que hay que hacer mañana (en orden)
1. Verificar con `apply` lo que haya entregado Codex (EX017–EX036) y mirar la tasa de citas rechazadas.
2. **Claude:** correr EX037–EX051 con agentes Haiku (unos 15 lotes). Después EX068 en adelante, en el orden que marque `luna_progress.md`, sin tocar lotes que Codex ya tenga.
3. **Unir filas partidas:** los agentes Haiku a veces separan tamaño y zeta de una misma muestra en dos filas (cada una con un campo vacío). Conviene unirlas por nombre de muestra en `apply` o pedirles que no las dividan.
4. Revisar la hoja `verificacion_conjunto_ampliado.csv` que llene Carlos para medir la precisión del extractor.
5. **22 de octubre: congelar la v0.1** con lo que exista, con fecha y etiqueta en GitHub.

## Notas de calidad
- Haiku (EX052–EX054): 23 artículos, 22 en E1. Usó más filas de descriptores por artículo que Codex (2,3 frente a 1,3) por dividir filas, y una muestra quedó sin nombre. Aún no hay una verificación humana de ninguno de los dos extractores.
- Estos tres lotes son del final de la lista de prioridad (menos tipos de espectro en figura), por eso hay más nanomateriales (18 de 23).
- Consumo de Haiku en esta tanda: unos 260 mil tokens para 23 artículos (`consumption_log.csv`).
