#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F7e_robustez.py

File type:
    Script

Purpose:
    Robustness of the relevance conclusions without human judgement (single judge and alternative consensus rules).

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
    - See docs/file_level_documentation.md (entry F7e_robustez.py).

Outputs:
    - See docs/file_level_documentation.md (entry F7e_robustez.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F7e_robustez.py

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
R = BIBLIO_BASE + "/resultados/adequacao_20261110/F7_painel_llm"; A = f"{R}/analise"
rng = np.random.default_rng(42)
pool = pd.read_csv(f"{A}/J_notas_3llm.csv"); L = pd.read_csv(f"{R}/listas_p100_com_jid.csv", keep_default_na=False)
L["rank"] = pd.to_numeric(L["rank"], errors="coerce"); L = L.dropna(subset=["rank"]).sort_values("rank")
estr = lambda s: s[4] if s.startswith("OAL") else s[-1]
L["estr"] = L.lista.map(estr)
M = pd.read_csv(f"{A}/J_metricas_por_lista.csv"); M["estr"] = M.lista.map(estr)
s1 = M.groupby(["juiz", "dominio", "estr"])[["P2@100", "nDCG@100"]].mean().unstack("estr").round(3)
s1.to_csv(f"{A}/robustez_juiz_unico.csv"); print(s1.to_string())
def dcg(g): return float(np.sum((2 ** g - 1) / np.log2(np.arange(2, len(g) + 2))))
pos = {d: g.reset_index(drop=True) for d, g in pool.groupby("dominio")}
listas = {k: g for k, g in L.groupby(["dominio", "lista"])}
out = []
for e in (0.05, 0.10, 0.20, 0.30):
    cont = {}
    for rep in range(1000):
        res = {}
        for d, g in pos.items():
            y = g["consenso"].to_numpy(float).copy(); m = rng.random(len(y)) < e
            passo = np.where(y == 2, -1, np.where(y == 0, 1, rng.choice([-1, 1], len(y))))
            y[m] = np.clip(y[m] + passo[m], 0, 2); nota = dict(zip(g["jid"], y)); ideal = np.sort(y)[::-1][:100]
            for (dd, lst), gl in listas.items():
                if dd != d: continue
                gr = np.nan_to_num(np.array([nota.get(j, 0) for j in gl["jid"][:100]]))
                res[(d, estr(lst), lst)] = ((gr >= 2).mean(), dcg(gr) / dcg(ideal))
        df = pd.DataFrame([(d, s, p, n) for (d, s, _), (p, n) in res.items()], columns=["d", "s", "p", "n"]).groupby(["d", "s"]).mean()
        for d in pos:
            for met in ("p", "n"):
                a, b, c = (df.loc[(d, k), met] for k in "ABC")
                for nome, ok in (("A>B", a > b), ("C>B", c > b), ("A>C", a > c)):
                    cont.setdefault((d, met, nome), []).append(ok)
    for (d, met, nome), v in cont.items():
        out.append({"erro_juiz": e, "dominio": d, "metrica": {"p": "P2@100", "n": "nDCG@100"}[met], "relacao": nome, "freq_mantida": np.mean(v)})
O = pd.DataFrame(out); O.to_csv(f"{A}/robustez_ruido_juiz.csv", index=False)
print(O.pivot_table(index=["metrica", "relacao", "dominio"], columns="erro_juiz", values="freq_mantida").round(3).to_string()); print("F7e FIM")
