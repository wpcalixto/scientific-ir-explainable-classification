#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F10d_metricas_cortes.py

File type:
    Script

Purpose:
    Computes retrieval metrics per list at cut-offs 10, 20, 50 and 100 with the median of the three LLM judges.

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
    - See docs/file_level_documentation.md (entry F10d_metricas_cortes.py).

Outputs:
    - See docs/file_level_documentation.md (entry F10d_metricas_cortes.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F10d_metricas_cortes.py

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

import numpy as np, pandas as pd
R = BIBLIO_BASE + "/resultados/adequacao_20261110/F7_painel_llm"
pool = pd.read_csv(f"{R}/analise/J_notas_3llm.csv"); L = pd.read_csv(f"{R}/listas_p100_com_jid.csv", keep_default_na=False)
L["rank"] = pd.to_numeric(L["rank"], errors="coerce"); L = L.dropna(subset=["rank"]).sort_values("rank")
G = pool.set_index("jid")["consenso"]
def dcg(g): return float(np.sum((2 ** g - 1) / np.log2(np.arange(2, len(g) + 2))))
out = []
for (d, lst), g in L.groupby(["dominio", "lista"]):
    gr = np.nan_to_num(G.reindex(g["jid"]).to_numpy(float)); ideal = np.sort(pool.loc[pool.dominio == d, "consenso"].to_numpy(float))[::-1]
    nrel = int((ideal >= 2).sum())
    for l in (10, 20, 50, 100):
        gk = gr[:l]
        out.append({"dominio": d, "lista": lst, "l": l, "P_estrita": (gk >= 2).sum() / l, "P_branda": (gk >= 1).sum() / l,
                    "R": (gk >= 2).sum() / nrel, "nDCG": dcg(gk) / dcg(ideal[:l]), "N_rel_pool": nrel})
O = pd.DataFrame(out).round(3); O.to_csv(f"{R}/analise/J_metricas_cortes.csv", index=False)
print(O[O.lista.str.startswith("OAL")].pivot_table(index=["dominio", "lista"], columns="l", values=["P_estrita", "nDCG"]).round(2).to_string())
print(O.groupby("dominio").N_rel_pool.first())
