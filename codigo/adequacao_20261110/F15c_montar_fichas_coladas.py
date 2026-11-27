#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F15c_montar_fichas_coladas.py

File type:
    Script

Purpose:
    Assembles the returned P@100 sheets from the transcribed 'doc_id<TAB>grade' lines.

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
    - See docs/file_level_documentation.md (entry F15c_montar_fichas_coladas.py).

Outputs:
    - See docs/file_level_documentation.md (entry F15c_montar_fichas_coladas.py).

Dependencies:
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F15c_montar_fichas_coladas.py

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

import os, sys, pandas as pd
TXT, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
V = BIBLIO_BASE + "/resultados/adequacao_20261110/F14_complementares_01A/validacao_P100"
def ler(f, pre):
    d = {}
    for l in open(f, encoding="utf8"):
        p = l.strip().split("\t")
        if len(p) == 2 and p[0].startswith(pre) and p[1].strip(): d[p[0].strip()] = p[1].strip()
    return d
fontes = {"MJ": ("Microarranjos_Y", "notas_P100_coladas_20261112_2251.txt"), "EJ": ("Metamateriais_Z", "notas_P100_coladas_20261112_2251.txt"),
          "RJ": ("Radiomica_X", "RJ_completo_311_20261112_2325.txt")}
for pre, (nome, f) in fontes.items():
    n = ler(f"{TXT}/{f}", pre); x = pd.read_excel(f"{V}/envio_P01B2/Folha_P100_{nome}.xlsx", keep_default_na=False, dtype=str)
    assert set(n) == set(x.doc_id), (pre, len(set(n) ^ set(x.doc_id)))
    x["relevancia_0_1_2_ou_NA"] = x.doc_id.map(n); x["comentario"] = ""
    x.to_excel(f"{OUT}/Folha_P100_{nome}.xlsx", index=False); print(nome, len(x), x.relevancia_0_1_2_ou_NA.value_counts().to_dict())
