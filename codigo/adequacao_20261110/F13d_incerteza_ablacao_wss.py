#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F13d_incerteza_ablacao_wss.py

File type:
    Script

Purpose:
    Re-runs the ablation with the same code, corpus and partitions to estimate its uncertainty and WSS@95%.

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
    - See docs/file_level_documentation.md (entry F13d_incerteza_ablacao_wss.py).

Outputs:
    - See docs/file_level_documentation.md (entry F13d_incerteza_ablacao_wss.py).

Dependencies:
    - numpy
    - pandas
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F13d_incerteza_ablacao_wss.py

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

import numpy as np, pandas as pd, warnings
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
warnings.filterwarnings("ignore")
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; O = f"{R}/F13_complementares"
SEED = 42; CLS = ["Applied", "Methodological", "General"]
c = pd.read_csv(f"{R}/F2_corpus/corpus_canonico.csv", keep_default_na=False, low_memory=False)
c = c[(c.resumo_ok.astype(str).isin(["1", "True", "true"])) & c.label.isin(CLS)].drop_duplicates("openalex_id")
X = (c.title + " " + c.abstract).tolist(); y = c.label.to_numpy()
TF = dict(ngram_range=(1, 2), min_df=3, max_df=0.85, max_features=10000, sublinear_tf=True)
cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
ABL = {"CountVec binário (1,2)": make_pipeline(CountVectorizer(binary=True, ngram_range=(1, 2), min_df=3, max_df=0.85, max_features=10000), LogisticRegression(max_iter=2000, class_weight="balanced")),
       "TF-IDF unigramas": make_pipeline(TfidfVectorizer(**{**TF, "ngram_range": (1, 1)}), LogisticRegression(max_iter=2000, class_weight="balanced")),
       "TF-IDF (1,2) sem balanceamento": make_pipeline(TfidfVectorizer(**TF), LogisticRegression(max_iter=2000)),
       "Protocolo completo": make_pipeline(TfidfVectorizer(**TF), LogisticRegression(max_iter=2000, class_weight="balanced"))}
rows = []
for k, m in ABL.items():
    r = cross_validate(m, X, y, cv=cv, scoring={"f1": "f1_macro", "acc": "accuracy"}, n_jobs=5)
    for i, (f, a) in enumerate(zip(r["test_f1"], r["test_acc"])): rows.append({"config": k, "particao": i, "f1": f, "acc": a})
A = pd.DataFrame(rows); A.to_csv(f"{O}/ablacao_por_particao.csv", index=False)
ref = A[A.config == "Protocolo completo"].set_index("particao").f1; res = []
for k, g in A.groupby("config", sort=False):
    dif = g.set_index("particao").f1 - ref
    res.append({"config": k, "n": len(c), "f1_media": round(g.f1.mean(), 4), "f1_dp": round(g.f1.std(ddof=1), 4),
                "dif_media": round(dif.mean(), 4), "dif_min": round(dif.min(), 4), "dif_max": round(dif.max(), 4),
                "particoes_acima_do_completo": int((dif > 0).sum())})
pd.DataFrame(res).to_csv(f"{O}/ablacao_resumo.csv", index=False); print(pd.DataFrame(res).to_string(index=False))
B = pd.read_csv(f"{R}/F6_benchmarks/metricas_benchmarks.csv"); rng = np.random.default_rng(42); wi = []
for m, g in B.groupby("modelo"):
    v = g.wss95.to_numpy(); bs = [rng.choice(v, len(v)).mean() for _ in range(10000)]
    wi.append({"modelo": m, "n_conjuntos": len(v), "wss_media": round(v.mean(), 4), "ic95_inf": round(np.percentile(bs, 2.5), 4),
               "ic95_sup": round(np.percentile(bs, 97.5), 4), "min": round(v.min(), 4), "max": round(v.max(), 4)})
pd.DataFrame(wi).to_csv(f"{O}/wss_ic.csv", index=False); print(pd.DataFrame(wi).to_string(index=False))
