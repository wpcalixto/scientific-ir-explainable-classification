#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F8b_folhas_21.py

File type:
    Script

Purpose:
    Produces the coded blind sheets (AV01-AV21) from the judgement pool.

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
    - See docs/file_level_documentation.md (entry F8b_folhas_21.py).

Outputs:
    - See docs/file_level_documentation.md (entry F8b_folhas_21.py).

Dependencies:
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F8b_folhas_21.py

Portability notes:
    All paths are resolved relative to the package base directory given by the BIBLIO_BASE environment variable
    (default: the package root, two levels above codigo/adequacao_20261110/). No machine-specific path is required.
    API keys, when needed, are read from ~/.config/bibliogenre/ and ~/.config/bibliometria/ and are not part of the package.

Reproducibility notes:
    Environment pinned in requirements.txt and environment/. Seeds and frozen parameters are written in the code and
    summarized in docs/parameters.md.

Warnings:
    Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.
"""

import os as _bb_os
BIBLIO_BASE = _bb_os.environ.get("BIBLIO_BASE") or _bb_os.path.abspath(
    _bb_os.path.join(_bb_os.path.dirname(_bb_os.path.abspath(__file__)), "..", ".."))

import os, pandas as pd
OUT = BIBLIO_BASE + "/resultados/adequacao_20261110/F8_julgamento"
docs = pd.read_csv(f"{OUT}/pool_mapa_NAO_ENVIAR.csv", keep_default_na=False)
DN = {"microarranjos": "1_Microarranjos", "radiomica": "2_Radiomica", "metamateriais": "3_Metamateriais"}
G = [("Fisica", ["metamateriais"], range(1, 8)), ("Biomedicina", ["microarranjos", "radiomica"], range(8, 15)),
     ("Computacao", ["microarranjos", "radiomica", "metamateriais"], range(15, 22))]
os.makedirs(f"{OUT}/folhas_21", exist_ok=True); reg = []
for grupo, doms, ids in G:
    for i in ids:
        cod = f"AV{i:02d}"
        with pd.ExcelWriter(f"{OUT}/folhas_21/Folha_{cod}.xlsx", engine="openpyxl") as xw:
            pd.DataFrame({"campo": ["codigo", "area_de_formacao", "nivel (senior / mestrado)", "anos_de_experiencia_na_area",
                                    "data_inicio", "data_fim"], "resposta": [cod, "", "", "", "", ""]}).to_excel(xw, sheet_name="0_Ficha", index=False)
            for d in doms:
                x = docs[docs["dominio"] == d].sample(frac=1, random_state=100 + i)[["doc_id", "titulo", "resumo"]]
                x["relevancia_0_1_2"] = ""; x["comentario"] = ""
                x.to_excel(xw, sheet_name=DN[d], index=False)
        reg.append({"codigo": cod, "grupo": grupo, "dominios": "+".join(doms), "n_docs": int(docs["dominio"].isin(doms).sum())})
pd.DataFrame(reg).to_csv(f"{OUT}/folhas_21/distribuicao.csv", index=False); print(pd.DataFrame(reg).groupby("grupo").first())
