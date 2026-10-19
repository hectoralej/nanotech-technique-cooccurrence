# Extraction task: physico-chemical characterization data of nanocarrier papers

You receive one or more "packets": text extracted from open-access articles (title, abstract, Methods, Results, figure captions, tables).
Work ONLY from the packet text. Never use outside knowledge to fill a field. If something is not in the packet, write `null`.

## Output

Write ONE JSON file (path given in your task) containing: `{"pass": "<A|B>", "batch": "<id>", "articles": [ <record>, ... ]}`.
One record per article, in the same order as the packets. The JSON must be valid (double quotes, no comments, no trailing commas).

### Record

```json
{
  "pmcid": "PMC...",
  "context": {
    "summary": "<=60 words: which nanocarrier, made of what, for what purpose, what the paper studies",
    "article_kind": "research | review | other",
    "nanocarrier_is_object_of_study": true,
    "carrier_type": "liposome | LNP | SLN | NLC | PLN | polymeric_NP | micelle | dendrimer | nanogel | inorganic_NP | virus_or_VLP | other",
    "depends_on_pcr_or_virus": false
  },
  "samples": [
    {"id": "S1", "name": "name used in the paper", "identity": "nanoparticle_loaded | nanoparticle_empty | pure_component | physical_mixture | process_intermediate | unclear",
     "composition": "short, from the paper", "formulation_defined_in": "table | text | figure | SI | not_defined"}
  ],
  "measurements": [
    {
      "technique": "micrograph | DLS | zeta | UVVis | FTIR | XRD | EDS | SAXS | DSC | TGA | Raman | NMR | XPS | NTA",
      "variant": "see list below",
      "measurand": "what is measured, e.g. 'z-average hydrodynamic diameter', 'zeta potential', 'particle morphology and diameter'",
      "assay_purpose": "e.g. particle characterization | drug quantification | colorimetric assay | plasmon band | crystallinity | thermal behaviour | elemental composition",
      "sample_id": "S1",
      "formulation_link": {"where": "figure | table | text | SI", "confidence": "explicit | inferred | paper_level"},
      "shown_as": "raw_curve | figure_panel | table | text_value | SI_only",
      "values": {},
      "conditions": {},
      "n_replicates": null,
      "quality_flags": [],
      "evidence": {"quote": "<=25 words copied VERBATIM from the packet", "location": "Methods > 2.3 | Table 2 | Fig. 3 caption | Results"},
      "confidence": "alta | media | baja"
    }
  ],
  "si_mentions": [{"technique": "DLS", "quote": "<=25 words verbatim saying that data are in the supplementary material"}],
  "notes": "optional, one line"
}
```

### Variants (use exactly these labels)

- micrograph: `cryoTEM`, `TEM_negstain`, `TEM_posstain`, `TEM_dried_unstained`, `TEM_prep_not_declared`, `HRTEM`, `STEM`, `SEM` (dried, coated or uncoated), `cryoSEM`, `ESEM`, `AFM`
  (AFM only if present; it is not a micrograph for the gate). Preparation state decides the variant: negative staining (uranyl acetate, phosphotungstic acid) => `TEM_negstain`;
  sample dried on a grid with no stain mentioned => `TEM_dried_unstained` only if the text says unstained/dried; if nothing is said about preparation => `TEM_prep_not_declared`.
- DLS: `z_average`, `intensity_peak`, `number_peak`, `volume_peak`, `size_unspecified` (use `size_unspecified` if the paper only says "particle size" measured by DLS/Zetasizer without saying which average)
- zeta: `ELS`, `PALS`, `unspecified`
- UVVis: `a_intrinsic` (absorbance spectrum of the particle itself, e.g. plasmon band), `b_quantification` (drug or lipid amount with a calibration curve), `c_assay` (colorimetric/reporter assay, plate reader), `d_turbidity`
- FTIR: `ATR`, `KBr`, `transmission`, `unspecified`
- XRD: `powder`, `thin_film`, `GIXRD`, `WAXS`
- EDS: `SEM_EDS`, `TEM_EDS`, `standalone`
- others: use the technique name as variant (`SAXS`, `SANS`, `Raman`, `SERS`, `DSC`, `TGA`, `NMR`, `XPS`, `NTA`).

