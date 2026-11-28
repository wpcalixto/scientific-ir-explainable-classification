#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F10c_classif_figuras_lime_ablacao.py

File type:
    Script

Purpose:
    Re-runs the classification analyses on the canonical corpus (unique documents with abstract): classifier comparison, SHAP, LIME, ablation and figures.

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
    - See docs/file_level_documentation.md (entry F10c_classif_figuras_lime_ablacao.py).

Outputs:
    - See docs/file_level_documentation.md (entry F10c_classif_figuras_lime_ablacao.py).

Dependencies:
    - lime
    - matplotlib
    - numpy
    - pandas
    - shap
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F10c_classif_figuras_lime_ablacao.py

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

import os, json, numpy as np, pandas as pd, matplotlib, warnings
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold, cross_validate, cross_val_predict, learning_curve
from sklearn.metrics import confusion_matrix, roc_curve, auc
warnings.filterwarnings("ignore")
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; OUT = f"{R}/F10_reexec/classificacao"; os.makedirs(OUT, exist_ok=True)
SEED = 42; CLS = ["Applied", "Methodological", "General"]
c = pd.read_csv(f"{R}/F2_corpus/corpus_canonico.csv", keep_default_na=False, low_memory=False)
c = c[(c.resumo_ok.astype(str).isin(["1", "True", "true"])) & c.label.isin(CLS)].drop_duplicates("openalex_id")
X = (c.title + " " + c.abstract).tolist(); y = c.label.to_numpy(); print("n =", len(c), dict(pd.Series(y).value_counts()))
TF = dict(ngram_range=(1, 2), min_df=3, max_df=0.85, max_features=10000, sublinear_tf=True)
cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
MOD = {"SVM": CalibratedClassifierCV(LinearSVC(class_weight="balanced"), cv=3), "RF": RandomForestClassifier(200, class_weight="balanced", min_samples_split=5, n_jobs=6, random_state=SEED),
       "RL": LogisticRegression(max_iter=2000, class_weight="balanced"), "NB": MultinomialNB(alpha=0.1)}
SC = {"acc": "accuracy", "f1": "f1_macro", "prec": "precision_macro", "rec": "recall_macro"}
res = []
for k, m in MOD.items():
    r = cross_validate(make_pipeline(TfidfVectorizer(**TF), m), X, y, cv=cv, scoring=SC, n_jobs=5)
    res.append({"modelo": k, **{f"{s}_media": r[f"test_{s}"].mean() for s in SC}, **{f"{s}_dp": r[f"test_{s}"].std() for s in SC}}); print(res[-1])
B = pd.DataFrame(res); B.to_csv(f"{OUT}/metricas_4modelos_dp.csv", index=False)
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})
fig, ax = plt.subplots(figsize=(6.5, 3.2)); w = 0.2; xs = np.arange(4)
for i, (s, nome) in enumerate([("acc", "Accuracy"), ("f1", "Macro F1"), ("prec", "Macro precision"), ("rec", "Macro recall")]):
    ax.bar(xs + (i - 1.5) * w, B[f"{s}_media"], w * 0.9, yerr=B[f"{s}_dp"], color=CAT[i], label=nome, capsize=2, edgecolor="white")
ax.set_xticks(xs, B.modelo); ax.set_ylim(0.5, 1); ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.15)); ax.grid(axis="y", color="#e4e3df")
fig.tight_layout(); fig.savefig(f"{OUT}/fig_classificadores_barras.pdf"); plt.close(fig)
pipe = make_pipeline(TfidfVectorizer(**TF), LogisticRegression(max_iter=2000, class_weight="balanced"))
P = cross_val_predict(pipe, X, y, cv=cv, method="predict_proba", n_jobs=5); classes = np.array(sorted(CLS)); pred = classes[P.argmax(1)]
cm = confusion_matrix(y, pred, labels=CLS); pd.DataFrame(cm, index=CLS, columns=CLS).to_csv(f"{OUT}/confusao_RL.csv")
fig, ax = plt.subplots(figsize=(3.4, 3)); ax.imshow(cm / cm.sum(1, keepdims=True), cmap="Blues", vmin=0, vmax=1)
for (i, j), v in np.ndenumerate(cm): ax.text(j, i, f"{v}", ha="center", va="center", color="white" if cm[i, j] / cm[i].sum() > 0.5 else "black")
ax.set_xticks(range(3), CLS, rotation=20); ax.set_yticks(range(3), CLS); ax.set_xlabel("Predicted"); ax.set_ylabel("LLM label")
fig.tight_layout(); fig.savefig(f"{OUT}/fig_confusion.pdf"); plt.close(fig)
fig, ax = plt.subplots(figsize=(3.4, 3)); aucs = {}
for i, cl in enumerate(CLS):
    j = list(classes).index(cl); fpr, tpr, _ = roc_curve(y == cl, P[:, j]); aucs[cl] = auc(fpr, tpr)
    ax.plot(fpr, tpr, color=CAT[i], lw=2, label=f"{cl} (AUC={aucs[cl]:.3f})")
