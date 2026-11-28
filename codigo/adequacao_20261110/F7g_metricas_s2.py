#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F7g_metricas_s2.py

File type:
    Script

Purpose:
    Retrieval metrics of the Semantic Scholar lists with the three LLM judges.

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
    - See docs/file_level_documentation.md (entry F7g_metricas_s2.py).

Outputs:
    - See docs/file_level_documentation.md (entry F7g_metricas_s2.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F7g_metricas_s2.py

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

import json, re, numpy as np, pandas as pd
import importlib.util
R = BIBLIO_BASE + "/resultados/adequacao_20261110/F7_painel_llm"; A = f"{R}/analise"
MODS = ["haiku", "gpt", "gemini"]
def nota(s):
    m = re.search(r"[012]", s or ""); return int(m.group()) if m else np.nan
resp = {}
for fn in ["respostas_J_s2.jsonl", "respostas_gpt_batch_s2.jsonl"]:
    for l in open(f"{R}/{fn}"):
        j = json.loads(l); resp.setdefault(j["id"], j["resposta"])
nov = pd.read_csv(f"{R}/pool_s2_novos.csv", keep_default_na=False)
for m in MODS: nov[m] = [nota(resp.get(f"{m}|{j}")) for j in nov.jid]
nov["consenso"] = nov[MODS].median(axis=1).round()
pool = pd.read_csv(f"{A}/J_notas_3llm.csv")
spec = importlib.util.spec_from_file_location("f7d", BIBLIO_BASE + "/codigo/adequacao_20261110/F7d_analise_painel.py")
src = open(spec.origin).read(); alpha_src = src[src.index("def alpha_ordinal"):src.index("linhas = []\nfor dom, g in list(pool.groupby")]
ns = {"np": np}; exec(alpha_src, ns); alpha = ns["alpha_ordinal"]
G = pd.concat([pool[["jid"] + MODS + ["consenso"]], nov[["jid"] + MODS + ["consenso"]]]).drop_duplicates("jid").set_index("jid")
L = pd.read_csv(f"{R}/listas_s2_com_jid.csv", keep_default_na=False).sort_values("rank")
def dcg(g): return float(np.sum((2 ** g - 1) / np.log2(np.arange(2, len(g) + 2))))
out = []
for (d, lst), g in L.groupby(["dominio", "lista"]):
    gr = np.nan_to_num(G.consenso.reindex(g.jid).to_numpy(float)); ideal = np.sort(pool.loc[pool.dominio == d, "consenso"].to_numpy(float))[::-1]; nrel = int((ideal >= 2).sum())
    for l in (10, 20, 50, 100):
        gk = gr[:l]; out.append({"dominio": d, "lista": lst, "l": l, "n_lista": len(g), "P_estrita": (gk >= 2).sum() / l, "P_branda": (gk >= 1).sum() / l, "R": (gk >= 2).sum() / nrel, "nDCG": dcg(gk) / dcg(ideal[:l])})
O = pd.DataFrame(out).round(3); O.to_csv(f"{A}/J_metricas_cortes_s2.csv", index=False)
nov.to_csv(f"{A}/J_notas_3llm_s2_novos.csv", index=False)
print(O.pivot_table(index=["dominio", "lista"], columns="l", values=["P_estrita", "nDCG"]).to_string())
print("n por lista:", L.groupby(["dominio", "lista"]).size().to_dict())
for d, g in nov.groupby("dominio"): print(d, len(g), "alpha", round(alpha(g[MODS].to_numpy(float)), 3), "dist", g.consenso.value_counts(normalize=True).round(3).to_dict())
print("alpha total novos", round(alpha(nov[MODS].to_numpy(float)), 3), "unânime", round((nov[MODS].nunique(axis=1) == 1).mean(), 3))
