#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F6b_validacao_externa_classificadores.py

File type:
    Script

Purpose:
    External validation of the classifiers on public screening benchmarks.

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
    - See docs/file_level_documentation.md (entry F6b_validacao_externa_classificadores.py).

Outputs:
    - See docs/file_level_documentation.md (entry F6b_validacao_externa_classificadores.py).

Dependencies:
    - numpy
    - pandas
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F6b_validacao_externa_classificadores.py

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

import os, glob, json, warnings
import numpy as np, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, f1_score, recall_score
warnings.filterwarnings("ignore")
BASE = BIBLIO_BASE + ""
IN = f"{BASE}/dados/externos/benchmarks_triagem"
OUT = f"{BASE}/resultados/adequacao_20261110/F6_benchmarks"; os.makedirs(OUT, exist_ok=True)
SEED = 42
def tfidf(): return TfidfVectorizer(min_df=3, max_df=0.85, ngram_range=(1, 2), max_features=10_000, sublinear_tf=True)
MOD = {
 "SVM": lambda: Pipeline([("tfidf", tfidf()), ("clf", CalibratedClassifierCV(LinearSVC(C=1.0, class_weight="balanced", random_state=SEED), cv=3))]),
 "RandomForest": lambda: Pipeline([("tfidf", tfidf()), ("clf", RandomForestClassifier(n_estimators=200, min_samples_split=5, class_weight="balanced", random_state=SEED, n_jobs=-1))]),
 "RegressaoLogistica": lambda: Pipeline([("tfidf", tfidf()), ("clf", LogisticRegression(C=1.0, max_iter=2000, class_weight="balanced", random_state=SEED))]),
 "NaiveBayes": lambda: Pipeline([("tfidf", tfidf()), ("clf", MultinomialNB(alpha=0.1))]),
}
def wss(y, s, r=0.95):
    o = np.argsort(-s); ys = y[o]; need = int(np.ceil(r * ys.sum()))
    k = int(np.searchsorted(np.cumsum(ys), need) + 1)
    return (len(y) - k) / len(y) - (1 - r)
rows = []
for f in sorted(glob.glob(f"{IN}/*.csv")):
    nome = os.path.basename(f)[:-4]
    d = pd.read_csv(f, dtype=str, keep_default_na=False)
    d = d[(d["title"] + d["abstract"]).str.len() > 0]
    y = d["label_included"].astype(int).values; X = (d["title"] + ". " + d["abstract"]).values
    k = min(5, int(y.sum()))
    if k < 2: continue
    for m, fn in MOD.items():
        P = cross_val_predict(fn(), X, y, cv=StratifiedKFold(k, shuffle=True, random_state=SEED), method="predict_proba")[:, 1]
        p = (P >= 0.5).astype(int)
        rows.append({"conjunto": nome, "n": len(y), "incluidos": int(y.sum()), "prevalencia_%": round(100 * y.mean(), 2), "folds": k,
                     "modelo": m, "auc": round(roc_auc_score(y, P), 4), "f1": round(f1_score(y, p, zero_division=0), 4),
                     "revocacao": round(recall_score(y, p, zero_division=0), 4), "wss95": round(wss(y, P), 4)})
        print(nome, m, rows[-1]["auc"], rows[-1]["wss95"], flush=True)
    pd.DataFrame(rows).to_csv(f"{OUT}/metricas_benchmarks.csv", index=False)
r = pd.DataFrame(rows)
r.groupby("modelo")[["auc", "f1", "revocacao", "wss95"]].agg(["mean", "std", "median"]).round(4).to_csv(f"{OUT}/resumo_por_modelo.csv")
print("F6 FIM", flush=True)
