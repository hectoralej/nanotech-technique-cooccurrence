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
 "calidad_figuras": {
  "n_figuras": 5539,
  "n_recortes": 8108,
  "n_recortes_clase": 4670,
  "n_articulos_recortes_clase": 1114,
  "auditoria": {
   "bien": 47,
   "total": 48,
   "pct": "97,9"
  },
  "iou": {
   "valor": "0,89",
   "n_figuras": 22,
   "n_paneles": 120
  },
  "imagen": {
   "es": "assets/figuras_calidad/flujo_calidad_figuras_es.png",
   "en": "assets/figuras_calidad/flujo_calidad_figuras_en.png"
  },
  "fuentes": "modelos/flujo_figuras/PROGRESO.md, figuras_vision.csv, segmentacion/cajas/paneles.csv, equipo/ESTADO_FIGURAS_24OCT_NOCHE.md"
 },
 "descriptores_v03": {
  "usables": 2538,
  "filas": 3116,
  "auditadas": 377,
  "fuente": "modelos/descriptores_v02/DESCRIPTORES_V03.md"
 },
 "figuras_recortes": {
  "n_figuras": 5539,
  "figuras_con_paneles": 1702,
  "paneles": {
   "n": 5539,
   "media": 4.41,
   "pct1": 17.8,
   "pct2": 20.8,
   "pct3": 61.5
  },
  "destinos": [
   {
    "id": "simple",
    "nombre": "Simple",
    "frase": "Un solo panel. Si es una micrografía de partículas, entra tal cual.",
    "n": 546,
    "pct": 9.9,
    "aceptada_auto": 511,
    "aceptada_arbitrada": 20,
    "cola_revision": 15,
    "ejemplos": [
     {
      "fig_id": "PMC10675202|Figure 7",
      "n_paneles": 1,
      "cajas": "assets/recortes/h_ejemplo_simple_1.jpg",
      "original": null,
      "credito": {
       "titulo": "Chitosan Nanoparticles Loaded with Capparis cartilaginea Decne Extract: Insights into Characterization and Antigenotoxicity In Vivo.",
       "doi": "https://doi.org/10.3390/pharmaceutics15112551",
       "licencia": "CC BY"
      }
     },
     {
      "fig_id": "PMC13266089|FIGURE 9",
      "n_paneles": 1,
      "cajas": "assets/recortes/h_ejemplo_simple_2.jpg",
      "original": null,
      "credito": {
       "titulo": "Plant-Mediated Fabrication of Silver Nanoparticles Using Elaeagnus angustifolia Flowers: In Vitro Evaluation of Antibacterial, Antifungal, Antioxidant, and Toxic Effects and Biomolecular Interactions With ct-DNA and HSA.",
       "doi": "https://doi.org/10.1155/bca/9779231",
       "licencia": "CC BY"
      }
     }
    ]
   },
   {
    "id": "pareja",
    "nombre": "Pareja",
    "frase": "Dos paneles, por ejemplo una micrografía y su espectro. Se separan en dos recortes.",
    "n": 910,
    "pct": 16.4,
    "aceptada_auto": 670,
    "aceptada_arbitrada": 44,
    "cola_revision": 196,
    "ejemplos": [
     {
      "fig_id": "PMC7913486|Figure 3",
      "n_paneles": 2,
      "cajas": "assets/recortes/h_ejemplo_pareja_1.jpg",
      "original": null,
      "credito": {
       "titulo": "Astaxanthin-Loaded Stealth Lipid Nanoparticles (AST-SSLN) as Potential Carriers for the Treatment of Alzheimer's Disease: Formulation Development and Optimization.",
       "doi": "https://doi.org/10.3390/nano11020391",
       "licencia": "CC BY"
      }
     },
     {
      "fig_id": "PMC7435648|Figure 5",
      "n_paneles": 2,
      "cajas": "assets/recortes/h_ejemplo_pareja_2.jpg",
      "original": null,
      "credito": {
       "titulo": "Green Synthesis of Silver Nanoparticles Using Parthenium Hysterophorus: Optimization, Characterization and In Vitro Therapeutic Evaluation.",
       "doi": "https://doi.org/10.3390/molecules25153324",
       "licencia": "CC BY"
      }
     }
    ]
   },
   {
    "id": "compuesta",
    "nombre": "Compuesta",
    "frase": "Tres o más paneles (micrografías, espectros, fotos, gráficos). Se separan con una caja por panel.",
    "n": 3392,
    "pct": 61.2,
    "aceptada_auto": 2243,
    "aceptada_arbitrada": 55,
    "cola_revision": 1094,
    "ejemplos": [
     {
      "fig_id": "PMC8196760|Figure 7",
      "n_paneles": 9,
      "cajas": "assets/recortes/h_ejemplo_compuesta_1.jpg",
      "original": null,
      "credito": {
       "titulo": "Chitosan/Gelatin/Silver Nanoparticles Composites Films for Biodegradable Food Packaging Applications.",
       "doi": "https://doi.org/10.3390/polym13111680",
       "licencia": "CC BY"
      }
     },
     {
      "fig_id": "PMC10039946|Figure 5",
      "n_paneles": 5,
      "cajas": "assets/recortes/h_ejemplo_compuesta_2.jpg",
      "original": null,
      "credito": {
       "titulo": "Electrospun nanofibers of cellulose acetate/metal organic framework-third generation PAMAM dendrimer for the removal of methylene blue from aqueous media.",
       "doi": "https://doi.org/10.1038/s41598-023-32097-3",
       "licencia": "CC BY"
      }
     }
    ]
   },
   {
    "id": "superpuesto",
    "nombre": "Superpuesto",
    "frase": "Varias curvas espectrales superpuestas en los mismos ejes. No sirve para entrenar.",
    "n": 394,
    "pct": 7.1,
    "aceptada_auto": 247,
    "aceptada_arbitrada": 83,
    "cola_revision": 64,
    "ejemplos": [
     {
      "fig_id": "PMC12567029|Figure 4",
      "n_paneles": 1,
      "cajas": "assets/recortes/h_ejemplo_superpuesto_1.jpg",
      "original": null,
      "credito": {
       "titulo": "Biosynthesis of Silver Nanoparticles Using Phytochemicals Extracted from Aqueous Clerodendrum glabrum for Anti-Diabetes and Anti-Inflammatory Activity: An In Vitro Study.",
       "doi": "https://doi.org/10.3390/nano15201560",
       "licencia": "CC BY"
      }
     },
     {
      "fig_id": "PMC6893062|Fig. 4",
      "n_paneles": 1,
      "cajas": "assets/recortes/h_ejemplo_superpuesto_2.jpg",
      "original": null,
      "credito": {
       "titulo": "A study of the influence of plasmonic resonance of gold nanoparticle doped PEDOT: PSS on the performance of organic solar cells based on CuPc/C60.",
       "doi": "https://doi.org/10.1016/j.heliyon.2019.e02675",
       "licencia": "CC BY"
      }
     }
    ]
   },
   {
    "id": "excluir",
    "nombre": "Excluir",
    "frase": "No es una micrografía ni un espectro útil (esquemas, tablas, fotos…). No se usa.",
    "n": 297,
    "pct": 5.4,
    "aceptada_auto": 2,
    "aceptada_arbitrada": 152,
    "cola_revision": 143,
    "ejemplos": [
     {
      "fig_id": "PMC12192994|Figure 16",
      "n_paneles": 6,
      "cajas": "assets/recortes/h_ejemplo_excluir_1.jpg",
      "original": null,
      "credito": {
       "titulo": "DMPC-Based Liposomal Vesicles for Encapsulation and Controlled Release of NMN and Matrigel in Sarcopenia Therapy.",
       "doi": "https://doi.org/10.3390/ijms26125594",
       "licencia": "CC BY"
      }
     },
     {
      "fig_id": "PMC10233837|Figure 4",
      "n_paneles": 8,
      "cajas": "assets/recortes/h_ejemplo_excluir_2.jpg",
      "original": null,
      "credito": {
       "titulo": "Caveat Emptor: Commercialized Manganese Oxide Nanoparticles Exhibit Unintended Properties.",
       "doi": "https://doi.org/10.1021/acsomega.3c00892",
       "licencia": "CC BY"
      }
     }
    ]
   }
  ],
  "compuesta_demo": {
   "fig_id": "PMC8619896|Figure 4",
   "n_paneles": 4,
   "n_cajas": 8,
   "original": "assets/recortes/demo_original.jpg",
   "cajas": "assets/recortes/demo_cajas.jpg",
   "recortes": [
    {
     "img": "assets/recortes/demo_recorte1.jpg",
     "tipo": "micro",
     "panel": "1"
    },
    {
     "img": "assets/recortes/demo_recorte2.jpg",
     "tipo": "micro",
     "panel": "2"
    },
    {
     "img": "assets/recortes/demo_recorte3.jpg",
     "tipo": "micro",
     "panel": "3"
    },
    {
     "img": "assets/recortes/demo_recorte4.jpg",
     "tipo": "micro",
     "panel": "4"
    }
   ],
   "credito": {
    "titulo": "Hybrid Radiobioconjugated Superparamagnetic Iron Oxide-Based Nanoparticles for Multimodal Cancer Therapy.",
    "anio": "2021",
    "doi": "https://doi.org/10.3390/pharmaceutics13111843",
    "licencia": "CC BY"
   }
  },
  "muestra": {
   "imagen": "assets/recortes/h_recortes_por_clase.jpg",
   "creditos": [
    {
     "clase": "Inorgánico",
     "credito": {
      "titulo": "Toxicological Evaluation of Luminescent Silica Nanoparticles as New Drug Nanocarriers in Different Cancer Cell Lines.",
      "doi": "https://doi.org/10.3390/ma11081310",
      "licencia": "CC BY"
     }
    },
    {
     "clase": "Inorgánico",
     "credito": {
      "titulo": "Functionalization of Photosensitized Silica Nanoparticles for Advanced Photodynamic Therapy of Cancer.",
      "doi": "https://doi.org/10.3390/ijms22126618",
      "licencia": "CC BY"
     }
    },
    {
     "clase": "Inorgánico",
     "credito": {
      "titulo": "Glucosamine Modified the Surface of pH-Responsive Poly(2-(diethylamino)ethyl Methacrylate) Brushes Grafted on Hollow Mesoporous Silica Nanoparticles as Smart Nanocarrier.",
      "doi": "https://doi.org/10.3390/polym12112749",
      "licencia": "CC BY"
     }
    },
    {
     "clase": "Lipídico",
     "credito": {
      "titulo": "Hydrogel-Nanolipid Formulations for the Complex Anti-Inflammatory and Antimicrobial Therapy of Periodontitis.",
      "doi": "https://doi.org/10.3390/pharmaceutics17050620",
      "licencia": "CC BY"
     }
    },
    {
     "clase": "Lipídico",
     "credito": {
      "titulo": "Stabilization of β-Carotene Liposomes with Chitosan-Lactoferrin Coating System: Vesicle Properties and Anti-Inflammatory In Vitro Studies.",
      "doi": "https://doi.org/10.3390/foods14060968",
      "licencia": "CC BY"
     }
    },
    {
     "clase": "Lipídico",
     "credito": {
      "titulo": "Sulconazole-Loaded Solid Lipid Nanoparticles for Enhanced Antifungal Activity: In Vitro and In Vivo Approach.",
      "doi": "https://doi.org/10.3390/molecules28227508",
      "licencia": "CC BY"
     }
    },
    {
     "clase": "Nanomaterial",
     "credito": {
      "titulo": "An Approach to Identifying Single-Nucleotide Mutations Using Noncovalent Associates of Gold Nanoparticles with Fluorescently Labeled Oligonucleotides.",
      "doi": "https://doi.org/10.3390/ijms252413230",
      "licencia": "CC BY"
     }
    },
    {
     "clase": "Nanomaterial",
     "credito": {
      "titulo": "Biomolecular strategy for designing antibiotic-silver nanoparticles conjugate via nitrate reductase mediated β-lactamase inhibition with molecular docking insights.",
      "doi": "https://doi.org/10.1038/s41598-025-30539-8",
      "licencia": "CC BY"
     }
    },
    {
     "clase": "Nanomaterial",
     "credito": {
      "titulo": "Small AgNP in the Biopolymer Nanocomposite System.",
      "doi": "https://doi.org/10.3390/ijms21249388",
      "licencia": "CC BY"
     }
    },
    {
     "clase": "Polimérico",
     "credito": {
      "titulo": "Anticancer Drug-Loaded Chitosan Nanoparticles for In Vitro Release, Promoting Antibacterial and Anticancer Activities.",
      "doi": "https://doi.org/10.3390/polym15193925",
      "licencia": "CC BY"
     }
    },
    {
     "clase": "Polimérico",
     "credito": {
      "titulo": "Bactericidal Activity of Usnic Acid-Chitosan Nanoparticles against Persister Cells of Biofilm-Forming Pathogenic Bacteria.",
      "doi": "https://doi.org/10.3390/md18050270",
      "licencia": "CC BY"
     }
    },
    {
     "clase": "Polimérico",
     "credito": {
      "titulo": "Preparation and In Vitro Characterization of Quercetin and Chlorhexidine-loaded PLGA Nanoparticles for Oral Biofilm-Associated Pathologies.",
      "doi": "https://doi.org/10.1007/s00784-026-06954-0",
      "licencia": "CC BY"
     }
    }
   ]
  },
  "recortes": {
   "total": 8108,
   "micro": 4987,
   "espectro": 1065,
   "otro": 2056,
   "elegibles_con_clase": 4670,
   "articulos_elegibles": 1114
  },
  "acuerdo": {
   "coinciden_pie_imagen": 67.8,
   "cola": 1512,
   "arbitradas": 354
  },
  "fuentes": "modelos/flujo_figuras/figuras_vision.csv, PROGRESO.md, segmentacion/cajas/paneles.csv e indice_recortes.csv, segmentacion/INSTRUCCIONES_CAJAS.md, entrega/ejemplos_presentacion/"
 },
 "recortes": {
  "imagen": {
   "n_articulos": 1112,
   "filas": [
    {
     "nombre": "ResNet50",
     "recortes_f1": 0.472,
     "mismas_vistas_f1": 0.447,
     "completa_f1": 0.416,
     "dif_f1": 0.056,
     "dif_f1_ic": [
      0.02,
      0.091
     ],
     "dif_mismas_vistas_f1": 0.031,
     "dif_mismas_vistas_acc": 0.006
    },
    {
     "nombre": "DINOv2",
     "recortes_f1": 0.509,
     "mismas_vistas_f1": 0.471,
     "completa_f1": 0.458,
     "dif_f1": 0.052,
     "dif_f1_ic": [
      0.013,
      0.086
     ],
     "dif_mismas_vistas_f1": 0.014,
     "dif_mismas_vistas_acc": 0.008
    }
   ],
   "promedio": {
    "recortes_f1": 0.515,
    "completa_f1": 0.472,
    "dif_f1": 0.042,
    "dif_ic": [
     0.007,
     0.079
    ]
   },
   "vistas_03": 1.32,
   "vistas_04": 4.18
  },
  "fusion": {
   "n_articulos": 786,
   "linea_base_acc": 0.363,
   "filas": [
    {
     "nombre": "Solo medidas (logística)",
     "acc": 0.471,
     "acc_bal": 0.423,
     "f1": 0.406
    },
    {
     "nombre": "Imagen, figura completa",
     "acc": 0.499,
     "acc_bal": 0.471,
     "f1": 0.475
    },
    {
     "nombre": "Imagen, recortes de panel",
     "acc": 0.541,
     "acc_bal": 0.511,
     "f1": 0.519
    },
    {
     "nombre": "Fusión medidas + figura completa",
     "acc": 0.547,
     "acc_bal": 0.499,
     "f1": 0.504
    },
    {
     "nombre": "Fusión medidas + recortes",
     "acc": 0.576,
     "acc_bal": 0.529,
     "f1": 0.535
    }
   ],
   "difs": [
    {
     "nombre": "imagen recortes - imagen completa",
     "f1": 0.044,
     "ic": [
      0.002,
      0.086
     ]
    },
    {
     "nombre": "fusión recortes - fusión completa",
     "f1": 0.031,
     "ic": [
      -0.01,
      0.071
     ]
    },
    {
     "nombre": "fusión recortes - solo medidas",
     "f1": 0.129,
     "ic": [
      0.082,
      0.172
     ]
    },
    {
     "nombre": "fusión completa - solo medidas",
     "f1": 0.099,
     "ic": [
      0.052,
      0.143
     ]
    },
    {
     "nombre": "solo medidas - imagen recortes",
     "f1": -0.114,
     "ic": [
      -0.163,
      -0.059
     ]
    }
   ]
  },
  "fuente": "modelos/comparacion/ANALISIS_04_RECORTES.md y ANALISIS_FUSION_04.md"
 },
 "nffa": {
  "n_articulos": 1114,
  "brazos": [
   {
    "id": "A",
    "nombre": "A · línea base (LVD → recortes)",
    "acc": 0.5476,
    "acc_sd": 0.0077,
    "f1": 0.5047,
    "f1_sd": 0.0104,
    "f1_ens": 0.5206
   },
   {
    "id": "B",
    "nombre": "B · NFFA antes de los recortes",
    "acc": 0.5332,
    "acc_sd": 0.0108,
    "f1": 0.4872,
    "f1_sd": 0.0109,
    "f1_ens": 0.5021
   },
   {
    "id": "C",
    "nombre": "C · control (etiquetas de NFFA mezcladas)",
    "acc": 0.5114,
    "acc_sd": 0.0102,
    "f1": 0.464,
    "f1_sd": 0.0109,
    "f1_ens": 0.476
   }
  ],
  "difs": [
   {
    "nombre": "B - A",
    "f1": -0.018531102832540336,
    "ic": [
     -0.04187501175942105,
     0.0051460187535826854
    ]
   },
   {
    "nombre": "B - C",
    "f1": 0.026052502383162923,
    "ic": [
     0.0007849321717547889,
     0.049986067690967695
    ]
   },
   {
    "nombre": "C - A",
    "f1": -0.04458360521570326,
    "ic": [
     -0.07030999433921592,
     -0.02009245586840141
    ]
   }
  ],
  "por_semilla_BA": "−0,033, −0,033 y +0,013",
  "ens_acc": "0,013",
  "ens_f1": "0,016",
  "veredicto": "NO CONCLUYENTE/MARGINAL: el IC de B − A incluye 0. Se informa como resultado nulo (el preentrenamiento morfológico externo no mejora de forma detectable con esta muestra).",
  "fuente": "modelos/comparacion/ANALISIS_06_NFFA.md y entrada_kabre/06_nffa/metricas_06.json"
 },
 "modelo_final": {
  "n_recortes": 4670,
  "n_articulos_entrenamiento": 1114,
  "n_articulos": 1114,
  "exactitud": 0.561,
  "exactitud_bal": 0.511,
  "f1": 0.521,
  "linea_base": 0.442,
  "n_linea_base": 1114,
  "mayoritaria_n": 492,
  "validacion": "5 particiones por artículo, ensamble de 3 semillas",
  "fuente": "modelos/modelo_final/LEEME.md y 02_onnx/modelo_card.json"
 },
 "figuras_modelos": {
  "hero": {
   "es": "assets/figuras_modelos/fig_hero_flujo_es.png",
   "en": "assets/figuras_modelos/fig_hero_flujo_en.png",
   "pie": {
    "es": "Fuentes: modelos/flujo_figuras/figuras_vision.csv e indice_recortes.csv. Solo figuras con paneles (compuestas y parejas con micrografía o espectro útil); las simples y las de espectros superpuestos no se recortan. La clase es la del ARTÍCULO, no la del recorte. *Validación cruzada por artículo, ensamble de 3 semillas de DINOv2 (modelos/comparacion/ANALISIS_06_NFFA.md); exploratorio; línea base de la clase mayoritaria: exactitud 0,442.",
    "en": "Sources: modelos/flujo_figuras/figuras_vision.csv and indice_recortes.csv. Only figures with panels (composite and pair figures with a micrograph or a clean spectrum); simple figures and overlaid-spectra figures are not cropped. The class is the ARTICLE's, not the crop's. *Article-level cross-validation, 3-seed DINOv2 ensemble (modelos/comparacion/ANALISIS_06_NFFA.md); exploratory; majority-class baseline: accuracy 0.442."
   }
  },
  "recortes": {
   "es": "assets/figuras_modelos/fig_modelos_2_es.png",
   "en": "assets/figuras_modelos/fig_modelos_2_en.png",
   "pie": {
    "es": "n = 1.112 artículos en (a) y las 3 primeras filas de (b); n = 786 en las 2 últimas (artículos con figura completa, recortes y medidas). IC 95 % por bootstrap de artículos (2.000). Los puntos huecos son el promedio de 200 sorteos sin IC. Fuentes: modelos/comparacion/ANALISIS_04_RECORTES.md y ANALISIS_FUSION_04.md. Con el mismo número de vistas por artículo la ventaja de los recortes se reduce (control); el IC de «fusión 04 − fusión 03» incluye el 0.",
    "en": "n = 1,112 articles in (a) and the first three rows of (b); n = 786 in the last two (articles with a full figure, crops and measurements). 95% CI by article bootstrap (2,000). Hollow points are the mean of 200 draws, without CI. Sources: modelos/comparacion/ANALISIS_04_RECORTES.md and ANALISIS_FUSION_04.md. With the same number of views per article the advantage of crops shrinks (control); the CI of “fusion 04 − fusion 03” includes 0."
   }
  },
  "nffa": {
   "es": "assets/figuras_modelos/fig_modelos_3_es.png",
   "en": "assets/figuras_modelos/fig_modelos_3_en.png",
   "pie": {
    "es": "1.114 artículos; 5 particiones por artículo; 3 semillas por brazo; la etapa 1 (NFFA, 7 morfologías, 8.204 teselas, 96,8 % de exactitud interna) corrió una vez. IC 95 % por bootstrap de artículos (2.000) sobre las probabilidades promediadas entre semillas. Resultado: B no supera a A (IC incluye 0); mezclar las etiquetas daña (C − A). Fuente: modelos/comparacion/ANALISIS_06_NFFA.md. Criterio fijado antes de ver los resultados.",
    "en": "1,114 articles; 5 article-level splits; 3 seeds per arm; stage 1 (NFFA, 7 morphologies, 8,204 tiles, 96.8% internal accuracy) ran once. 95% CI by article bootstrap (2,000) on probabilities averaged across seeds. Result: B does not beat A (CI includes 0); shuffling the labels hurts (C − A). Source: modelos/comparacion/ANALISIS_06_NFFA.md. Criterion fixed before seeing the results."
   }
  }
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
  "grupos": [
   "Datos",
   "Figuras",
   "Evaluación estadística",
   "Modelos"
  ],
  "filas": [
   {
    "id": "D1",
    "seccion": "A. Datos",
    "grupo": "Datos",
    "decision": "Solo artículos de **acceso abierto con licencia CC BY** (y 1 CC0)",
    "porque": "Poder redistribuir imágenes y datos con crédito al DOI",
    "evidencia": "`curation/v0.1/VALIDACION.md` (1.823 CC BY + 1 CC0)",
    "estado": "Cerrada"
   },
   {
    "id": "D2",
    "seccion": "A. Datos",
    "grupo": "Datos",
    "decision": "**Cada dato lleva una cita textual verificada por código** (cita y números deben aparecer en el artículo)",
    "porque": "Que la IA no invente: trazabilidad hasta la fuente",
    "evidencia": "2 citas rechazadas en toda la base; `curation/extended.py`",
    "estado": "Cerrada"
   },
   {
    "id": "D3",
    "seccion": "A. Datos",
    "grupo": "Datos",
    "decision": "**Excluir vectores virales (AAV, virus como portador)**",
    "porque": "Se caracterizan con técnicas distintas a las de nanopartículas; el alcance del proyecto son nanoportadores y nanomateriales. Las nanopartículas **contra** virus o con antígenos sí se incluyen",
    "evidencia": "Discusión con el profesor (23/10); el Atlas conserva 8 artículos con «virus» en el título que no usan virus como portador. **Falta respaldarlo con una figura** (técnicas más comunes por artículo con micrografía)",
    "estado": "Cerrada; evidencia por completar"
   },
   {
    "id": "D4",
    "seccion": "A. Datos",
    "grupo": "Datos",
    "decision": "Dos niveles de evidencia: **E1** (micrografía + medidas + espectro) y **E2** (micrografía + medidas o espectro)",
    "porque": "Regla flexible para ampliar la base sin perder la micrografía",
    "evidencia": "1.130 E1 y 577 E2",
    "estado": "Cerrada"
   },
   {
    "id": "D5",
    "seccion": "A. Datos",
    "grupo": "Datos",
    "decision": "Las medidas (tamaño, PDI, zeta) se aceptan **de cualquier licencia**, las **imágenes solo de licencia verde**",
    "porque": "Permiso de redistribución",
    "evidencia": "Política de la puerta",
    "estado": "Cerrada"
   },
   {
    "id": "D6",
    "seccion": "A. Datos",
    "grupo": "Figuras",
    "decision": "Se trabaja con la **figura completa**, no con paneles recortados",
    "porque": "El extractor identifica figuras; no hay coordenadas de paneles",
    "evidencia": "Mediana de 1 figura por artículo",
    "estado": "**Superada por D27 (recorte de paneles).** La figura completa sigue siendo la línea base v0.1 y la principal limitación de sus cifras"
   },
   {
    "id": "D7",
    "seccion": "A. Datos",
    "grupo": "Datos",
    "decision": "Clases de portador en 4 grupos: lipídico, polimérico, inorgánico, nanomaterial",
    "porque": "Suficientes ejemplos por clase",
    "evidencia": "`curation/v0.1/tabla_modelo.csv`; «nanomaterial» se solapa con inorgánico (ver `modelos/REVISION_CRITICA.md`, punto 6)",
    "estado": "Abierta"
   },
   {
    "id": "D8",
    "seccion": "A. Datos",
    "grupo": "Datos",
    "decision": "**QC en 20 artículos, asistido por IA**, no humano",
    "porque": "La revisión manual completa no escala; el jurado no revisa dato a dato",
    "evidencia": "`equipo/qc_carlos/` (micrografías 19/19, espectros 14/16, descriptores 9/10 sobre lo comprobable)",
    "estado": "Cerrada; se declara como asistida por IA"
   },
   {
    "id": "D9",
    "seccion": "B. Evaluación y modelos",
    "grupo": "Evaluación estadística",
    "decision": "**Toda evaluación separa por artículo** (5 particiones, `fold`)",
    "porque": "Figuras o muestras del mismo artículo se parecen; mezclarlas inflaría el resultado",
    "evidencia": "Comprobado: el vecino más cercano de una imagen es del mismo artículo solo en el 2,7 % de los casos",
    "estado": "Cerrada"
   },
   {
    "id": "D10",
    "seccion": "B. Evaluación y modelos",
    "grupo": "Modelos",
    "decision": "**Escalera de complejidad**: media global → media por clase → lineal → Ridge → Random Forest → Gradient Boosting → vectores de imagen → fusión",
    "porque": "Ver cuánto aporta cada peldaño y no saltar a lo complejo sin base",
    "evidencia": "`modelos/tabular*/`, `producto/modelo_tabular/`",
    "estado": "Cerrada"
   },
   {
    "id": "D11",
    "seccion": "B. Evaluación y modelos",
    "grupo": "Evaluación estadística",
    "decision": "**Intervalos de confianza por bootstrap de artículos** y línea base siempre visible",
    "porque": "No presentar un número sin su incertidumbre",
    "evidencia": "`REPORTE_TABULAR*.md`",
    "estado": "Cerrada"
   },
   {
    "id": "D12",
    "seccion": "B. Evaluación y modelos",
    "grupo": "Evaluación estadística",
    "decision": "Para predecir la clase **se prohíben `family`, `carrier_type`, `categoria_uso`, el título y la muestra** como entradas (con prueba automática)",
    "porque": "Son la respuesta disfrazada",
    "evidencia": "`modelos/tabular/modelo_clase.py`",
    "estado": "Cerrada"
   },
   {
    "id": "D13",
    "seccion": "B. Evaluación y modelos",
    "grupo": "Evaluación estadística",
    "decision": "Banderas de **material** (quitosano, plata, sílice…) **no** entran en los clasificadores de clase",
    "porque": "También delatan la respuesta",
    "evidencia": "`modelos/tabular_v2/`",
    "estado": "Cerrada"
   },
   {
    "id": "D14",
    "seccion": "B. Evaluación y modelos",
    "grupo": "Modelos",
    "decision": "Primero **vectores de imagen congelados** (ResNet50, DINOv2) y solo después ajuste fino",
    "porque": "Con ~1.600 artículos, una red completa sobreajusta; el congelado es barato y reproducible",
    "evidencia": "`modelos/comparacion/ANALISIS_RAPIDO_EMBEDDINGS.md`",
    "estado": "Cerrada: el ajuste fino se probó y no superó a los congelados (D23)"
   },
   {
    "id": "D15",
    "seccion": "B. Evaluación y modelos",
    "grupo": "Modelos",
    "decision": "Usar **Kabré** para lo que necesite GPU (ajuste fino) y los vectores; el producto **no depende** de él",
    "porque": "Plazo y riesgo (nodos interrumpibles, cuenta por curso)",
    "evidencia": "`equipo/KABRE_PLAN.md`; términos de uso",
    "estado": "Cerrada"
   },
   {
    "id": "D16",
    "seccion": "B. Evaluación y modelos",
    "grupo": "Modelos",
    "decision": "La **etiqueta de la base y la predicción del modelo se muestran siempre por separado**",
    "porque": "Honestidad: la predicción es exploratoria",
    "evidencia": "Atlas, panel del modelo",
    "estado": "Cerrada"
   },
   {
    "id": "D17",
    "seccion": "B. Evaluación y modelos",
    "grupo": "Modelos",
    "decision": "**Resultados modestos presentados como modestos** (tamaño R² 0,24; imagen sola F1 0,44 [0,42–0,47]; imagen + medidas 0,56 [0,54–0,59]; ajuste fino 0,46 [0,44–0,48]; fusión tardía del ajuste fino con medidas 0,58 [0,55–0,60]), siempre con su intervalo y su línea base",
    "porque": "Es lo que se puede defender; la base carece de parámetros de formulación",
    "evidencia": "`modelos/comparacion/METRICAS_CON_IC.md`, `METRICAS_AJUSTE_FINO_CON_IC.md`, `REVISION_CRITICA.md`",
    "estado": "Cerrada"
   },
   {
    "id": "D18",
    "seccion": "B. Evaluación y modelos",
    "grupo": "Modelos",
    "decision": "Las banderas de **formulación** (método, material) son menciones de texto, **proxies ruidosos**; el 30 % de una muestra auditada fue dudoso",
    "porque": "No son recetas confirmadas",
    "evidencia": "`modelos/tabular_v2/REPORTE_TABULAR_V2.md`",
    "estado": "Cerrada"
   },
   {
    "id": "D23",
    "seccion": "B. Evaluación y modelos",
    "grupo": "Modelos",
    "decision": "**Probar el ajuste fino de ResNet50 y DINOv2** (10 épocas, GPU L40S de Kabré, 5 particiones por artículo) antes de concluir que la red no es el problema",
    "porque": "Comprobar con evidencia si más capacidad de modelo ayuda",
    "evidencia": "F1 0,406 (ResNet50) y 0,443 (DINOv2); promedio 0,460 [0,437–0,484]; frente al modelo del Atlas 0,442 la diferencia es +0,018 [−0,008, +0,045]: no es clara. DINOv2 sobreajusta (0,96 en entrenamiento frente a 0,48 en prueba). `modelos/kabre/03_ajuste_fino.ipynb`, `modelos/comparacion/METRICAS_AJUSTE_FINO_CON_IC.md`",
    "estado": "Cerrada: el límite está en las imágenes, no en la arquitectura"
   },
   {
    "id": "D24",
    "seccion": "B. Evaluación y modelos",
    "grupo": "Modelos",
    "decision": "Combinar las predicciones afinadas con las medidas por **fusión tardía con peso fijo 50/50 elegido de antemano**",
    "porque": "Evitar ajustar el peso con los datos de prueba",
    "evidencia": "F1 0,580 [0,554–0,603]; +0,054 [+0,032, +0,077] sobre las medidas solas. Exploratorio",
    "estado": "Cerrada"
   },
   {
    "id": "D19",
    "seccion": "C. Producto y proceso",
    "grupo": "Datos",
    "decision": "El Atlas lista solo artículos E1/E2 (**1.707**); los 117 sin evidencia quedan fuera",
    "porque": "Una ficha sin micrografía, medidas ni espectros no aporta",
    "evidencia": "",
    "estado": "Cerrada"
   },
   {
    "id": "D20",
    "seccion": "C. Producto y proceso",
    "grupo": "Datos",
    "decision": "La web no depende de nadie: se regenera con `python web/build_data.py` desde los CSV congelados",
    "porque": "Reproducible",
    "evidencia": "",
    "estado": "Cerrada"
   },
   {
    "id": "D21",
    "seccion": "C. Producto y proceso",
    "grupo": "Datos",
    "decision": "La versión de datos se **congela como `v0.1`** (checksums, `.gitattributes`)",
    "porque": "Todo el equipo trabaja sobre los mismos bytes",
    "evidencia": "",
    "estado": "Cerrada"
   },
   {
    "id": "D22",
    "seccion": "C. Producto y proceso",
    "grupo": "Datos",
    "decision": "**Agradecer a Kabré (CeNAT/CNCA)** en el informe, README y créditos del video",
    "porque": "Lo exigen sus términos de uso",
    "evidencia": "",
    "estado": "Pendiente de escribir"
   },
   {
    "id": "D25",
    "seccion": "E. Decisiones propuestas el 24 de octubre (las confirma Héctor)",
    "grupo": "Figuras",
    "decision": "Clasificar cada figura **mirándola** (hojas de contacto) y no solo por su pie de figura, en cinco destinos: simple, pareja, compuesta, superpuesto, excluir",
    "porque": "Los pies de figura fallan: imagen y pie coinciden en el 67,8 % de las 5.539 figuras",
    "evidencia": "`modelos/flujo_figuras/PROGRESO.md`, `modelos/tipologia_figuras/`",
    "estado": "Propuesta, la confirma Héctor"
   },
   {
    "id": "D26",
    "seccion": "E. Decisiones propuestas el 24 de octubre (las confirma Héctor)",
    "grupo": "Figuras",
    "decision": "**Dos revisores independientes** (Claude y Codex) y un **árbitro** para los desacuerdos; lo dudoso va a una **cola de revisión**",
    "porque": "No fiarse de una sola IA",
    "evidencia": "En 678 figuras comunes coinciden en el destino el 89,8 % y en el número de paneles el 88,8 %; 354 figuras se aceptan por arbitraje y 1.512 quedan en la cola. `modelos/flujo_figuras/PROGRESO.md`, `cola_desacuerdos.csv`, `INSTRUCCIONES_ARBITRO.md`",
    "estado": "Propuesta, la confirma Héctor"
   },
   {
    "id": "D27",
    "seccion": "E. Decisiones propuestas el 24 de octubre (las confirma Héctor)",
    "grupo": "Figuras",
    "decision": "**Recortar paneles** con cajas normalizadas sobre la figura completa; insets como cajas hijas; cascadas como una caja por curva; biología como «otro»",
    "porque": "Una micrografía por muestra, sin gráficos mezclados",
    "evidencia": "8.108 recortes (4.987 micrografía, 1.065 espectro, 2.056 otro). `modelos/flujo_figuras/segmentacion/INSTRUCCIONES_CAJAS.md`, `cajas/paneles.csv`",
    "estado": "Propuesta, la confirma Héctor"
   },
   {
    "id": "D28",
    "seccion": "E. Decisiones propuestas el 24 de octubre (las confirma Héctor)",
    "grupo": "Figuras",
    "decision": "**Validación humana**: cajas dibujadas a mano por Héctor en 22 figuras, comparadas con las del modelo",
    "porque": "Medir la calidad contra una referencia humana",
    "evidencia": "IoU 0,89 en 22 figuras (120 paneles) y auditoría a ciegas 47/48 en número de paneles. `equipo/ESTADO_FIGURAS_24OCT_NOCHE.md`, `segmentacion/evaluar_contra_humano.py`",
    "estado": "Propuesta, la confirma Héctor"
   },
   {
    "id": "D29",
    "seccion": "E. Decisiones propuestas el 24 de octubre (las confirma Héctor)",
    "grupo": "Evaluación estadística",
    "decision": "**Partición por artículo** (5 particiones): nunca un mismo artículo en entrenamiento y en prueba",
    "porque": "Evitar fuga de información (refuerza D9)",
    "evidencia": "D9 y la columna `fold` de `curation/v0.1/tabla_modelo.csv`",
    "estado": "Propuesta, la confirma Héctor"
   },
   {
    "id": "D30",
    "seccion": "E. Decisiones propuestas el 24 de octubre (las confirma Héctor)",
    "grupo": "Evaluación estadística",
    "decision": "**No elegir nada con los datos de prueba**: épocas fijas (última época) y peso de fusión 50/50 fijado de antemano (D24)",
    "porque": "Evitar cifras infladas",
    "evidencia": "`modelos/comparacion/METRICAS_AJUSTE_FINO_CON_IC.md`, `ANALISIS_FUSION_04.md`",
    "estado": "Propuesta, la confirma Héctor"
   },
   {
    "id": "D31",
    "seccion": "E. Decisiones propuestas el 24 de octubre (las confirma Héctor)",
    "grupo": "Evaluación estadística",
    "decision": "**Control de «mismo número de vistas por artículo»** al comparar recortes con figura completa",
    "porque": "Los recortes dan ≈ 3 veces más vistas por artículo (4,18 frente a 1,32); sin el control la mejora se sobreestima: en ResNet50 la diferencia de exactitud baja a ≈ +0,006",
    "evidencia": "`modelos/comparacion/ANALISIS_04_RECORTES.md`",
    "estado": "Propuesta, la confirma Héctor"
   },
   {
    "id": "D32",
    "seccion": "E. Decisiones propuestas el 24 de octubre (las confirma Héctor)",
    "grupo": "Evaluación estadística",
    "decision": "**Intervalos por bootstrap de artículos** en todas las comparaciones, y decir «no concluyente» cuando el intervalo incluye 0",
    "porque": "Honestidad con muestras pequeñas",
    "evidencia": "Por ejemplo, el intervalo de la fusión con recortes frente a la fusión con figura completa incluye el cero. `modelos/comparacion/ANALISIS_FUSION_04.md`",
    "estado": "Propuesta, la confirma Héctor"
   },
   {
    "id": "D33",
    "seccion": "E. Decisiones propuestas el 24 de octubre (las confirma Héctor)",
    "grupo": "Modelos",
    "decision": "Probar el **preentrenamiento intermedio con NFFA-EUROPE** (SEM, CC BY 4.0) antes de ajustar con nuestros recortes, con un **control de etiquetas mezcladas** y el criterio fijado antes de ver los resultados",
    "porque": "Una idea razonable que se prueba y se descarta con datos",
    "evidencia": "**No mejora**: B − A = −0,019 [−0,042, +0,005] (incluye el cero); mezclar las etiquetas daña (C − A = −0,045 [−0,070, −0,020]). 1.114 artículos, 3 semillas por brazo. `modelos/comparacion/ANALISIS_06_NFFA.md`",
    "estado": "Propuesta, la confirma Héctor"
   },
   {
    "id": "D34",
    "seccion": "E. Decisiones propuestas el 24 de octubre (las confirma Héctor)",
    "grupo": "Modelos",
    "decision": "**Ensamble de 3 semillas** para el modelo final",
    "porque": "Reducir la variación del azar",
    "evidencia": "En el brazo A mejora ≈ +0,013 de exactitud y +0,016 de F1 macro frente a una semilla. `modelos/comparacion/ANALISIS_06_NFFA.md`, `modelos/modelo_final/LEEME.md`",
    "estado": "Propuesta, la confirma Héctor"
   }
  ],
  "experimentos": [
   "**Mejorar las figuras**: separar figuras compuestas (varios paneles tratados como uno) y aumentar las figuras recogidas por artículo.",
   "**Entrenar sin una clase** (sin inorgánicos, sin poliméricas…): mide cuánto depende el modelo de cada clase y si generaliza.",
   "Otra validación (anidada o externa) y exponer todas las decisiones, como este registro."
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
     "nombre": "Imagen sola (vectores congelados)",
     "valor": 0.442,
     "lo": 0.416,
     "hi": 0.467
    },
    {
     "id": "ajuste",
     "nombre": "Imagen sola (ajuste fino en GPU)",
     "valor": 0.46,
     "lo": 0.437,
     "hi": 0.484
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
     "nombre": "Fusión: congelados + medidas",
     "valor": 0.561,
     "lo": 0.535,
     "hi": 0.585
    },
    {
     "id": "fusion_tardia",
     "nombre": "Fusión tardía: ajuste fino + medidas",
     "valor": 0.58,
     "lo": 0.554,
     "hi": 0.603,
     "destacado": true
    }
   ],
   "n_filas": 2100,
   "n_articulos": 1641,
   "metrica": "F1 macro (4 clases) · línea base v0.1 (figura completa)",
   "fuente": "modelos/comparacion/METRICAS_CON_IC.md y METRICAS_AJUSTE_FINO_CON_IC.md",
   "titulo": "Solo la imagen: F1 ≈ 0,44. Con las medidas: ≈ 0,58",
   "texto": "Vectores de ResNet50 y DINOv2 congelados, un clasificador sencillo encima y la <strong>figura completa</strong> (a menudo con varios paneles). <strong>La imagen sola es débil</strong>: F1 0,44 [0,42–0,47] frente a 0,16 de la línea base. Probamos también <strong>ajustar las redes completas en GPU</strong>: tampoco mejora de forma clara (0,46 [0,44–0,48]; diferencia +0,018 [−0,008, +0,045], su intervalo incluye el cero) y DINOv2 sobreajusta. <strong>El límite está en las imágenes, no en la arquitectura.</strong> Combinar la imagen con las medidas ayuda un poco: con los vectores congelados sube de 0,53 a 0,56, y la fusión tardía con el ajuste fino llega a <strong>0,58 [0,55–0,60]</strong>, +0,054 [+0,032, +0,077] sobre las medidas solas (intervalo sin el cero). El vecino más cercano de una imagen es del mismo artículo solo en el 2,7 % de los casos: no hay fuga por reparto.",
   "aviso": "Cifras exploratorias (2.100 figuras; 1.000 remuestreos por artículo). El intervalo no incluye la incertidumbre de reentrenar ni la de haber probado varias variantes. La fusión tardía usa un peso fijo 50/50 elegido de antemano. Una variante con otra regla de decisión llega a 0,475 [0,451–0,499]; no se usa como titular."
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
   "n": 10,
   "archivo": "assets/figuras/figura_10.png",
   "pie": "Escalera de modelos de la ronda 1: tamaño (R²) y clase (F1 macro)."
  }
 ],
 "siguientes_hecho": [
  "**Recortes de panel:** 8.108 recortes, 4.670 de micrografías de partículas con clase (preliminar: su ventaja viene en buena parte de más vistas por artículo).",
  "**Ajuste fino en GPU** de ResNet50 y DINOv2: F1 0,46 [0,44–0,48], sin mejora clara frente a los vectores congelados (0,44).",
  "**Experimento NFFA:** no mejoró (B − A = −0,019 [−0,042, +0,005]).",
  "**Modelo final:** DINOv2 con ensamble de 3 semillas; exactitud 0,561 y F1 0,521 por validación cruzada por artículo (n = 1.114).",
  "**Demo «sube tu micrografía»** en el navegador, con ONNX."
 ],
 "siguientes": [
  "**Recoger más figuras por artículo** (el modelo con figura completa ve ≈ 1,32 por artículo; con recortes, ≈ 4,18).",
  "**Entrenar sin una clase** (sin inorgánicos, sin poliméricas…): mide cuánto depende el modelo de cada clase y si generaliza.",
  "**Modelos específicos por clase**, con espectros de referencia (seminario 3).",
  "**Validación externa**, con artículos nuevos.",
  "**Extraer más condiciones de preparación** (proporciones, métodos), que hoy faltan en la base.",
  "**Revisión humana a ciegas** de una muestra de extracciones."
 ]
};