ax.plot([0, 1], [0, 1], color="#999", lw=0.8, ls="--"); ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate"); ax.legend(loc="lower right", fontsize=7)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_roc.pdf"); plt.close(fig)
n, tr, va = learning_curve(pipe, X, y, cv=cv, scoring="f1_macro", train_sizes=np.linspace(0.1, 1, 6), n_jobs=5)
pd.DataFrame({"n": n, "treino": tr.mean(1), "treino_dp": tr.std(1), "valid": va.mean(1), "valid_dp": va.std(1)}).to_csv(f"{OUT}/curva_treino_validacao.csv", index=False)
fig, ax = plt.subplots(figsize=(3.6, 3))
for v, cor, nome in [(tr, CAT[0], "Training"), (va, CAT[1], "Validation")]:
    ax.plot(n, v.mean(1), color=cor, lw=2, marker="o", ms=3, label=nome); ax.fill_between(n, v.mean(1) - v.std(1), v.mean(1) + v.std(1), color=cor, alpha=0.2)
ax.set_xlabel("Training documents"); ax.set_ylabel("Macro F1"); ax.legend(); fig.tight_layout(); fig.savefig(f"{OUT}/fig_learning.pdf"); plt.close(fig)
import shap
pipe.fit(X, y); vec, lr = pipe.steps[0][1], pipe.steps[1][1]; Xt = vec.transform(X); fn = vec.get_feature_names_out()
rng = np.random.default_rng(SEED); idx = rng.choice(Xt.shape[0], 2000, replace=False)
ex = shap.LinearExplainer(lr, Xt[rng.choice(Xt.shape[0], 500, replace=False)]); sv = ex.shap_values(Xt[idx])
sv = np.stack(sv, -1) if isinstance(sv, list) else sv
imp = np.abs(sv).mean(0)
glob = pd.Series(imp.sum(1), index=fn).sort_values(ascending=False); glob.head(30).to_csv(f"{OUT}/shap_global_top30.csv")
porc = {cl: pd.Series(imp[:, list(lr.classes_).index(cl)], index=fn).sort_values(ascending=False).head(10) for cl in CLS}
pd.DataFrame({cl: list(v.index) for cl, v in porc.items()}).to_csv(f"{OUT}/shap_top10_classe.csv", index=False)
fig, ax = plt.subplots(figsize=(4, 4.5)); g = glob.head(20)[::-1]; ax.barh(g.index, g.values, color=CAT[0]); ax.set_xlabel("mean |SHAP| (sum over classes)")
fig.tight_layout(); fig.savefig(f"{OUT}/fig_shap_global.pdf"); plt.close(fig)
fig, axs = plt.subplots(1, 3, figsize=(9, 3))
for a, (cl, v), cor in zip(axs, porc.items(), CAT):
    a.barh(v.index[::-1], v.values[::-1], color=cor); a.set_title(cl); a.tick_params(labelsize=7)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_shap_classes.pdf"); plt.close(fig)
from lime.lime_text import LimeTextExplainer
le = LimeTextExplainer(class_names=list(lr.classes_), random_state=SEED); rows = []
fig, axs = plt.subplots(1, 3, figsize=(10, 3.2))
for a, cl, cor in zip(axs, CLS, CAT):
    j = list(classes).index(cl); ok = np.where((y == cl) & (pred == cl))[0]; d = ok[P[ok, j].argmax()]
    e = le.explain_instance(X[d], pipe.predict_proba, labels=[j], num_features=10, num_samples=2000)
    lst = e.as_list(label=j); rows += [{"classe": cl, "openalex_id": c.openalex_id.iloc[d], "titulo": c.title.iloc[d], "confianca": P[d, j], "termo": t, "peso": w} for t, w in lst]
    t, w = zip(*lst[::-1]); a.barh(t, w, color=["#1baf7a" if x > 0 else "#e34948" for x in w]); a.set_title(f"{cl} (p={P[d, j]:.2f})", fontsize=9); a.tick_params(labelsize=7)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_lime.pdf"); plt.close(fig); pd.DataFrame(rows).to_csv(f"{OUT}/lime_casos.csv", index=False)
ABL = {"CountVec binário (1,2)": make_pipeline(CountVectorizer(binary=True, ngram_range=(1, 2), min_df=3, max_df=0.85, max_features=10000), LogisticRegression(max_iter=2000, class_weight="balanced")),
       "TF-IDF unigramas": make_pipeline(TfidfVectorizer(**{**TF, "ngram_range": (1, 1)}), LogisticRegression(max_iter=2000, class_weight="balanced")),
       "TF-IDF (1,2) sem balanceamento": make_pipeline(TfidfVectorizer(**TF), LogisticRegression(max_iter=2000)),
       "Protocolo completo": pipe}
ab = []
for k, m in ABL.items():
    r = cross_validate(m, X, y, cv=cv, scoring=SC, n_jobs=5); ab.append({"config": k, **{s: r[f"test_{s}"].mean() for s in SC}})
A = pd.DataFrame(ab); A["dF1"] = A.f1 - A.loc[A.config == "Protocolo completo", "f1"].iloc[0]; A.round(3).to_csv(f"{OUT}/ablacao.csv", index=False)
json.dump({"n": len(c), "auc_por_classe_RL": aucs, "seed": SEED}, open(f"{OUT}/metadados_F10c.json", "w"), indent=1)
print(B.round(3).to_string()); print(aucs); print(A.round(3).to_string()); print(pd.DataFrame(rows)[["classe", "confianca", "termo", "peso"]].round(3).to_string()); print("F10c FIM")
