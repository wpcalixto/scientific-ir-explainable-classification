#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F8f_analise_13_fichas.py

File type:
    Script

Purpose:
    Analyses the 13 human sheets (K-W): agreement, P@10 by strategy and comparison with the LLM judges.

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
    - See docs/file_level_documentation.md (entry F8f_analise_13_fichas.py).

Outputs:
    - See docs/file_level_documentation.md (entry F8f_analise_13_fichas.py).

Dependencies:
    - numpy
    - pandas
    - scipy
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F8f_analise_13_fichas.py

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

import re, hashlib, json, itertools, os, numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score
from scipy.stats import kendalltau, spearmanr
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; F = f"{R}/F8_julgamento/fichas_reais_20261111"
O = f"{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas"; os.makedirs(O, exist_ok=True)
AV = list("WUVTSRQPONMLK")
nt = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower())[:80]
mapa = pd.read_csv(f"{R}/F8_julgamento/pool_mapa_NAO_ENVIAR.csv", keep_default_na=False)
D = mapa[["doc_id", "dominio", "chave", "titulo", "listas"]].copy(); rel = {}
for k in AV:
    h = pd.read_csv(f"{F}/ficha_{k}.csv", keep_default_na=False)
    m = h.merge(mapa[["doc_id", "titulo"]], on="doc_id", how="left", suffixes=("", "_mapa"))
    rel[k] = {"n": len(h), "fora_mapa": int(m.titulo_mapa.isna().sum()), "titulos_diferentes": int((m.titulo.map(nt) != m.titulo_mapa.map(nt)).sum()),
              "duplicados": int(h.doc_id.duplicated().sum()), "notas_invalidas": int((~h.nota.astype(str).isin(["0", "1", "2"])).sum())}
    D = D.merge(h[["doc_id", "nota"]].rename(columns={"nota": k}), on="doc_id", how="left")
    D[k] = pd.to_numeric(D[k])
D["jid"] = [f"{d[:2]}_{hashlib.md5(c.encode()).hexdigest()[:12]}" for d, c in zip(D.dominio, D.chave)]
L = pd.read_csv(f"{R}/F7_painel_llm/analise/J_notas_3llm.csv", keep_default_na=False)
D = D.merge(L[["jid", "haiku", "gpt", "gemini", "consenso"]], on="jid", how="left")
for c in ["haiku", "gpt", "gemini", "consenso"]: D[c] = pd.to_numeric(D[c]).round().astype(int)
D["n_aval"] = D[AV].notna().sum(1)
def med(cols): return D[cols].median(axis=1, skipna=True).apply(np.floor).astype(int)
D["H_med"] = med(AV); D["H_med_semWU"] = med([k for k in AV if k not in "WU"]); D["H_med_WUV"] = med(list("WUV"))
def alpha_ord(M):
    o = np.zeros((3, 3))
    for row in M:
        v = [int(x) for x in row if not pd.isna(x)]; m = len(v)
        if m < 2: continue
        for a, b in itertools.permutations(range(m), 2): o[v[a], v[b]] += 1 / (m - 1)
    n_c = o.sum(1); n = n_c.sum(); d2 = np.zeros((3, 3))
    for c in range(3):
        for k in range(3):
            lo, hi = min(c, k), max(c, k); d2[c, k] = (n_c[lo:hi + 1].sum() - (n_c[c] + n_c[k]) / 2) ** 2
    De = sum(n_c[c] * n_c[k] * d2[c, k] for c in range(3) for k in range(3))
    return 1 - (n - 1) * (o * d2).sum() / De if De > 0 else np.nan
kw = lambda a, b: cohen_kappa_score(a, b, weights="quadratic")
def kwpar(g, a, b):
    s = g[[a, b]].dropna(); return (kw(s[a].astype(int), s[b].astype(int)), len(s)) if len(s) >= 20 else (np.nan, len(s))
