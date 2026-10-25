# Nano2Predict video script · English narration (v3, October 24)

Versión en inglés de [GUION.md](GUION.md) (v3). **La narración está en inglés** porque el video se entrega en ese idioma; las indicaciones de pantalla y las notas para el equipo siguen en español. Si cambia una cifra o una frase, hay que cambiarla en los dos archivos.

**Total length:** 10:00 maximum (target: 9:50). **Atlas demo:** 2:30. **Budget:** problem 1:00 · how the database was built 1:30 · **from figure to crop 1:30 (new)** · Atlas 2:30 · models and decisions 2:00 · limitations and closing 1:20 = 9:50.
**How to read it:** "Narración" is the text to read aloud, at about 150 words per minute. Numbers are written the English way (1,824 = "one thousand eight hundred twenty-four").

> **Voces propuestas:** **Voice A**: problem, database, figure to crop, closing. **Voice B**: models and decisions. La demo del Atlas la narra quien la grabe (Carlos).

## Importante: la pantalla está en español
El Atlas, la presentación y las figuras 1–10 están en español. Opciones, de menor a mayor esfuerzo: (1) **subtítulos en inglés** sobre la narración (la presentación ya trae el diagrama de calidad de figuras en inglés: botón **EN**); (2) rótulos en inglés sobre las figuras clave; (3) regenerar las figuras en inglés (Codex de Héctor). En la demo, una frase: *"The interface is in Spanish, the language of the project."*

**Términos: pantalla (español) ↔ narración (inglés)**
| Pantalla | Narración |
|---|---|
| micrografía · recorte de panel | micrograph · panel crop |
| figura compuesta / pareja / simple / superpuesta / excluir | composite / pair / simple / overlaid spectra / exclude |
| línea base · intervalo de confianza | baseline · confidence interval |
| utilizables | usable |
| exactitud · F1 macro | accuracy · macro F1 score |

## Number rules (mandatory)
**Yes, with these numbers:** 1,824 articles read · 1,707 with evidence · 2,726 micrographs · 3,116 measurement rows, of which **2,538 are usable** after the v03 audit (say "usable", never "validated") · 4,015 spectra · every data point with a code-verified quote (only 2 articles had quotes rejected) · **5,539 figures classified one by one** · **8,108 panel crops** · **4,670 crops of particle micrographs with a class** · blind audit **47 out of 48** figures with the exact number of panels · model boxes against human boxes **IoU 0.89 on 22 figures** · size R² ≈ 0.24 against 0.18, median relative error ≈ 44% · class from measurements macro F1 ≈ 0.51 against 0.12 · image only ≈ 0.44 [0.42–0.47] against 0.16 · GPU fine-tuning 0.46 [0.44–0.48], no clear gain · panel crops (different samples: n = 1,112 and 786): a small gain, partly from more views per article, and the fusion CI includes zero · NFFA: no improvement (B − A = −0.019 [−0.042, +0.005]) · final model (n = 1,114, article-level cross-validation): accuracy 0.56 and F1 0.52 against 0.44 for the majority class · everything evaluated by article, with confidence intervals.
**Do not say:** "validated by humans" · "the model predicts / is accurate" · "we predict size" without the 44% error · "it works in production" · "a neural network solves the problem" · formulation-flag numbers as a main result · **"IoU 0.88 against Codex" (it has no report)** · **"we reviewed 20 articles" as the quality-control centerpiece** · **mixing numbers from different samples in one sentence or table** (every number with its n).

---

## Block 1 · The problem (0:00–1:00) · Voice A
**Se ve en pantalla:** portada (5 s) → «El problema» con la **Figura 1**.

**Narration:**
> A nanoparticle can deliver a drug precisely where it is needed.
> But designing a good one depends heavily on experimentation: synthesize, measure, repeat.
> Every laboratory publishes the size, charge and shape of its particles in an article. That data exists, but it is locked inside PDFs: in tables, in figure captions, in isolated sentences.
> Training a model requires three things together: the micrograph, the measurements of that same sample, and the source they came from.
> Without that foundation, there are no models. So we began by building it.
> With it, we asked what can be predicted from the image and the measurements. If it worked, a laboratory could get guidance before it synthesizes. Today, this is exploratory, and that is how we present it.
> We read 1,824 open-access articles. In 1,707 of them, we found useful evidence: 2,726 micrographs, 3,116 rows of measurements and 4,015 spectra.
> And every data point comes with its source quote.

*(≈ 150 words · 1:00)*

---

