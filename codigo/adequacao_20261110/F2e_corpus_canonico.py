#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F2e_corpus_canonico.py

File type:
    Script

Purpose:
    Builds the canonical corpus (deduplication, matching with Scopus by DOI or title, overlap and growth).

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
    - See docs/file_level_documentation.md (entry F2e_corpus_canonico.py).

Outputs:
    - See docs/file_level_documentation.md (entry F2e_corpus_canonico.py).

Dependencies:
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F2e_corpus_canonico.py

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

import os, re, json, glob, unicodedata
import pandas as pd
BASE = BIBLIO_BASE + ""
COL = f"{BASE}/dados/coleta_v2_20261110"; EXT = f"{COL}/externas"
OUT = f"{BASE}/resultados/adequacao_20261110/F2_corpus"; os.makedirs(OUT, exist_ok=True)
DOMS = ["microarranjos", "radiomica", "metamateriais"]; ESTS = ["A", "B", "C"]
def ndoi(d):
    d = str(d or "").strip().lower()
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d) if d and d != "nan" else ""
def ntit(t):
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", t)[:200]
def ntok(s):
    return len(re.findall(r"\w+", str(s))) if isinstance(s, str) else 0

partes = []
for d in DOMS:
    for e in ESTS:
        x = pd.read_csv(f"{COL}/{d}_busca_{e}.csv", dtype=str, keep_default_na=False)
        x["est"] = e; partes.append(x)
bruto = pd.concat(partes, ignore_index=True)
bruto["doi_n"] = bruto["doi"].map(ndoi); bruto["tit_n"] = bruto["title"].map(ntit)
flags = (bruto.assign(v=1).pivot_table(index=["dominio", "openalex_id"], columns="est", values="v", aggfunc="max", fill_value=0)
         .rename(columns=lambda c: f"em_{c}").reset_index())
bruto["tem_resumo"] = bruto["abstract"].str.len() > 0
prim = (bruto.sort_values("tem_resumo", ascending=False).drop_duplicates(["dominio", "openalex_id"])
        .drop(columns=["est", "estrategia"]))
can = flags.merge(prim, on=["dominio", "openalex_id"])
can["n_tokens_resumo"] = can["abstract"].map(ntok)
can["resumo_ok"] = can["n_tokens_resumo"] >= 10
can["year"] = pd.to_numeric(can["year"], errors="coerce").astype("Int64")
can["cited_by_count"] = pd.to_numeric(can["cited_by_count"], errors="coerce").fillna(0).astype(int)
rot = pd.read_csv(f"{BASE}/resultados/adequacao_20261110/F2_rotulacao_v2/rotulos_v2_final.csv", dtype=str, keep_default_na=False)
can = can.merge(rot[["dominio", "openalex_id", "label"]], on=["dominio", "openalex_id"], how="left")
ndom = can.groupby("openalex_id")["dominio"].nunique()
can["n_dominios"] = can["openalex_id"].map(ndom)
cols = ["dominio", "openalex_id", "doi_n", "title", "year", "type", "journal", "cited_by_count", "em_A", "em_B", "em_C",
        "abstract_fonte", "n_tokens_resumo", "resumo_ok", "label", "n_dominios", "tit_n", "abstract", "primary_topic_field", "keywords"]
can[cols].to_csv(f"{OUT}/corpus_canonico.csv", index=False)

esp = json.load(open(f"{COL}/resumo_coleta_v2.json"))["estrategias"]
scop = json.load(open(f"{EXT}/contagens_scopus.json"))["contagens"]
outr = json.load(open(f"{EXT}/contagens_externas.json"))["contagens"]
eli = json.load(open(f"{EXT}/contagens_elicit.json"))["resumo"]
fl = []
for d in DOMS:
    for e in ESTS + ["União"]:
        s = can[can["dominio"] == d] if e == "União" else can[(can["dominio"] == d) & (can[f"em_{e}"] == 1)]
        r = {"dominio": d, "estrategia": e,
             "oal_total_api": esp.get(f"{d}/busca_{e}", {}).get("esperado", "") if e != "União" else "",
             "unicos_id": len(s), "unicos_doi": s.loc[s["doi_n"] != "", "doi_n"].nunique(),
             "sem_doi": int((s["doi_n"] == "").sum()), "com_resumo": int((s["abstract"] != "").sum()),
             "resumo_ge10_tokens": int(s["resumo_ok"].sum()),
             "rotulados": int(s["label"].isin(["Applied", "Methodological", "General"]).sum()),
             "Applied": int((s["label"] == "Applied").sum()), "Methodological": int((s["label"] == "Methodological").sum()),
             "General": int((s["label"] == "General").sum()), "em_outro_dominio": int((s["n_dominios"] > 1).sum())}
        if e != "União":
            t = f"{d}_busca_{e}"
            r.update({"scopus_total": scop[t]["scopus_total"], "wos_total": outr[t]["wos_total"],
                      "s2_total": outr[t]["s2_bulk_total"],
                      "elicit_semantico": eli[f"semantico|{t}"]["ate_2025"], "elicit_keyword": eli[f"keyword|{t}"]["ate_2025"]})
        fl.append(r)
