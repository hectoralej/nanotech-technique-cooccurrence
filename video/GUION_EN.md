# Nano2Predict video script · English narration (v1, Friday October 23)

Versión en inglés de [GUION.md](GUION.md). **La narración está en inglés** porque el video se entrega en ese idioma. Las indicaciones de pantalla y las notas para el equipo siguen en español. Si cambia una cifra o una frase, hay que cambiarla en los dos archivos.

**Total length:** 10:00 maximum (target: finish at 9:50). **Atlas demo:** 2:30 (required: between 2:00 and 3:00).
**How to read it:** "Narración" is the text to read aloud, at about 150 words per minute. Sentences are short on purpose. Numbers are written the English way (1,824 = "one thousand eight hundred twenty-four").

> **Voces propuestas** (a confirmar el sábado): **Voice A**: problem, database, closing. **Voice B**: models and limitations. La demo del Atlas la narra quien la grabe (Carlos).

## Importante: la pantalla está en español
El Atlas, la presentación y las figuras (1–10) están en español. Hay tres opciones, de menor a mayor esfuerzo; hay que elegir una el sábado:
1. **Subtítulos en inglés** sobre la narración y dejar la interfaz en español (lo más simple). En la demo, una frase de contexto: *"The interface is in Spanish, the language of the project."*
2. **Rótulos en inglés** sobre las figuras clave (1, 8, 9, 10) hechos en el montaje.
3. **Regenerar las figuras en inglés** (Codex de Héctor; los CSV de `figuras/figuras_para_el_video/datos/` ya tienen los datos).

**Términos: lo que se lee en pantalla (español) ↔ lo que se dice (inglés)**
| Pantalla | Narración |
|---|---|
| micrografía | micrograph |
| descriptores / medidas | measurements |
| tamaño, PDI, potencial zeta | size, PDI (polydispersity index), zeta potential |
| línea base | baseline |
| exactitud · F1 macro | accuracy · macro F1 score |
| intervalo de confianza | confidence interval |
| figura completa / panel | full figure / panel |
| acceso abierto · CC BY | open access · CC BY (Creative Commons Attribution) |
| liposoma · portador lipídico, polimérico, inorgánico, nanomaterial | liposome · lipid, polymer, inorganic, nanomaterial carrier |

## Number rules (mandatory) / Reglas de cifras
**Yes, say it with these numbers:** 1,824 articles read · 1,707 with evidence (1,130 E1 + 577 E2) · 2,726 micrographs · 3,116 measurement rows · 4,015 spectra · every data point has a quote verified by code (only 2 articles had quotes rejected) · size: R² ≈ 0.24 against 0.18 for the baseline, with a median relative error of ≈ 44% · carrier class from measurements: macro F1 ≈ 0.51 against 0.12 for the majority class · image only: macro F1 ≈ 0.44 [0.42–0.47] against 0.16 for the majority class · image plus measurements ≈ 0.56 [0.54–0.59] against 0.53 [0.50–0.55] for measurements alone (difference +0.035 [0.014–0.056]) · everything evaluated by article, with confidence intervals.
**Do not say:** "validated by humans" · "the model predicts / is accurate" · "we predict size" without the 44% error · formulation-flag numbers as a main result · "a neural network solves the problem" · "it works in production".
**Cifra de imagen (confirmada por Héctor, 23 oct):** se usa la del Atlas, **0.44**. El 0.475 es una variante exploratoria y no se dice. Las cifras de imagen son exploratorias: Héctor entrega las finales (ajuste fino) el sábado a las 3 pm; entonces se actualizan aquí, en `GUION.md` y en `producto/presentacion/construir_datos.py`.

---

## Block 1 · The problem (0:00–1:00) · Voice A
**Se ve en pantalla:** portada de la presentación (5 s) → sección «El problema» con la **Figura 1**.

