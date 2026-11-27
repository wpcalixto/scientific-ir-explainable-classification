#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F4a_teste_apis.py

File type:
    Script

Purpose:
    Syntax test of the external APIs (counts only).

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
    - See docs/file_level_documentation.md (entry F4a_teste_apis.py).

Outputs:
    - See docs/file_level_documentation.md (entry F4a_teste_apis.py).

Dependencies:
    - requests

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F4a_teste_apis.py

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

import os, json, requests, urllib.parse
K = lambda n: open(os.path.expanduser(f"~/.config/bibliogenre/{n}")).read().strip()
FS = '("feature selection" OR "variable selection" OR "feature ranking" OR "gene selection")'
EV = '(AUC OR ROC OR "area under the curve" OR "area under curve" OR "receiver operating characteristic")'
q = f'microarray AND {FS} AND {EV}'
def show(nome, r, f):
    try: print(nome, "HTTP", r.status_code, f(r.json()) if r.status_code == 200 else r.text[:200].replace(K_HIDE, "***"))
    except Exception as e: print(nome, "ERRO", type(e).__name__, str(e)[:150])
K_HIDE = "zzzz"
try:
    k = K("scopus_api_key"); K_HIDE = k
    sq = f'TITLE-ABS({q}) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(re)) AND PUBYEAR < 2026'
    r = requests.get("https://api.elsevier.com/content/search/scopus", params={"query": sq, "count": 1},
                     headers={"X-ELS-APIKey": k, "Accept": "application/json"}, timeout=60)
    show("SCOPUS", r, lambda j: j["search-results"]["opensearch:totalResults"])
except Exception as e: print("SCOPUS ERRO", type(e).__name__)
try:
    k = K("wos_starter_api_key"); K_HIDE = k
    wq = f'TS=({q}) AND PY=(1900-2025) AND DT=(Article OR Review)'
    r = requests.get("https://api.clarivate.com/apis/wos-starter/v1/documents", params={"q": wq, "db": "WOS", "limit": 1},
                     headers={"X-ApiKey": k}, timeout=60)
    show("WOS", r, lambda j: j["metadata"]["total"])
except Exception as e: print("WOS ERRO", type(e).__name__)
try:
    k = K("s2_api_key"); K_HIDE = k
    sb = '(microarray) + ("feature selection" | "variable selection" | "feature ranking" | "gene selection") + (AUC | ROC | "area under the curve" | "receiver operating characteristic")'
    r = requests.get("https://api.semanticscholar.org/graph/v1/paper/search/bulk", params={"query": sb, "year": "-2025", "fields": "title"},
                     headers={"x-api-key": k}, timeout=60)
    show("S2_bulk", r, lambda j: j.get("total"))
    r = requests.get("https://api.semanticscholar.org/graph/v1/paper/search", params={"query": "microarray feature selection AUC ROC", "limit": 1, "year": "-2025"},
                     headers={"x-api-key": k}, timeout=60)
    show("S2_relevancia", r, lambda j: j.get("total"))
except Exception as e: print("S2 ERRO", type(e).__name__)
try:
    k = K("lens_api_key"); K_HIDE = k
    body = {"query": {"bool": {"must": [{"query_string": {"query": q, "fields": ["title", "abstract"], "default_operator": "and"}}],
                               "filter": [{"range": {"year_published": {"lte": 2025}}}, {"terms": {"publication_type": ["journal article", "review"]}}]}},
            "size": 1, "include": ["lens_id", "title"]}
    r = requests.post("https://api.lens.org/scholarly/search", json=body, headers={"Authorization": f"Bearer {k}"}, timeout=60)
    show("LENS", r, lambda j: j.get("total"))
except Exception as e: print("LENS ERRO", type(e).__name__)
