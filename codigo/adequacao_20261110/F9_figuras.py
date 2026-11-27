#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F9_figuras.py

File type:
    Script

Purpose:
    Draws result figures (vector PDF) from the F3, F5, F6 and F7d outputs.

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
    - See docs/file_level_documentation.md (entry F9_figuras.py).

Outputs:
    - See docs/file_level_documentation.md (entry F9_figuras.py).

Dependencies:
    - matplotlib
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F9_figuras.py

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

import os, pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; OUT = f"{R}/F9_figuras"; os.makedirs(OUT, exist_ok=True)
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]; INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False})
DOM = {"microarranjos": "Microarrays", "radiomica": "Radiomics", "metamateriais": "Metamaterials"}

d = pd.read_csv(f"{R}/F4_F5/delta_por_base.csv"); bases = ["OpenAlex", "Scopus", "WoS", "SemanticScholar"]
d = d[d.base.isin(bases)]
fig, ax = plt.subplots(figsize=(6.5, 3)); w = 0.2; x = np.arange(3)
for i, b in enumerate(bases):
    v = [d[(d.dominio == k) & (d.base == b)].delta_A_B.squeeze() for k in DOM]
    ax.bar(x + (i - 1.5) * w, v, w * 0.9, color=CAT[i], label=b.replace("SemanticScholar", "Semantic Scholar"), edgecolor="white", linewidth=1)
ax.set_xticks(x, DOM.values()); ax.set_ylabel(r"$\delta = |A|/|B|$"); ax.grid(axis="x", visible=False)
ax.legend(ncol=4, loc="upper left"); fig.tight_layout(); fig.savefig(f"{OUT}/fig_delta_bases.pdf"); plt.close(fig)

M = pd.read_csv(f"{R}/F7_painel_llm/analise/J_metricas_por_lista.csv"); c = M[M.juiz == "consenso"]
ordem = [f"OAL_{s}_{r}" for s in "ABC" for r in ("bm25", "cit")] + [f"{p}_{s}" for p in ("scopus_top100", "wos_top100", "elicit_semantico") for s in "ABC"]
H = c.pivot(index="lista", columns="dominio", values="P2@100").loc[ordem, list(DOM)]
import re
nome = lambda s: re.sub(r"_cit$", " (cit.)", re.sub(r"_bm25$", " (BM25)", s)).replace("scopus_top100", "Scopus").replace("wos_top100", "WoS").replace("elicit_semantico", "Elicit").replace("OAL", "OpenAlex").replace("_", " ")
from matplotlib.colors import LinearSegmentedColormap
cm = LinearSegmentedColormap.from_list("b", ["#cde2fb", "#86b6ef", "#2a78d6", "#184f95", "#0d366b"])
fig, ax = plt.subplots(figsize=(4.6, 5.2)); ax.grid(False)
im = ax.imshow(H.values, cmap=cm, vmin=0, vmax=1, aspect="auto")
for (i, j), v in np.ndenumerate(H.values):
    ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8, color="white" if v > 0.55 else INK)
ax.set_xticks(range(3), DOM.values()); ax.set_yticks(range(len(ordem)), [nome(s) for s in ordem])
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(length=0); cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03); cb.set_label("P@100 (grade 2, 3-LLM consensus)"); cb.outline.set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_precisao_listas.pdf"); plt.close(fig)

b = pd.read_csv(f"{R}/F6_benchmarks/metricas_benchmarks.csv")
mods = ["RegressaoLogistica", "RandomForest", "SVM", "NaiveBayes"]; lab = {"RegressaoLogistica": "LR", "RandomForest": "RF", "SVM": "SVM", "NaiveBayes": "NB"}
mods = [m for m in mods if m in set(b.modelo)]
P = b.pivot(index="conjunto", columns="modelo", values="wss95")[mods].sort_values(mods[0])
fig, ax = plt.subplots(figsize=(6, 5.2)); y = np.arange(len(P))
for i, m in enumerate(mods):
    ax.scatter(P[m], y, s=28, color=CAT[i], label=lab[m], edgecolor="white", linewidth=0.8, zorder=3)
REN = {"Chou_2003": "Cohen 2006 Opioids", "Chou_2004": "Cohen 2006 SkeletalMuscleRelaxants", "Nelson_2002": "Cohen 2006 Estrogens"}
ax.set_yticks(y, [REN.get(s, s).replace("_", " ") for s in P.index]); ax.set_xlabel("WSS@95%"); ax.axvline(0, color=INK2, lw=0.8)
ax.grid(axis="y", visible=False); ax.legend(ncol=4, loc="lower right", bbox_to_anchor=(1, 1.0))
fig.tight_layout(); fig.savefig(f"{OUT}/fig_wss_benchmarks.pdf"); plt.close(fig)

L = pd.read_csv(f"{R}/F3_classificacao/curva_aprendizagem.csv")
fig, ax = plt.subplots(figsize=(5, 3))
for i, m in enumerate([m for m in mods if m in set(L.modelo)]):
    g = L[L.modelo == m].sort_values("n"); ax.plot(g.n, g.f1_macro, color=CAT[i], lw=2, marker="o", ms=4, label=lab[m])
ax.set_ylim(0.70, 0.85); ax.set_xlabel("Training documents (unique, 3 domains)"); ax.set_ylabel("Macro F1 (5-fold CV)"); ax.legend(ncol=4, loc="lower right")
fig.tight_layout(); fig.savefig(f"{OUT}/fig_curva_aprendizagem.pdf"); plt.close(fig)
print(sorted(os.listdir(OUT)))
