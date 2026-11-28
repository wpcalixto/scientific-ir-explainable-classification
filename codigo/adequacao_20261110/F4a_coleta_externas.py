#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F4a_coleta_externas.py

File type:
    Script

Purpose:
    Collects the external platforms (Scopus, Web of Science, Semantic Scholar) on the same day as the OpenAlex collection.

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
    - See docs/file_level_documentation.md (entry F4a_coleta_externas.py).

Outputs:
    - See docs/file_level_documentation.md (entry F4a_coleta_externas.py).

Dependencies:
    - requests

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F4a_coleta_externas.py

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
K = lambda n: open(os.path.expanduser(f"~/.config/bibliogenre/{n}")).read().strip()
SK, WK, S2K = K("scopus_api_key"), K("wos_starter_api_key"), K("s2_api_key")
LOG = open(f"{OUT}/coleta_externas.log", "a", encoding="utf-8")
def log(m):
    s = f"{dt.datetime.now().isoformat(timespec='seconds')} {m}"; print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
KW = {
 ("microarranjos", "busca_A"): "microarray feature selection AUC ROC",
 ("microarranjos", "busca_B"): "gene expression transcriptomic omics feature selection classification",
 ("microarranjos", "busca_C"): "gene expression feature selection gene selection AUC ROC",
 ("radiomica", "busca_A"): "radiomics feature selection AUC ROC",
 ("radiomica", "busca_B"): "medical imaging CT MRI feature selection classification",
 ("radiomica", "busca_C"): "texture features CT MRI feature selection AUC ROC",
 ("metamateriais", "busca_A"): "metamaterial metasurface machine learning design",
 ("metamateriais", "busca_B"): "photonic crystal frequency selective surface machine learning optimization design",
 ("metamateriais", "busca_C"): "subwavelength resonant structure inverse design deep learning",
}
def req(method, url, tries=7, **kw):
    for i in range(tries):
        try:
            r = requests.request(method, url, timeout=120, **kw)
            if r.status_code == 200: return r
            log(f"  HTTP {r.status_code} {url.split('?')[0][-40:]} (tentativa {i+1})")
            if r.status_code in (400, 401, 403): return r
        except Exception as e:
            log(f"  ERRO {type(e).__name__} (tentativa {i+1})")
        time.sleep(min(90, 3 * 2 ** i))
    return None
def gravar(nome, rows):
    if not rows: return
    with open(f"{OUT}/{nome}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
cont = {}
log("=" * 70); log("COLETA EXTERNAS — INÍCIO")
for dom, ests in CFG["consultas"].items():
    for est, q in ests.items():
        tag = f"{dom}_{est}"; cont[tag] = {}
        sq = f"TITLE-ABS({q}) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(re)) AND PUBYEAR < 2026"
        H = {"X-ELS-APIKey": SK, "Accept": "application/json"}
        top, todos, cursor, total = [], [], "*", None
        while cursor:
            r = req("GET", "https://api.elsevier.com/content/search/scopus", headers=H,
                    params={"query": sq, "count": 25, "cursor": cursor, "sort": "relevancy",
                            "field": "dc:identifier,prism:doi,dc:title,prism:coverDate,citedby-count,prism:publicationName"})
            if r is None or r.status_code != 200: log(f"[SCOPUS {tag}] falhou"); break
            sr = r.json()["search-results"]; total = int(sr["opensearch:totalResults"])
            ents = [e for e in sr.get("entry", []) if "error" not in e]
            if not ents: break
            for e in ents:
                row = {"rank": len(todos) + 1, "scopus_id": e.get("dc:identifier", ""), "doi": (e.get("prism:doi") or "").lower(),
                       "title": e.get("dc:title", ""), "date": e.get("prism:coverDate", ""), "cited_by": e.get("citedby-count", ""),
                       "source": e.get("prism:publicationName", "")}
                todos.append(row)
            nxt = sr.get("cursor", {}).get("@next")
            cursor = nxt if nxt and nxt != cursor else None
            time.sleep(0.15)
        gravar(f"scopus_top100_{tag}", todos[:100]); gravar(f"scopus_todos_{tag}", todos)
        cont[tag]["scopus_total"] = total; cont[tag]["scopus_obtidos"] = len(todos)
        log(f"[SCOPUS {tag}] total={total} obtidos={len(todos)}")
        wq = f"TS=({q}) AND PY=(1900-2025) AND DT=(Article OR Review)"
        rows, total = [], None
        for page in (1, 2):
            r = req("GET", "https://api.clarivate.com/apis/wos-starter/v1/documents", headers={"X-ApiKey": WK},
                    params={"q": wq, "db": "WOS", "limit": 50, "page": page, "sortField": "RS+D"})
            if r is None or r.status_code != 200: log(f"[WOS {tag}] falhou p{page}"); break
            j = r.json(); total = j["metadata"]["total"]
            for h in j.get("hits", []):
                ids = h.get("identifiers", {}) or {}
                rows.append({"rank": len(rows) + 1, "uid": h.get("uid", ""), "doi": (ids.get("doi") or "").lower(),
                             "title": h.get("title", ""), "year": (h.get("source") or {}).get("publishYear", ""),
                             "source": (h.get("source") or {}).get("sourceTitle", "")})
            if len(j.get("hits", [])) < 50: break
            time.sleep(1.1)
        gravar(f"wos_top100_{tag}", rows); cont[tag]["wos_total"] = total; cont[tag]["wos_obtidos"] = len(rows)
        log(f"[WOS {tag}] total={total} top={len(rows)}")
        sb = q.replace(" AND ", " + ").replace(" OR ", " | ")
        r = req("GET", "https://api.semanticscholar.org/graph/v1/paper/search/bulk", headers={"x-api-key": S2K},
                params={"query": sb, "year": "-2025", "publicationTypes": "JournalArticle,Review", "fields": "title"})
        cont[tag]["s2_bulk_total"] = r.json().get("total") if r is not None and r.status_code == 200 else None
        time.sleep(2)
        rows = []
        for off in (0, 50):
            r = req("GET", "https://api.semanticscholar.org/graph/v1/paper/search", headers={"x-api-key": S2K},
                    params={"query": KW[(dom, est)], "year": "-2025", "publicationTypes": "JournalArticle,Review",
                            "offset": off, "limit": 50, "fields": "title,year,externalIds,abstract,citationCount,venue"})
            if r is None or r.status_code != 200: log(f"[S2 {tag}] falhou off{off}"); break
            for p in r.json().get("data", []):
                rows.append({"rank": len(rows) + 1, "s2_id": p.get("paperId", ""), "doi": ((p.get("externalIds") or {}).get("DOI") or "").lower(),
                             "title": p.get("title", ""), "year": p.get("year", ""), "cited_by": p.get("citationCount", ""),
                             "source": p.get("venue", ""), "abstract": p.get("abstract") or ""})
            time.sleep(2)
        gravar(f"s2_top100_{tag}", rows); cont[tag]["s2_top"] = len(rows); cont[tag]["s2_keywords"] = KW[(dom, est)]
        log(f"[S2 {tag}] bulk_total={cont[tag]['s2_bulk_total']} top={len(rows)}")
json.dump({"data": dt.datetime.now().isoformat(timespec="seconds"), "contagens": cont}, open(f"{OUT}/contagens_externas.json", "w"), indent=1, ensure_ascii=False)
log("COLETA EXTERNAS — FIM")
