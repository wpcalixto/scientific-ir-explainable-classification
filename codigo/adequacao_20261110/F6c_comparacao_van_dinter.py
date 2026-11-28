#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F6c_comparacao_van_dinter.py

File type:
    Script

Purpose:
    Compares the WSS@95% of the four classifiers with published values (van Dinter et al.).

Repository:
    scientific-ir-explainable-classification

Version:
    v1.0.1

Date:
    2026-11-27

Developer:
    Prof. Wesley Pacheco Calixto

Authors:
    Wesley Pacheco Calixto; ORCID 0000-0002-1928-4432; ISR/University of Coimbra; EMC/UFG; CPDT/IFG
    Viviane M. Gomes Pacheco; ORCID 0000-0003-3693-4377; EMC/UFG; PUC Goias; CPDT/IFG
    Clóves Gonçalves Rodrigues; ORCID 0000-0003-0140-9847; PUC Goias
    Antonio Paulo Coimbra; ORCID 0000-0003-3780-2405; ISR/University of Coimbra

Corresponding author:
    Wesley Pacheco Calixto, wesley.pacheco@ufg.br

License:
    MIT

Citation:
    If you use this code, please cite:
    Calixto, W. P., Pacheco, V. M. G., Rodrigues, C. G., & Coimbra, A. P. (2026). Reproducibility package for a protocol for scientific information retrieval with explainable text classification: code, bibliographic search datasets, LLM and human relevance judgements and analysis results (v1.0.1) [Data set and software]. Zenodo. https://doi.org/10.5281/zenodo.24615095

Related publication:
    Protocol for scientific information retrieval with explainable text classification: design and cross-domain evaluation (manuscript; DOI not yet available)

Inputs:
    - See docs/file_level_documentation.md (entry F6c_comparacao_van_dinter.py).

Outputs:
    - See docs/file_level_documentation.md (entry F6c_comparacao_van_dinter.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F6c_comparacao_van_dinter.py

Portability notes:
    All paths are resolved relative to the package base directory given by the BIBLIO_BASE environment variable
    (default: the package root, two levels above codigo/adequacao_20261110/). No machine-specific path is required.
    API keys, when needed, are read from ~/.config/bibliogenre/ and ~/.config/bibliometria/ and are not part of the package.

Reproducibility notes:
    Environment pinned in requirements.txt and environment/. Seeds and frozen parameters are written in the code and
    summarized in docs/parameters.md.

Warnings:
    None.
"""

import os as _bb_os
BIBLIO_BASE = _bb_os.environ.get("BIBLIO_BASE") or _bb_os.path.abspath(
    _bb_os.path.join(_bb_os.path.dirname(_bb_os.path.abspath(__file__)), "..", ".."))

import io, pandas as pd, numpy as np
R = BIBLIO_BASE + "/resultados/adequacao_20261110/F6_benchmarks"
PUB = """conjunto,Cohen2006,Matwin2010,Cohen2008,Howard2016,Kontonatsios2020,vanDinter_M2,vanDinter_M5
Wassenaar_2017,,,,0.752,0.758,0.792,0.735
Rooney_2015,,,,0.805,0.848,0.071,0.059
Walker_2018,,,,0.714,0.707,0.708,0.592
Cohen_2006_ACEInhibitors,0.566,0.523,0.733,0.801,0.787,0.783,0.805
Cohen_2006_ADHD,0.680,0.622,0.526,0.793,0.665,0.698,0.683
Cohen_2006_Antihistamines,0.000,0.149,0.236,0.137,0.310,0.168,0.162
Cohen_2006_AtypicalAntipsychotics,0.141,0.206,0.170,0.251,0.329,0.212,0.234
Cohen_2006_BetaBlockers,0.284,0.367,0.465,0.428,0.587,0.504,0.514
Cohen_2006_CalciumChannelBlockers,0.122,0.234,0.430,0.448,0.424,0.159,0.177
Nelson_2002,0.183,0.375,0.414,0.471,0.397,0.119,0.171
Cohen_2006_NSAIDS,0.497,0.528,0.672,0.730,0.723,0.571,0.611
Chou_2003,0.133,0.554,0.364,0.826,0.533,0.295,0.290
Cohen_2006_OralHypoglycemics,0.090,0.085,0.136,0.117,0.095,0.065,0.085
Cohen_2006_ProtonPumpInhibitors,0.277,0.229,0.328,0.378,0.400,0.243,0.254
Chou_2004,0.000,0.265,0.374,0.556,0.286,0.229,0.162
Cohen_2006_Statins,0.247,0.315,0.491,0.436,0.566,0.443,0.446
Cohen_2006_Triptans,0.034,0.274,0.346,0.412,0.434,0.266,0.259
Cohen_2006_UrinaryIncontinence,0.261,0.296,0.432,0.530,0.531,0.272,0.306
"""
pub = pd.read_csv(io.StringIO(PUB)).set_index("conjunto")
nos = pd.read_csv(f"{R}/metricas_benchmarks.csv").pivot(index="conjunto", columns="modelo", values="wss95")
nos.columns = [f"nosso_{c}" for c in nos.columns]
T = nos.join(pub, how="inner"); T.to_csv(f"{R}/comparacao_wss95_publicados.csv")
drug = [c for c in T.index if c not in ("Wassenaar_2017", "Rooney_2015", "Walker_2018")]
res = pd.DataFrame({"media_drug_15": T.loc[drug].mean(), "media_swift_3": T.loc[["Wassenaar_2017", "Rooney_2015", "Walker_2018"]].mean(),
                    "media_18": T.mean()}).round(3)
ref = "nosso_RegressaoLogistica"
res["LR_vence_em_n_de_18"] = [np.nan if c == ref else int((T[ref] > T[c]).sum()) for c in res.index]
res.to_csv(f"{R}/comparacao_wss95_resumo.csv"); print(res.to_string()); print("F6c FIM")