**Narration:**
> A nanoparticle can carry a drug exactly where it is needed.
> But designing a good one is still, to a large extent, trial and error.
> Every lab measures the size, the charge and the shape of its particles. And then publishes the results in a paper.
> That data exists. But it is locked inside PDFs: in tables, in figure captions, in single sentences.
> To train a model, you need three things together: the micrograph, the measurements of that same sample, and the source they came from.
> Without that database, there are no models. So we started by building it.
> We read 1,824 open-access papers. In 1,707 of them, we found useful evidence.
> In total: 2,726 micrographs, 3,116 rows of measurements, and 4,015 spectra.
> And every single data point comes with its source quote.

*(≈ 150 words · 1:00)*

---

## Block 2 · How the database was built (1:00–3:00) · Voice A
**Se ve en pantalla:** sección «Cómo se construyó»: **Figura 8** → el **ejemplo interactivo de extracción con cita** (pestaña «Lípidos (NLC)») → **Figura 9**.

**Narration:**
> The process has four steps.
> First, the search. We used Europe PMC, and only open-access papers with a Creative Commons license. That lets us show the images, always crediting the original paper.
> Second, extraction. A language model reads the full text, and proposes which micrographs there are, which technique was used, and the values for size, PDI and zeta potential.
> But an AI can make mistakes. Or make things up.
> So the third step is the central rule of the project. Every data point must come with a quote from the paper. And a program checks that this quote, and those numbers, really appear in the text.
> *[Show the example]* Here is a real case. The system extracted a size of 161 nanometers, a PDI of 0.444, and a zeta potential of minus 28.5 millivolts. And this is the sentence in the paper it came from.
> If the quote is not found, the data point is rejected. In the whole database, the code rejected quotes in only two papers.
> The fourth step is quality control. We reviewed a sample of 20 papers, with the help of an AI.
> Of what could be checked: 19 out of 19 micrographs were correct, 9 out of 10 measurements, and 14 out of 16 spectra.
> This is a small sample, and the review was AI-assisted, not done by people. We present it as a preliminary estimate, not as the accuracy of the whole database.

*(≈ 235 words · 1:35 at a calm pace; leaves 25 s for the screen)*

---

## Block 3 · Atlas demo (3:00–5:30) · Carlos records and narrates
**Se ve en pantalla:** grabación del Atlas (`producto/web/`). Ajustar los conteos de filtros tras la revisión visual final de Carlos.

| Time | Acción en pantalla | Narration |
|---|---|---|
| 3:00–3:15 | Portada del Atlas con las cuatro cifras. | "This is the Nano2Predict Atlas. It brings together published evidence on nanocarriers: their papers, their micrographs, and the techniques used to characterize them. The interface is in Spanish, the language of the project." |
| 3:15–3:45 | Explorador: **Liposoma** + microscopía **cryoTEM**. Mostrar cómo baja el número de resultados. | "I can combine a type of carrier with a technique. For example, liposomes observed with cryo-electron microscopy. The list shrinks to the papers that document both." |
| 3:45–4:30 | Abrir una ficha con imagen y descriptores. Desplegar una cita. Pulsar «Copiar cita/DOI». | "Each record shows the micrograph, the paper's DOI, and the measurements of size, PDI and zeta potential. Next to every measurement, the exact quote that supports it. With one click, I can copy the quote or the DOI to cite it." |
| 4:30–5:05 | En un artículo con predicción real, mostrar el panel del modelo: clase de la base **separada** de la predicción, y los vecinos. | "Here is the model. The label from the database and the model's prediction are always shown separately, because the prediction is exploratory. Below, the micrographs that look most similar to the model, always from other papers." |
| 5:05–5:20 | Filtrar por **XRD** y abrir un artículo de nanomaterial. | "We can also explore by spectral technique, for example X-ray diffraction, and see which material was characterized." |
| 5:20–5:30 | Ir a «Cómo se construyó». | "And at the end, how it was built: every data point keeps its path back to the source." |

**Condiciones antes de grabar:** igual que en `GUION.md` (confirmar que los JSON del modelo sean los finales; cronometrar dos ensayos; si pasa de 2:40, recortar el segmento de XRD). Verificar el número de resultados de «Liposoma + cryoTEM» (hoy: 15) antes de decirlo.

---

## Block 4 · Models (5:30–8:00) · Voice B
**Se ve en pantalla:** sección «Modelos» de la presentación (escalera interactiva) → **Figura 10** → gráfica de comparación imagen/medidas/fusión (pendiente de Héctor).

