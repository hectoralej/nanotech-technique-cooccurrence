# Auditoría humana de la base v0.1: plan, tiempos y reparto

**Objetivo:** reemplazar el control de calidad «asistido por IA en 20 artículos» por una **estimación de precisión hecha por personas**, con intervalo de confianza, y medir el **acuerdo entre revisores**. Revisar todo es imposible; una muestra aleatoria estratificada (semilla fija, `generar_muestra.py`) basta para estimar la precisión.

## Qué se revisa
| Hoja | Población | Muestra (únicas) | Qué se pregunta | Precisión que permite afirmar |
|---|---:|---:|---|---|
| Descriptores | 3.116 filas | 120 | ¿La cita respalda esos valores para esa muestra? | si ≈ 90 % acierto: ± 5,4 puntos |
| Espectros | 4.015 filas | ~85 | ¿Esa figura muestra esa técnica para esa muestra? | ± 6 puntos |
| Micrografías | 2.726 paneles | ~55 | ¿Es una micrografía de nanopartículas y la variante es correcta? | si 0 errores en 60: error ≤ 5 % (regla de tres) |
Más un subconjunto **común** (15 descriptores, 10 espectros, 6 micrografías) que revisan las tres personas: sirve para el acuerdo (kappa de Fleiss). La muestra está estratificada por clase y las clases raras (cubosoma, nanoemulsión) están sobrerrepresentadas a propósito.

## Cuánto tarda (estimación de Claude, no medida)
Tiempos por ítem: descriptor con cita de texto ≈ 20 s; descriptor con fila de tabla (hay que abrir el artículo) ≈ 75 s (el 59 % de las filas son de tabla); espectro ≈ 25 s; micrografía ≈ 12 s; etiquetar un panel en la hoja ≈ 7 s.

| Opción | Ítems | Tiempo total | Por persona |
|---|---:|---:|---:|
| Revisar todo (exhaustivo) | 9.857 filas + paneles | ≈ 95 horas | imposible |
| **Muestra completa, una sola persona** | 270 únicas + 300 paneles | ≈ 3,2 h | 3,2 h |
| Muestra reducida (80 / 60 / 45), una sola persona | 185 + 300 paneles | ≈ 2,3 h | 2,3 h |
| **Muestra completa repartida entre tres** | 270 únicas + 31 comunes por persona + paneles (30 comunes + 90 propios) | ≈ 3,9 h en total | **≈ 1,3–1,4 h cada uno** |

La muestra completa repartida entre las tres personas cuesta poco más de una hora cada una, tiene intervalos de confianza razonables y **añade una medida de acuerdo entre personas** que una sola persona no puede dar. Reducir la muestra solo ahorra ~50 minutos y ensancha los intervalos.

## Cómo hacerlo
1. Cada persona abre su libro (`Auditoria_Hector.xlsx`, `Auditoria_Bryan.xlsx`, `Auditoria_Carlos.xlsx`), lee la hoja LEEME y responde **sí / no / dudoso** (menú desplegable). Los enlaces abren el artículo (DOI) y la imagen.
2. No se comentan las respuestas hasta terminar (las filas amarillas son las comunes).
3. Los tres libros se envían a Héctor y se ejecuta `python modelos/auditoria_humana/calcular_resultados.py` (precisión con IC de Wilson, acuerdo y desacuerdos): sale `RESULTADOS_AUDITORIA.md`.
4. Con la cifra humana, se actualiza la Figura 9 y el guion («revisión humana en una muestra de N filas»).
**Los «dudoso» no cuentan como acierto ni como error**; se informan aparte.

## Qué no cubre
No revisa si el artículo mismo es correcto; no sustituye la validación externa; el 59 % de las filas de descriptores tiene una cita de tabla donde la pregunta correcta es si la columna es la que dice la IA.
