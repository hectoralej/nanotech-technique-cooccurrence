# Qué técnicas capturar y qué pares imagen–espectro son realistas

Base: 2.025 artículos de acceso abierto (2018–2026), 7 familias de nanoportadores, texto completo de Europe PMC.

## Hallazgos

1. **DLS, zeta y TEM dominan en lípidos y polímeros.** Según la familia: DLS 48–91 %, zeta 46–91 %, TEM 32–68 %. En inorgánicas mandan UV-Vis (68 %), TEM (62 %) y SEM (49 %); DLS y zeta bajan a ~42 %.
2. **Las técnicas secundarias van en bloque: UV-Vis, SEM, FTIR y XRD.** Se reportan juntas: FTIR–XRD (phi 0,39 en orgánicas, 0,49 en inorgánicas), y en inorgánicas EDS con SEM (0,43) y con XRD (0,47). DLS y zeta son la pareja más fuerte (0,73). El resto casi no se correlaciona.
3. **AAV es la excepción.** DLS 5 % y zeta 3 %, pero qPCR/ddPCR 75 %. Solo 19 % de los artículos de AAV traen microscopía (TEM 65 %, cryo-EM 44 % de esos), y 87 % de ellos trae también qPCR/ddPCR o ultracentrifugación; solo 9 % trae DLS.
4. **El qPCR fuera de AAV es otra cosa.** Aparece en 9–37 % de los artículos (LNP 37 %), pero aprox. 74 % de los fragmentos hablan de expresión génica (RT-qPCR) y solo 3 % de título de vector (clasificación por palabras clave). Es una lectura biológica del efecto, no una caracterización del nanoportador.
5. **Pares imagen–espectro: abundantes por artículo, escasos por figura.** Entre los artículos con micrografía, 50–89 % traen también un espectro, pero solo 4–31 % lo muestran en la misma figura (inorgánicas 31 %, liposomas 20 %, poliméricas 17 %).

## Qué decidir

- **Capturar siempre:** DLS, zeta, TEM, SEM, UV-Vis y el estado de preparación de la muestra de microscopía electrónica (con la opción «no declarado»).
- **Capturar como opcional:** FTIR, XRD, DSC/TGA, RMN y cryo-EM (relevante en LNP y AAV).
- **Solo una bandera de texto:** EDS (salvo inorgánicas), AFM, NTA, SAXS, XPS, Raman. SAXS aparece en muy pocos artículos: no vale un módulo.
- **Separar dos campos de PCR:** «qPCR de título» (útil en AAV) y «RT-qPCR de expresión» (resto). Son cosas distintas.
- **Para AAV:** El par útil es micrografía + título o lleno/vacío (qPCR, ultracentrifugación), no micrografía + DLS.
- En inorgánicas, 60 % de los artículos con microscopía electrónica muestran TEM sin declarar tinción ni cryo.

## Pares micrografía + espectro en la misma figura (estimación para la literatura abierta 2018–2026)

| Familia | En la misma figura | Artículos estimados |
|---|---|---|
| Inorgánicas | 31 % | ≈ 4.170 |
| Poliméricas | 17 % | ≈ 860 |
| Liposomas | 20 % | ≈ 670 |
| LNP | 10 % | ≈ 110 |
| SLN/NLC | 4 % | ≈ 30 |
| PLN | 8 % | ≈ 10 |

## Antes de confiar

- La validación del detector la hice yo, sola y con un conjunto pequeño (56 artículos). Falta que dos personas del equipo lo revisen.
- Tu observación de que un modelo puede aprender solo de micrografías de vectores virales no se puede comprobar con estos datos. Solo vemos que, en AAV, la imagen viene con títulos y no con tamaño o zeta. Adenovirus no está en la muestra.
- Una parte de los artículos de liposomas, inorgánicas y AAV usa el material como herramienta y no estudia el nanoportador. «Misma figura» y la separación expresión/título del qPCR son aproximaciones por texto.

## Figuras

- `entrega/decision_1_que_capturar.png`: Qué capturar. Cuanto más oscura la celda, más artículos reportan la técnica. De aquí salen los niveles de captura.
- `entrega/decision_5_que_se_correlaciona.png`: Qué se correlaciona. Cada línea une técnicas que aparecen juntas más de lo esperado. DLS, zeta y TEM forman un bloque; FTIR, XRD, EDS, SEM y DSC/TGA, otro.
- `entrega/decision_4_AAV_excepcion.png`: AAV frente al resto. AAV casi no usa DLS ni zeta y se apoya en qPCR/ddPCR.
- `entrega/decision_3_pares_imagen_espectro.png`: Pares imagen–espectro. Azul: emparejar por artículo. Naranja: por figura. Decide con qué familia empezar.

Diagrama del procedimiento: `entrega/diagrama_procedimiento.svg`. Informe completo: `REPORT.md`.
