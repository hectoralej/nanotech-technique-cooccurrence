# Informe de revisión asistida — TAREAS_CARLOS_v2

**Fecha:** 21 de octubre de 2026  
**Alcance realizado:** revisión asistida por IA de los 41 casos priorizados de Tarea 1 y cotejo de las 20 filas de Tarea 2 contra páginas, tablas, figuras o PDFs de artículos.  
**Estado:** informe de hallazgos y propuestas; no es una anotación humana ni una aprobación final de los datos.

## Importante sobre el carácter de la revisión

No puedo hacer una revisión *humana* ni registrar decisiones como si fueran tuyas. Lo realizado es una lectura independiente asistida por IA de las fuentes disponibles. Los estados `si/no` de la revisión de Carlos permanecen separados y deben ser decididos por ti al abrir la evidencia. `no_comprobable` significa que la evidencia disponible en esta pasada no permite cerrar la respuesta; no significa automáticamente que el dato sea erróneo.

La revisión de fuentes se apoyó en subagentes de lectura, pero revisé e integré los resultados antes de guardar los artefactos. Ningún subagente modificó los CSV fuente ni escribió al repositorio remoto.

## Artefactos

- [CSV de 20 artículos con propuestas de revisión IA](verificacion_conjunto_ampliado_revision_IA.csv). Es una copia ampliada que agrega columnas terminadas en `_revision_IA`; las columnas de Carlos se conservaron vacías.
- [CSV de trabajo humano para Tarea 2](verificacion_conjunto_ampliado_carlos.csv). Sigue sin respuestas humanas.
- [Plantilla humana de Tarea 1 con 68 filas](verificacion_repositorio_verde_pre_IA_plantilla.csv). Mantiene valores preexistentes con sufijo `_pre_IA` y las columnas `_humano` vacías.
- [Pistas de licencia de Tarea 1](evidencia_preliminar_licencias_tarea1.md).
- [Notas de evidencia por artículo de Tarea 2](evidencia_preliminar_tarea2.md).
- [Estado y preparación general](estado_y_preparacion.md).

## Qué hice

1. Cotejé los 20 artículos del conjunto ampliado contra la evidencia citada (caption/figura, tabla de caracterización y/o texto de métodos cuando estuvo disponible).
2. Añadí a un archivo separado una propuesta IA para micrografías, descriptores, espectros, condición de nanotransportador y licencia, con una nota de evidencia y enlace de fuente por fila.
3. Revisé 41 casos únicos de Tarea 1: los cinco DOI con aviso editorial o discrepancia priorizada, los ocho controles seleccionados y las filas con señales de riesgo o incertidumbre en la preparación previa. Las propuestas de Tarea 1 quedan resumidas abajo y las pistas completas de licencias están en el archivo enlazado.
4. Conservé la separación entre evidencia/propuesta de IA y decisiones humanas. No hice cambios en GitHub.

## Resultados de Tarea 2: 20 filas

| Campo cotejado | Propuesta `si` | Propuesta `no` | `no_comprobable` | Observación |
|---|---:|---:|---:|---|
| Micrografías | 19 | 0 | 1 | Una fila necesita revisar captions directamente. |
| Descriptores | 9 | 1 | 10 | En varias filas los descriptores no se extrajeron; esos vacíos no se cuentan como falsedad. |
| Espectros | 14 | 2 | 4 | Hay asignaciones de figura potencialmente equivocadas y dos campos no cerrados. |
| ¿Es nanotransportador? | 20 | 0 | 0 | Los 20 artículos describen sistemas de transporte a escala nano según su título/métodos. |
| Licencia visible | 14 | 0 | 6 | Se propone `no_comprobable` cuando no se verificó la etiqueta del artículo de forma suficiente en fuente editorial. |

### Hallazgos que requieren atención

