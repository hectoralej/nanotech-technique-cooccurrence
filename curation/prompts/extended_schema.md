# Extended set: light extraction from a short evidence packet

Each batch file lists several articles. For each one you get a SHORT evidence packet: title, abstract (cut), the figure captions about microscopy and spectra, key sentences about size/PDI/zeta/microscopy/spectra, and the size/zeta tables.
Work ONLY from the packet. If something is not in the packet, leave it out. Never use outside knowledge. Be fast: read each packet once.

## Output
ONE valid JSON file at the `output` path of the batch: `{"batch": "<id>", "articles": [ <record>, ... ]}`, one record per article in batch order.

```json
{
  "pmcid": "PMC...",
  "context": {"article_kind": "research | review | other",
              "carrier_type": "liposome | LNP | SLN | NLC | PLN | polymeric_NP | micelle | nanogel | inorganic_NP | cubosome | nanoemulsion | nanomaterial | other | not_a_nanocarrier",
              "nanocarrier_is_object_of_study": true, "virus_or_pcr": false},
  "panels": [{"fig": "Fig. 2", "variant": "TEM_negstain | TEM_posstain | TEM_dried_unstained | TEM_prep_not_declared | cryoTEM | SEM | STEM | HRTEM | AFM",
              "sample": "name used in the paper", "shows_nanocarrier": true, "scale_bar_in_caption": true,
              "quote": "<=25 words copied VERBATIM from the caption"}],
  "descriptors": [{"sample": "name", "size_nm": 120.5, "pdi": 0.21, "zeta_mV": -25.3, "medium": "water | PBS | buffer | serum | culture_medium | other | not_declared",
                   "source": "Table 1 | text | Fig. 3", "quote": "<=25 words VERBATIM (a table row is fine)"}],
  "spectra": [{"technique": "FTIR | XRD | UVVis | SAXS | EDS | Raman", "fig": "Fig. 4", "applies_to": "nanoparticle | component | mixture | unclear",
               "sample": "name", "quote": "<=25 words VERBATIM from the caption or sentence"}]
}
```

## Rules
1. `panels`: one row per distinct microscopy figure (max 6). `shows_nanocarrier` is false for cells, tissue, bulk materials, scaffolds or a control that is not the nanocarrier. AFM is allowed but is not a micrograph for the gate.
2. `descriptors`: one row per formulation that has a number (max 8). `size_nm` is the DLS/Zetasizer size, not a size read from TEM unless the text says so; use `null` for what is not given. Write `not_declared` if the medium is not in the packet.
3. `spectra`: only FTIR, XRD, UV-Vis, SAXS, EDS/EDX and Raman (SERS counts as Raman). `applies_to` = `nanoparticle` only if it is the nanocarrier (loaded or empty); `component` if it is a pure drug, lipid or polymer; `mixture` for a physical mixture.
4. Every row needs a verbatim `quote` that really appears in the packet. If you cannot quote it, do not write the row.
5. **Nanoparticles that are not formulated for delivery** (green or biogenic synthesis, antimicrobial or antioxidant nanoparticles, commercial nanoparticles, sensor or catalysis nanoparticles that are characterised by microscopy plus size/zeta or spectra) are **still extracted**: set `carrier_type: "nanomaterial"`, `nanocarrier_is_object_of_study: true` (the particles are the object of study) and fill `panels`, `descriptors` and `spectra` as usual. Lignin nanoparticles are `polymeric_NP`.
   Use `carrier_type: "not_a_nanocarrier"` and leave the lists empty only if the article is a review, or if no nanoparticle of its own is characterised (bulk materials, scaffolds, cells, a protein or a molecule).
6. Virus, AAV, phage or VLP carriers: `virus_or_pcr: true` and empty lists.

Reply with ONE line: `extended <batch>: <n> articles, problems: <none|list>`. Do not paste the JSON.
