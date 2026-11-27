#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F14j_conferencia_pre_envio.py

File type:
    Script

Purpose:
    Read-only pre-dispatch check of the nine version-2 blind sheets.

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
    - See docs/file_level_documentation.md (entry F14j_conferencia_pre_envio.py).

Outputs:
    - See docs/file_level_documentation.md (entry F14j_conferencia_pre_envio.py).

Dependencies:
    - openpyxl
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F14j_conferencia_pre_envio.py

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

import os, hashlib, pandas as pd, openpyxl
O = BIBLIO_BASE + "/resultados/adequacao_20261110/F14_complementares_01A/validacao_P100"
M = pd.read_csv(f"{O}/mapa_documentos_v2_NAO_ENVIAR.csv", keep_default_na=False)
DOM = {"Microarranjos": "microarranjos", "Radiomica": "radiomica", "Metamateriais": "metamateriais"}
COLS = ["doc_id", "titulo", "resumo", "relevancia_0_1_2_ou_NA", "comentario"]
PROIB = ["OAL_", "scopus", "wos_", "elicit", "estrategia", "Strategy", "bm25", "consenso"]
rows, sha = [], []
for f in sorted(os.listdir(f"{O}/folhas_v2")):
    p = f"{O}/folhas_v2/{f}"; d = DOM[f.split("_")[2]]; wb = openpyxl.load_workbook(p); ws = wb.active
    form = any(isinstance(c.value, str) and c.value.startswith("=") for r in ws.iter_rows() for c in r)
    links = any(c.hyperlink for r in ws.iter_rows() for c in r); comm = any(c.comment for r in ws.iter_rows() for c in r)
    hid = any(dim.hidden for dim in ws.column_dimensions.values()) or any(dim.hidden for dim in ws.row_dimensions.values())
    x = pd.read_excel(p, keep_default_na=False); md = M[M.dominio == d]
    texto = (x.titulo.astype(str) + " " + x.resumo.astype(str))
    rows.append({"folha": f, "separadores": len(wb.sheetnames), "colunas_ok": list(x.columns) == COLS, "linhas": len(x),
                 "ids_iguais_ao_mapa": set(x.doc_id) == set(md.doc_id), "ids_unicos": x.doc_id.is_unique,
                 "calibracao_presente": int(x.doc_id.isin(md[md.tipo == "calibracao"].doc_id).sum()),
                 "sem_resumo_marcados": int((x.resumo == "(sem resumo)").sum()), "sem_resumo_no_mapa": int(md.sem_resumo.astype(str).eq("True").sum()),
                 "notas_vazias": bool((x["relevancia_0_1_2_ou_NA"].astype(str) == "").all()),
                 "formulas": form, "hiperligacoes": links, "comentarios_celula": comm, "ocultos": hid, "nomes_definidos": len(wb.defined_names) > 0,
                 "termos_de_origem_no_texto": int(texto.str.contains("|".join(PROIB), case=False).sum())})
    sha.append(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {f}")
R = pd.DataFrame(rows); R.to_csv(f"{O}/auditoria/conferencia_pre_envio.csv", index=False)
open(f"{O}/auditoria/SHA256_folhas_v2.txt", "w").write("\n".join(sha) + "\n"); print(R.T.to_string()); print("\n".join(sha))