- **Fila 2:** existe una discrepancia entre las notas de lectura sobre la Fig. 4 (XRD frente a gráficos de superficie de respuesta). La página del editor no pudo recuperarse durante el cotejo; por eso la propuesta de espectro queda `no_comprobable`, no `si` ni `no`. [Artículo MDPI](https://www.mdpi.com/1999-4923/17/4/478).
- **Fila 9:** los valores extraídos describen B-PLN1–3, mientras que la micrografía destacada es de B-PLN4. Es una alerta de correspondencia de muestra; no demuestra por sí sola que los valores sean incorrectos.
- **Fila 12:** las medidas de Tabla 2 están respaldadas, pero queda por comprobar la correspondencia entre la formulación nombrada en la fila y la muestra de la micrografía TEM. La asignación de UV-Vis no quedó suficientemente sustentada en la revisión y se dejó como propuesta `no` con nota para que Carlos coteje la caption.
- **Fila 14:** se extrajeron F1–F3, pero el artículo incluye F1–F5 antes/después de liofilización; extracción parcial.
- **Fila 16:** posible cruce/duplicación de descriptores entre LipoPEI vacía y complejos con pDNA; la propuesta de descriptores es `no` y exige cotejo de cada formulación.
- **Fila 17:** una curva de UV-Vis corresponde a taurina libre, no al nanotransportador; propuesta `no` para esa asignación espectral.
- **Fila 18:** el UV-Vis citado puede corresponder a liberación/estándares y no a un espectro de partícula aislada. Los descriptores de tamaño/zeta no se extrajeron, por tanto están `no_comprobable`.
- **Fila 20:** las figuras capturadas son compatibles con el artículo, pero la extracción parece parcial en paneles/formulaciones. La nota lo deja explícito.
- **Filas 3, 4, 5, 7, 10, 11, 13, 15:** persisten puntos no verificables (caption, descriptores completos o licencia específica). El detalle por fila, con enlaces, está en el CSV IA.

## Resultados de Tarea 1: 41 casos priorizados

### Confirmaciones o discrepancias concretas

- **n=6:** artículo confirma 98 nm, potencial zeta −38.66 ± 0.33 mV y liposomas esféricos por TEM.
- **n=12:** la tabla confirma 205 ± 4 nm y +48 ± 2 mV; la Fig. 7 es TEM de PLNs. Falta resolver la correspondencia de muestra con la fila que la describe como liposoma 2X3/DOPE.
- **n=13:** confirma 248.98 ± 4.0 nm y −33.45 ± 0.48 mV; Fig. 1B TEM y 1D SEM de FN-SLN.
- **n=20:** Tabla 1 confirma 128 ± 4 nm y −4.2 ± 1.1 mV para LAmB; DLS en agua, zeta en NaCl 0.9%; Fig. 1A Cryo-TEM.
- **n=22:** tabla y Fig. 3A respaldan tamaño/zeta de liposomas vacíos y TEM; licencia CC BY 4.0.
- **n=24:** Lipo 105.3 ± 0.55 nm y −12.8 ± 1.6 mV; el artículo describe medición en agua desionizada. El corrigendum afecta Fig. 7I, no Fig. 4A SEM usada aquí. No se debe extender el aviso a la caracterización de Fig. 4A.
- **n=31:** la licencia es CC BY 3.0 (no 4.0); los campos científicos señalados no se cotejaron independientemente en esta pasada.
- **n=35:** discrepancia importante: la tabla reporta −23.2 **meV**, mientras que la fila usa mV como potencial zeta. El tamaño 130 nm coincide. Requiere revisar unidad/campo antes de aceptar.
- **n=46:** valores 174 nm y +17.7 mV, con medio agua, compatibles; la figura de SEM indicada aún requiere cotejo independiente.
- **n=50:** Tabla 1 confirma Ag NPs 59.8 ± 2.8 nm y +25.7 ± 1.5 mV en agua desionizada; el artículo usa TEM (Fig. 4) y SEM (Fig. 6), que no son contradictorios.
- **n=55:** se confirmó una corrección editorial de 2024 que reemplaza imágenes de Fig. 5; la Fig. 1c de la fila no es el panel corregido.
- **n=59:** Tabla 3 confirma 180 ± 0.208 nm y −32.4 ± 0.1 mV para el gel cargado. Los valores de 329 nm y TEM cercano a 200 nm pertenecen al gel combinado, no a esta formulación: revisar correspondencia de muestra.
- **Licencias exactas identificadas en fuentes consultadas:** n=1 CC BY 4.0; n=24 CC BY 4.0; n=26 CC BY 4.0; n=31 CC BY 3.0; n=33, 39, 47, 50–56, 59–60, 62–63 y 65 incluyen confirmaciones de licencia detalladas en el memo de Tarea 1. n=27 y n=61 tienen Creative Commons Attribution sin versión confirmada; n=48 permanece discrepante/no confirmada directamente.

### Casos donde el cotejo científico quedó incompleto

No se adoptaron automáticamente los `no` que ya aparecían en la pre-IA. Falta verificación humana independiente de los campos en **n=2, 7, 23, 29, 30, 32, 38, 41, 42, 57 y 64**. Además, el cotejo de campos marcados como dudosos en **n=1, 12, 13, 15, 20, 24, 27, 35, 46, 48, 50, 55, 59 y 61** quedó parcial: la confirmación de un campo no cierra los demás.

El memo de licencias explica la evidencia y límites de las **22 licencias** objetivo. En particular, n=48 aún requiere resolver una discrepancia CC BY frente a CC BY-NC; n=27 y n=61 no tienen versión numérica cerrada. Una pista de licencia no debe copiarse al campo humano sin abrir la etiqueta del artículo correspondiente.

## Qué queda pendiente

- Tú debes decidir y anotar los campos humanos de las 20 filas de Tarea 2 y de la cola Tarea 1; la IA no ha firmado esas columnas.
- Cotejar directamente las captions/tablas para los casos no comprobables y las correspondencias de muestra señaladas, en particular T2 filas 2, 9, 12, 16 y 20; T1 n=12, 24, 35, 50 y 59.
- Completar verificación editorial de licencias con etiqueta del artículo, especialmente las marcadas `no_comprobable` en el CSV de Tarea 2 y n=48, n=27, n=61 en Tarea 1.
- No se resolvieron aquí los 70 avisos editoriales inconclusos ni se realizó la doble anotación humana de la fase 1; siguen diferidos según el estado de preparación.

## Límite y trazabilidad

Las etiquetas en `verificacion_conjunto_ampliado_revision_IA.csv` son recomendaciones revisables, no verdades finales. En la copia humana, las seis columnas de decisión/notas de las 20 filas siguen vacías (0 filas con contenido humano al cierre de este informe). No se alteró el archivo fuente descargado ni se envió ningún cambio a GitHub.