### `values` and `conditions` (numbers as reported; keep units in the key)

- DLS values: `size_nm`, `size_sd_nm`, `pdi`, `pdi_sd`. conditions: `medium` (`water | PBS | buffer | serum | culture_medium | other:<text> | not_declared`), `temperature_C`, `angle_deg`, `dilution`, `instrument`.
- zeta values: `zeta_mV`, `zeta_sd_mV`. conditions: `medium` (same list), `pH`, `ionic_strength`, `model` (Smoluchowski | Huckel | not_declared), `instrument`.
- micrograph values: `size_nm` (if measured from images), `size_sd_nm`, `n_particles_measured`, `morphology`. conditions: `prep_state`, `scale_bar_present` (true | false | null), `instrument`, `n_images`.
- UVVis: `lambda_max_nm` or `range_nm`; FTIR: `main_peaks_cm-1` (list); XRD: `main_peaks_2theta` (list), `radiation`; EDS: `elements`; DSC/TGA: key temperatures. Keep short.
- If a condition is not stated in the packet, write `"not_declared"` (for `medium`) or `null`. Never guess.

## Rules (important)

1. **Context first.** Before any measurement, fill `context`. If the nanocarrier is only a tool or reagent (not designed, formulated or characterized as the subject), set `nanocarrier_is_object_of_study` to false. Set `depends_on_pcr_or_virus` to true ONLY if the carrier itself is a virus, virus-like particle or phage, or the nanocarrier's own characterization relies on PCR (titers, genome copies, cargo quantified by PCR). A qPCR/RT-qPCR used as a biological readout (gene expression, bacterial burden, viral load in an infection model) does NOT count: keep it false. Reviews => `article_kind: "review"`, and stop (empty `measurements`).
2. **Evidence is mandatory.** Every measurement has `evidence.quote` (<= 25 words, copied exactly, including numbers and symbols) and `location`. If you cannot quote it, do not record the measurement.
3. **Sample identity.** Decide for each measurement which sample was measured. Pure components, physical mixtures and process intermediates are NOT nanoparticle_loaded/empty. Use `unclear` when you cannot tell.
4. **Formulation link.** `explicit` = the measured sample is named in a formulation table/text with its composition; `inferred` = clear from context but not tabulated; `paper_level` = only one general description.
5. **One row per technique and sample.** For DLS and zeta, one row per formulation/sample that has a number (maximum 12 per technique per article; if there are more set a quality flag `more_samples_than_recorded`). Tables with several formulations: read each row. Quote the table row.
6. **Micrographs:** record one row per distinct imaged sample and variant (e.g. TEM of the loaded particles, SEM of the particles). Do not count images of cells or tissue unless they show the nanocarrier itself. `shown_as` = `figure_panel` if there is a figure caption for it, `SI_only` if only the supplement is cited, `text_value` if only described in text.
7. **Complementary techniques (UVVis, FTIR, XRD, EDS, DSC, TGA, Raman, NMR, XPS, NTA, SAXS):** record only if applied to the nanoparticle (or pure components - then say so in `sample_id`/identity). UV-Vis plate-reader viability assays and HPLC UV detectors are not UVVis measurements of the particle: use `c_assay` only if the assay is about the particle (encapsulation, release), otherwise skip.
8. **Quality flags** (free list, use these when applicable): `medio_no_declarado`, `valores_solo_en_SI`, `sin_replicas`, `muestra_ambigua`, `solo_lista_de_picos`, `tamano_sin_n`, `more_samples_than_recorded`, `dato_dudoso`.
9. **SI mentions:** if the packet says that a technique's data are only in the supplementary material, add it to `si_mentions` (and a measurement with `shown_as: "SI_only"` only if you can quote it).
10. Be strict: when in doubt, lower `confidence` to `baja` or leave the field `null`. A missing value is better than a wrong one.

## Reply

After writing the file, reply with ONE short line: `pass <A|B> batch <id>: <n> articles written, problems: <none|list>`. Do not paste the JSON in your reply.
