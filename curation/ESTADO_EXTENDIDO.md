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

## Checkpoint Claude 20 % (EX103-EX127, 21 oct)
Tanda 1 hecha: EX103-EX107 (50 articulos, ~420 mil tokens de Haiku). apply: 953 articulos leidos (E1 562, E2 333, no 58), 2 citas rechazadas (sin nuevas). Uso: semanal 6 %, 5 horas 45 %. Siguiente: tanda 2 = EX108-EX112.

## Checkpoint Claude 40 % (EX103-EX127, 21 oct)
Tanda 2 hecha: EX108-EX112 (50 articulos, ~400 mil tokens). apply: 1.023 articulos leidos (E1 605, E2 353, no 65), 2 citas rechazadas (sin nuevas). Uso: semanal 7 %, 5 horas 48 %. Siguiente: tanda 3 = EX113-EX117.

## Checkpoint Claude 60 % (EX103-EX127, 21 oct)
Tanda 3 hecha: EX113-EX117 (50 articulos, ~410 mil tokens). apply: 1.103 articulos leidos (E1 646, E2 384, no 73), 2 citas rechazadas (sin nuevas). Uso: semanal 7 %, 5 horas 51 %. Siguiente: tanda 4 = EX118-EX122, luego EX123-EX127.

## Checkpoint Claude 80 % (EX103-EX127, 21 oct)
Tanda 4 hecha: EX118-EX122 (50 articulos, ~430 mil tokens). apply: 1.153 articulos leidos (E1 675, E2 403, no 75), 2 citas rechazadas (sin nuevas). Uso: semanal 7 %, 5 horas 53 %. Falta la tanda 5 = EX123-EX127.

## Checkpoint Claude 100 % (EX103-EX127, 21 oct)
Tanda 5 hecha: EX123-EX127. Mis 25 lotes (250 articulos) completos: EX103-EX127 (~2,1 M tokens de Haiku). apply: 1.233 articulos leidos (E1 730, E2 425, no 78), 2 citas rechazadas (sin nuevas); 1.488 paneles, 1.649 descriptores, 2.395 espectros (incluye lo que Codex lleva de EX078-EX102). Uso: semanal 8 %, 5 horas 56 %. Siguiente: verificar EX078-EX102 y EX128-EX160 (Codex); quedan por repartir EX161-EX185 (E1) y EX055-EX067 (E2).

## Checkpoint Claude E1 20 % (EX161-EX185, 21 oct)
Tanda 1 hecha: EX161-EX165 (50 articulos, ~420 mil tokens). apply: 1.506 articulos leidos (E1 804, E2 566, no 136), 2 citas rechazadas (sin nuevas). Uso: semanal 8 %, 5 horas 60 %. E2 (EX055-EX067) lo hace Codex con BRIEF_CODEX_CORRIDA_5.md. Siguiente: tanda 2 = EX166-EX170.

## Checkpoint Claude E1 40 % (EX161-EX185, 21 oct)
Tanda 2 hecha: EX166-EX170 (50 articulos, ~390 mil tokens). apply: 1.586 articulos leidos (E1 838, E2 606, no 142), 2 citas rechazadas (sin nuevas). Uso: semanal 9 %, 5 horas 63 %. Siguiente: tanda 3 = EX171-EX175.

## Checkpoint Claude E1 60 % (EX161-EX185, 21 oct)
Tanda 3 hecha: EX171-EX175 (50 articulos, ~400 mil tokens). apply: 1.656 articulos leidos (E1 870, E2 635, no 151), 2 citas rechazadas (sin nuevas). Uso: semanal 9 %, 5 horas 67 %. Siguiente: tanda 4 = EX176-EX180, luego EX181-EX185.

## Checkpoint Claude E1 80 % (EX161-EX185, 21 oct)
Tanda 4 hecha: EX176-EX180 (50 articulos, ~400 mil tokens). apply: 1.726 articulos leidos (E1 894, E2 674, no 158), 2 citas rechazadas (sin nuevas). Uso: semanal 10 %, 5 horas 70 %. Falta la tanda 5 = EX181-EX185 (46 articulos).

## Checkpoint Claude E1 100 % (EX161-EX185, 21 oct)
Tanda 5 hecha: EX181-EX185. Mis 25 lotes E1 (236 articulos) completos (~2,0 M tokens de Haiku). apply: 1.772 articulos leidos (E1 921, E2 691, no 160), 2 citas rechazadas (sin nuevas); 2.042 paneles, 2.244 descriptores, 2.974 espectros. Uso: semanal 10 %, 5 horas 73 %. Codex ya lleva EX055-EX061 de E2 (BRIEF_CODEX_CORRIDA_5.md); faltan EX062-EX067. Siguiente: unir filas partidas, muestra de revision para Carlos (incluida la duda de la velocidad de Codex), congelar v0.1.

## Cierre de extraccion (21 oct, noche)
Todos los lotes EX001-EX185 tienen salida. apply: 1.824 articulos leidos (E1 932, E2 717, sin categoria 175), 2 citas rechazadas; 2.092 paneles, 2.314 descriptores, 3.005 espectros. Codex E2 (EX055-EX067): 122 articulos, 1,58 descriptores/articulo, 4 vacios; cada lote 1-5 min segun luna_progress.md; Codex no afirma lectura integra de los paquetes. Rendimiento por articulo (descriptores): Codex EX128-EX160 0,54 frente a Claude 1,65-1,80: revisar con muestra a mano (posible lectura superficial).

## Repaso de Codex (21 oct, noche)
Comparacion con Haiku sobre 50 articulos (EX130,137,144,151,158): Codex 28 filas de descriptores y 45 tecnicas de espectro frente a 68 y 78 de Haiku; en 25 de 50 articulos Haiku hallo un espectro que Codex no. Rendimiento bajo en EX078-EX102 (0,44 desc/art) y EX128-EX160 (0,16-0,67). Decision: Codex repasa esos 58 lotes con BRIEF_CODEX_REPASO_RIGUROSO.md (salida en work/llm/E_v2/, auditoria en work/ext/auditoria_E_v2.md). Pendiente de Claude: fusionar E y E_v2 (mejor por articulo) en apply y verificar citas de E_v2. Los 5 lotes de Haiku para la comparacion estan en el scratchpad de la sesion (no en el repo).

## Repaso riguroso de Codex fusionado (21 oct, tarde)
Codex entrego E_v2 de los 58 lotes (EX078-EX102, EX128-EX160; 573 articulos; 1,80 desc/art y 2,20 espectros/art frente a 0,2-0,7 antes). apply ahora une E y E_v2 (dedup por fig/muestra/tecnica; cada fila se verifica) y repara comas finales en memoria (E_v2/EX143.json tenia una). Resultado: 1.824 articulos, E1 1.130, E2 577, no 117; 2.726 paneles, 3.251 descriptores, 4.015 espectros; 2 citas rechazadas, 35 numeros no hallados (anulados); solo 11 citas v2 pasan de 25 palabras. Codex dice que quedan citas largas y filas de tabla por completar: no bloquea.
