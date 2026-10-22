# Checkpoint congelación v0.1

Fecha: 2026-10-21

## Hecho

- Leídos `BRIEF_CODEX_CONGELAR_V01.md`, `TEXTO_PARA_CODEX_CONGELAR.md`, `PUNTO_DE_REINICIO.md` y `PLAN_EQUIPO_FINAL.md`.
- Creada `explicacion_corrida_rapida.md`, separando los hechos registrados de lo que solo puede inferirse.
- Ejecutado `python -m curation.extended apply` como línea base.

## Línea base

- Artículos: 1.824 (E1 1.130, E2 577, no 117).
- Paneles: 2.726.
- Descriptores: 3.251.
- Espectros: 4.015.
- Citas rechazadas: 2.

## Perfil de posibles uniones

En `ext_descriptores.csv`, una normalización conservadora de nombres detecta 134 grupos de más de una fila (275 filas candidatas). Dentro de esos grupos, 12 contienen valores numéricos distintos en el mismo campo, 3 tienen medios declarados distintos y 73 tienen textos `source` distintos. Los grupos con contradicciones no deben unirse.

## Decisión de Héctor y resultado

Héctor autorizó unir aunque `source` difiera, conservar el `source` de la fila principal y añadir `source_principal`, `source_secundaria` y `quote_secundaria` a `filas_unidas.csv`. Se mantiene la regla de no unir si se contradicen números o medios declarados.

- `apply` final: 1.824 artículos (E1 1.130, E2 577, no 117), 2.726 paneles, 3.116 descriptores y 4.015 espectros; 135 uniones auditadas.
- Validación: sin referencias huérfanas, discrepancias de archivo/figura ni artículos E1/E2 sin panel o E1 sin descriptor/espectro. Cinco valores extremos y una repetición de muestra/mediciones con medios/fuentes distintos permanecen sin corregir.
- Documentación y artefactos de congelación: `curation/v0.1/`.
- Las salidas `E` y `E_v2` no se modificaron. No se ejecutó `git`.
