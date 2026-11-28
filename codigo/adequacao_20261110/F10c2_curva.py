#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F10c2_curva.py

File type:
    Script

Purpose:
    Computes the training versus validation learning curve of logistic regression in the three domains with shuffled training subsamples.

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
    - See docs/file_level_documentation.md (entry F10c2_curva.py).

Outputs:
    - See docs/file_level_documentation.md (entry F10c2_curva.py).

Dependencies:
    - matplotlib
    - numpy
    - pandas
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F10c2_curva.py

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

import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold, learning_curve
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; OUT = f"{R}/F10_reexec/classificacao"; CLS = ["Applied", "Methodological", "General"]
c = pd.read_csv(f"{R}/F2_corpus/corpus_canonico.csv", keep_default_na=False, low_memory=False)
c = c[(c.resumo_ok.astype(str).isin(["1", "True", "true"])) & c.label.isin(CLS)].drop_duplicates("openalex_id")
X = (c.title + " " + c.abstract).tolist(); y = c.label.to_numpy()
pipe = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_df=0.85, max_features=10000, sublinear_tf=True), LogisticRegression(max_iter=2000, class_weight="balanced"))
n, tr, va = learning_curve(pipe, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=42), scoring="f1_macro", train_sizes=np.linspace(0.1, 1, 6), shuffle=True, random_state=42, n_jobs=5)
pd.DataFrame({"n": n, "treino": tr.mean(1), "treino_dp": tr.std(1), "valid": va.mean(1), "valid_dp": va.std(1)}).to_csv(f"{OUT}/curva_treino_validacao.csv", index=False)
fig, ax = plt.subplots(figsize=(3.6, 3))
for v, cor, nome in [(tr, "#2a78d6", "Training"), (va, "#eb6834", "Validation")]:
    ax.plot(n, v.mean(1), color=cor, lw=2, marker="o", ms=3, label=nome); ax.fill_between(n, v.mean(1) - v.std(1), v.mean(1) + v.std(1), color=cor, alpha=0.2)
ax.spines[["top", "right"]].set_visible(False); ax.set_xlabel("Training documents"); ax.set_ylabel("Macro F1"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_learning.pdf"); print(pd.read_csv(f"{OUT}/curva_treino_validacao.csv").round(3).to_string())
