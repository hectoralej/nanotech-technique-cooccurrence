"""Pruebas del detector sobre frases de ejemplo, incluidas las trampas de la seccion 3.4 del brief."""
from src.detect import definition, detect, evidence_snippet


def hit(text: str, tech: str, section: str = "results") -> bool:
    return detect({section: text})[tech][section]


# ------------------------------------------------------------------ cryo vs TEM
def test_cryo_tem_not_counted_as_tem():
    t = "Cryo-TEM images showed unilamellar vesicles."
    assert hit(t, "cryoEM")
    assert not hit(t, "TEM")


def test_cryo_full_term_variants():
    for t in ["cryogenic transmission electron microscopy was used", "cryo-electron microscopy of the capsids",
              "cryoTEM grids were prepared", "samples were vitrified on Quantifoil grids", "cryo-ET revealed", "Vitrobot Mark IV"]:
        assert hit(t, "cryoEM"), t


def test_tem_alone_not_cryo():
    t = "Samples were imaged by TEM at 120 kV on carbon-coated copper grids."
    assert hit(t, "TEM") and not hit(t, "cryoEM")


def test_stem_not_counted_as_tem():
    t = "Scanning transmission electron microscopy (STEM) with a HAADF detector was used."
    r = detect({"results": t})
    assert r["STEM"]["results"] and not r["TEM"]["results"]


def test_cryo_sem_is_sem_not_cryoem():
    r = detect({"results": "Cryo-SEM images of the freeze-fractured gel."})
    assert r["SEM"]["results"] and not r["cryoEM"]["results"]


# ------------------------------------------------------------------ siglas ambiguas
def test_sem_standard_error_excluded():
    for t in ["Data are presented as mean ± SEM (n = 3).", "values were 12.3 ± 0.4 nm (SEM)", "Results are expressed as mean ± SEM"]:
        assert not hit(t, "SEM"), t


def test_sem_microscopy_accepted():
    assert hit("SEM images revealed spherical particles.", "SEM")
    assert hit("The morphology was observed by scanning electron microscopy.", "SEM")
    assert hit("FE-SEM micrographs were acquired.", "SEM")


def test_sem_acronym_with_full_term_elsewhere_still_filters_error_bars():
    r = detect({"methods": "Samples were examined by scanning electron microscopy.",
                "results": "Viability was 80 ± 3 % (mean ± SEM)."})
    assert r["SEM"]["methods"] and not r["SEM"]["results"]


def test_tem1_beta_lactamase_excluded():
    assert not hit("The TEM-1 beta-lactamase gene confers resistance.", "TEM")
    assert not hit("Mutants of TEM1 were expressed.", "TEM")


def test_nta_nickel_excluded_and_nanoparticle_tracking_accepted():
    assert not hit("The protein was purified using a Ni-NTA column.", "NTA")
    assert hit("Particle concentration was measured by NTA (NanoSight NS300).", "NTA")
    assert hit("nanoparticle tracking analysis was performed", "NTA")


def test_auc_area_under_curve_not_ultracentrifugation():
    assert not hit("The AUC of the plasma concentration curve was calculated.", "AUC")
    assert hit("Analytical ultracentrifugation (AUC) quantified empty capsids.", "AUC")
    assert hit("SV-AUC was run at 20 000 rpm", "AUC")


def test_eds_syndrome_excluded():
    assert not hit("Patients with Ehlers-Danlos syndrome (EDS) were enrolled.", "EDS")
    assert hit("EDS mapping confirmed the elemental composition on the SEM image.", "EDS")


def test_tga_and_dsc_context():
    assert hit("TGA showed weight loss at 300 °C.", "DSC_TGA")
    assert not hit("Approved by the TGA in Australia.", "DSC_TGA")
    assert hit("Thermal behavior was studied by DSC at 10 °C/min.", "DSC_TGA")


def test_itc_not_counted_as_dsc():
    assert not hit("Binding was measured by isothermal titration calorimetry.", "DSC_TGA")
    assert hit("Differential scanning calorimetry showed an endotherm.", "DSC_TGA")


def test_near_infrared_not_ftir():
    assert not hit("Near-infrared spectroscopy and NIR fluorescence imaging were used.", "FTIR")
    assert hit("ATR-FTIR spectra were recorded.", "FTIR")
    assert hit("Fourier transform infrared spectroscopy confirmed the amide bond.", "FTIR")


# ------------------------------------------------------------------ DLS / zeta
def test_dls_and_zeta_distinct():
    r = detect({"methods": "Size and PDI by dynamic light scattering; zeta potential by electrophoretic light scattering."})
    assert r["DLS"]["methods"] and r["zeta"]["methods"]
    r2 = detect({"methods": "Zeta potential was measured."})
    assert r2["zeta"]["methods"] and not r2["DLS"]["methods"]


def test_zetasizer_contextual():
    r = detect({"methods": "Hydrodynamic size and PDI were measured with a Zetasizer Nano ZS."})
    assert r["DLS"]["methods"]
    r2 = detect({"methods": "Surface charge (zeta) was determined on a Zetasizer Nano ZS in mV."})
    assert r2["zeta"]["methods"]


def test_saxs_sans_xrd_distinct():
    assert hit("SAXS profiles were fitted.", "SAXS") and not hit("SAXS profiles were fitted.", "XRD")
    assert hit("small-angle neutron scattering (SANS)", "SAXS")
    assert hit("XRD patterns showed crystalline peaks", "XRD")
    assert hit("powder X-ray diffraction", "XRD")