## Block 2 · How the database was built (1:00–2:30) · Voice A
**Se ve en pantalla:** «Cómo se construyó»: la línea de proceso se anima → el **ejemplo de extracción con cita** (pestaña «Lípidos (NLC)»).

**Narration:**
> First, the search. We used Europe PMC, and only open-access articles with a Creative Commons license. That lets us show the images, always crediting the original article.
> Second, extraction. A language model reads the full text and proposes which micrographs there are, which technique was used, and the values for size, PDI and zeta potential.
> But an AI can make mistakes. Or make things up.
> So the central rule is this: every data point must come with a quote from the article. And a program checks that this quote, and those numbers, really appear in the text.
> *[Show the example]* Here is a real case: 161 nanometers, a PDI of 0.444, and a zeta potential of minus 28.5 millivolts. And this is the sentence in the article it came from. If the quote is not found, the data point is rejected. In the whole database, the code rejected quotes in only two articles.
> Then we audited the descriptors: of 3,116 rows, 2,538 are usable.

*(≈ 150 words · 1:00; ≈ 30 s remain for the process line and the example)*

---

## Block 3 · From figure to crop (2:30–4:00) · Voice A
**Se ve en pantalla:** las pantallas de la sección «De la figura al recorte». Las imágenes de artículos llevan su crédito (artículo, DOI, licencia CC BY). **La figura del flujo (`fig_hero_flujo`, botón EN) se queda al menos 8 s en pantalla.**

| Screen | Se ve | Narration |
|---|---|---|
| 1 · The problem | Barras apiladas de los cinco destinos | "Here is a problem: a figure in an article is almost never a single micrograph. We classified all 5,539 figures one by one, by looking at the image. Six out of ten are composite: three or more panels mixed together. And some carry overlaid spectra. A model cannot learn well from that. The quality of the images, not the architecture, was what limited the result the most." |
| 2 · Five destinations | Pulsar «Compuesta» y «Superpuesto» | "Every figure goes to one of five destinations: simple, pair, composite, overlaid spectra, or exclude. Overlaid spectra cannot be used for training." |
| 3 · Three steps | «figura original → cajas → recortes» | "For composite figures, a model draws one box per panel, and each box is cropped." |
| 4 · The flow | **`fig_hero_flujo`** (≥ 8 s) | "This is the whole path: of 5,539 figures, 1,702 have panels. From them come 8,108 panel crops, and 4,670 are micrographs of particles with a carrier class: that is what goes into the model. Insets, spectra, fluorescence and biology stay out." |
| 5 · Untouched sample | Rejilla al azar por clase | "This is a random sample, with no cherry-picking. Some crops carry a piece of the neighboring panel, and the class is the article's, not the crop's." |
| 6 · Quality | Cifras y diagrama (botón EN) | "How did we check this stage? A blind audit got the number of panels right in 47 out of 48 figures, and the model's boxes match boxes drawn by hand by a person, with an IoU of 0.89 on 22 figures. These are small samples. Anything doubtful goes to a review queue: precision before quantity." |

*(≈ 215 words · ≈ 1:25; ≈ 5 s remain. If it does not fit, drop screen 2)*

---

## Block 4 · Atlas demo (4:00–6:30) · Carlos records and narrates
**Se ve en pantalla:** grabación del Atlas **actualizado** de Carlos (no la carpeta `web/` del zip de la presentación).

| Time | Acción en pantalla | Narration |
|---|---|---|
| 4:00–4:12 | Portada del Atlas con las cuatro cifras. | "This is the Nano2Predict Atlas: published evidence on nanocarriers, with their articles, their micrographs, and the techniques used to characterize them. The interface is in Spanish, the language of the project." |
| 4:12–4:38 | Explorador: **Liposoma** + **cryoTEM**. | "I can combine a type of carrier with a technique. For example, liposomes observed with cryo-electron microscopy. The list shrinks to the articles that document both." |
| 4:38–5:10 | Abrir una ficha; desplegar una cita; «Copiar cita/DOI». | "Each record shows the micrograph, the article's DOI, and the measurements of size, PDI and zeta potential. Next to every measurement, the exact quote that supports it, which you can copy with one click." |
| 5:10–5:25 | Vista **«Figuras y paneles»**. | "In Figures and Panels, each figure appears with the boxes that separate its panels, and the crops next to it. You can filter by figure type, technique and class." |
| 5:25–5:50 | Panel del modelo: clase de la base **separada** de la predicción; vecinos. | "Here is the model. The label from the database and the model's prediction are always shown separately, because the prediction is exploratory. Below, the most similar micrographs, always from other articles." |
| 5:50–6:20 | **Demo «sube tu micrografía»**: subir el recorte de una partícula. | "And this is the demo: I upload the micrograph of a particle, and the model, which runs inside the browser, returns the carrier class it predicts. With three warnings: it only works on micrographs of particles, its probabilities are not calibrated, and the class is the article's." |
| 6:20–6:30 | «Cómo se construyó». | "And every data point keeps its path back to the source." |

