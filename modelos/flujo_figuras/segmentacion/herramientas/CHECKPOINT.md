# Checkpoint EXSCLAIM — 24/10/2026

Encargo completo leído. Control de fuente terminado; control de licencia NO superado.

Parada exigida por el brief: no se pudo verificar de forma inequívoca la licencia aplicable a los pesos externos. Original además declara GPL-3.0 en LICENSE y MIT en setup.py; actual declara MIT en LICENSE.

No instalar ni descargar pesos hasta resolverlo. No hubo inferencia, cajas ni métricas locales. Hay 22 figuras en el CSV y no hay cajas_humano_*.json al comprobarlo.

Informe: INFORME_EXSCLAIM.md. Auditoría reproducible: auditar_fuentes.py; evidencia en resultados/.

Pendiente: aclaración oficial de licencias, versión fija, entorno aislado, prueba CPU, adaptación de cajas y evaluación. Comparador existente falla potencialmente con menos predicciones y su campo tipo igual está fijado al 100 %; no fue modificado. FigEx2 queda pendiente para HPC y de verificar licencia.