def test_nmr_and_uvvis():
    assert hit("1H NMR spectra were recorded in CDCl3", "NMR")
    assert hit("UV-Vis absorption spectra showed a plasmon band at 520 nm", "UVVis")
    assert hit("UV/Vis spectrophotometry", "UVVis")


def test_dls_derived_quantities_count_only_in_results():
    r = detect({"methods": "Size and zeta potential were measured on a Zetasizer Nano ZS.",
                "results": "The z-average diameter was 95 nm with a PDI of 0.12."})
    assert r["DLS"]["methods"] and r["DLS"]["results"]
    assert definition(r["DLS"], "primary")
    # en Metodos "PDI" por si solo no basta
    assert not detect({"methods": "PDI was calculated from the cumulants."})["DLS"]["methods"]


def test_electron_diffraction_not_xrd():
    assert not hit("The SAED diffraction pattern showed rings.", "XRD")
    assert hit("The diffraction peaks matched the reference card.", "XRD")


def test_unicode_hyphens_normalised():
    assert hit("UV‐Vis spectra were recorded.", "UVVis")
    assert hit("Samples were imaged by cryo‑TEM.", "cryoEM")
    assert hit("FT–IR spectra", "FTIR")


def test_surface_plasmon_resonance_biacore_not_uvvis():
    assert not hit("Binding affinities were measured by surface plasmon resonance (SPR) on a Biacore 8K.", "UVVis")
    assert hit("The surface plasmon resonance band of the AuNPs appeared at 520 nm.", "UVVis")


def test_extended_ribogreen_not_matching_quantitative():
    assert not hit("Quantitative analysis and quantity of mRNA were determined.", "RiboGreen_EE", "methods")
    assert hit("Encapsulation efficiency was measured with the Quant-iT RiboGreen assay.", "RiboGreen_EE", "methods")


def test_extended_acronym_traps():
    assert not hit("The AUC of the curve was computed.", "AUC", "results")
    assert hit("Genome titers were measured by ddPCR.", "qPCR_ddPCR", "methods")
    assert not hit("BET inhibitors were administered.", "BET", "methods")
    assert hit("The BET surface area was 300 m2/g.", "BET", "results")


def test_hplc_uv_detector_not_uvvis():
    assert not hit("MRN was detected at 355 nm using a UV-Vis detector (Shimadzu SPD-20A) after HPLC.", "UVVis", "methods")
    assert hit("UV-Vis spectra were recorded on a Jasco V-530 spectrophotometer.", "UVVis", "methods")


def test_xrd_diffractograms_and_diffractometer():
    assert hit("The diffractograms of the samples are shown in Figure 3.", "XRD")
    assert hit("Samples were analysed on an X-ray diffractometer.", "XRD", "methods")


def test_zp_abbreviation_only_in_results():
    assert hit("The ZP of the particles was -20 mV.", "zeta", "results")
    assert not hit("ZP was measured.", "zeta", "methods")


def test_uvvis_spectrophotometer_with_wavelength_but_not_plate_reader():
    assert hit("Drug content was read on a spectrophotometer at a wavelength of 323 nm.", "UVVis", "methods")
    assert not hit("Absorbance was read on a microplate spectrophotometer at 450 nm (ELISA).", "UVVis", "methods")


# ------------------------------------------------------------------ subbanderas
def test_subflags_negative_stain():
    r = detect({"methods": "TEM grids were negatively stained with 2% uranyl acetate."})
    assert r["TEM"]["subflags"]["neg_stain"]
    r2 = detect({"methods": "Negative staining solution was prepared."})   # sin TEM -> subbandera no se activa
    assert not r2["TEM"]["subflags"]["neg_stain"]


# ------------------------------------------------------------------ secciones y definiciones
def test_section_flags_and_definitions():
    r = detect({"methods": "Size was measured by DLS.", "results": "", "caption": "", "other": "Dynamic light scattering is common."})
    assert r["DLS"]["methods"] and not r["DLS"]["results"] and r["DLS"]["other"]
    assert not definition(r["DLS"], "primary")          # Metodos pero sin Resultados/pie
    assert definition(r["DLS"], "methods_only") and definition(r["DLS"], "any")
    r2 = detect({"methods": "Particle size was measured by DLS.", "results": "DLS showed a size of 100 nm."})
    assert definition(r2["DLS"], "primary")
    r3 = detect({"methods": "", "results": "", "caption": "(B) TEM image of the particles.", "other": "TEM was discussed."})
    assert definition(r3["TEM"], "caption_only") and not definition(r3["TEM"], "primary")


def test_mention_in_introduction_is_not_primary():
    r = detect({"intro": "Cryo-TEM has been used to study LNP morphology.", "methods": "", "results": ""})
    assert r["cryoEM"]["other"] and not definition(r["cryoEM"], "primary")


# ------------------------------------------------------------------ evidencia
def test_evidence_snippet_max_25_words():
    text = " ".join(f"w{i}" for i in range(100)) + " dynamic light scattering " + " ".join(f"z{i}" for i in range(100))
    s = text.index("dynamic")
    ev = evidence_snippet(text, s, s + len("dynamic light scattering"))
    assert len(ev.split()) <= 25 and "dynamic light scattering" in ev


def test_detect_returns_evidence_and_section():
    r = detect({"methods": "Cells were grown. Size by DLS.", "caption": "DLS curves."})
    assert r["DLS"]["evidence"] and r["DLS"]["evidence_section"] in {"results", "caption", "methods", "other", "abstract"}
    assert len(r["DLS"]["evidence"].split()) <= 25
