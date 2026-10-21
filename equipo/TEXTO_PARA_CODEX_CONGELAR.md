# Texto para pegar en Codex (adjunta o indica el archivo del brief)

Hola Codex. Tu repaso riguroso de EX078–EX102 y EX128–EX160 salió muy bien: ya está fusionado en la base (1.824 artículos; E1 1.130, E2 577; 3.251 descriptores; 4.015 espectros) y las citas pasan la verificación por código. Gracias.

Te dejo una última tarea de cierre: **congelar la versión 0.1** de la base. Las instrucciones completas están en `curation\BRIEF_CODEX_CONGELAR_V01.md` dentro de `C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence`. Léelo entero antes de empezar. En resumen:

1. **Primero, 5 minutos:** contesta por escrito, en `curation\work\ext\explicacion_corrida_rapida.md`, por qué tu corrida anterior de EX128–EX160 fue tan rápida (17 minutos para 33 lotes) y extrajo tan poco, mientras que el repaso riguroso salió bien. Quiero entender qué cambió para mejorar las instrucciones; no es un reproche.
2. **Unir filas partidas de descriptores** (tamaño y zeta de la misma muestra en filas distintas) con un cambio mínimo en la función `apply` de `curation\extended.py`, con las reglas del brief: no inventar, no unir muestras distintas, no tocar columnas.
3. **Validar** los 4 CSV `ext_*` y escribir el informe de validación.
4. **Documentar** la versión en la carpeta `curation\v0.1\` (LEEME con diccionario de columnas, cambios, validación, resumen de números en JSON y checksums).

Plazo: jueves 22 de octubre, 6 pm. No ejecutes git ni hagas push. Cuando termines, dame un reporte corto con cifras antes/después y lo que no pudiste verificar; Claude lo revisará después antes de que la etiqueta v0.1 se suba a GitHub.
