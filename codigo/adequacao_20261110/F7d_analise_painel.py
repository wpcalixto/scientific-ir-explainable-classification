#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F7d_analise_painel.py

File type:
    Script

Purpose:
    Analyses the three-LLM panel: agreement between judges, consensus and retrieval metrics.

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
    - See docs/file_level_documentation.md (entry F7d_analise_painel.py).

Outputs:
    - See docs/file_level_documentation.md (entry F7d_analise_painel.py).

Dependencies:
    - numpy
    - pandas
    - scipy
    - sklearn
    - statsmodels

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F7d_analise_painel.py

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

import json, re, os, numpy as np, pandas as pd
from itertools import combinations
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.inter_rater import fleiss_kappa, aggregate_raters
from scipy.stats import kendalltau
R = BIBLIO_BASE + "/resultados/adequacao_20261110"
D = f"{R}/F7_painel_llm"; OUT = f"{R}/F7_painel_llm/analise"; os.makedirs(OUT, exist_ok=True)
MODS = ["haiku", "gpt", "gemini"]; SEED = 42; rng = np.random.default_rng(SEED)

resp = {}
for fn in ["respostas_R.jsonl", "respostas_J.jsonl", "respostas_gpt_batch.jsonl"]:
    for l in open(f"{D}/{fn}"):
        j = json.loads(l); resp.setdefault(j["id"], j["resposta"])
CL = {"applied": "Applied", "methodological": "Methodological", "general": "General"}
def rot(s):
    m = re.match(r"\W*(\w+)", s or ""); return CL.get(m.group(1).lower(), "INVALID") if m else "INVALID"
def nota(s):
    m = re.search(r"[012]", s or ""); return int(m.group()) if m else np.nan

am = pd.read_csv(f"{D}/amostra_rotulacao.csv", keep_default_na=False)
am["haiku"] = am["label"]
for m in ["gpt", "gemini"]: am[m] = [rot(resp.get(f"{m}|{c}")) for c in am["custom_id"]]
linhas = []
for dom, g in list(am.groupby("dominio")) + [("todos", am)]:
    ok = g[(g[MODS] != "INVALID").all(axis=1)]
    d = {"dominio": dom, "n": len(g), "n_validos": len(ok)}
    for a, b in combinations(MODS, 2):
        d[f"kappa_{a}_{b}"] = cohen_kappa_score(ok[a], ok[b]); d[f"acordo_{a}_{b}"] = (ok[a] == ok[b]).mean()
    t, _ = aggregate_raters(ok[MODS].to_numpy()); d["fleiss_kappa_3"] = fleiss_kappa(t)
    d["acordo_unanime_3"] = (ok[MODS].nunique(axis=1) == 1).mean()
    for m in MODS: d[f"invalidos_{m}"] = int((g[m] == "INVALID").sum())
    linhas.append(d)
pd.DataFrame(linhas).round(3).to_csv(f"{OUT}/R_concordancia_rotulos.csv", index=False)
pd.concat({m: am.groupby("dominio")[m].value_counts().unstack(fill_value=0) for m in MODS}).to_csv(f"{OUT}/R_distribuicao_rotulos.csv")
am[["dominio", "openalex_id"] + MODS].to_csv(f"{OUT}/R_rotulos_3llm.csv", index=False)

pool = pd.read_csv(f"{D}/pool_relevancia_p100.csv", keep_default_na=False)
for m in MODS: pool[m] = [nota(resp.get(f"{m}|{j}")) for j in pool["jid"]]
pool["consenso"] = pool[MODS].median(axis=1).round()
def alpha_ordinal(X):
    """α de Krippendorff ordinal (unidades nas linhas, avaliadores nas colunas; NaN = em falta)."""
    vals = np.array([0, 1, 2]); o = np.zeros((3, 3))
    for row in X:
        v = row[~np.isnan(row)].astype(int); n = len(v)
        if n < 2: continue
        for i in range(n):
            for k in range(n):
                if i != k: o[v[i], v[k]] += 1 / (n - 1)
    nc = o.sum(1); N = nc.sum()
    dist = np.zeros((3, 3))
    for c in range(3):
        for k in range(3):
            lo, hi = min(c, k), max(c, k)
            dist[c, k] = (nc[lo:hi + 1].sum() - (nc[lo] + nc[hi]) / 2) ** 2
    do = (o * dist).sum(); de = (np.outer(nc, nc) * dist).sum() / (N - 1)
    return 1 - do / de
