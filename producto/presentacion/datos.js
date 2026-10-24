window.DATOS = {
 "version": "v0.1",
 "cifras": {
  "leidos": 1824,
  "evidencia": 1707,
  "E1": 1130,
  "E2": 577,
  "micrografias": 2726,
  "descriptores": 3116,
  "espectros": 4015,
  "imagenes_descargadas": 2149
 },
 "qc": {
  "fuente": "equipo/qc_carlos/RESUMEN_QC.md",
  "n_articulos": 20,
  "asistido_por_ia": true,
  "filas": [
   {
    "campo": "Micrografías",
    "si": 19,
    "no": 0,
    "no_comprobable": 1
   },
   {
    "campo": "Descriptores",
    "si": 9,
    "no": 1,
    "no_comprobable": 10
   },
   {
    "campo": "Espectros",
    "si": 14,
    "no": 2,
    "no_comprobable": 4
   }
  ]
 },
 "ejemplos": [
  {
   "pmcid": "PMC8986208",
   "titulo": "In vitro and in vivo characterization of Entacapone-loaded nanostructured lipid carriers developed by quality-by-design approach.",
   "anio": "2022",
   "doi": "https://doi.org/10.1080/10717544.2022.2058651",
   "licencia": "cc by",
   "portador": "NLC",
   "nivel": "E1",
   "microscopia": "SEM",
   "figura": "Figure 3.",
   "cita_panel": "Scanning electron microscopic (SEM) photograph of Entacapone-loaded NLCs.",
   "imagen": "assets/ejemplos/PMC8986208.jpg",
   "imagen_original": "IDRD_A_2058651_F0003_B.jpg",
   "muestra": "optimized Entacapone-NLCs",
   "size_nm": "161.2",
   "pdi": "0.444",
   "zeta_mV": "-28.5",
   "medio": "not_declared",
   "fuente": "Zetasizer; Figure 4 result",
   "cita": "measurement of particle size, PDI, and zeta potential using Malvern Zeta Sizer and found to be 161.2 ± 16 nm, 0.444, and −28.5 mV, respectively"
  },
  {
   "pmcid": "PMC12775131",
   "titulo": "Biomolecular strategy for designing antibiotic-silver nanoparticles conjugate via nitrate reductase mediated β-lactamase inhibition with molecular docking insights.",
   "anio": "2026",
   "doi": "https://doi.org/10.1038/s41598-025-30539-8",
   "licencia": "cc by",
   "portador": "nanomaterial",
   "nivel": "E1",
   "microscopia": "SEM",
   "figura": "Fig. 3",
   "cita_panel": "SEM micrographs illustrating the surface morphology of (a) AgNPs and (b) Amp–AgNPs.",
   "imagen": "assets/ejemplos/PMC12775131.jpg",
   "imagen_original": "41598_2025_30539_Fig3_HTML.jpg",
   "muestra": "Amp–AgNPs",
   "size_nm": "27.26",
   "pdi": "0.192",
   "zeta_mV": "-24.9",
   "medio": "not_declared",
   "fuente": "text",
   "cita": "Amp–AgNPs conjugate was stable (3 months), semi-spherical crystalline, polydisperse (PDI: 0.192), average diameter of 27.26 nm, zeta potential of − 24.9 mV"
  },
  {
   "pmcid": "PMC11945751",
   "titulo": "Ceftriaxone-Loaded Liposomal Nanoparticles for Pulmonary Delivery Against Lower Respiratory Tract Infections: Development and Characterization.",
   "anio": "2025",
   "doi": "https://doi.org/10.3390/ph18030414",
   "licencia": "cc by",
   "portador": "liposome",
   "nivel": "E1",
   "microscopia": "TEM_prep_not_declared",
   "figura": "Figure 1",
   "cita_panel": "TEM images of liposomal NPs; (a) before (200 nm) and (b) after freeze-drying of blank liposomes (500 nm)",
   "imagen": "assets/ejemplos/PMC11945751.jpg",
   "imagen_original": "pharmaceuticals-18-00414-g001.jpg",
   "muestra": "Blank liposome (before freeze-drying)",
   "size_nm": "169.4",
   "pdi": "0.347",
   "zeta_mV": "-50.1",
   "medio": "water",
   "fuente": "Table 2",
   "cita": "169.4 ± 18.0 | 146.1 ± 12.4 | 0.347 ± 0.0 | 0.590 ± 0.0 | −50.1 ± 1.9 | −50.8 ± 1.3"
  },
  {
   "pmcid": "PMC11102914",
   "titulo": "Enhancing therapeutic efficacy: sustained delivery of 5-fluorouracil (5-FU) via thiolated chitosan nanoparticles targeting CD44 in triple-negative breast cancer.",
   "anio": "2024",
   "doi": "https://doi.org/10.1038/s41598-024-55900-1",
   "licencia": "cc by",
   "portador": "polymeric_NP",
   "nivel": "E1",
   "microscopia": "SEM",
   "figura": "Figure 5",
   "cita_panel": "SEM images (A: upper) show spherical and smooth surfaces of nanoparticles of Empty HA-ThCs",
   "imagen": "assets/ejemplos/PMC11102914.jpg",
   "imagen_original": "41598_2024_55900_Fig5_HTML.jpg",
   "muestra": "Empty HA-ThCs-NPs",
   "size_nm": "309.2",
   "pdi": "1.0",
   "zeta_mV": "7.85",
   "medio": "not_declared",
   "fuente": "Results",
   "cita": "For Empty HA-ThCs-NPs, the mean smallest nanoparticle size was 309.2 nm, ZP 7.85 mV with PDI of 1.0."
  }
 ],
 "decisiones": {
  "secciones": [
   "A. Datos",
   "B. Evaluación y modelos",
   "C. Producto y proceso"
  ],
  "filas": [
   {
    "id": "D1",
    "seccion": "A. Datos",
    "decision": "Solo artículos de **acceso abierto con licencia CC BY** (y 1 CC0)",
    "porque": "Poder redistribuir imágenes y datos con crédito al DOI",
    "evidencia": "`curation/v0.1/VALIDACION.md` (1.823 CC BY + 1 CC0)",
    "estado": "Cerrada"
   },
   {
    "id": "D2",
    "seccion": "A. Datos",
    "decision": "**Cada dato lleva una cita textual verificada por código** (cita y números deben aparecer en el artículo)",
    "porque": "Que la IA no invente: trazabilidad hasta la fuente",
    "evidencia": "2 citas rechazadas en toda la base; `curation/extended.py`",
    "estado": "Cerrada"
   },
   {
    "id": "D3",
    "seccion": "A. Datos",
    "decision": "**Excluir vectores virales (AAV, virus como portador)**",
    "porque": "Se caracterizan con técnicas distintas a las de nanopartículas; el alcance del proyecto son nanoportadores y nanomateriales. Las nanopartículas **contra** virus o con antígenos sí se incluyen",
    "evidencia": "Discusión con el profesor (23/10); el Atlas conserva 8 artículos con «virus» en el título que no usan virus como portador. **Falta respaldarlo con una figura** (técnicas más comunes por artículo con micrografía)",
    "estado": "Cerrada; evidencia por completar"
   },
   {
    "id": "D4",
    "seccion": "A. Datos",
    "decision": "Dos niveles de evidencia: **E1** (micrografía + medidas + espectro) y **E2** (micrografía + medidas o espectro)",
    "porque": "Regla flexible para ampliar la base sin perder la micrografía",
    "evidencia": "1.130 E1 y 577 E2",
    "estado": "Cerrada"
   },
   {
    "id": "D5",
    "seccion": "A. Datos",
    "decision": "Las medidas (tamaño, PDI, zeta) se aceptan **de cualquier licencia**, las **imágenes solo de licencia verde**",
    "porque": "Permiso de redistribución",
    "evidencia": "Política de la puerta",
    "estado": "Cerrada"
   },
   {
    "id": "D6",
    "seccion": "A. Datos",
    "decision": "Se trabaja con la **figura completa**, no con paneles recortados",
    "porque": "El extractor identifica figuras; no hay coordenadas de paneles",
    "evidencia": "Mediana de 1 figura por artículo",
    "estado": "**Abierta: es la principal limitación del modelo de imágenes**"
   },
   {
    "id": "D7",
    "seccion": "A. Datos",
    "decision": "Clases de portador en 4 grupos: lipídico, polimérico, inorgánico, nanomaterial",
    "porque": "Suficientes ejemplos por clase",
    "evidencia": "`curation/v0.1/tabla_modelo.csv`; «nanomaterial» se solapa con inorgánico (ver `modelos/REVISION_CRITICA.md`, punto 6)",
    "estado": "Abierta"
   },
   {
    "id": "D8",
    "seccion": "A. Datos",
    "decision": "**QC en 20 artículos, asistido por IA**, no humano",
    "porque": "La revisión manual completa no escala; el jurado no revisa dato a dato",
    "evidencia": "`equipo/qc_carlos/` (micrografías 19/19, espectros 14/16, descriptores 9/10 sobre lo comprobable)",
    "estado": "Cerrada; se declara como asistida por IA"
   },
   {
    "id": "D9",
    "seccion": "B. Evaluación y modelos",
    "decision": "**Toda evaluación separa por artículo** (5 particiones, `fold`)",
    "porque": "Figuras o muestras del mismo artículo se parecen; mezclarlas inflaría el resultado",
    "evidencia": "Comprobado: el vecino más cercano de una imagen es del mismo artículo solo en el 2,7 % de los casos",
    "estado": "Cerrada"
   },
   {
    "id": "D10",
    "seccion": "B. Evaluación y modelos",
    "decision": "**Escalera de complejidad**: media global → media por clase → lineal → Ridge → Random Forest → Gradient Boosting → vectores de imagen → fusión",
    "porque": "Ver cuánto aporta cada peldaño y no saltar a lo complejo sin base",
    "evidencia": "`modelos/tabular*/`, `producto/modelo_tabular/`",
    "estado": "Cerrada"
   },
   {
    "id": "D11",
    "seccion": "B. Evaluación y modelos",
    "decision": "**Intervalos de confianza por bootstrap de artículos** y línea base siempre visible",
    "porque": "No presentar un número sin su incertidumbre",
    "evidencia": "`REPORTE_TABULAR*.md`",
    "estado": "Cerrada"
   },
   {
    "id": "D12",
    "seccion": "B. Evaluación y modelos",
    "decision": "Para predecir la clase **se prohíben `family`, `carrier_type`, `categoria_uso`, el título y la muestra** como entradas (con prueba automática)",
    "porque": "Son la respuesta disfrazada",
    "evidencia": "`modelos/tabular/modelo_clase.py`",
    "estado": "Cerrada"
   },
   {
    "id": "D13",
    "seccion": "B. Evaluación y modelos",
    "decision": "Banderas de **material** (quitosano, plata, sílice…) **no** entran en los clasificadores de clase",
    "porque": "También delatan la respuesta",
    "evidencia": "`modelos/tabular_v2/`",
    "estado": "Cerrada"
   },
   {
    "id": "D14",
    "seccion": "B. Evaluación y modelos",
    "decision": "Primero **vectores de imagen congelados** (ResNet50, DINOv2) y solo después ajuste fino",
    "porque": "Con ~1.600 artículos, una red completa sobreajusta; el congelado es barato y reproducible",
    "evidencia": "`modelos/comparacion/ANALISIS_RAPIDO_EMBEDDINGS.md`",
    "estado": "Cerrada: el ajuste fino se probó y no superó a los congelados (D23)"
   },
   {
    "id": "D15",
    "seccion": "B. Evaluación y modelos",
    "decision": "Usar **Kabré** para lo que necesite GPU (ajuste fino) y los vectores; el producto **no depende** de él",
    "porque": "Plazo y riesgo (nodos interrumpibles, cuenta por curso)",
    "evidencia": "`equipo/KABRE_PLAN.md`; términos de uso",
    "estado": "Cerrada"
   },
   {
    "id": "D16",
    "seccion": "B. Evaluación y modelos",
    "decision": "La **etiqueta de la base y la predicción del modelo se muestran siempre por separado**",
    "porque": "Honestidad: la predicción es exploratoria",
    "evidencia": "Atlas, panel del modelo",
    "estado": "Cerrada"
   },
   {
    "id": "D17",
    "seccion": "B. Evaluación y modelos",
    "decision": "**Resultados modestos presentados como modestos** (tamaño R² 0,24; imagen sola F1 0,44 [0,42–0,47]; imagen + medidas 0,56 [0,54–0,59]; ajuste fino 0,46 [0,44–0,48]; fusión tardía del ajuste fino con medidas 0,58 [0,55–0,60]), siempre con su intervalo y su línea base",
    "porque": "Es lo que se puede defender; la base carece de parámetros de formulación",
    "evidencia": "`modelos/comparacion/METRICAS_CON_IC.md`, `METRICAS_AJUSTE_FINO_CON_IC.md`, `REVISION_CRITICA.md`",
    "estado": "Cerrada"
   },
   {
    "id": "D18",
    "seccion": "B. Evaluación y modelos",
    "decision": "Las banderas de **formulación** (método, material) son menciones de texto, **proxies ruidosos**; el 30 % de una muestra auditada fue dudoso",
    "porque": "No son recetas confirmadas",
    "evidencia": "`modelos/tabular_v2/REPORTE_TABULAR_V2.md`",
    "estado": "Cerrada"
   },
   {
    "id": "D23",
    "seccion": "B. Evaluación y modelos",
    "decision": "**Probar el ajuste fino de ResNet50 y DINOv2** (10 épocas, GPU L40S de Kabré, 5 particiones por artículo) antes de concluir que la red no es el problema",
    "porque": "Comprobar con evidencia si más capacidad de modelo ayuda",
    "evidencia": "F1 0,406 (ResNet50) y 0,443 (DINOv2); promedio 0,460 [0,437–0,484]; frente al modelo del Atlas 0,442 la diferencia es +0,018 [−0,008, +0,045]: no es clara. DINOv2 sobreajusta (0,96 en entrenamiento frente a 0,48 en prueba). `modelos/kabre/03_ajuste_fino.ipynb`, `modelos/comparacion/METRICAS_AJUSTE_FINO_CON_IC.md`",
    "estado": "Cerrada: el límite está en las imágenes, no en la arquitectura"
   },
   {
    "id": "D24",
    "seccion": "B. Evaluación y modelos",
    "decision": "Combinar las predicciones afinadas con las medidas por **fusión tardía con peso fijo 50/50 elegido de antemano**",
    "porque": "Evitar ajustar el peso con los datos de prueba",
    "evidencia": "F1 0,580 [0,554–0,603]; +0,054 [+0,032, +0,077] sobre las medidas solas. Exploratorio",
    "estado": "Cerrada"
   },
   {
    "id": "D19",
    "seccion": "C. Producto y proceso",
    "decision": "El Atlas lista solo artículos E1/E2 (**1.707**); los 117 sin evidencia quedan fuera",
    "porque": "Una ficha sin micrografía, medidas ni espectros no aporta",
    "evidencia": "",
    "estado": "Cerrada"
   },
   {
    "id": "D20",
    "seccion": "C. Producto y proceso",
    "decision": "La web no depende de nadie: se regenera con `python web/build_data.py` desde los CSV congelados",
    "porque": "Reproducible",
    "evidencia": "",
    "estado": "Cerrada"
   },
   {
    "id": "D21",
    "seccion": "C. Producto y proceso",
    "decision": "La versión de datos se **congela como `v0.1`** (checksums, `.gitattributes`)",
    "porque": "Todo el equipo trabaja sobre los mismos bytes",
    "evidencia": "",
    "estado": "Cerrada"
   },
   {
    "id": "D22",
    "seccion": "C. Producto y proceso",
    "decision": "**Agradecer a Kabré (CeNAT/CNCA)** en el informe, README y créditos del video",
    "porque": "Lo exigen sus términos de uso",
    "evidencia": "",
    "estado": "Pendiente de escribir"
   }
  ],
  "experimentos": [
   "**Mejorar las figuras**: separar figuras compuestas (varios paneles tratados como uno) y aumentar las figuras recogidas por artículo.",
   "**Entrenar sin una clase** (sin inorgánicos, sin poliméricas…): mide cuánto depende el modelo de cada clase y si generaliza.",
   "**Ajuste fino en Nukwa** (con GPU) de la CNN y del transformer.",
   "Otra validación (anidada o externa) y exponer todas las decisiones, como este registro.",
   "Contacto con el CNCA por alianzas y proyectos (a través del profesor)."
  ]
 },
 "modelos": {
  "tamano": {
   "items": [
    {
     "id": "tamano_dummy",
     "nombre": "Media global",
     "valor": -0.003,
     "lo": -0.009,
     "hi": -0.001,
     "base": true
    },
    {
     "id": "tamano_media_clase",
     "nombre": "Media por clase",
     "valor": 0.18,
     "lo": 0.127,
     "hi": 0.226,
     "base": true
    },
    {
     "id": "tamano_B_lineal",
     "nombre": "Lineal",
     "valor": 0.237,
     "lo": 0.181,
     "hi": 0.288,
     "base": false
    },
    {
     "id": "tamano_B_ridge",
     "nombre": "Ridge",
     "valor": 0.24,
     "lo": 0.189,
     "hi": 0.287,
     "base": false
    },
    {
     "id": "tamano_B_rf300",
     "nombre": "Random Forest 300",
     "valor": 0.198,
     "lo": 0.129,
     "hi": 0.263,
     "base": false
    },
    {
     "id": "tamano_B_rf500",
     "nombre": "Random Forest 500",
     "valor": 0.162,
     "lo": 0.085,
     "hi": 0.236,
     "base": false
    },
    {
     "id": "tamano_B_hgb",
     "nombre": "Boosting",
     "valor": 0.167,
     "lo": 0.09,
     "hi": 0.239,
     "base": false
    }
   ],
   "n_filas": 2749,
   "n_articulos": 1080,
   "fuente": "modelos/tabular/REPORTE_TABULAR.md · figura 10",
   "metrica": "R² de log10(tamaño)"
  },
  "clase": {
   "items": [
    {
     "id": "clase4_mayoritaria",
     "nombre": "Clase mayoritaria",
     "valor": 0.118,
     "lo": 0.108,
     "hi": 0.127,
     "base": true
    },
    {
     "id": "clase4_logistica",
     "nombre": "Logística",
     "valor": 0.513,
     "lo": 0.482,
     "hi": 0.544,
     "base": false
    },
    {
     "id": "clase4_rf",
     "nombre": "Random Forest",
     "valor": 0.488,
     "lo": 0.456,
     "hi": 0.516,
     "base": false
    },
    {
     "id": "clase4_hgb",
     "nombre": "Boosting",
     "valor": 0.473,
     "lo": 0.442,
     "hi": 0.502,
     "base": false
    }
   ],
   "n_filas": 3028,
   "n_articulos": 1201,
   "fuente": "modelos/tabular/REPORTE_TABULAR.md · figura 10",
   "metrica": "F1 macro (4 clases)"
  },
  "imagen": {
   "items": [
    {
     "id": "may",
     "nombre": "Clase mayoritaria",
     "valor": 0.156,
     "lo": 0.149,
     "hi": 0.162,
     "base": true
    },
    {
     "id": "atlas",
     "nombre": "Imagen sola (modelo del Atlas)",
     "valor": 0.442,
     "lo": 0.416,
     "hi": 0.467
    },
    {
     "id": "medidas",
     "nombre": "Solo medidas (logística)",
     "valor": 0.526,
     "lo": 0.5,
     "hi": 0.553
    },
    {
     "id": "fusion",
     "nombre": "Fusión: imagen + medidas",
     "valor": 0.561,
     "lo": 0.535,
     "hi": 0.585,
     "destacado": true
    }
   ],
   "n_filas": 2100,
   "n_articulos": 1641,
   "metrica": "F1 macro (4 clases)",
   "fuente": "modelos/comparacion/METRICAS_CON_IC.md",
   "titulo": "Solo la imagen: F1 ≈ 0,44. Imagen + medidas: ≈ 0,56",
   "texto": "Vectores de ResNet50 y DINOv2 congelados, un clasificador sencillo encima y la <strong>figura completa</strong> (a menudo con varios paneles). <strong>La imagen sola es débil</strong>: F1 0,44 [0,42–0,47] frente a 0,16 de la línea base. Combinarla con las medidas ayuda un poco: de 0,53 a 0,56. La diferencia es de +0,035 [0,014–0,056]: pequeña, pero su intervalo no incluye el cero. El vecino más cercano de una imagen es del mismo artículo solo en el 2,7 % de los casos: no hay fuga por reparto.",
   "aviso": "Cifras exploratorias (2.100 figuras; 1.000 remuestreos por artículo). El intervalo no incluye la incertidumbre de reentrenar ni la de haber probado varias variantes. Una variante con otra regla de decisión llega a 0,475 [0,451–0,499]; no se usa como titular. El ajuste fino en el clúster puede sustituir estas cifras."
  }
 },
 "figuras": [
  {
   "n": 1,
   "archivo": "assets/figuras/figura_1.png",
   "pie": "Cobertura de la base: 1.824 artículos leídos, 1.707 con evidencia."
  },
  {
   "n": 2,
   "archivo": "assets/figuras/figura_2.png",
   "pie": "Artículos por año de publicación y clase de portador."
  },
  {
   "n": 3,
   "archivo": "assets/figuras/figura_3.png",
   "pie": "Artículos por tipo de portador."
  },
  {
   "n": 4,
   "archivo": "assets/figuras/figura_4.png",
   "pie": "Micrografías por tipo de microscopía y clase."
  },
  {
   "n": 5,
   "archivo": "assets/figuras/figura_5.png",
   "pie": "Espectros por técnica y clase."
  },
  {
   "n": 6,
   "archivo": "assets/figuras/figura_6.png",
   "pie": "Distribución del tamaño de partícula (DLS) por clase."
  },
  {
   "n": 7,
   "archivo": "assets/figuras/figura_7.png",
   "pie": "Pares tamaño – potencial zeta."
  },
  {
   "n": 8,
   "archivo": "assets/figuras/figura_8.png",
   "pie": "Flujo de construcción de la base."
  },
  {
   "n": 9,
   "archivo": "assets/figuras/figura_9.png",
   "pie": "Control de calidad asistido por IA: muestra de 20 artículos."
  },
  {
   "n": 10,
   "archivo": "assets/figuras/figura_10.png",
   "pie": "Escalera de modelos de la ronda 1: tamaño (R²) y clase (F1 macro)."
  }
 ]
};
