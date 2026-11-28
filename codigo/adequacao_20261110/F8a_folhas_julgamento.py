#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F8a_folhas_julgamento.py

File type:
    Script

Purpose:
    Builds the human judgement pool (depth 10) and the first two blind sheets (assessors W and U).

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
    - See docs/file_level_documentation.md (entry F8a_folhas_julgamento.py).

Outputs:
    - See docs/file_level_documentation.md (entry F8a_folhas_julgamento.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F8a_folhas_julgamento.py

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

import os, re, json, time, urllib.request, urllib.parse
import numpy as np, pandas as pd
BASE = BIBLIO_BASE + ""
EXT = f"{BASE}/dados/coleta_v2_20261110/externas"
OUT = f"{BASE}/resultados/adequacao_20261110/F8_julgamento"; os.makedirs(OUT, exist_ok=True)
L = pd.read_csv(f"{BASE}/resultados/adequacao_20261110/F4_F5/listas_ranqueadas.csv", keep_default_na=False)
ok = L["lista"].str.match(r"^(OAL_[ABC]_(cit|bm25)|scopus_top100_[ABC]|wos_top100_[ABC]|elicit_semantico_[ABC])$")
P = L[ok & (L["rank"] <= 10)].copy()
can = pd.read_csv(f"{BASE}/resultados/adequacao_20261110/F2_corpus/corpus_canonico.csv", dtype=str, keep_default_na=False)
tk = lambda t: "t:" + re.sub(r"[^a-z0-9]", "", str(t).lower())[:120]
txt = {}
for r in can.itertuples():
    for k in ([r.doi_n] if r.doi_n else []) + [tk(r.title)]:
        if k not in txt or (not txt[k][1] and r.abstract): txt[k] = (r.title, r.abstract)
for f in [f for f in os.listdir(EXT) if f.startswith(("elicit_semantico", "elicit_keyword", "s2_top100")) and f.endswith(".csv")]:
    for r in pd.read_csv(f"{EXT}/{f}", dtype=str, keep_default_na=False).itertuples():
        for k in ([r.doi.lower()] if r.doi else []) + [tk(r.title)]:
            if k not in txt or (not txt[k][1] and r.abstract): txt[k] = (r.title, r.abstract)
def busca(k, title):
    for kk in [k, tk(title)]:
        if kk in txt and txt[kk][1]: return txt[kk]
    return txt.get(k, (title, ""))
P["titulo"], P["resumo"] = zip(*[busca(r.chave, r.title) for r in P.itertuples()])
falta = sorted({r.chave for r in P.itertuples() if not r.resumo and not r.chave.startswith("t:")})
extra = {}
for i in range(0, len(falta), 40):
    q = urllib.parse.urlencode({"filter": "doi:" + "|".join(falta[i:i+40]), "per-page": 50, "select": "doi,title,abstract_inverted_index"})
    try:
        j = json.loads(urllib.request.urlopen("https://api.openalex.org/works?" + q, timeout=60).read())
        for w in j["results"]:
            inv = w.get("abstract_inverted_index") or {}
            ab = " ".join(t for _, t in sorted((p, t) for t, ps in inv.items() for p in ps))
            extra[(w.get("doi") or "").lower().replace("https://doi.org/", "")] = (w.get("title") or "", ab)
    except Exception as e:
        print("openalex", type(e).__name__)
    time.sleep(1)
P["resumo"] = [r.resumo or extra.get(r.chave, ("", ""))[1] for r in P.itertuples()]
P["titulo"] = [r.titulo or extra.get(r.chave, ("", ""))[0] for r in P.itertuples()]
docs = P.groupby(["dominio", "chave"]).agg(titulo=("titulo", "first"), resumo=("resumo", lambda s: max(s, key=len)),
                                           listas=("lista", lambda s: ";".join(sorted(set(s)))), n_listas=("lista", "nunique")).reset_index()
rng = np.random.default_rng(20261110)
docs["doc_id"] = [f"{d[:2].upper()}{i:04d}" for i, d in zip(rng.permutation(len(docs)), docs["dominio"])]
docs.to_csv(f"{OUT}/pool_mapa_NAO_ENVIAR.csv", index=False)
DN = {"microarranjos": "1_Microarranjos", "radiomica": "2_Radiomica", "metamateriais": "3_Metamateriais"}
for av, seed in [("W", 1), ("U", 2)]:
    with pd.ExcelWriter(f"{OUT}/Folha_julgamento_{av}.xlsx", engine="openpyxl") as xw:
        for d, nome in DN.items():
            x = docs[docs["dominio"] == d].sample(frac=1, random_state=seed)[["doc_id", "titulo", "resumo"]]
            x["relevancia_0_1_2"] = ""; x["comentario"] = ""
            x.to_excel(xw, sheet_name=nome, index=False)
res = docs.groupby("dominio").agg(n=("doc_id", "size"), sem_resumo=("resumo", lambda s: int((s == "").sum())),
                                  em_2plus_listas=("n_listas", lambda s: int((s > 1).sum())))
res.to_csv(f"{OUT}/pool_resumo.csv"); print(res)
