#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F14k_folhas_quarto_avaliador.py

File type:
    Script

Purpose:
    Produces three complementary blind sheets (fourth assessor per domain) without changing the sample.

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
    - See docs/file_level_documentation.md (entry F14k_folhas_quarto_avaliador.py).

Outputs:
    - See docs/file_level_documentation.md (entry F14k_folhas_quarto_avaliador.py).

Dependencies:
    - numpy
    - openpyxl
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F14k_folhas_quarto_avaliador.py

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

import os, hashlib, numpy as np, pandas as pd, openpyxl
O = BIBLIO_BASE + "/resultados/adequacao_20261110/F14_complementares_01A/validacao_P100"
M = pd.read_csv(f"{O}/mapa_documentos_v2_NAO_ENVIAR.csv", keep_default_na=False)
nome = {"microarranjos": "Microarranjos", "radiomica": "Radiomica", "metamateriais": "Metamateriais"}
rng = np.random.default_rng(4343); rows, sha = [], []
for d in ["metamateriais", "microarranjos", "radiomica"]:
    g = M[M.dominio == d]; p = f"{O}/folhas_v2/Folha_P100_{nome[d]}_avaliador4.xlsx"
    assert not os.path.exists(p), "folha já existe; não sobrescrever"
    f = g.iloc[rng.permutation(len(g))][["doc_id", "titulo", "resumo"]].copy(); f["resumo"] = f.resumo.where(f.resumo.str.strip() != "", "(sem resumo)")
    f = f.assign(relevancia_0_1_2_ou_NA="", comentario="")
    with pd.ExcelWriter(p, engine="openpyxl") as xw: f.to_excel(xw, sheet_name=nome[d], index=False)
    x = pd.read_excel(p, keep_default_na=False); wb = openpyxl.load_workbook(p); ws = wb.active
    outras = [pd.read_excel(f"{O}/folhas_v2/Folha_P100_{nome[d]}_avaliador{a}.xlsx").doc_id.tolist() for a in (1, 2, 3)]
    rows.append({"folha": os.path.basename(p), "linhas": len(x), "ids_iguais_ao_mapa": set(x.doc_id) == set(g.doc_id),
                 "colunas_ok": list(x.columns) == ["doc_id", "titulo", "resumo", "relevancia_0_1_2_ou_NA", "comentario"],
                 "calibracao": int(x.doc_id.isin(g[g.tipo == "calibracao"].doc_id).sum()), "sem_resumo": int((x.resumo == "(sem resumo)").sum()),
                 "notas_vazias": bool((x.relevancia_0_1_2_ou_NA.astype(str) == "").all()), "separadores": len(wb.sheetnames),
                 "formulas_ligacoes_ocultos": any((isinstance(c.value, str) and c.value.startswith("=")) or c.hyperlink for r in ws.iter_rows() for c in r) or any(v.hidden for v in ws.column_dimensions.values()),
                 "ordem_diferente_das_outras_3": all(x.doc_id.tolist() != o for o in outras)})
    sha.append(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {os.path.basename(p)}")
pd.DataFrame(rows).to_csv(f"{O}/auditoria/conferencia_avaliador4.csv", index=False)
open(f"{O}/auditoria/SHA256_folhas_v2_avaliador4.txt", "w").write("\n".join(sha) + "\n"); print(pd.DataFrame(rows).T.to_string()); print("\n".join(sha))
