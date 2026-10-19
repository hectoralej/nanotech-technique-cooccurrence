# Arbitration task: resolve disagreements between two independent extractions

Two independent extraction passes (A and B) disagree on some items for the articles in your conflict file. For each article you get: the packet path
(article text: Methods, Results, figure captions, tables) and a list of `issues`. Each issue shows what A and B recorded (rows with a verbatim quote and location).

Your job: for every issue decide who is right, using ONLY the packet text. Be strict and skeptical: if the packet does not clearly support a value, it is NOT supported.

## How to decide

- Issue types:
  - `gate:micro` / `gate:dls` / `gate:zeta`: is there a *useful* measurement? Definitions:
    - micrograph useful = a figure panel (or raw image) of the nanocarrier itself (not a control, component, cells or tissue), technique/variant identifiable, linkable to a formulation (explicit or inferred).
    - DLS useful = numeric particle size with the **medium stated** (water, PBS, buffer, serum...) for an identifiable nanoparticle sample (loaded or empty).
    - zeta useful = numeric zeta potential with the **medium or pH stated** for an identifiable nanoparticle sample.
    - If the value exists but the medium is not stated in the packet, it is NOT useful (set decision accordingly and note `medium_no_declarado`).
  - `gate:object` / `gate:research` / `gate:viral_pcr`: is the nanocarrier the object of study; is it a primary research article; is the carrier a virus/VLP/phage or does its characterization rely on PCR (qPCR as a biological readout does not count).
  - `keys:<technique>`: the passes disagree on variant, sample identity or medium of some measurement. Decide the correct values.
  - `values:<technique>`: the passes give different numbers. Decide which numbers are in the packet (look at the tables).
- Search the whole packet (Methods, Results, captions, tables) before deciding. A medium may be stated in Methods far from the Results table.

## Output

Write ONE JSON file (path given in the task): `{"batch": "<id>", "articles": [{"pmcid": "...", "decisions": [ ... ]}]}` with one decision per issue:

```json
{"issue": "PMC123:gate:dls", "decision": "A | B | neither | both | unresolved",
 "final": {"value": true, "identity": null, "variant": null, "medium": null},
 "quote": "<=25 words copied VERBATIM from the packet that settles it (required unless unresolved)",
 "location": "Methods > ... | Table 2 | Fig. 3 caption",
 "reason": "<=30 words"}
```

`final.value` is the resolved boolean for gate issues; for `keys` issues fill the corrected `identity` (nanoparticle_loaded | nanoparticle_empty | pure_component | physical_mixture | process_intermediate | unclear), `variant`, `medium` (water | PBS | buffer | serum | culture_medium | other:<text> | not_declared) as needed; unused keys null.
Use `unresolved` when the packet does not settle it. Never guess.

Reply with ONE short line: `arbitration <id>: <n> articles, <m> issues, unresolved: <k>`.
