# Note for the SHORT packet (pass A, expansion rounds)

The packet you receive is an EXCERPT, not the whole article: title, abstract, the sentences about DLS / zeta / microscopy / other techniques (tagged [M] methods, [R] results), the figure captions about them, and the tables about size, zeta and composition.

- Work fast and in one pass: read the packet once, fill the record, write the file. Do not re-read.
- The excerpt may not contain the medium, the formulation composition or the preparation state. In that case write `not_declared` / `null` and add the flag `medio_no_declarado`. Never infer from general knowledge.
- Tables are complete: read each formulation row of the size/zeta tables (one row per formulation, up to the limits in the rules).
- Every measurement still needs a verbatim quote (<= 25 words) copied from the packet, including table rows (copy a row exactly as printed, without the header).
- Complementary techniques (FTIR, XRD, DSC, ...): record them only if the excerpt shows they were applied to the nanoparticle.
- `pass` in the output file is `"A"`.
