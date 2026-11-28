#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    patch02.py

File type:
    Script

Purpose:
    Patch applied to the legacy LDA preprocessing script for the F10 re-execution (LDA fitted on unique documents).

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
    - See docs/file_level_documentation.md (entry patch02.py).

Outputs:
    - See docs/file_level_documentation.md (entry patch02.py).

Dependencies:
    - Python standard library only

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/patch02.py

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

import sys
f=sys.argv[1]; s=open(f).read()
old='    # 1. Pré-processamento\n    print("\\n[1] Pré-processamento...")\n    df_dom = preprocessar_corpus(df_dom)'
assert old in s, "old1"
s=s.replace(old,'    # F10: LDA ajustada sobre documentos únicos (corpus canónico); a ACP usa a pertença a cada estratégia\n    df_longo = df_dom.copy()\n    df_dom = df_dom.drop_duplicates("openalex_id").copy()\n'+old)
old2='    pca_topicos(df_com_topicos, k_otimo, dominio)'
assert old2 in s, "old2"
s=s.replace(old2,'    cols_t = [f"topic_{t}" for t in range(k_otimo)]\n    df_pca = df_longo[["openalex_id", "estrategia"]].merge(df_com_topicos[["openalex_id"] + cols_t], on="openalex_id", how="inner")\n    pca_topicos(df_pca, k_otimo, dominio)')
open(f,"w").write(s); print("ok")
