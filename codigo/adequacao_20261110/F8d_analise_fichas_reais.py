#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F8d_analise_fichas_reais.py

File type:
    Script

Purpose:
    Analyses the first three human sheets (W, U, V): consistency and agreement with the LLM judges.

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
    - See docs/file_level_documentation.md (entry F8d_analise_fichas_reais.py).

Outputs:
    - See docs/file_level_documentation.md (entry F8d_analise_fichas_reais.py).

Dependencies:
    - numpy
    - pandas
    - scipy
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F8d_analise_fichas_reais.py

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

import re, hashlib, json, itertools, numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score
from scipy.stats import kendalltau, spearmanr
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; F = f"{R}/F8_julgamento/fichas_reais_20261111"
O = f"{R}/F8_julgamento/analise_fichas_reais_20261111"; import os; os.makedirs(O, exist_ok=True)
nt = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower())[:80]
mapa = pd.read_csv(f"{R}/F8_julgamento/pool_mapa_NAO_ENVIAR.csv", keep_default_na=False)
H = {k: pd.read_csv(f"{F}/ficha_{k}.csv", keep_default_na=False) for k in "WUV"}
rel = {}
for k, h in H.items():
    m = h.merge(mapa[["doc_id", "titulo", "dominio"]], on="doc_id", how="left", suffixes=("", "_mapa"))
    rel[f"{k}_ids_fora_mapa"] = int(m.titulo_mapa.isna().sum())
    rel[f"{k}_titulos_diferentes"] = int((m.titulo.map(nt) != m.titulo_mapa.map(nt)).sum())
    rel[f"{k}_ids_duplicados"] = int(h.doc_id.duplicated().sum())
    rel[f"{k}_notas_invalidas"] = int((~h.nota.astype(str).isin(["0", "1", "2"])).sum())
D = mapa[["doc_id", "dominio", "chave", "titulo", "listas"]].copy()
for k, h in H.items(): D = D.merge(h[["doc_id", "nota"]].rename(columns={"nota": k}), on="doc_id")
for k in "WUV": D[k] = D[k].astype(int)
D["jid"] = [f"{d[:2]}_{hashlib.md5(c.encode()).hexdigest()[:12]}" for d, c in zip(D.dominio, D.chave)]
L = pd.read_csv(f"{R}/F7_painel_llm/analise/J_notas_3llm.csv", keep_default_na=False)
D = D.merge(L[["jid", "haiku", "gpt", "gemini", "consenso"]], on="jid", how="left")
rel["docs"] = len(D); rel["docs_sem_nota_llm"] = int(D.consenso.isna().sum())
for c in ["haiku", "gpt", "gemini", "consenso"]: D[c] = pd.to_numeric(D[c]).round().astype(int)
D["H_med"] = D[["W", "U", "V"]].median(axis=1).astype(int)
D["tn"] = D.titulo.map(nt); dup = []
for (dom, tn), g in D.groupby(["dominio", "tn"]):
    if len(g) > 1: dup.append({"tipo": "mesmo dominio", "dominio": dom, "doc_ids": ";".join(g.doc_id), **{k: ";".join(map(str, g[k])) for k in "WUV"}})
for tn, g in D.groupby("tn"):
    if g.dominio.nunique() > 1: dup.append({"tipo": "dominios diferentes", "dominio": ";".join(g.dominio), "doc_ids": ";".join(g.doc_id), **{k: ";".join(map(str, g[k])) for k in "WUV"}})
pd.DataFrame(dup).to_csv(f"{O}/duplicados.csv", index=False)
def alpha_ord(M):
    cats = [0, 1, 2]; o = np.zeros((3, 3))
    for row in M:
        v = [x for x in row if x is not None and not (isinstance(x, float) and np.isnan(x))]; m = len(v)
        if m < 2: continue
        for a, b in itertools.permutations(range(m), 2): o[v[a], v[b]] += 1 / (m - 1)
    n_c = o.sum(1); n = n_c.sum(); d2 = np.zeros((3, 3))
    for c in cats:
        for k in cats:
            lo, hi = min(c, k), max(c, k); d2[c, k] = (n_c[lo:hi + 1].sum() - (n_c[c] + n_c[k]) / 2) ** 2
    De = sum(n_c[c] * n_c[k] * d2[c, k] for c in cats for k in cats)
    return 1 - (n - 1) * (o * d2).sum() / De if De > 0 else np.nan
