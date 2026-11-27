#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F10c3_fig_learning.py

File type:
    Script

Purpose:
    Redraws the learning-curve figure from curva_treino_validacao.csv.

Repository:
    scientific-ir-explainable-classification

Version:
    v1.0.0

Date:
    2026-11-27

Developer:
    Prof. Wesley Pacheco Calixto

Authors:
    Viviane M. Gomes Pacheco; ORCID 0000-0003-3693-4377; EMC/UFG; PUC Goias; CPDT/IFG
    Clóves Gonçalves Rodrigues; ORCID 0000-0003-0140-9847; PUC Goias
    Antonio Paulo Coimbra; ORCID 0000-0003-3780-2405; ISR/University of Coimbra
    Wesley Pacheco Calixto; ORCID 0000-0002-1928-4432; ISR/University of Coimbra; EMC/UFG; CPDT/IFG

Corresponding author:
    Wesley Pacheco Calixto, wesley.pacheco@ufg.br

License:
    MIT

Citation:
    If you use this code, please cite:
    Pacheco, V. M. G., Rodrigues, C. G., Coimbra, A. P., & Calixto, W. P. (2026). Reproducibility package for a protocol for scientific information retrieval with explainable text classification: code, bibliographic search datasets, LLM and human relevance judgements and analysis results (v1.0.0) [Data set and software]. Zenodo. https://doi.org/10.5281/zenodo.19791096

Related publication:
    Protocol for scientific information retrieval with explainable text classification: design and cross-domain evaluation (manuscript; DOI not yet available)

Inputs:
    - See docs/file_level_documentation.md (entry F10c3_fig_learning.py).

Outputs:
    - See docs/file_level_documentation.md (entry F10c3_fig_learning.py).

Dependencies:
    - matplotlib
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F10c3_fig_learning.py

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

import pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
O = BIBLIO_BASE + "/resultados/adequacao_20261110/F10_reexec/classificacao"
c = pd.read_csv(f"{O}/curva_treino_validacao.csv")
fig, ax = plt.subplots(figsize=(3.6, 3))
for col, cor, nome in [("treino", "#2a78d6", "Training"), ("valid", "#eb6834", "Validation")]:
    ax.plot(c.n, c[col], color=cor, lw=2, marker="o", ms=3, label=nome); ax.fill_between(c.n, c[col] - c[col + "_dp"], c[col] + c[col + "_dp"], color=cor, alpha=0.2)
ax.set_xticks([0, 5000, 10000, 15000]); ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x/1000:.0f}k"))
ax.spines[["top", "right"]].set_visible(False); ax.set_xlabel("Training documents"); ax.set_ylabel("Macro F1"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(f"{O}/fig_learning.pdf")
