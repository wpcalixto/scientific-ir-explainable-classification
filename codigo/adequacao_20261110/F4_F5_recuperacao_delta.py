#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F4_F5_recuperacao_delta.py

File type:
    Script

Purpose:
    Judgement-independent retrieval analyses and the delta ratio by platform, with purity and reintegration.

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
    - See docs/file_level_documentation.md (entry F4_F5_recuperacao_delta.py).

Outputs:
    - See docs/file_level_documentation.md (entry F4_F5_recuperacao_delta.py).

Dependencies:
    - numpy
    - pandas
    - scipy
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F4_F5_recuperacao_delta.py

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

import os, re, json, math, glob
import numpy as np, pandas as pd
from collections import Counter
from scipy.spatial.distance import jensenshannon
from sklearn.feature_extraction.text import CountVectorizer
BASE = BIBLIO_BASE + ""
COL = f"{BASE}/dados/coleta_v2_20261110"; EXT = f"{COL}/externas"
OUT = f"{BASE}/resultados/adequacao_20261110/F4_F5"; os.makedirs(OUT, exist_ok=True)
DOMS = ["microarranjos", "radiomica", "metamateriais"]; ESTS = ["A", "B", "C"]
CFG = json.load(open(f"{BASE}/codigo/adequacao_20261110/consultas_v2.json"))
HST = {d: re.compile(r"\b(" + v + r")", re.I) for d, v in CFG["hst"].items()}
NUC = {"microarranjos": r"\b(microarray|gene expression|transcriptom|expression profil|rna-seq|gene signature|omics|genomic)",
       "radiomica": r"\b(radiomic|computed tomography|\bct\b|magnetic resonance|mri|pet\b|positron|ultrasound|mammograph|radiolog|medical imag)",
       "metamateriais": r"\b(metamaterial|metasurface|frequency selective surface|split-ring|photonic crystal|subwavelength|unit cell)"}
can = pd.read_csv(f"{BASE}/resultados/adequacao_20261110/F2_corpus/corpus_canonico.csv", dtype=str, keep_default_na=False)
can["year"] = pd.to_numeric(can["year"], errors="coerce"); can["cit"] = pd.to_numeric(can["cited_by_count"], errors="coerce").fillna(0)
can["txt"] = (can["title"] + " " + can["abstract"]).str.lower()
top = {}
for f in glob.glob(f"{COL}/*_busca_[ABC].csv"):
    for r in pd.read_csv(f, dtype=str, keep_default_na=False, usecols=["openalex_id", "topics"]).itertuples():
        top.setdefault(r.openalex_id, r.topics.split(";")[0].strip())
can["topico"] = can["openalex_id"].map(top).fillna("")
sub = lambda d, e: can[(can["dominio"] == d) & (can[f"em_{e}"] == "1")]

sco = json.load(open(f"{EXT}/contagens_scopus.json"))["contagens"]; ou = json.load(open(f"{EXT}/contagens_externas.json"))["contagens"]
esp = json.load(open(f"{COL}/resumo_coleta_v2.json"))["estrategias"]
dl = []
for d in DOMS:
    n = {"OpenAlex": {e: esp[f"{d}/busca_{e}"]["esperado"] for e in ESTS},
         "Scopus": {e: sco[f"{d}_busca_{e}"]["scopus_total"] for e in ESTS},
         "WoS": {e: ou[f"{d}_busca_{e}"]["wos_total"] for e in ESTS},
         "SemanticScholar": {e: ou[f"{d}_busca_{e}"]["s2_bulk_total"] for e in ESTS}}
    A, B, C = (set(sub(d, e)["openalex_id"]) for e in ESTS)
    for b, v in n.items():
        dl.append({"dominio": d, "base": b, "A": v["A"], "B": v["B"], "C": v["C"], "delta_A_B": round(v["A"] / v["B"], 3),
                   "delta_A_C": round(v["A"] / v["C"], 3),
                   **({"A_contido_em_B_%": round(100 * len(A & B) / len(A), 1), "A_contido_em_C_%": round(100 * len(A & C) / len(A), 1),
                       "A_exclusivo_%": round(100 * len(A - B - C) / len(A), 1)} if b == "OpenAlex" else {})})