kw = lambda a, b: cohen_kappa_score(a, b, weights="quadratic")
linhas = []
for dom, g in [("todos", D)] + list(D.groupby("dominio")):
    r = {"dominio": dom, "n": len(g), "alpha_humanos": alpha_ord(g[["W", "U", "V"]].values), "alpha_LLM": alpha_ord(g[["haiku", "gpt", "gemini"]].values),
         "alpha_6": alpha_ord(g[["W", "U", "V", "haiku", "gpt", "gemini"]].values),
         "kw_Hmed_LLMcons": kw(g.H_med, g.consenso), "exata_Hmed_LLMcons": (g.H_med == g.consenso).mean()}
    for a, b in itertools.combinations("WUV", 2): r[f"kw_{a}{b}"] = kw(g[a], g[b]); r[f"exata_{a}{b}"] = (g[a] == g[b]).mean()
    for k in "WUV":
        outros = [x for x in "WUV" if x != k]
        r[f"kwLOO_{k}"] = np.mean([kw(g[k], g[x]) for x in outros]); r[f"kw_{k}_LLMcons"] = kw(g[k], g.consenso)
        r[f"alpha_sem_{k}"] = alpha_ord(g[outros].values)
    linhas.append(r)
C = pd.DataFrame(linhas); C.round(3).to_csv(f"{O}/concordancia.csv", index=False)
excl = [k for k in "WUV" if C.loc[C.dominio == "todos", f"kwLOO_{k}"].iloc[0] < 0.20]
P = []
for _, x in D.iterrows():
    for l in x.listas.split(";"): P.append({"dominio": x.dominio, "lista": l.strip(), "H_med": x.H_med, "LLM": x.consenso,
                                            "H_med_sem_excl": int(np.median([x[k] for k in "WUV" if k not in excl])) if excl else x.H_med})
P = pd.DataFrame(P); Q = P.groupby(["dominio", "lista"]).agg(n=("LLM", "size"), P10_humanos=("H_med", lambda s: (s == 2).mean()),
    P10_humanos_sem_excl=("H_med_sem_excl", lambda s: (s == 2).mean()), P10_LLM=("LLM", lambda s: (s == 2).mean())).reset_index()
Q["estrategia"] = Q.lista.str.extract(r"_([ABC])(?:_|$)"); Q.round(3).to_csv(f"{O}/P10_por_lista.csv", index=False)
S = Q.groupby(["dominio", "estrategia"])[["P10_humanos", "P10_humanos_sem_excl", "P10_LLM"]].mean().reset_index(); S.round(3).to_csv(f"{O}/P10_por_estrategia.csv", index=False)
cor = []
for dom, g in Q.groupby("dominio"):
    cor.append({"dominio": dom, "tau_listas": kendalltau(g.P10_humanos, g.P10_LLM)[0], "rho_listas": spearmanr(g.P10_humanos, g.P10_LLM)[0],
                "ordem_ABC_humanos": "".join(S[S.dominio == dom].sort_values("P10_humanos", ascending=False).estrategia),
                "ordem_ABC_LLM": "".join(S[S.dominio == dom].sort_values("P10_LLM", ascending=False).estrategia)})
pd.DataFrame(cor).round(3).to_csv(f"{O}/ordenacao_humanos_vs_LLM.csv", index=False)
D.drop(columns=["tn"]).to_csv(f"{O}/notas_humanos_LLM.csv", index=False)
rel["excluidos_criterio_kwLOO<0.20"] = excl
json.dump(rel, open(f"{O}/conferencia.json", "w"), indent=1, ensure_ascii=False)
pd.set_option("display.width", 250)
print(json.dumps(rel, ensure_ascii=False)); print(pd.DataFrame(dup).to_string()); print(C.round(3).T.to_string()); print(S.round(3).to_string()); print(pd.DataFrame(cor).round(3).to_string())
