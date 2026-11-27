#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F14g_analise_facetas.py

File type:
    Script

Purpose:
    Analyses the controlled facet experiment (F14d).

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
    - See docs/file_level_documentation.md (entry F14g_analise_facetas.py).

Outputs:
    - See docs/file_level_documentation.md (entry F14g_analise_facetas.py).

Dependencies:
    - gensim
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F14g_analise_facetas.py

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

import os, re, json, gzip, pandas as pd
from gensim.parsing.porter import PorterStemmer
B = BIBLIO_BASE + ""; R = f"{B}/resultados/adequacao_20261110"; D = f"{B}/dados/experimento_facetas_20261112"
O = f"{R}/F14_complementares_01A/facetas"; os.makedirs(O, exist_ok=True); P = PorterStemmer()
Q = json.load(open(f"{D}/consultas.json"))
def ler(d, v):
    out = {}
    with gzip.open(f"{D}/{d}_{v}.jsonl.gz", "rt") as f:
        for l in f:
            w = json.loads(l); inv = w.get("abstract_inverted_index") or {}
            pos = sorted((p, t) for t, ps in inv.items() for p in ps); out[w["id"]] = ((w.get("title") or "") + " " + " ".join(t for _, t in pos)).lower(), bool(inv)
    return out
can = pd.read_csv(f"{R}/F2_corpus/corpus_canonico.csv", keep_default_na=False, low_memory=False).drop_duplicates(["dominio", "openalex_id"])
tok = lambda t: re.findall(r"[a-z0-9]+", t)
def grupos(q):
    out = []
    for g in re.split(r"\)\s+AND\s+\(|\s+AND\s+(?![^(]*\))", q.strip()):
        ts = [t.strip().strip('"') for t in re.split(r"\s+OR\s+", g.strip().strip("()"))]
        out.append((re.compile("|".join(r"\b" + re.escape(t.lower()).replace(r"\ ", r"[\s-]+") for t in ts)), [" " + " ".join(P.stem(w) for w in tok(t.lower())) + " " for t in ts]))
    return out
T, X, Lr = [], [], []
for d, vs in Q.items():
    S = {v: ler(d, v) for v in vs}
    for e in "ABC":
        orig = set(can[(can.dominio == d) & (can[f"em_{e}"].astype(str) == "1")].openalex_id); hoje = set(S[f"{e}_orig"])
        T.append({"dominio": d, "estrategia": e, "n_10nov": len(orig), "n_12nov": len(hoje), "intersecao": len(orig & hoje),
                  "jaccard": round(len(orig & hoje) / len(orig | hoje), 4), "variacao_%": round(100 * (len(hoje) - len(orig)) / len(orig), 2)})
    a, ar, bf, b = (set(S[k]) for k in ["A_ref", "A_faceta_relaxada", "B_faceta_de_A", "B_ref"]); cc = set(S["C_objeto_de_C"]); un = set(S["uniao_HST_ou_amplos"])
    X.append({"dominio": d, "A_ref": len(a), "A_faceta_relaxada": len(ar), "B_faceta_de_A": len(bf), "B_ref": len(b), "C_objeto_de_C": len(cc), "uniao_HST_ou_amplos": len(un),
              "efeito_objeto_|A|/|B_faceta_de_A|": round(len(a) / len(bf), 3), "efeito_faceta_com_HST_|A|/|A_relax|": round(len(a) / len(ar), 3),
              "efeito_faceta_com_amplos_|Bf|/|B|": round(len(bf) / len(b), 3), "efeito_conjunto_delta_hoje": round(len(a) / len(b), 3),
              "|A|/|C_objeto|": round(len(a) / len(cc), 3), "contencao_A_em_B_faceta_de_A": round(len(a & bf) / len(a), 3),
              "contencao_A_em_B_ref": round(len(a & b) / len(a), 3), "A_exclusivo_face_a_B_faceta_de_A": len(a - bf),
              "acrescimo_uniao_sobre_amplos_%": round(100 * (len(un) - len(bf)) / len(bf), 1)})
    for v, docs in S.items():
        G = grupos(Q[d][v]); com = [t for t, r in docs.values() if r]
        lit = sum(all(g[0].search(t) for g in G) for t in com); st = [" " + " ".join(P.stem(w) for w in tok(t)) + " " for t in com]
        stem = sum(all(any(x in s for x in g[1]) for g in G) for s in st)
        Lr.append({"dominio": d, "variante": v, "n": len(docs), "com_resumo": len(com), "literal_%": round(100 * lit / max(len(com), 1), 1), "porter_%": round(100 * stem / max(len(com), 1), 1)})
for nm, df in [("temporal", T), ("desenho_2x2", X), ("literal_vs_radicais", Lr)]:
    pd.DataFrame(df).to_csv(f"{O}/{nm}.csv", index=False); print(pd.DataFrame(df).to_string(index=False))
