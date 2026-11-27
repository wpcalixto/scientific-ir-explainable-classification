#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F20_verifica_metricas_SES.py

File type:
    Script

Purpose:
    Verifies the denominators of R@l and the identifier sets of the external search engine lists.

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
    - See docs/file_level_documentation.md (entry F20_verifica_metricas_SES.py).

Outputs:
    - See docs/file_level_documentation.md (entry F20_verifica_metricas_SES.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F20_verifica_metricas_SES.py

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

import sys, hashlib, numpy as np, pandas as pd
OUT = sys.argv[1]
R = BIBLIO_BASE + "/resultados/adequacao_20261110/F7_painel_llm"; A = f"{R}/analise"
pool = pd.read_csv(f"{A}/J_notas_3llm.csv"); nov = pd.read_csv(f"{A}/J_notas_3llm_s2_novos.csv", keep_default_na=False)
L = pd.read_csv(f"{R}/listas_s2_com_jid.csv", keep_default_na=False).sort_values("rank"); pub = pd.read_csv(f"{A}/J_metricas_cortes_s2.csv")
G = pd.concat([pool[["jid", "consenso"]], nov[["jid", "consenso"]]]).drop_duplicates("jid").set_index("jid").consenso
no_pool = set(pool.jid)
def dcg(g): return float(np.sum((2 ** g - 1) / np.log2(np.arange(2, len(g) + 2))))
rows = []
for (d, lst), g in L.groupby(["dominio", "lista"]):
    gr = np.nan_to_num(G.reindex(g.jid).to_numpy(float)); ids = g.jid.to_numpy()
    ideal = np.sort(pool.loc[pool.dominio == d, "consenso"].to_numpy(float))[::-1]; nrel = int((ideal >= 2).sum())
    for l in (10, 20, 50, 100):
        gk, ik = gr[:l], ids[:l]; rel = gk >= 2
        rel_pool = int(sum(r and (j in no_pool) for r, j in zip(rel, ik))); rel_ses = int(rel.sum()) - rel_pool
        ideal_l = ideal[:l]; idcg_todas2 = bool((ideal_l == 2).all() and len(ideal_l) == l)
        p = pub[(pub.dominio == d) & (pub.lista == lst) & (pub.l == l)].iloc[0]
        r_calc = rel.sum() / nrel; n_calc = dcg(gk) / dcg(ideal_l)
        rows.append({"dominio": d, "estrategia": lst[-1], "corte": l, "docs_recuperados": int(min(len(g), l)), "relevantes_recuperados": int(rel.sum()),
                     "relevantes_no_pool_principal": rel_pool, "relevantes_so_SES": rel_ses, "denominador_R@l": nrel,
                     "formula_R_calculada": "(relevantes da lista SES, incl. só-SES) / N_rel do pool principal",
                     "conjunto_IDCG": f"top-{l} do pool principal do domínio ({'todas nota 2 = DCG máximo possível' if idcg_todas2 else 'não todas nota 2'})",
                     "R_publicado": p.R, "R_recalculado": round(r_calc, 3), "nDCG_publicado": p.nDCG, "nDCG_recalculado": round(n_calc, 3),
                     "verif_R": "INCOMPATÍVEL" if rel_ses > 0 else "CONFIRMADO",
                     "verif_nDCG": "CONFIRMADO" if idcg_todas2 else "INCOMPATÍVEL",
                     "nota": ("lista com 40 documentos: posições 41–100 sem documento (ganho 0); P usa denominador nominal l" if len(g) < l else "")})
T = pd.DataFrame(rows); T.to_csv(f"{OUT}/P03_PEND01_SES_36_linhas.csv", index=False)
for f in ["J_notas_3llm.csv", "J_notas_3llm_s2_novos.csv", "J_metricas_cortes_s2.csv"]: print(f, hashlib.sha256(open(f"{A}/{f}", "rb").read()).hexdigest())
print("reprodução R/nDCG publicados:", bool((abs(T.R_publicado - T.R_recalculado) < 0.0015).all() and (abs(T.nDCG_publicado - T.nDCG_recalculado) < 0.0015).all()))
print(T.verif_R.value_counts().to_dict(), T.verif_nDCG.value_counts().to_dict())
pd.set_option("display.width", 220); print(T[["dominio", "estrategia", "corte", "relevantes_recuperados", "relevantes_no_pool_principal", "relevantes_so_SES", "denominador_R@l", "R_publicado", "verif_R", "verif_nDCG"]].to_string(index=False))