**Narration:**
> With this database, we asked: can we predict anything useful?
> We built a ladder. We started with the simplest model and climbed one step at a time. At every step, we compared against a baseline.
> First question: particle size.
> Always predicting the average explains nothing: R-squared of zero. Predicting the average of each carrier type explains 18 percent.
> Our best model, a regularized linear regression using techniques and measurements, reaches 0.24.
> That is a real improvement, but a small one. The typical error is still around 44 percent.
> And the more complex models, like Random Forest and boosting, did not improve it.
> Second question: the type of carrier. Lipid, polymer, inorganic, or nanomaterial.
> Using the measurements, the macro F1 score is 0.51. Always answering the most common class gives 0.12.
> Third question: is the image alone enough?
> We used features from two pretrained networks, ResNet and DINOv2, kept frozen, with a simple classifier on top.
> The result: a macro F1 of 0.44, with a confidence interval from 0.42 to 0.47. The baseline is 0.16. Better than chance, but the image alone is weak. And note: we used the full figure, which often mixes several panels.
> Fourth: combining the image with the measurements. It rises from 0.53 to 0.56. It is a small gain, but its confidence interval does not include zero.
> Everything is evaluated by splitting by paper: figures from the same paper are never in both training and testing. And every number comes with its confidence interval.
> These are exploratory numbers. The results are modest. And we present them as modest.

*(≈ 275 words · 1:50; leaves 40 s for the charts)*

---

## Block 5 · Decisions and limitations (8:00–9:00) · Voice B
**Se ve en pantalla:** sección «Decisiones» (tabla filtrable) → sección «Limitaciones».

**Narration:**
> We made decisions, and we wrote them down.
> We excluded viral vectors, like AAV. They are characterized with different techniques, and our scope is nanoparticles.
> We work with the full figure, not cropped panels. This is the main limitation of the image model.
> For the class models, we forbade the carrier type and the title as inputs, because they would be the answer in disguise. An automatic test guarantees it.
> And we know what we are missing. The database has no formulation parameters: no ratios, no preparation conditions. That is why size is so hard to predict.
> The labels come from an AI, and the quality check covered 20 papers, assisted by an AI.
> And there is still no external validation.

*(≈ 125 words · 0:50)*

---

## Block 6 · Next steps and credits (9:00–10:00) · Voice A
**Se ve en pantalla:** sección «Siguientes pasos» → créditos (Europe PMC, Kabré CeNAT/CNCA).

**Narration:**
> What comes next?
> First, cropping the panels of each figure, and collecting more figures per paper. That way, the image model will see micrographs, not charts.
> Second, fine-tuning the networks on a GPU, and training with one class removed to see how much the model depends on each one.
> Third, extracting preparation conditions, and validating with new papers and with blind human review.
> Thank you to Europe PMC, for opening access to the literature.
> Thank you to the Kabré cluster, from CeNAT and its National Advanced Computing Laboratory, where we computed the image features.
> And thank you to our professor, William [apellido por confirmar], for the questions and the guidance.
> Nano2Predict: from the literature, to evidence you can check.

*(≈ 110 words · 0:45; 15 s of margin)*

---

## Pendientes antes de grabar la versión en inglés
1. **Elegir cómo se maneja la pantalla en español** (ver la sección «Importante»).
2. **Probar la narración en voz alta con cronómetro.** El inglés ocupa un poco más que el español: si el Bloque 4 pasa de 2:30, quitar la frase sobre boosting.
3. **Revisar la pronunciación:** «Kabré» (ka-BRÉ), «DINOv2» («dino v two»), «cryo-EM» («cry-oh E M»), «PDI» («P D I»), «CeNAT» («seh-NAHT»).
4. **Cifras finales de imagen** (ajuste fino, sábado 3 pm) y **figura de comparación** (Figura 11): las entrega Héctor; entonces se actualizan las cifras del Bloque 4.
5. **Voces y apellido del profesor.**
6. Si se cambia una cifra o frase en `GUION.md`, repetirlo aquí.