pd.DataFrame(fl).to_csv(f"{OUT}/fluxo_corpus.csv", index=False)

sob = []
for d in DOMS:
    s = can[can["dominio"] == d]
    A, B, C = (set(s.loc[s[f"em_{e}"] == 1, "openalex_id"]) for e in ESTS)
    sob.append({"dominio": d, "A": len(A), "B": len(B), "C": len(C), "A∩B": len(A & B), "A∩C": len(A & C), "B∩C": len(B & C),
                "A∩B∩C": len(A & B & C), "A_so": len(A - B - C), "B_so": len(B - A - C), "C_so": len(C - A - B),
                "A⊂B∪C_%": round(100 * len(A & (B | C)) / max(1, len(A)), 1), "uniao": len(A | B | C)})
pd.DataFrame(sob).to_csv(f"{OUT}/sobreposicao_estrategias.csv", index=False)
cross = can[can["n_dominios"] > 1].groupby("openalex_id")["dominio"].apply(lambda v: "+".join(sorted(v))).value_counts()
cross.rename_axis("dominios").reset_index(name="n").to_csv(f"{OUT}/documentos_multidominio.csv", index=False)

ser = []
for d in DOMS:
    for e in ESTS + ["União"]:
        s = can[can["dominio"] == d] if e == "União" else can[(can["dominio"] == d) & (can[f"em_{e}"] == 1)]
        for y, n in s["year"].value_counts().sort_index().items():
            ser.append({"dominio": d, "estrategia": e, "ano": int(y), "n": int(n)})
ser = pd.DataFrame(ser); ser.to_csv(f"{OUT}/crescimento_unicos.csv", index=False)
cres = []
for (d, e), g in ser.groupby(["dominio", "estrategia"]):
    g = g.set_index("ano")["n"]
    a = lambda lo, hi: int(g[(g.index >= lo) & (g.index <= hi)].sum())
    p1, p2 = a(2016, 2020), a(2021, 2025)
    cres.append({"dominio": d, "estrategia": e, "ano_min": int(g.index.min()), "ano_mediano": int(pd.Series(g.index.repeat(g.values)).median()),
                 "n_2016_2020": p1, "n_2021_2025": p2, "delta_pct_5a": round(100 * (p2 - p1) / p1, 1) if p1 else None})
pd.DataFrame(cres).to_csv(f"{OUT}/crescimento_resumo.csv", index=False)

cob = []
for d in DOMS:
    for e in ESTS:
        o = can[(can["dominio"] == d) & (can[f"em_{e}"] == 1)]
        f = f"{EXT}/scopus_todos_{d}_busca_{e}.csv"
        sc = pd.read_csv(f, dtype=str, keep_default_na=False) if os.path.exists(f) else pd.DataFrame(columns=["doi", "title"])
        sc["doi_n"] = sc["doi"].map(ndoi); sc["tit_n"] = sc["title"].map(ntit)
        od, ot = set(o["doi_n"]) - {""}, set(o["tit_n"]) - {""}
        sc["em_oal"] = sc["doi_n"].isin(od) | sc["tit_n"].isin(ot)
        sd, st = set(sc["doi_n"]) - {""}, set(sc["tit_n"]) - {""}
        o_em_sc = o["doi_n"].isin(sd) | o["tit_n"].isin(st)
        cob.append({"dominio": d, "estrategia": e, "oal": len(o), "scopus": len(sc), "intersecao_scopus_em_oal": int(sc["em_oal"].sum()),
                    "so_scopus": int((~sc["em_oal"]).sum()), "so_oal": int((~o_em_sc).sum()),
                    "pct_scopus_coberto_por_oal": round(100 * sc["em_oal"].mean(), 1) if len(sc) else None,
                    "pct_oal_coberto_por_scopus": round(100 * o_em_sc.mean(), 1) if len(o) else None})
pd.DataFrame(cob).to_csv(f"{OUT}/cobertura_oal_scopus.csv", index=False)

ck = []
for d in DOMS:
    pool = can[can["dominio"] == d]; pd_, pt = set(pool["doi_n"]) - {""}, set(pool["tit_n"]) - {""}
    for e in ESTS:
        for plat, pat in [("scopus_top100", "scopus_top100"), ("wos_top100", "wos_top100"), ("s2_top100", "s2_top100"),
                          ("elicit_semantico", "elicit_semantico"), ("elicit_keyword", "elicit_keyword")]:
            f = f"{EXT}/{pat}_{d}_busca_{e}.csv"
            if not os.path.exists(f): continue
            x = pd.read_csv(f, dtype=str, keep_default_na=False)
            em = x["doi"].map(ndoi).isin(pd_) | x["title"].map(ntit).isin(pt)
            ck.append({"dominio": d, "estrategia": e, "plataforma": plat, "n": len(x), "no_pool_oal": int(em.sum()),
                       "pct_no_pool": round(100 * em.mean(), 1) if len(x) else None})
pd.DataFrame(ck).to_csv(f"{OUT}/cobertura_externas_no_pool.csv", index=False)
print("F2 OK", len(can), "registos domínio×ID;", can["openalex_id"].nunique(), "IDs únicos")
