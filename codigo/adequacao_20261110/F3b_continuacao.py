#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F3b_continuacao.py

File type:
    Script

Purpose:
    Continuation of F3 (learning curve, SHAP and metadata) after an interruption.

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
    - See docs/file_level_documentation.md (entry F3b_continuacao.py).

Outputs:
    - See docs/file_level_documentation.md (entry F3b_continuacao.py).

Dependencies:
    - numpy
    - pandas
    - shap
    - sklearn
    - statsmodels

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F3b_continuacao.py

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

import os, json, itertools, warnings
import numpy as np, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score, confusion_matrix, precision_recall_fscore_support
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.multitest import multipletests
warnings.filterwarnings("ignore")
BASE = BIBLIO_BASE + ""
OUT = f"{BASE}/resultados/adequacao_20261110/F3_classificacao"; os.makedirs(OUT, exist_ok=True)
SEED, K, NB = 42, 5, 2000
CL = ["Applied", "Methodological", "General"]
rng = np.random.default_rng(SEED)
def tfidf(): return TfidfVectorizer(min_df=3, max_df=0.85, ngram_range=(1, 2), max_features=10_000, sublinear_tf=True)
MOD = {
 "SVM": lambda: Pipeline([("tfidf", tfidf()), ("clf", CalibratedClassifierCV(LinearSVC(C=1.0, class_weight="balanced", random_state=SEED), cv=3))]),
 "RandomForest": lambda: Pipeline([("tfidf", tfidf()), ("clf", RandomForestClassifier(n_estimators=200, min_samples_split=5, class_weight="balanced", random_state=SEED, n_jobs=-1))]),
 "RegressaoLogistica": lambda: Pipeline([("tfidf", tfidf()), ("clf", LogisticRegression(C=1.0, max_iter=2000, class_weight="balanced", random_state=SEED))]),
 "NaiveBayes": lambda: Pipeline([("tfidf", tfidf()), ("clf", MultinomialNB(alpha=0.1))]),
}
c = pd.read_csv(f"{BASE}/resultados/adequacao_20261110/F2_corpus/corpus_canonico.csv", dtype={"openalex_id": str}, keep_default_na=False)
c = c[(c["resumo_ok"].astype(str) == "True") & c["label"].isin(CL)].copy()
c["texto"] = c["title"] + ". " + c["abstract"]
uniq = c.sort_values("dominio").drop_duplicates("openalex_id")
def mets(y, p, P):
    Y = np.array([[v == k for k in CL] for v in y], int)
    pres = [k for k in range(3) if 0 < Y[:, k].sum() < len(y)]
    auc = roc_auc_score(Y[:, pres], P[:, pres], average="macro") if pres else np.nan
    return {"acc": accuracy_score(y, p), "f1_macro": f1_score(y, p, average="macro", labels=CL, zero_division=0),
            "f1_weighted": f1_score(y, p, average="weighted", labels=CL, zero_division=0), "auc_ovr_macro": auc}
def boot(y, p, P):
    n = len(y); r = {k: [] for k in ["acc", "f1_macro", "f1_weighted", "auc_ovr_macro"]}
    for _ in range(NB):
        i = rng.integers(0, n, n)
        for k, v in mets(y[i], p[i], P[i]).items(): r[k].append(v)
    return {k: (np.nanpercentile(v, 2.5), np.nanpercentile(v, 97.5)) for k, v in r.items()}
def oof(df, nome):
    y = df["label"].values; X = df["texto"].values
    skf = StratifiedKFold(K, shuffle=True, random_state=SEED); res = {}
    for m, f in MOD.items():
        P = cross_val_predict(f(), X, y, cv=skf, method="predict_proba", n_jobs=1)
        ordem = sorted(set(y)); Pf = np.zeros((len(y), 3))
        for j, k in enumerate(ordem): Pf[:, CL.index(k)] = P[:, j]
        p = np.array(CL)[Pf.argmax(1)]; res[m] = (p, Pf)
    return y, res
yd = uniq["dominio"].values
Pd = cross_val_predict(MOD["RegressaoLogistica"](), uniq["texto"].values, yd, cv=StratifiedKFold(K, shuffle=True, random_state=SEED))
conf = {"acc_prever_dominio": float(accuracy_score(yd, Pd))}
lc = []
for frac in [0.1, 0.2, 0.4, 0.6, 0.8, 1.0]:
    sub = uniq.groupby("label", group_keys=False).sample(frac=frac, random_state=SEED) if frac < 1 else uniq
    for m in ["RegressaoLogistica", "SVM"]:
        p = cross_val_predict(MOD[m](), sub["texto"].values, sub["label"].values, cv=StratifiedKFold(K, shuffle=True, random_state=SEED))
        lc.append({"frac": frac, "n": len(sub), "modelo": m, "f1_macro": f1_score(sub["label"].values, p, average="macro")})
pd.DataFrame(lc).to_csv(f"{OUT}/curva_aprendizagem.csv", index=False)

import shap
NUC = {"microarranjos": ["microarray", "gene", "expression", "genes", "transcriptom", "omics", "rna"],
       "radiomica": ["radiomic", "ct", "mri", "imaging", "image", "tumor", "tumour", "radiolog"],
       "metamateriais": ["metamaterial", "metasurface", "electromagnetic", "photonic", "optical", "antenna", "terahertz", "wave"]}
sh, nuc = [], []
for d in ["microarranjos", "radiomica", "metamateriais", "tres_dominios"]:
    df = uniq if d == "tres_dominios" else c[c["dominio"] == d]
    pipe = MOD["RegressaoLogistica"]().fit(df["texto"].values, df["label"].values)
    Xt = pipe["tfidf"].transform(df["texto"].values); voc = pipe["tfidf"].get_feature_names_out()
    ex = shap.LinearExplainer(pipe["clf"], Xt, feature_perturbation="interventional")
    sv = ex.shap_values(Xt)
    sv = [sv[:, :, k] for k in range(sv.shape[2])] if isinstance(sv, np.ndarray) and sv.ndim == 3 else sv
    for k, cl in enumerate(pipe["clf"].classes_):
        imp = np.abs(np.asarray(sv[k])).mean(0); ordem = np.argsort(-imp)[:25]
        for r, j in enumerate(ordem): sh.append({"modelo_treino": d, "classe": cl, "rank": r + 1, "termo": voc[j], "mean_abs_shap": float(imp[j])})
        tot = imp.sum()
        for dn, termos in NUC.items():
            msk = np.array([any(t in v.split() or v.startswith(t) for t in termos) for v in voc])
            nuc.append({"modelo_treino": d, "classe": cl, "termos_dominio": dn, "pct_importancia": round(100 * imp[msk].sum() / tot, 2)})
pd.DataFrame(sh).to_csv(f"{OUT}/shap_top25_dominio_classe.csv", index=False)
pd.DataFrame(nuc).to_csv(f"{OUT}/shap_peso_termos_dominio.csv", index=False)
json.dump({"confundimento": conf, "n_por_dominio": c["dominio"].value_counts().to_dict(), "n_tres_dominios": len(uniq),
           "desvio": "SVC(probability) -> CalibratedClassifierCV(LinearSVC, cv=3); DeLong -> bootstrap pareado da AUC macro OvR",
           "sementes": SEED, "bootstrap": NB}, open(f"{OUT}/metadados_F3.json", "w"), indent=1, ensure_ascii=False)
print("F3 FIM", flush=True)