linhas = []
for dom, g in list(pool.groupby("dominio")) + [("todos", pool)]:
    ok = g.dropna(subset=MODS); d = {"dominio": dom, "n": len(g), "n_validos": len(ok)}
    for a, b in combinations(MODS, 2):
        d[f"kappa_pond_{a}_{b}"] = cohen_kappa_score(ok[a].astype(int), ok[b].astype(int), weights="quadratic")
        d[f"acordo_{a}_{b}"] = (ok[a] == ok[b]).mean()
    d["alpha_ordinal_3"] = alpha_ordinal(g[MODS].to_numpy(float))
    d["acordo_unanime_3"] = (ok[MODS].nunique(axis=1) == 1).mean()
    for m in MODS + ["consenso"]:
        for v in (0, 1, 2): d[f"p{v}_{m}"] = (g[m] == v).mean()
    linhas.append(d)
pd.DataFrame(linhas).round(3).to_csv(f"{OUT}/J_concordancia_relevancia.csv", index=False)
pool[["dominio", "jid", "chave", "title"] + MODS + ["consenso"]].to_csv(f"{OUT}/J_notas_3llm.csv", index=False)

L = pd.read_csv(f"{D}/listas_p100_com_jid.csv", keep_default_na=False)
L["rank"] = pd.to_numeric(L["rank"], errors="coerce"); L = L.dropna(subset=["rank"])
G = pool.set_index("jid")
def dcg(gr): return float(np.sum((2 ** gr - 1) / np.log2(np.arange(2, len(gr) + 2))))
def metr(gr, ideal, k):
    gk = gr[:k]; ik = np.sort(ideal)[::-1][:k]
    gk = np.nan_to_num(gk)
    return {f"P@{k}": (gk >= 1).sum() / k, f"P2@{k}": (gk >= 2).sum() / k,
            f"nDCG@{k}": dcg(gk) / dcg(ik) if dcg(ik) > 0 else np.nan}
linhas = []
for (dom, lst), g in L.sort_values("rank").groupby(["dominio", "lista"]):
    for juiz in MODS + ["consenso"]:
        ideal = pool.loc[pool["dominio"] == dom, juiz].dropna().to_numpy()
        gr = G.loc[g["jid"], juiz].to_numpy(float)
        d = {"dominio": dom, "lista": lst, "juiz": juiz, "n_lista": len(g)}
        for k in (10, 100): d.update(metr(gr, ideal, k))
        if juiz == "consenso":
            for k in (10, 100):
                gk = np.nan_to_num(gr[:k]); bs = [((rng.choice(gk, len(gk)) >= 1).mean()) for _ in range(2000)]
                d[f"P@{k}_ic_inf"], d[f"P@{k}_ic_sup"] = np.percentile(bs, [2.5, 97.5])
        linhas.append(d)
M = pd.DataFrame(linhas); M.round(3).to_csv(f"{OUT}/J_metricas_por_lista.csv", index=False)

est = []
for dom, g in M.groupby("dominio"):
    for met in ["P@10", "nDCG@10", "P@100", "nDCG@100"]:
        w = g.pivot(index="lista", columns="juiz", values=met)
        for a, b in combinations(MODS + ["consenso"], 2):
            est.append({"dominio": dom, "metrica": met, "juiz_a": a, "juiz_b": b, "tau": kendalltau(w[a], w[b]).statistic})
pd.DataFrame(est).round(3).to_csv(f"{OUT}/J_estabilidade_ranking_listas.csv", index=False)
json.dump({"modelos": MODS, "consenso": "mediana das 3 notas", "relevante_P": "nota>=1 (P2: nota>=2)",
           "nDCG": "ganho 2^g-1; ideal = todas as notas do pool do domínio (prof. 100) pelo mesmo juiz",
           "bootstrap": 2000, "seed": SEED}, open(f"{OUT}/metadados_F7d.json", "w"), indent=1, ensure_ascii=False)
print(pd.read_csv(f"{OUT}/R_concordancia_rotulos.csv")[["dominio", "n_validos", "fleiss_kappa_3", "acordo_unanime_3", "kappa_haiku_gpt", "kappa_haiku_gemini", "kappa_gpt_gemini"]].to_string())
print(pd.read_csv(f"{OUT}/J_concordancia_relevancia.csv")[["dominio", "n_validos", "alpha_ordinal_3", "acordo_unanime_3", "kappa_pond_haiku_gpt", "kappa_pond_haiku_gemini", "kappa_pond_gpt_gemini", "p2_consenso", "p1_consenso", "p0_consenso"]].to_string())
c = M[M.juiz == "consenso"].pivot(index="lista", columns="dominio", values="nDCG@10").round(2); print(c.to_string())
print(pd.DataFrame(est).groupby(["metrica"])["tau"].median().round(2).to_string())
print("F7d FIM")
