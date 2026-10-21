# Task: is the measurement medium declared? (rescue pass)

You receive a batch file with several articles. For each article and each technique (DLS = particle size, zeta = zeta potential) you get:
- `rows`: measurements already extracted (sample name and value) whose **medium was not declared** in the first extraction;
- `sentences`: candidate sentences from the article (Methods first) that mention the technique near a medium word (water, PBS, buffer, serum, culture medium...).

Work ONLY from these sentences. Do not use outside knowledge.

## Decide, per article and technique
Is there a sentence that clearly says in which medium the nanoparticles were **dispersed or diluted for that size or zeta measurement**?

Accept only if:
- the sentence is about the measurement itself (the sample for DLS/zeta was diluted or dispersed in X, or measured in X);
- it applies to **all** the samples in `rows` (one general Methods statement is enough).

Do NOT accept:
- the medium used to prepare the nanoparticles (hydration medium, synthesis solvent), for drug release, or for cell exposure;
- a medium that applies only to some samples (use `applies_to: "some"`);
- anything that is not in the sentences.

## Output
Write ONE valid JSON file to the `output` path of the batch: `{"batch": "<id>", "articles": [{"pmcid": "...", "decisions": [ ... ]}]}` with one decision per technique listed in `needs` of that article:

```json
{"technique": "DLS", "medium": "water | PBS | buffer | serum | culture_medium | other:<text> | not_found",
 "applies_to": "all_samples | some | unclear",
 "quote": "<=25 words copied VERBATIM from one of the sentences (required unless not_found)",
 "reason": "<=20 words"}
```

Be strict: when in doubt, `not_found`. Reply with ONE line: `rescue <batch>: <n> articles, accepted: <k>`. Do not paste the JSON.
