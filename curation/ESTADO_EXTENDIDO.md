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

## Checkpoint Claude 20 % (21 oct, manana)
Tanda 1 hecha: EX037-EX041 (50 articulos, ~420 mil tokens de Haiku, ~8,4 mil por articulo; proyeccion de mis 25 lotes: ~2,1 M). Uso: semanal 3 %, 5 horas 18 %. Descarga de textos terminada (2.435/2.435): falta correr screen + packets para los lotes nuevos. Siguiente: tanda 2 = EX042-EX046, luego EX047-EX051, EX068-EX072, EX073-EX077. Los agentes Haiku parten a veces la cita del zeta (solo la frase del tamano); el codigo lo marca.

## Checkpoint Claude 40 % (21 oct)
Tanda 2 hecha: EX042-EX046 (50 articulos, ~400 mil tokens; el consumo de EX042-043 es estimado). Acumulado mio: 100 articulos, ~820 mil tokens. Se corrio screen + packets con la descarga terminada: hay lotes nuevos despues de EX152. Siguiente: tanda 3 = EX047-EX051.

## Checkpoint Claude 60 % (21 oct)
Tanda 3 hecha: EX047-EX051 (50 articulos, ~400 mil tokens; EX047-048 estimado). Acumulado mio: 150 articulos, ~1,2 M tokens. Siguiente: tanda 4 = EX068-EX072, tanda 5 = EX073-EX077.

## Checkpoint Claude 80 % (21 oct)
Tanda 4 hecha: EX068-EX072 (50 articulos, ~410 mil tokens). Acumulado mio: 200 articulos, ~1,6 M tokens. Falta la tanda 5 = EX073-EX077.

## Checkpoint Claude 100 % (21 oct)
Tanda 5 hecha: EX073-EX077. Mis 25 lotes (250 articulos) completos: EX037-EX051 y EX068-EX077. Siguiente: verificar lo de Codex (EX078-EX102), repartir EX103-EX185 y EX055-EX067.

## Checkpoint Claude 100 % (21 oct)
Tanda 5 hecha: EX073-EX077. Mis 25 lotes (250 articulos) completos: EX037-EX051 y EX068-EX077 (~2,3 M tokens de Haiku, 5 % del limite semanal). apply ahora salta filas que no son objetos. Siguiente: verificar EX078-EX102 de Codex, repartir EX103-EX185 y EX055-EX067.
