#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F13e_verificacao_filtro_local.py

File type:
    Script

Purpose:
    A posteriori verification of the Boolean filter on the retrieved records (not applied during collection).

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
    - See docs/file_level_documentation.md (entry F13e_verificacao_filtro_local.py).

Outputs:
    - See docs/file_level_documentation.md (entry F13e_verificacao_filtro_local.py).

Dependencies:
    - gensim
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F13e_verificacao_filtro_local.py

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

import re, json, pandas as pd
from gensim.parsing.porter import PorterStemmer
B = BIBLIO_BASE + ""; R = f"{B}/resultados/adequacao_20261110"
CFG = json.load(open(f"{B}/codigo/adequacao_20261110/consultas_v2.json")); P = PorterStemmer()
can = pd.read_csv(f"{R}/F2_corpus/corpus_canonico.csv", keep_default_na=False, low_memory=False).drop_duplicates(["dominio", "openalex_id"])
tok = lambda t: re.findall(r"[a-z0-9]+", t.lower())
def grupos(q):
    out = []
    for g in re.split(r"\)\s+AND\s+\(|\s+AND\s+(?![^(]*\))", q.strip()):
        termos = [t.strip().strip('"') for t in re.split(r"\s+OR\s+", g.strip().strip("()"))]
        lit = re.compile("|".join(r"\b" + re.escape(t.lower()).replace(r"\ ", r"[\s-]+") for t in termos))
        stm = [" " + " ".join(P.stem(w) for w in tok(t)) + " " for t in termos]
        out.append((lit, stm))
    return out
rows = []
for d, ests in CFG["consultas"].items():
    for k, q in ests.items():
        e = k[-1]; G = grupos(q); s = can[(can.dominio == d) & (can[f"em_{e}"].astype(str) == "1")]
        txt = (s.title + " " + s.abstract).str.lower(); st = txt.map(lambda t: " " + " ".join(P.stem(w) for w in tok(t)) + " ")
        lit = txt.map(lambda t: all(g[0].search(t) for g in G)); stem = st.map(lambda t: all(any(x in t for x in g[1]) for g in G))
        cr = (s.resumo_ok.astype(str) == "True").to_numpy()
        rows.append({"dominio": d, "estrategia": e, "n": len(s), "n_com_resumo": int(cr.sum()), "literal_%": round(100 * lit[cr].mean(), 1),
                     "radicais_%": round(100 * stem[cr].mean(), 1), "radicais_todos_%": round(100 * stem.mean(), 1)})
O = pd.DataFrame(rows); O.to_csv(f"{R}/F13_complementares/verificacao_filtro_local.csv", index=False); print(O.to_string(index=False))
