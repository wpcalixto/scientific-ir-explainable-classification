#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F14a_wss_diferenca_pareada.py

File type:
    Script

Purpose:
    95% confidence interval of the paired WSS@95% difference between logistic regression and each other classifier.

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
    - See docs/file_level_documentation.md (entry F14a_wss_diferenca_pareada.py).

Outputs:
    - See docs/file_level_documentation.md (entry F14a_wss_diferenca_pareada.py).

Dependencies:
    - numpy
    - pandas
    - scipy

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F14a_wss_diferenca_pareada.py

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

import os, numpy as np, pandas as pd
from scipy.stats import wilcoxon
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; O = f"{R}/F14_complementares_01A"; os.makedirs(O, exist_ok=True)
B = pd.read_csv(f"{R}/F6_benchmarks/metricas_benchmarks.csv").pivot(index="conjunto", columns="modelo", values="wss95")
assert len(B) == 18 and B.notna().all().all()
rng = np.random.default_rng(42); rows = []
for m in ["RandomForest", "SVM", "NaiveBayes"]:
    d = (B["RegressaoLogistica"] - B[m]).to_numpy(); bs = [rng.choice(d, len(d)).mean() for _ in range(10000)]
    rows.append({"comparacao": f"RL - {m}", "n": len(d), "dif_media": round(d.mean(), 4), "ic95_inf": round(np.percentile(bs, 2.5), 4),
                 "ic95_sup": round(np.percentile(bs, 97.5), 4), "RL_melhor": int((d > 0).sum()), "p_wilcoxon": round(wilcoxon(d).pvalue, 4)})
pd.DataFrame(rows).to_csv(f"{O}/wss_diferenca_pareada.csv", index=False); print(pd.DataFrame(rows).to_string(index=False))
