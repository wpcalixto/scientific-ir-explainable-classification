#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F10b_caracterizacao.py

File type:
    Script

Purpose:
    Characterizes the canonical corpus (one record per domain and document): annual series, main journals, countries and institutions.

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
    - See docs/file_level_documentation.md (entry F10b_caracterizacao.py).

Outputs:
    - See docs/file_level_documentation.md (entry F10b_caracterizacao.py).

Dependencies:
    - matplotlib
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F10b_caracterizacao.py

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

import os, collections, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = BIBLIO_BASE + ""; S = f"{R}/resultados/adequacao_20261110/F10_reexec"
O = f"{S}/caracterizacao"; os.makedirs(O, exist_ok=True)
d = pd.read_csv(f"{S}/dados_openalex/consolidado_todos_dominios.csv", low_memory=False).drop_duplicates(["dominio", "openalex_id"])
DOM = {"microarranjos": "Microarrays", "radiomica": "Radiomics", "metamateriais": "Metamaterials"}
CAT = {"microarranjos": "#2a78d6", "radiomica": "#eb6834", "metamateriais": "#1baf7a"}
anos = range(2018, 2026)
T = d[d.year.between(2018, 2025)].groupby(["dominio", "year"]).size().unstack(0).reindex(anos).fillna(0).astype(int)
T.to_csv(f"{O}/serie_anual.csv")
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e4e3df", "axes.axisbelow": True, "legend.frameon": False})
fig, ax = plt.subplots(figsize=(5, 3.2))
for k in DOM:
    ax.plot(T.index, T[k], color=CAT[k], lw=2, marker="o", ms=4, label=DOM[k])
ax.set_xlabel("Year"); ax.set_ylabel("Documents"); ax.legend(loc="upper left")
fig.tight_layout(); fig.savefig(f"{O}/fig_temporal.pdf"); plt.close(fig)
def top(col, sep=";", n=5):
    out = []
    for k in DOM:
        c = collections.Counter()
        for v in d.loc[d.dominio == k, col].dropna().astype(str):
            c.update({x.strip() for x in v.split(sep) if x.strip()})
        for i, (x, m) in enumerate(c.most_common(n), 1): out.append({"dominio": k, "pos": i, col: x, "n": m})
    return pd.DataFrame(out)
for col in ["countries", "institutions"]:
    top(col).to_csv(f"{O}/top5_{col}.csv", index=False)
j = d.groupby("dominio").journal.value_counts().groupby(level=0).head(5).reset_index(); j.to_csv(f"{O}/top5_journals.csv", index=False)
anos_all = d.groupby("dominio").year.describe()[["min", "25%", "50%", "75%", "max"]]; anos_all.to_csv(f"{O}/anos_resumo.csv")
print(T.to_string()); print(anos_all.to_string())
for f in ["top5_countries", "top5_institutions", "top5_journals"]: print(pd.read_csv(f"{O}/{f}.csv").to_string())
print("F10b FIM")