dt = pd.DataFrame(dl); dt.to_csv(f"{OUT}/delta_por_base.csv", index=False)
cv = dt.groupby("dominio")["delta_A_B"].agg(lambda s: round(s.std() / s.mean(), 3)).rename("cv_delta_entre_bases")
cv.reset_index().to_csv(f"{OUT}/delta_variacao_entre_bases.csv", index=False)

ri, nv, pu = [], [], []
for d in DOMS:
    g = can[can["dominio"] == d]; S = {e: set(sub(d, e)["openalex_id"]) for e in ESTS}; G = set(g["openalex_id"])
    hst = g.set_index("openalex_id")["txt"].map(lambda t: bool(HST[d].search(t)))
    nuc = g.set_index("openalex_id")["txt"].map(lambda t: bool(re.search(NUC[d], t)))
    for e in ESTS:
        ids = S[e]; out = set().union(*(S[x] for x in ESTS if x != e))
        ri.append({"dominio": d, "estrategia": e, "n": len(ids), "com_HST_%": round(100 * hst[list(ids)].mean(), 1),
                   "sem_HST_fora_de_A": len([i for i in ids - S["A"] if not hst[i]])})
        nv.append({"dominio": d, "estrategia": e, "n": len(ids), "exclusivos": len(ids - out), "novidade_%": round(100 * len(ids - out) / len(ids), 1),
                   "redundancia_%": round(100 * len(ids & out) / len(ids), 1), "revocacao_relativa_G_%": round(100 * len(ids) / len(G), 1)})
        pu.append({"dominio": d, "estrategia": e, "pureza_termos_nucleares_%": round(100 * nuc[list(ids)].mean(), 1)})
    fora = g[~g["openalex_id"].map(nuc)]["topico"].value_counts().head(10)
    for t, k in fora.items(): pu.append({"dominio": d, "estrategia": "topicos_sem_termo_nuclear", "topico": t, "n": int(k)})
pd.DataFrame(ri).to_csv(f"{OUT}/reintegracao_hst.csv", index=False)
pd.DataFrame(nv).to_csv(f"{OUT}/novidade_redundancia.csv", index=False)
pd.DataFrame(pu).to_csv(f"{OUT}/pureza_dominio.csv", index=False)

dv = []
for d in DOMS:
    dist = {e: Counter(sub(d, e)["topico"]) for e in ESTS}
    vocab = sorted(set().union(*dist.values()))
    vec = {e: np.array([dist[e][t] for t in vocab], float) for e in ESTS}
    for e in ESTS:
        p = vec[e] / vec[e].sum(); H = -np.sum(p[p > 0] * np.log2(p[p > 0]))
        dv.append({"dominio": d, "estrategia": e, "n_topicos": int((vec[e] > 0).sum()), "entropia_bits": round(H, 3),
                   "entropia_norm": round(H / math.log2(max(2, (vec[e] > 0).sum())), 3), "topico_1": dist[e].most_common(1)[0][0]})
    for a, b in [("A", "B"), ("A", "C"), ("B", "C")]:
        dv.append({"dominio": d, "estrategia": f"JS({a},{b})", "js_div_bits2": round(jensenshannon(vec[a], vec[b], base=2) ** 2, 4)})
pd.DataFrame(dv).to_csv(f"{OUT}/diversidade_tematica.csv", index=False)

def termos(q):
    q = re.sub(r"\b(AND|OR|NOT)\b", " ", q)
    return [t.lower() for t in re.findall(r'"([^"]+)"|([A-Za-z][A-Za-z\-]+)', q) for t in t if t]
