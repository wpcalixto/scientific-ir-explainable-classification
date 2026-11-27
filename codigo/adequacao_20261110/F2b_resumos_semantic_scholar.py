#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F2b_resumos_semantic_scholar.py

File type:
    Script

Purpose:
    Completes missing abstracts through the Semantic Scholar batch API (by DOI).

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
    - See docs/file_level_documentation.md (entry F2b_resumos_semantic_scholar.py).

Outputs:
    - See docs/file_level_documentation.md (entry F2b_resumos_semantic_scholar.py).

Dependencies:
    - requests

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F2b_resumos_semantic_scholar.py

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

import csv, os, json, time, shutil, glob, datetime as dt
import requests
OUT = BIBLIO_BASE + "/dados/coleta_v2_20261110"
KEY = open(os.path.expanduser("~/.config/bibliogenre/s2_api_key")).read().strip()
LOG = open(f"{OUT}/coleta_v2.log", "a", encoding="utf-8")
def log(m):
    s = f"{dt.datetime.now().isoformat(timespec='seconds')} {m}"; print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
csv.field_size_limit(10**9)
files = sorted(f for f in glob.glob(f"{OUT}/*_busca_*.csv") if not f.endswith("_antes_s2.csv"))
falta = set()
data = {}
for f in files:
    rows = list(csv.DictReader(open(f, encoding="utf-8"))); data[f] = rows
    falta |= {r["doi"] for r in rows if not r["abstract"] and r["doi"]}
log(f"S2: DOIs sem resumo a procurar = {len(falta)}")
achados, dois = {}, sorted(falta)
for i in range(0, len(dois), 400):
    lote = dois[i:i+400]
    for t in range(6):
        try:
            r = requests.post("https://api.semanticscholar.org/graph/v1/paper/batch", params={"fields": "abstract"},
                              json={"ids": [f"DOI:{d}" for d in lote]}, headers={"x-api-key": KEY}, timeout=120)
            if r.status_code == 200:
                for d, p in zip(lote, r.json()):
                    if p and p.get("abstract"): achados[d] = p["abstract"]
                break
            log(f"  S2 HTTP {r.status_code} (tentativa {t+1})")
        except Exception as e:
            log(f"  S2 ERRO {type(e).__name__} (tentativa {t+1})")
        time.sleep(min(60, 2 ** t * 3))
    time.sleep(1.1)
log(f"S2: resumos encontrados = {len(achados)} de {len(falta)}")
for f, rows in data.items():
    shutil.copy(f, f.replace(".csv", "_antes_s2.csv"))
    for r in rows:
        if not r["abstract"] and r["doi"] in achados:
            r["abstract"], r["abstract_fonte"] = achados[r["doi"]], "semantic_scholar"
    with open(f, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    log(f"  {os.path.basename(f)}: sem resumo após S2 = {sum(1 for r in rows if not r['abstract'])} de {len(rows)}")
log("S2 — FIM")
