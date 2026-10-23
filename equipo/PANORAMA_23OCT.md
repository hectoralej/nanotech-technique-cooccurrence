# Panorama del proyecto (viernes 23 de octubre, tarde) — para el líder

**Plazo:** domingo 25, 5:45 pm. Meta interna: subir el video el domingo antes de las 2 pm. Congelar resultados el sábado a las 3 pm y la web a las 5 pm.

## 1. Dónde estamos
| Frente | Estado | Responsable |
|---|---|---|
| Base de datos v0.1 | Congelada y en GitHub (1.824 leídos, 1.707 con evidencia, 2.726 micrografías, 3.116 filas de medidas, 4.015 espectros) | Héctor |
| Atlas web | Revisado y aprobado; panel del modelo con predicciones reales. Faltan páginas de método/modelos, créditos, capturas, demo | Carlos (+ Bryan) |
| Modelos tabulares | Rondas 1 y 2 hechas y auditadas | Codex de Héctor |
| Modelos de imagen | Vectores ResNet50 y DINOv2 en Kabré; análisis local; sin ajuste fino todavía | Héctor + Claude |
| Figuras del video | 10 figuras con buen estilo; 4 con defectos (ver `encargos/CODEX_RONDA_3.md`, R1) | Codex de Héctor |
| Guion, presentación y video | Sin empezar; ahora de Bryan | Bryan |
| Documentación de decisiones | `equipo/DECISIONES.md` (nuevo) | Claude/Héctor |

## 2. Lo que dice la evidencia (hoy)
- **Tamaño de partícula:** modelos simples R² ≈ 0,24 (frente a 0,18 de la línea base); con banderas de formulación hasta 0,285 con Random Forest, pero la mejora para Ridge incluye el cero y el 30 % de las banderas auditadas fue dudoso. Conclusión: la formulación ayuda poco y las banderas son proxies ruidosos.
- **Clase de portador:** solo con mediciones F1 ≈ 0,51 (frente a 0,12). Con banderas de método y contexto sube a 0,64, pero **no la usaría como cifra principal**: el método (sol-gel, hidratación de película, gelificación iónica) casi delata la clase. Es un hallazgo interesante, no un modelo físico.
- **Imágenes:** con regresión logística F1 0,39; con SVM no lineal 0,47; imagen + medidas 0,55 frente a 0,52 de las medidas (repetible en 5 particiones). Sin fuga por artículo.
- **Lectura honesta:** los resultados son modestos y bien documentados. El profesor lo valoró precisamente por eso.

## 3. Qué dijo el profesor, y qué hacemos con cada cosa
| Sugerencia | Qué haremos | Quién | Cuándo |
|---|---|---|---|
| Mejorar las figuras: separar compuestas | Heurística de franjas blancas (prueba de concepto) y, en el clúster, filtrar recortes de micrografía con un modelo de visión | Codex (R4) + Héctor/Claude | Sábado |
| Más figuras por artículo | Buscar todas las figuras con pie de micrografía y descargarlas | Codex (R3) | Sábado 2 pm |
| Entrenar quitando una clase | Experimento de ablación con los vectores ya calculados | Codex (R2) | Sábado 12 m |
| Ajuste fino en Nukwa | Cuaderno de ajuste fino (CNN y transformer) tras la prueba de humo en Nukwa | Claude + Héctor | Sábado mañana-tarde |
| Documentar todas las decisiones | `equipo/DECISIONES.md`; Bryan lo convierte en contenido del video y del sitio | Bryan | Sábado |
| Otra validación | Validación anidada o externa; fusión con procedencia anidada | Héctor/Claude | Si hay tiempo |
| Contacto con el CNCA | Lo gestiona el profesor; pedir soporte para colas | Héctor | — |

## 4. Camino crítico del sábado
1. **Viernes noche:** prueba de humo en Nukwa (Héctor) → Claude escribe los cuadernos 03 (cuadrantes y alta resolución, en Kura) y 04 (ajuste fino, en Nukwa).
2. **Sábado mañana:** Codex entrega figuras corregidas y ablación; Bryan, guion v1; Carlos, páginas integradas.
3. **Sábado 3 pm:** se congelan los resultados de modelos. Lo que no tenga métricas verificadas pasa a «trabajo futuro».
4. **Sábado 5 pm:** web congelada y grabación de la demo. **Noche:** narración.
5. **Domingo:** montaje, revisión, subida antes de las 2 pm.

## 5. Riesgos y cómo se mitigan
| Riesgo | Mitigación |
|---|---|
| Kabré se llena o interrumpe un trabajo | Puntos de control por época; el producto usa los vectores congelados ya calculados |
| La cuenta de Kabré expira (es por curso) | Bajar resultados a la computadora; no depender de ella tras el domingo |
| Sobredeclarar resultados en el video | Tabla «qué decir / qué no decir» en `encargos/BRYAN.md` |
| Cifras desactualizadas en el video | Un solo origen: `equipo/DECISIONES.md` y los JSON de `modelos/` y `producto/` |
| Choques de archivos entre Bryan y Carlos | Carpetas separadas (ver `encargos/CARLOS.md`) |
| Falta de tiempo en R3/R4 | Son experimentos: si no están validados el sábado a las 3 pm, quedan como trabajo futuro |
