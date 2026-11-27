#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F2a_coleta_openalex_v2.py

File type:
    Script

Purpose:
    Collects the OpenAlex records of strategies A, B and C in the three domains (server-side Boolean search, cursor pagination).

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
    - See docs/file_level_documentation.md (entry F2a_coleta_openalex_v2.py).

Outputs:
    - See docs/file_level_documentation.md (entry F2a_coleta_openalex_v2.py).

Dependencies:
    - requests

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F2a_coleta_openalex_v2.py

Portability notes:
    All paths are resolved relative to the package base directory given by the BIBLIO_BASE environment variable
    (default: the package root, two levels above codigo/adequacao_20261110/). No machine-specific path is required.
    API keys, when needed, are read from ~/.config/bibliogenre/ and ~/.config/bibliometria/ and are not part of the package.

Reproducibility notes:
    Environment pinned in requirements.txt and environment/. Seeds and frozen parameters are written in the code and
    summarized in docs/parameters.md.

Warnings:
    Re-running queries the live APIs and needs API keys; results will differ from the archived collection of 2026-11-10 (use the files in dados/).
"""

import os as _bb_os
BIBLIO_BASE = _bb_os.environ.get("BIBLIO_BASE") or _bb_os.path.abspath(
    _bb_os.path.join(_bb_os.path.dirname(_bb_os.path.abspath(__file__)), "..", ".."))

import json, gzip, csv, os, sys, time, hashlib, urllib.parse, datetime as dt
import requests
BASE = BIBLIO_BASE + ""
CFG = json.load(open(f"{BASE}/codigo/adequacao_20261110/consultas_v2.json"))
OUT = f"{BASE}/dados/coleta_v2_20261110"
KEY = open(os.path.expanduser("~/.config/bibliogenre/openalex")).read().strip()
SELECT = ("id,doi,title,publication_year,publication_date,type,language,primary_location,authorships,"
          "cited_by_count,open_access,concepts,topics,keywords,abstract_inverted_index,is_retracted")
LOG = open(f"{OUT}/coleta_v2.log", "a", encoding="utf-8")
def log(m):
    s = f"{dt.datetime.now().isoformat(timespec='seconds')} {m}"; print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
def get(params, tries=6):
    url = "https://api.openalex.org/works?" + "&".join(f"{k}={urllib.parse.quote(str(v), safe=':,|<*')}" for k, v in params.items())
    for i in range(tries):
        try:
            r = requests.get(url + "&api_key=" + KEY, timeout=120, headers={"User-Agent": "bibliometria-coleta/2.0"})
            if r.status_code == 200: return r.json()
            log(f"  HTTP {r.status_code} (tentativa {i+1}/{tries})")
        except Exception as e:
            log(f"  ERRO {type(e).__name__} (tentativa {i+1}/{tries})")
        time.sleep(min(60, 2 ** i * 2))
    raise RuntimeError("falha definitiva após repetições")
def abstract(inv):
    if not inv: return ""
    pos = {}
    for w, ps in inv.items():
        for p in ps: pos[p] = w
    return " ".join(pos[i] for i in sorted(pos))
def row(w, dom, est):
    pl = w.get("primary_location") or {}; src = pl.get("source") or {}
    au = w.get("authorships") or []
    inst = sorted({i.get("display_name","") for a in au for i in (a.get("institutions") or []) if i.get("display_name")})
    ctry = sorted({c for a in au for c in (a.get("countries") or [])})
    tp = w.get("topics") or []
    ab = abstract(w.get("abstract_inverted_index"))
    return {"openalex_id": w["id"], "doi": (w.get("doi") or "").replace("https://doi.org/", "").lower(),
            "title": w.get("title") or "", "abstract": ab, "abstract_fonte": "openalex" if ab else "",
            "year": w.get("publication_year"), "publication_date": w.get("publication_date"),
            "type": w.get("type"), "language": w.get("language"),
            "journal": src.get("display_name") or "", "publisher": src.get("host_organization_name") or "",
            "authors": "; ".join((a.get("author") or {}).get("display_name","") for a in au),
            "institutions": "; ".join(inst), "countries": "; ".join(ctry),
            "cited_by_count": w.get("cited_by_count"), "is_oa": (w.get("open_access") or {}).get("is_oa"),
            "concepts": "; ".join(c["display_name"] for c in (w.get("concepts") or [])),
            "topics": "; ".join(t["display_name"] for t in tp),
            "primary_topic_field": ((tp[0].get("field") or {}).get("display_name") if tp else ""),
            "keywords": "; ".join(k.get("display_name","") for k in (w.get("keywords") or [])),
            "dominio": dom, "estrategia": est}
def main():
    log("=" * 70); log("COLETA OPENALEX v2 — INÍCIO"); log(f"filtros comuns: {CFG['filtros_comuns']}")
    resumo = {"inicio": dt.datetime.now().isoformat(timespec="seconds"), "estrategias": {}}
    for dom, ests in CFG["consultas"].items():
        for est, q in ests.items():
            filt = f"title_and_abstract.search:{q},{CFG['filtros_comuns']}"
            n_esp = get({"filter": filt, "per-page": 1})["meta"]["count"]
            log(f"[{dom}/{est}] esperado={n_esp}")
            cursor, rows = "*", []
            with gzip.open(f"{OUT}/raw_{dom}_{est}.jsonl.gz", "wt", encoding="utf-8") as raw:
                while cursor:
                    d = get({"filter": filt, "per-page": 200, "cursor": cursor, "select": SELECT})
                    for w in d["results"]:
                        raw.write(json.dumps(w, ensure_ascii=False) + "\n"); rows.append(row(w, dom, est))
                    cursor = d["meta"].get("next_cursor")
                    if not d["results"]: break
                    time.sleep(0.12)
            ids = {r["openalex_id"] for r in rows}
            ok = len(ids) == n_esp
            log(f"[{dom}/{est}] obtido={len(rows)} unicos={len(ids)} com_resumo={sum(1 for r in rows if r['abstract'])} {'OK' if ok else 'DIVERGE do esperado'}")
            with open(f"{OUT}/{dom}_{est}.csv", "w", newline="", encoding="utf-8") as f:
                wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["openalex_id"]); wr.writeheader(); wr.writerows(rows)
            resumo["estrategias"][f"{dom}/{est}"] = {"esperado": n_esp, "obtido": len(rows), "unicos": len(ids),
                                                     "com_resumo_openalex": sum(1 for r in rows if r["abstract"]), "consulta": q}
    resumo["fim"] = dt.datetime.now().isoformat(timespec="seconds")
    json.dump(resumo, open(f"{OUT}/resumo_coleta_v2.json", "w"), indent=1, ensure_ascii=False)
    log("COLETA OPENALEX v2 — FIM")
if __name__ == "__main__":
    main()
