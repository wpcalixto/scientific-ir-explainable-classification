#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F4b_coleta_scopus.py

File type:
    Script

Purpose:
    Scopus collection: counts, top-100 by relevance and full DOI lists.

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
    - See docs/file_level_documentation.md (entry F4b_coleta_scopus.py).

Outputs:
    - See docs/file_level_documentation.md (entry F4b_coleta_scopus.py).

Dependencies:
    - requests

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F4b_coleta_scopus.py

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

import os, json, csv, time, datetime as dt, requests
BASE = BIBLIO_BASE + ""
CFG = json.load(open(f"{BASE}/codigo/adequacao_20261110/consultas_v2.json"))
OUT = f"{BASE}/dados/coleta_v2_20261110/externas"; os.makedirs(OUT, exist_ok=True)
SK = open(os.path.expanduser("~/.config/bibliogenre/scopus_api_key")).read().strip()
H = {"X-ELS-APIKey": SK, "Accept": "application/json"}
U = "https://api.elsevier.com/content/search/scopus"
LOG = open(f"{OUT}/coleta_scopus.log", "a", encoding="utf-8")
def log(m):
    s = f"{dt.datetime.now().isoformat(timespec='seconds')} {m}"; print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
def get(params, tries=7):
    for i in range(tries):
        try:
            r = requests.get(U, headers=H, params=params, timeout=120)
            if r.status_code == 200: return r.json()["search-results"]
            log(f"  HTTP {r.status_code} (tentativa {i+1})")
            if r.status_code in (400, 401, 403): return None
        except Exception as e:
            log(f"  ERRO {type(e).__name__} (tentativa {i+1})")
        time.sleep(min(90, 3 * 2 ** i))
    return None
def linha(e, rank):
    return {"rank": rank, "scopus_id": e.get("dc:identifier", ""), "doi": (e.get("prism:doi") or "").lower(),
            "title": e.get("dc:title", ""), "date": e.get("prism:coverDate", ""), "cited_by": e.get("citedby-count", ""),
            "source": e.get("prism:publicationName", "")}
def paginar(query, sort=None, limite=5000):
    rows, start, total = [], 0, None
    while True:
        p = {"query": query, "count": 25, "start": start}
        if sort: p["sort"] = sort
        sr = get(p)
        if sr is None: break
        total = int(sr["opensearch:totalResults"])
        ents = [e for e in sr.get("entry", []) if "error" not in e]
        rows += [linha(e, start + i + 1) for i, e in enumerate(ents)]
        start += 25
        if not ents or start >= min(total, limite): break
        time.sleep(0.12)
    return total, rows
def gravar(nome, rows):
    if not rows: return
    with open(f"{OUT}/{nome}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
cont = {}
log("=" * 70); log("SCOPUS — INÍCIO")
for dom, ests in CFG["consultas"].items():
    for est, q in ests.items():
        tag = f"{dom}_{est}"
        base = f"TITLE-ABS({q}) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(re))"
        total, top = paginar(base + " AND PUBYEAR < 2026", sort="relevancy", limite=100)
        gravar(f"scopus_top100_{tag}", top)
        todos = []
        if total is not None and total <= 5000:
            _, todos = paginar(base + " AND PUBYEAR < 2026")
        elif total is not None:
            fatias = [("PUBYEAR < 2011", "ate2010")] + [(f"PUBYEAR = {y}", str(y)) for y in range(2011, 2026)]
            for cond, nome in fatias:
                t, rows = paginar(f"{base} AND {cond}")
                if t and t > 5000: log(f"  [{tag}] fatia {nome} tem {t} > 5000 (truncada)")
                todos += rows
        vistos, uniq = set(), []
        for r in todos:
            k = r["scopus_id"] or r["doi"] or r["title"]
            if k not in vistos: vistos.add(k); uniq.append(r)
        gravar(f"scopus_todos_{tag}", uniq)
        cont[tag] = {"scopus_total": total, "scopus_top": len(top), "scopus_todos": len(uniq)}
        log(f"[SCOPUS {tag}] total={total} top={len(top)} todos={len(uniq)}")
json.dump({"data": dt.datetime.now().isoformat(timespec="seconds"), "contagens": cont}, open(f"{OUT}/contagens_scopus.json", "w"), indent=1, ensure_ascii=False)
log("SCOPUS — FIM")
