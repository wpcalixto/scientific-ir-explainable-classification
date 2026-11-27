#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F21_reconstroi_rotulos_finais.py

File type:
    Script

Purpose:
    Read-only reconstruction of the passage from the raw LLM labels to the final labels.

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
    - See docs/file_level_documentation.md (entry F21_reconstroi_rotulos_finais.py).

Outputs:
    - See docs/file_level_documentation.md (entry F21_reconstroi_rotulos_finais.py).

Dependencies:
    - Python standard library only

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F21_reconstroi_rotulos_finais.py

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

import csv, re, hashlib, collections, sys
R = BIBLIO_BASE + "/resultados/adequacao_20261110/F2_rotulacao_v2"
csv.field_size_limit(10**9)
C = {"applied": "Applied", "methodological": "Methodological", "general": "General"}
src = list(csv.DictReader(open(f"{R}/rotulos_v2.csv", encoding="utf8"))); fin = list(csv.DictReader(open(f"{R}/rotulos_v2_final.csv", encoding="utf8")))
rec = []
for x in src:
    y = dict(x); y["label_original"] = x["label"]
    if x["label"] == "INVALID":
        m = re.match(r"\W*(\w+)", x["resposta_bruta"]); y["label"] = C.get(m.group(1).lower(), "INVALID") if m else "INVALID"
    rec.append(y)
key = lambda r: (r["dominio"], r["openalex_id"])
F = {key(r): r for r in fin}; dif = [k for k in map(key, rec) if F[k]["label"] != dict((key(r), r) for r in rec)[k]["label"]] if False else []
Rm = {key(r): r for r in rec}
dif = [k for k in Rm if Rm[k]["label"] != F[k]["label"] or Rm[k]["label_original"] != F[k]["label_original"]]
inv = [r for r in src if r["label"] == "INVALID"]; rest = [r for r in rec if r["label"] == "INVALID"]
print("sha256 rotulos_v2.csv:", hashlib.sha256(open(f"{R}/rotulos_v2.csv", "rb").read()).hexdigest())
print("sha256 rotulos_v2_final.csv:", hashlib.sha256(open(f"{R}/rotulos_v2_final.csv", "rb").read()).hexdigest())
print("registos:", len(src), len(fin), "| INVALID em rotulos_v2:", len(inv))
print("destino dos INVALID:", dict(collections.Counter(Rm[key(r)]["label"] for r in inv)))
print("divergências reconstrução × final (label e label_original):", len(dif))
print("INVALID restante:", [(r["dominio"], r["openalex_id"], r["sem_resumo"], r["resposta_bruta"][:60]) for r in rest])
print("totais finais com rótulo:", sum(1 for r in fin if r["label"] in C.values()))