def bm25(textos, consulta, k1=1.2, b=0.75):
    frases = termos(consulta)
    cvz = CountVectorizer(vocabulary=sorted(set(frases)), ngram_range=(1, 4), token_pattern=r"(?u)\b[\w\-]+\b", lowercase=True)
    X = cvz.transform(textos).tocsc().astype(float)
    dl_ = np.array([len(t.split()) for t in textos], float); avg = dl_.mean(); N = len(textos)
    dfreq = np.asarray((X > 0).sum(0)).ravel(); idf = np.log(1 + (N - dfreq + 0.5) / (dfreq + 0.5))
    X = X.tocoo(); s = np.zeros(N)
    np.add.at(s, X.row, idf[X.col] * X.data * (k1 + 1) / (X.data + k1 * (1 - b + b * dl_[X.row] / avg)))
    return s
listas, rk = [], []
for d in DOMS:
    for e in ESTS:
        g = sub(d, e).copy(); g["idade"] = (2026 - g["year"]).clip(lower=1)
        g["s_cit"] = g["cit"]; g["s_citano"] = g["cit"] / g["idade"]; g["s_bm25"] = bm25(g["txt"].tolist(), CFG["consultas"][d][f"busca_{e}"])
        tops = {}
        for r in ["cit", "citano", "bm25"]:
            t = g.sort_values([f"s_{r}", "openalex_id"], ascending=[False, True]).head(100)
            tops[r] = list(t["openalex_id"])
            rk.append({"dominio": d, "estrategia": e, "ranking": r, "ano_mediano_top100": float(t["year"].median()),
                       "ano_mediano_estrategia": float(g["year"].median()), "cit_mediana_top100": float(t["cit"].median()),
                       "com_HST_top100_%": round(100 * t["txt"].map(lambda x: bool(HST[d].search(x))).mean(), 1)})
            for i, w in enumerate(tops[r], 1): listas.append({"dominio": d, "lista": f"OAL_{e}_{r}", "rank": i, "openalex_id": w, "doi": "", "title": ""})
        for a, b in [("cit", "citano"), ("cit", "bm25"), ("citano", "bm25")]:
            rk.append({"dominio": d, "estrategia": e, "ranking": f"Jaccard_top100({a},{b})", "valor": round(len(set(tops[a]) & set(tops[b])) / len(set(tops[a]) | set(tops[b])), 3)})
pd.DataFrame(rk).to_csv(f"{OUT}/rankings_top100.csv", index=False)
for d in DOMS:
    for e in ESTS:
        for plat in ["scopus_top100", "wos_top100", "s2_top100", "elicit_semantico", "elicit_keyword"]:
            f = f"{EXT}/{plat}_{d}_busca_{e}.csv"
            if not os.path.exists(f): continue
            x = pd.read_csv(f, dtype=str, keep_default_na=False).head(100)
            for i, r in enumerate(x.itertuples(), 1):
                listas.append({"dominio": d, "lista": f"{plat}_{e}", "rank": i, "openalex_id": "", "doi": (r.doi or "").lower(), "title": r.title})
L = pd.DataFrame(listas)
m = can.drop_duplicates(["dominio", "openalex_id"]).set_index(["dominio", "openalex_id"])
L["doi"] = [r.doi or (m.loc[(r.dominio, r.openalex_id), "doi_n"] if r.openalex_id else "") for r in L.itertuples()]
L["title"] = [r.title or (m.loc[(r.dominio, r.openalex_id), "title"] if r.openalex_id else "") for r in L.itertuples()]
L["chave"] = [r.doi if r.doi else "t:" + re.sub(r"[^a-z0-9]", "", r.title.lower())[:120] for r in L.itertuples()]
L.to_csv(f"{OUT}/listas_ranqueadas.csv", index=False)
pool = []
for d in DOMS:
    for prof in [10, 20, 100]:
        for conj, filtro in [("todas", lambda s: True), ("OAL_cit+bm25+externas", lambda s: not s.endswith("_citano"))]:
            x = L[(L["dominio"] == d) & (L["rank"] <= prof) & L["lista"].map(filtro)]
            pool.append({"dominio": d, "profundidade": prof, "conjunto_listas": conj, "n_listas": x["lista"].nunique(), "pool_unico": x["chave"].nunique()})
pd.DataFrame(pool).to_csv(f"{OUT}/tamanho_pool.csv", index=False)
print("F4/F5 FIM")
