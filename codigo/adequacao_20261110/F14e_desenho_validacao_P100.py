#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F14e_desenho_validacao_P100.py

File type:
    Script

Purpose:
    Precision study and stratified sampling design of the human validation of P@100.

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
    - See docs/file_level_documentation.md (entry F14e_desenho_validacao_P100.py).

Outputs:
    - See docs/file_level_documentation.md (entry F14e_desenho_validacao_P100.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F14e_desenho_validacao_P100.py

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

import os, numpy as np, pandas as pd
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; O = f"{R}/F14_complementares_01A/validacao_P100"; os.makedirs(O, exist_ok=True)
L = pd.read_csv(f"{R}/F7_painel_llm/listas_p100_com_jid.csv")
L = L[L.lista.str.match(r"^(OAL_[ABC]_(bm25|cit)|scopus_top100_[ABC]|wos_top100_[ABC]|elicit_semantico_[ABC])$")].copy()
L["estrategia"] = L.lista.str.extract(r"_([ABC])(?:_|$)")[0]
J = pd.read_csv(f"{R}/F7_painel_llm/analise/J_notas_3llm.csv").set_index("jid").consenso
H = pd.read_csv(f"{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv").set_index("jid").H_med
FAIXAS = [(11, 30), (31, 60), (61, 100)]
L["faixa"] = pd.cut(L["rank"], [10, 30, 60, 100], labels=["11-30", "31-60", "61-100"])
F = L[L.faixa.notna()].copy(); F["p_llm"] = (J.reindex(F.jid).to_numpy() >= 2).astype(float)
EST = F.groupby(["dominio", "estrategia", "lista", "faixa"], observed=True).agg(N=("jid", "size"), p=("p_llm", "mean")).reset_index()
def var_estr(n, conserv):
    E = EST.copy(); E["n"] = np.minimum(n, E.N); pp = 0.5 if conserv else E.p
    E["v"] = E.N ** 2 * pp * (1 - pp) / E.n * (E.N - E.n) / np.maximum(E.N - 1, 1) / 100 ** 2
    V = E.groupby(["dominio", "estrategia"]).v.sum() / 25
    return V
rng = np.random.default_rng(42); linhas = []
for n in [3, 4, 5, 6, 8, 10]:
    for cons in [False, True]:
        V = var_estr(n, cons)
        hw = 1.96 * np.sqrt(V); hwd = {d: max(1.96 * np.sqrt(V[d, a] + V[d, b]) for a, b in [("A", "B"), ("A", "C"), ("C", "B")]) for d in V.index.get_level_values(0).unique()}
        unic = []
        for _ in range(100):
            S = F.groupby(["dominio", "lista", "faixa"], observed=True, group_keys=False).apply(lambda g: g.sample(min(n, len(g)), random_state=int(rng.integers(1e9))))
            u = set(S.jid) - set(H.index); unic.append(len(u))
        linhas.append({"n_por_estrato": n, "p": "0,5 (conservador)" if cons else "consenso LLM", "posicoes_sorteadas": int(EST.N.clip(upper=n).sum()),
                       "documentos_novos_medio": int(np.mean(unic)), "semiamplitude_IC95_estrategia_max": round(float(hw.max()), 3),
                       "semiamplitude_IC95_estrategia_media": round(float(hw.mean()), 3), "semiamplitude_IC95_diferenca_max": round(max(hwd.values()), 3)})
T = pd.DataFrame(linhas); T.to_csv(f"{O}/estudo_precisao.csv", index=False); print(T.to_string(index=False))
EST.to_csv(f"{O}/estratos.csv", index=False)
print("estratos:", len(EST), "| documentos únicos na população 11-100:", F.jid.nunique(), "| já julgados por humanos:", len(set(F.jid) & set(H.index)))
