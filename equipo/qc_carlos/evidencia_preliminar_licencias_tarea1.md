# Evidencia preliminar de licencias — Tarea 1

**Filas objetivo:** 22.  
**Naturaleza:** búsqueda asistida por IA de texto de licencia y enlaces. No se escribió ninguna licencia en el CSV. Carlos debe comprobar la etiqueta del artículo directamente en el sitio del editor y decidir qué registrar. Un PDF oficial puede aportar evidencia, pero si la etiqueta de la página editorial no quedó accesible se indica abajo.

## Etiqueta localizada en material editorial

Estas son pistas textuales de una página del editor o de su PDF. Confirma directamente la etiqueta del DOI antes de editar el CSV.

| n | DOI | Texto/licencia localizada | Fuente y límite |
|---:|---|---|---|
| 27 | [10.1002/marc.202500428](https://onlinelibrary.wiley.com/doi/10.1002/marc.202500428) | Wiley lo identifica como OA; PDF oficial dice “open access under the terms of the Creative Commons Attribution License”, sin versión exacta recuperada. | PDF Wiley; la página HTML no mostró el texto Creative Commons en la pasada. |
| 33 | [10.1038/s41598-017-16563-3](https://www.nature.com/articles/s41598-017-16563-3) | PDF oficial: “This article is licensed under a Creative Commons Attribution 4.0 International License”. | PDF oficial de Nature. |
| 39 | [10.1038/s41598-019-56320-2](https://www.nature.com/articles/s41598-019-56320-2) | PDF oficial: licencia Creative Commons Attribution 4.0 International. | PDF oficial de Nature. |
| 47 | [10.1080/10717544.2017.1337823](https://www.tandfonline.com/doi/full/10.1080/10717544.2017.1337823) | PDF editorial: Open Access bajo Creative Commons Attribution; el enlace de licencia apunta a CC BY 4.0. | PDF del editor; HTML dio error 403, por lo que no se confirmó etiqueta HTML. |
| 51 | [10.1021/acs.jpcb.1c05319](https://pubs.acs.org/doi/abs/10.1021/acs.jpcb.1c05319) | ACS: “This publication is licensed under a Creative Commons Attribution 4.0 International License.” | Texto editorial indexado/página ACS. |
| 52 | [10.3390/pharmaceutics13111751](https://www.mdpi.com/1999-4923/13/11/1751/pdf?version=1635134191) | PDF MDPI: “Creative Commons Attribution (CC BY) license” con enlace a CC BY 4.0. | PDF oficial; la página HTML devolvió 429. |
| 54 | [10.1021/acsnano.1c09367](https://pubs.acs.org/doi/abs/10.1021/acsnano.1c09367) | ACS: “This publication is licensed under CC-BY 4.0.” | Página/editor ACS. |
| 56 | [10.1038/s41598-022-13112-5](https://www.nature.com/articles/s41598-022-13112-5) | PDF oficial: licencia Creative Commons Attribution 4.0 International. | PDF oficial de Nature. |
| 60 | [10.1021/acs.biomac.2c00576](https://pubs.acs.org/doi/10.1021/acs.biomac.2c00576) | ACS: “This publication is licensed under a Creative Commons Attribution 4.0 International License.” | Texto editorial indexado/página ACS. |
| 65 | [10.1021/acs.molpharmaceut.2c00439](https://pubs.acs.org/doi/abs/10.1021/acs.molpharmaceut.2c00439) | ACS: licencia Creative Commons Attribution 4.0 International. | Texto editorial indexado/página ACS. |

## Requieren comprobación directa de Carlos

| n | DOI | Pista y motivo pendiente |
|---:|---|---|
| 1 | [10.3390/pharmaceutics15031021](https://www.mdpi.com/1999-4923/15/3/1021) | MDPI devolvió 429. Un PDF espejo dice CC BY 4.0, pero metadatos de otro repositorio muestran CC BY 2.5/ar; hay que resolverlo en editor/PDF MDPI. |
| 15 | [10.1002/smsc.202400145](https://onlinelibrary.wiley.com/doi/10.1002/smsc.202400145) | Wiley marca Open Access; el texto exacto de licencia no se recuperó. CC BY 4.0 proviene de ScienceOpen, fuente secundaria. |
| 26 | [10.1002/advs.76516](https://onlinelibrary.wiley.com/doi/10.1002/advs.76516) | Wiley no fue accesible; PMC reproduce CC BY 4.0, pero no prueba que se viera la etiqueta en la página del editor. |
| 31 | [PMCID PMC5316245](https://pmc.ncbi.nlm.nih.gov/articles/PMC5316245/) | PMC reproduce “Creative Commons Attribution License” y enlace CC BY 3.0. Es copia de artículo, no página del editor. Confirmar la versión y etiqueta editorial. |
| 48 | [10.1080/10717544.2017.1410263](https://www.tandfonline.com/doi/full/10.1080/10717544.2017.1410263) | Taylor & Francis dio 403. Fuentes secundarias discrepan entre CC BY y CC BY-NC 3.0; no asumir ninguna. |
| 50 | [10.3390/polym13193350](https://www.mdpi.com/2073-4360/13/19/3350) | Página MDPI devolvió 429; no se recuperó texto exacto de licencia. |
| 53 | [10.3390/pharmaceutics13122010](https://www.mdpi.com/1999-4923/13/12/2010) | PDF espejo reproduce CC BY 4.0; la página/PDF oficial no se recuperó en la pasada. |
| 55 | [10.3390/biomedicines10050985](https://www.mdpi.com/2227-9059/10/5/985) | PDF de Semantic Scholar dice CC BY 4.0, pero es copia secundaria; MDPI devolvió 429. |
| 59 | [10.3390/gels8070402](https://www.mdpi.com/2310-2861/8/7/402) | PDF de Semantic Scholar reproduce CC BY 4.0 y OpenAlex lo clasifica CC BY, pero no se obtuvo etiqueta directa MDPI. |
| 61 | [10.1155/2022/9217268](https://onlinelibrary.wiley.com/doi/10.1155/2022/9217268) | Wiley accesible, pero no se encontró la etiqueta Creative Commons; una copia PDF secundaria la describe como CC Attribution sin versión. |
| 62 | [10.3390/gels8090593](https://www.mdpi.com/2310-2861/8/9/593) | Página oficial no recuperada; OpenAlex secundario indica CC BY. El PDF MDPI enlazado necesita revisión directa. |
| 63 | [10.3390/foods11203162](https://www.mdpi.com/2304-8158/11/20/3162) | MDPI devolvió 429 y no se recuperó el PDF/etiqueta del artículo; no inferir licencia a partir de la política general. |

## Uso recomendado

1. Abrir cada DOI en la página del editor y buscar el renglón de licencia del propio artículo.
2. Registrar `CC BY`, `CC0`, otra licencia o `no localizada` exactamente según lo visible.
3. Si solo hay PDF, comprobar que sea el PDF del editor y anotar esa fuente; no equiparar un mirror o metadato secundario con la comprobación directa solicitada.
4. Las pistas de esta nota no cambian los valores de la plantilla; las 22 decisiones siguen pendientes de Carlos.
