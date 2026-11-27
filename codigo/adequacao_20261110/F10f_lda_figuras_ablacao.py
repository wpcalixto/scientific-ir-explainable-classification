#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F10f_lda_figuras_ablacao.py

File type:
    Script

Purpose:
    Builds the composite LDA figures (coherence curves and PCA by strategy) and the LDA-features row of the ablation.

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
    - See docs/file_level_documentation.md (entry F10f_lda_figuras_ablacao.py).

Outputs:
    - See docs/file_level_documentation.md (entry F10f_lda_figuras_ablacao.py).

Dependencies:
    - matplotlib
    - numpy
    - pandas
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F10f_lda_figuras_ablacao.py

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

import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.patches as mp
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; S = f"{R}/F10_reexec"; D = f"{S}/dados_processados"
DOM = {"microarranjos": "Microarrays", "metamateriais": "Metamaterials", "radiomica": "Radiomics"}
COR = {"busca_A": "#2a78d6", "busca_B": "#eb6834", "busca_C": "#1baf7a"}
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, axs = plt.subplots(1, 3, figsize=(9, 2.8))
for a, (d, n) in zip(axs, DOM.items()):
    c = pd.read_csv(f"{D}/coherence_scores_{d}.csv"); k = c.k[c.coherence.idxmax()]
    a.plot(c.k, c.coherence, color="#2a78d6", lw=2, marker="o", ms=3); a.axvline(k, color="#e34948", ls="--", lw=1); a.set_title(f"{n} (k*={k})"); a.set_xlabel("k"); a.set_ylabel("$c_v$")
fig.tight_layout(); fig.savefig(f"{S}/figuras_pdf/fig_coherence.pdf"); plt.close(fig)
long = pd.read_csv(f"{S}/dados_openalex/consolidado_todos_dominios.csv", usecols=["openalex_id", "dominio", "estrategia"], low_memory=False)
fig, axs = plt.subplots(1, 3, figsize=(10, 3.3)); abl = []
can = pd.read_csv(f"{R}/F2_corpus/corpus_canonico.csv", usecols=["dominio", "openalex_id", "label"], keep_default_na=False)
for a, (d, n) in zip(axs, DOM.items()):
    t = pd.read_csv(f"{D}/lda_doc_topics_{d}.csv", low_memory=False); cols = [x for x in t.columns if x.startswith("topic_")]
    m = long[long.dominio == d].merge(t[["openalex_id"] + cols], on="openalex_id")
    Z = PCA(2, random_state=42).fit_transform(StandardScaler().fit_transform(m[cols]))
    for e, cor in COR.items():
        z = Z[m.estrategia == e]; a.scatter(z[:, 0], z[:, 1], s=3, alpha=0.25, color=cor)
        mu, cov = z.mean(0), np.cov(z.T); v, w = np.linalg.eigh(cov); o = v.argsort()[::-1]; v, w = v[o], w[:, o]
        a.add_patch(mp.Ellipse(mu, 2 * 2.447 * np.sqrt(v[0]), 2 * 2.447 * np.sqrt(v[1]), angle=np.degrees(np.arctan2(w[1, 0], w[0, 0])), fill=False, color=cor, lw=1.5, ls="--"))
    a.set_title(n); a.set_xlabel("PC1"); a.set_ylabel("PC2")
    y = t[["openalex_id"]].merge(can[can.dominio == d], on="openalex_id", how="left")["label"]
    ok = y.isin(["Applied", "Methodological", "General"]).to_numpy()
    r = cross_validate(LogisticRegression(max_iter=2000, class_weight="balanced"), t.loc[ok, cols], y[ok], cv=StratifiedKFold(5, shuffle=True, random_state=42),
                       scoring={"acc": "accuracy", "f1": "f1_macro", "prec": "precision_macro", "rec": "recall_macro"})
    abl.append({"dominio": d, "k": len(cols), "n": int(ok.sum()), **{s: r[f"test_{s}"].mean() for s in ["acc", "f1", "prec", "rec"]}})
axs[0].legend(handles=[mp.Patch(color=c, label=e.replace("busca_", "Strategy ")) for e, c in COR.items()], frameon=False, fontsize=7)
fig.tight_layout(); fig.savefig(f"{S}/figuras_pdf/fig_pca.pdf"); plt.close(fig)
A = pd.DataFrame(abl); A.round(3).to_csv(f"{S}/classificacao/ablacao_lda_por_dominio.csv", index=False); print(A.round(3).to_string())
for d in DOM:
    tp = pd.read_csv(f"{D}/lda_topics_{d}.csv"); print("==", d)
    for k, g in tp.groupby("topico"): print(k, ", ".join(g.sort_values(g.columns[-1], ascending=False).termo.head(5)) if "termo" in g else g.head(1))
