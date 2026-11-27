#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F14f_amostra_folhas_P100.py

File type:
    Script

Purpose:
    Draws the stratified sample of positions 11-100 and produces the blind sheets of the human P@100 validation.

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
    - See docs/file_level_documentation.md (entry F14f_amostra_folhas_P100.py).

Outputs:
    - See docs/file_level_documentation.md (entry F14f_amostra_folhas_P100.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F14f_amostra_folhas_P100.py

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

import os, sys, numpy as np, pandas as pd
n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; O = f"{R}/F14_complementares_01A/validacao_P100"
os.makedirs(f"{O}/folhas", exist_ok=True)
L = pd.read_csv(f"{R}/F7_painel_llm/listas_p100_com_jid.csv")
L = L[L.lista.str.match(r"^(OAL_[ABC]_(bm25|cit)|scopus_top100_[ABC]|wos_top100_[ABC]|elicit_semantico_[ABC])$") & (L["rank"] > 10)].copy()
L["estrategia"] = L.lista.str.extract(r"_([ABC])(?:_|$)")[0]
L["faixa"] = pd.cut(L["rank"], [10, 30, 60, 100], labels=["11-30", "31-60", "61-100"]).astype(str)
H = set(pd.read_csv(f"{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv").jid)
rng = np.random.default_rng(42); partes = []
for (d, lst, fx), g in L.sort_values(["dominio", "lista", "rank"]).groupby(["dominio", "lista", "faixa"], sort=True):
    g = g.iloc[rng.permutation(len(g))].copy(); g["ordem_no_estrato"] = range(1, len(g) + 1); g["N_estrato"] = len(g); partes.append(g)
P = pd.concat(partes); P["n_estrato"] = P.N_estrato.clip(upper=n); P["pi"] = P.n_estrato / P.N_estrato; P["peso"] = 1 / P.pi
P["sorteado"] = P.ordem_no_estrato <= n; P["ja_julgado_top10"] = P.jid.isin(H)
P.to_csv(f"{O}/amostra_posicoes_NAO_ENVIAR.csv", index=False)
S = P[P.sorteado]; novos = S[~S.ja_julgado_top10]
pool = pd.read_csv(f"{R}/F7_painel_llm/pool_relevancia_p100.csv").drop_duplicates("jid").set_index("jid")
pref = {"microarranjos": "MJ", "radiomica": "RJ", "metamateriais": "EJ"}; mapa = []
for d, g in novos.groupby("dominio"):
    js = sorted(g.jid.unique()); ids = rng.permutation(len(js))
    for j, k in zip(js, ids):
        mapa.append({"dominio": d, "jid": j, "doc_id": f"{pref[d]}{k + 1:04d}", "titulo": pool.loc[j, "title"],
                     "resumo": pool.loc[j, "abstract"] if isinstance(pool.loc[j, "abstract"], str) else "",
                     "estratos": ";".join(sorted(set(g[g.jid == j].lista + "|" + g[g.jid == j].faixa)))})
M = pd.DataFrame(mapa); M.to_csv(f"{O}/mapa_documentos_NAO_ENVIAR.csv", index=False)
nome = {"microarranjos": "Microarranjos", "radiomica": "Radiomica", "metamateriais": "Metamateriais"}
for d, g in M.groupby("dominio"):
    for a in (1, 2, 3):
        f = g.iloc[rng.permutation(len(g))][["doc_id", "titulo", "resumo"]].assign(relevancia_0_1_2="", comentario="")
        with pd.ExcelWriter(f"{O}/folhas/Folha_P100_{nome[d]}_avaliador{a}.xlsx", engine="openpyxl") as xw:
            f.to_excel(xw, sheet_name=nome[d], index=False)
print("n por estrato:", n, "| posições sorteadas:", int(P.sorteado.sum()), "| já julgadas no top-10:", int(S.ja_julgado_top10.sum()),
      "| documentos novos por domínio:", M.groupby("dominio").size().to_dict(), "| total:", len(M), "| sem resumo:", int((M.resumo == "").sum()))