**Antes de grabar:** igual que en `GUION.md`: verificar la narración de «Figuras y paneles» y de la demo contra la web real (no estaban en `main`); usar un recorte de partículas en la demo; confirmar `prueba: false`; cronometrar dos ensayos.

---

## Block 5 · Models and decisions (6:30–8:30) · Voice B
**Se ve en pantalla:** «Modelos» (pestañas tamaño, clase, imagen) → «Con recortes de panel (preliminar)» con **`fig_modelos_2`** (≥ 8 s) → «Lo que no funcionó: NFFA» con **`fig_modelos_3`** (≥ 8 s) → «Modelo final» → «Decisiones» (grupo «Figuras»). Botón EN para las figuras.

**Narration:**
> With this database, we asked: can we predict anything useful? We built a ladder, from simple to complex, and at every step we compared against a baseline.
> Size: our best model reaches 0.24, against 0.18 for the baseline. That is a real improvement, but a small one: the typical error is still around 44 percent.
> Carrier type, from the measurements: a macro F1 of 0.51, against 0.12 for always answering the most common class. With the image alone, 0.44 against 0.16: it is weak, and fine-tuning the full networks does not clearly improve it.
> *[Crops figure]* And with panel crops instead of the full figure? A small improvement: from 0.42 to 0.47 with ResNet50, and from 0.46 to 0.51 with DINOv2. But largely because crops give more views per article: with the same number of views, the advantage in accuracy falls below one point. And in the fusion with measurements, the interval includes zero. These are different samples: 1,112 and 786 articles.
> *[NFFA figure]* We also tried pretraining on microscopy images from another database, NFFA. It did not work: it does not improve, and with shuffled labels it gets worse. It is a negative result, and we present it as one.
> *[Final model]* The final model is DINOv2, with three seeds, trained on 4,670 crops. Its reference performance, by article-level cross-validation: accuracy 0.56 and F1 0.52, against 0.44 for the majority class. It is exploratory.
> Everything is evaluated by article, with its confidence interval. And we wrote down our decisions, with their reasons and their evidence.

*(≈ 265 words · ≈ 1:50; ≈ 10 s remain: this is the tightest block. If it does not fit, drop the size sentence or the decisions sentence)*

---

## Block 6 · Limitations and closing (8:30–9:50) · Voice A
**Se ve en pantalla:** «Limitaciones» → «Siguientes pasos» → créditos.

**Narration:**
> And we know what we are missing. The panel crops are preliminary: they improve the image model, but partly because they give more views per article. The database has no formulation parameters: ratios, preparation conditions. The class "nanomaterial" is a general category. A sample of 20 articles was reviewed with the help of an AI; a broad human audit is still missing. And there is no external validation.
> What comes next? More figures per article. Training with one class left out, to learn how much the model depends on each class, whether it has learned real features of the particles or simply follows the most abundant class, and where to collect more data first. Extracting the preparation conditions. And validating on new articles and with blinded human review.
> Our thanks to Europe PMC, for opening access to the scientific literature. Our thanks to the Kabré cluster, of CeNAT and its National Advanced Computing Collaboratory (CNCA), where we computed the image features and tested GPU fine-tuning. And our thanks to Professor William Zamora, for his questions and guidance.
> Nano2Predict: from the literature, to evidence you can verify.

*(≈ 175 words · ≈ 1:15; ≈ 5 s remain)*

---

## Pendientes antes de grabar la versión en inglés
1. Elegir cómo se maneja la pantalla en español (subtítulos, rótulos o figuras en inglés).
2. Probar la narración en voz alta con cronómetro: el inglés suele ocupar algo más. Si el Bloque 5 se pasa, quitar la frase de las decisiones («For example: …»).
3. Pronunciación: «Kabré» (ka-BRÉ), «DINOv2» («dino v two»), «cryo-EM» («cry-oh E M»), «PDI» («P D I»), «CeNAT» («seh-NAHT»), «IoU» («I-o-U» o «intersection over union»).
4. Cifras con recortes y modelo final (pendientes de Héctor) y los otros pendientes de `GUION.md`.
