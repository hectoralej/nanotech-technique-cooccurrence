# Cuaderno 06: ¿ayuda preentrenar con NFFA-EUROPE (SEM) antes de ajustar con nuestros recortes?

**Resultado: no.** Fuente de todas las cifras: `modelos/comparacion/entrada_kabre/06_nffa/` (`metricas_06.json`, `tabla_brazos.csv`, `metricas_etapa1.json`, `log_descarga.json`).

**Diseño (fijado antes de ver resultados).** DINOv2 ViT-S/14 (LVD-142M), la receta del cuaderno 04, 5 particiones por artículo, 3 semillas por brazo, 1.114 artículos comunes. Métrica única: F1 macro por artículo con las probabilidades promediadas entre semillas; IC 95 % por bootstrap de artículos (2.000).
- **A (línea base):** LVD → nuestros recortes.
- **B:** LVD → NFFA (7 morfologías, 8.204 teselas de entrenamiento y 912 de validación, 8 épocas) → nuestros recortes.
- **C (control):** igual que B, pero con las etiquetas de NFFA mezcladas al azar.

NFFA-EUROPE Majority SEM, registro B2SHARE `1nysp-05236`, licencia CC BY 4.0. Se usaron 7 de 10 carpetas (Particles, Powder, Nanowires, Fibres, Films_Coated_Surface, Porous_Sponge, Biological), con la banda blanca de metadatos del instrumento recortada. Md5 verificado en las 7.

| Brazo | Exactitud (media ± sd) | F1 macro (media ± sd) | F1 macro (ensamble de 3 semillas) |
|---|---:|---:|---:|
| A | 0,548 ± 0,008 | 0,505 ± 0,010 | 0,521 |
| B | 0,533 ± 0,011 | 0,487 ± 0,011 | 0,502 |
| C | 0,511 ± 0,010 | 0,464 ± 0,011 | 0,476 |

| Diferencia (ensamble) | ΔF1 macro | IC 95 % |
|---|---:|---|
| B − A | −0,019 | [−0,042, +0,005] |
| B − C | +0,026 | [+0,001, +0,050] |
| C − A | −0,045 | [−0,070, −0,020] |

Por semilla, B − A = −0,033, −0,033 y +0,013.

**Lectura.** NFFA no mejora (el IC de B − A incluye 0 y el centro es negativo). Mezclar las etiquetas daña el modelo de forma clara (C − A). Las etiquetas reales de NFFA parecen evitar ese daño, pero sin superar la línea base (B − C apenas excluye 0). En NFFA el modelo llegó a 0,968 de exactitud interna: tarea fácil, poco que aprender.

**Límites.** La etapa 1 corrió una vez (semilla 0). Una sola configuración (8 épocas, lr 3e-5, ajuste completo, 224 px). La etiqueta «Particles» de NFFA es ruidosa. No se probó 384 px ni MicroNet con ResNet50.

**Efecto de las semillas (brazo A).** El ensamble de 3 semillas mejora ≈ +0,013 de exactitud y +0,016 de F1 macro frente a una semilla: el modelo final usa ensamble.
