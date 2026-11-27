#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F15f_conferencia_M3.py

File type:
    Script

Purpose:
    Checks the implementation of the document-level Bayesian bootstrap (M3) of the human P@100.

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
    - See docs/file_level_documentation.md (entry F15f_conferencia_M3.py).

Outputs:
    - See docs/file_level_documentation.md (entry F15f_conferencia_M3.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F15f_conferencia_M3.py

Portability notes:
    All paths are resolved relative to the package base directory given by the BIBLIO_BASE environment variable
    (default: the package root, two levels above codigo/adequacao_20261110/). No machine-specific path is required.
    API keys, when needed, are read from ~/.config/bibliogenre/ and ~/.config/bibliometria/ and are not part of the package.

Reproducibility notes:
    Environment pinned in requirements.txt and environment/. Seeds and frozen parameters are written in the code and
    summarized in docs/parameters.md.

Warnings:
    Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.
"""

import os as _bb_os
BIBLIO_BASE = _bb_os.environ.get("BIBLIO_BASE") or _bb_os.path.abspath(
    _bb_os.path.join(_bb_os.path.dirname(_bb_os.path.abspath(__file__)), "..", ".."))

import os, sys, numpy as np, pandas as pd
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; V = f"{R}/F14_complementares_01A/validacao_P100"
S = pd.read_csv(f"{V}/amostra_posicoes_NAO_ENVIAR.csv"); S = S[S.sorteado].reset_index(drop=True)
H = pd.read_csv(f"{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv").set_index("jid").H_med
NC = pd.read_csv(f"{V}/F15_resultados_20261112/controlo/notas_consolidadas.csv", keep_default_na=False, dtype=str)
nova = NC[NC.tipo == "amostra"].set_index("jid").nota.astype(float)
S["y"] = np.where(S.ja_julgado_top10, H.reindex(S.jid).to_numpy(), nova.reindex(S.jid).to_numpy()) >= 2
L = pd.read_csv(f"{R}/F7_painel_llm/listas_p100_com_jid.csv"); L = L[L.lista.isin(S.lista.unique()) & (L["rank"] <= 10)]
h10 = L.assign(r=(H.reindex(L.jid).to_numpy() >= 2)).groupby(["dominio", "lista"]).r.sum()
def estimar(w):
    x = S.assign(w=w, wy=w * S.y).groupby(["dominio", "lista", "estrategia", "faixa"]).agg(w=("w", "sum"), wy=("wy", "sum"), N=("N_estrato", "first")).reset_index()
    x["tot"] = x.N * x.wy / x.w
    l = x.groupby(["dominio", "lista", "estrategia"]).tot.sum().reset_index(); l["P"] = (l.tot + h10.reindex(pd.MultiIndex.from_frame(l[["dominio", "lista"]])).to_numpy()) / 100
    e = l.groupby(["dominio", "estrategia"]).P.mean(); out = {f"{d}|{s}": v for (d, s), v in e.items()}
    for d in S.dominio.unique():
        for a, b in [("A", "B"), ("A", "C"), ("C", "B")]: out[f"{d}|{a}-{b}"] = e[(d, a)] - e[(d, b)]
    return out
base = estimar(np.ones(len(S)))
rng = np.random.default_rng(7); reps = []
for _ in range(2000):
    w = np.zeros(len(S))
    for d, g in S.groupby("dominio"):
        u = g.jid.unique(); gam = rng.gamma(1.0, 1.0, len(u)); wd = dict(zip(u, gam / gam.sum() * len(u)))
        w[g.index] = g.jid.map(wd).to_numpy()
    reps.append(estimar(w))
B = pd.DataFrame(reps); B.round(5).to_csv(f"{OUT}/F15f_replicas_M3.csv", index=False)
ref = pd.read_csv(f"{V}/F15e_bootstrap_20261113/B_intervalos_dados_reais.csv").set_index("alvo")
r = pd.DataFrame({"estimativa": pd.Series(base), "F15f_inf": B.quantile(.025), "F15f_sup": B.quantile(.975)})
r["F15e_inf"] = ref["doc-bayes_inf"].reindex(r.index); r["F15e_sup"] = ref["doc-bayes_sup"].reindex(r.index); r["est_F15e"] = ref.estimativa.reindex(r.index)
r["dif_max"] = np.maximum(abs(r.F15f_inf - r.F15e_inf), abs(r.F15f_sup - r.F15e_sup))
r.round(4).to_csv(f"{OUT}/F15f_conferencia_M3.csv"); print(r.round(4).to_string()); print("estimativas iguais:", bool((abs(r.estimativa - r.est_F15e) < 1e-4).all()), "| diferença máxima dos limites:", round(r.dif_max.max(), 4))