linhas, porav = [], []
for dom, g in [("todos", D)] + list(D.groupby("dominio")):
    pres = [k for k in AV if g[k].notna().any()]
    r = {"dominio": dom, "n_docs": len(g), "n_avaliadores": len(pres), "alpha_humanos": alpha_ord(g[pres].values),
         "alpha_humanos_semWU": alpha_ord(g[[k for k in pres if k not in "WU"]].values), "alpha_LLM": alpha_ord(g[["haiku", "gpt", "gemini"]].values)}
    for ref in ["H_med", "H_med_semWU", "H_med_WUV"]:
        r[f"kw_{ref}_LLMcons"] = kw(g[ref], g.consenso); r[f"exata_{ref}_LLMcons"] = (g[ref] == g.consenso).mean()
    pares = [kwpar(g, a, b)[0] for a, b in itertools.combinations(pres, 2)]
    r["kw_par_mediana"] = np.nanmedian(pares); r["kw_par_min"] = np.nanmin(pares); r["kw_par_max"] = np.nanmax(pares)
    linhas.append(r)
    for k in pres:
        s = g[[k, "consenso"]].dropna()
        porav.append({"dominio": dom, "avaliador": k, "n": len(s), "kwLOO_media": np.nanmean([kwpar(g, k, x)[0] for x in pres if x != k]),
                      "kw_LLMcons": kw(s[k].astype(int), s.consenso), "exata_LLMcons": (s[k] == s.consenso).mean(),
                      "prop_nota2": (s[k] == 2).mean()})
C = pd.DataFrame(linhas); C.round(3).to_csv(f"{O}/concordancia.csv", index=False)
PA = pd.DataFrame(porav); PA.round(3).to_csv(f"{O}/por_avaliador.csv", index=False)
excl = PA[(PA.dominio == "todos") & (PA.kwLOO_media < 0.20)].avaliador.tolist(); rel["excluidos_kwLOO<0.20"] = excl
pd.DataFrame([{"par": a + b, "kw": kwpar(D, a, b)[0], "n": kwpar(D, a, b)[1]} for a, b in itertools.combinations(AV, 2)]).round(3).to_csv(f"{O}/kw_pares.csv", index=False)
P = []
for _, x in D.iterrows():
    for l in x.listas.split(";"): P.append({"dominio": x.dominio, "lista": l.strip(), "H": x.H_med, "H_semWU": x.H_med_semWU, "H_WUV": x.H_med_WUV, "LLM": x.consenso})
P = pd.DataFrame(P); st = lambda s: (s == 2).mean()
Q = P.groupby(["dominio", "lista"]).agg(n=("LLM", "size"), P10_humanos=("H", st), P10_humanos_semWU=("H_semWU", st), P10_humanos_WUV=("H_WUV", st), P10_LLM=("LLM", st)).reset_index()
Q["estrategia"] = Q.lista.str.extract(r"_([ABC])(?:_|$)"); Q.round(3).to_csv(f"{O}/P10_por_lista.csv", index=False)
cols = ["P10_humanos", "P10_humanos_semWU", "P10_humanos_WUV", "P10_LLM"]
S = Q.groupby(["dominio", "estrategia"])[cols].mean().reset_index(); S.round(3).to_csv(f"{O}/P10_por_estrategia.csv", index=False)
cor = []
for dom, g in Q.groupby("dominio"):
    s = S[S.dominio == dom]
    cor.append({"dominio": dom, "tau_listas": kendalltau(g.P10_humanos, g.P10_LLM)[0], "rho_listas": spearmanr(g.P10_humanos, g.P10_LLM)[0],
                **{f"ordem_{c}": "".join(s.sort_values(c, ascending=False).estrategia) for c in cols}})
pd.DataFrame(cor).round(3).to_csv(f"{O}/ordenacao_humanos_vs_LLM.csv", index=False)
D.to_csv(f"{O}/notas_humanos_LLM.csv", index=False)
json.dump(rel, open(f"{O}/conferencia.json", "w"), indent=1, ensure_ascii=False)
pd.set_option("display.width", 250); print(json.dumps(rel, ensure_ascii=False)); print(C.round(3).T.to_string())
print(PA[PA.dominio == "todos"].round(3).to_string()); print(S.round(3).to_string()); print(pd.DataFrame(cor).round(3).to_string())
