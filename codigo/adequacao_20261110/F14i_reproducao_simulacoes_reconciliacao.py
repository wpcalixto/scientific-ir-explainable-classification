#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F14i_reproducao_simulacoes_reconciliacao.py

File type:
    Script

Purpose:
    Read-only audit that reproduces the simulations and reconciles the P@100 sample and sheets.

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
    - See docs/file_level_documentation.md (entry F14i_reproducao_simulacoes_reconciliacao.py).

Outputs:
    - See docs/file_level_documentation.md (entry F14i_reproducao_simulacoes_reconciliacao.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F14i_reproducao_simulacoes_reconciliacao.py

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

import os, numpy as np, pandas as pd
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; O = f"{R}/F14_complementares_01A/validacao_P100"; A = f"{O}/auditoria"; os.makedirs(A, exist_ok=True)
P = pd.read_csv(f"{O}/amostra_posicoes_NAO_ENVIAR.csv"); n = int(P.n_estrato.max())
J = pd.read_csv(f"{R}/F7_painel_llm/analise/J_notas_3llm.csv").set_index("jid").consenso
L = pd.read_csv(f"{R}/F7_painel_llm/listas_p100_com_jid.csv"); L = L[L.lista.isin(P.lista.unique()) & (L["rank"] <= 10)]
P["y"] = (J.reindex(P.jid).to_numpy() >= 2).astype(float); L = L.assign(y=(J.reindex(L.jid).to_numpy() >= 2).astype(float))
top = L.groupby(["dominio", "lista"]).y.sum(); grp = P.groupby(["dominio", "lista", "faixa"]); est = list(grp.groups.keys())
def estimar(amostra):
    lst = {}
    for (d, l, f), p in amostra.items(): lst.setdefault((d, l), top.get((d, l), 0.0)); lst[(d, l)] += grp.get_group((d, l, f)).shape[0] * p
    out = {}
    for (d, l), v in lst.items(): out.setdefault((d, l.split("_")[-1] if l.split("_")[-1] in "ABC" else l.split("_")[1]), []).append(v / 100)
    return {k_: np.mean(v) for k_, v in out.items()}
rng = np.random.default_rng(42); ys = {g: grp.get_group(g).y.to_numpy() for g in est}; sims = []
for _ in range(2000): sims.append(estimar({g: rng.choice(ys[g], min(n, len(ys[g])), replace=False).mean() for g in est}))
Sm = pd.DataFrame(sims); Sm.columns = [f"{d}|{e}" for d, e in Sm.columns]; Sm.index.name = "replica"; Sm.round(6).to_csv(f"{A}/simulacoes_2000_replicas.csv")
V = pd.read_csv(f"{O}/verificacao_desenho.csv"); conf = []
for r in V.itertuples():
    if r.alvo.startswith("P@100"): s = Sm[f"{r.dominio}|{r.alvo[-1]}"]
    else: a, b = r.alvo.split("-"); s = Sm[f"{r.dominio}|{a}"] - Sm[f"{r.dominio}|{b}"]
    conf.append({"dominio": r.dominio, "alvo": r.alvo, "dp_publicado": r.dp_simulado, "dp_reproduzido": round(s.std(), 4), "igual": round(s.std(), 4) == r.dp_simulado})
C = pd.DataFrame(conf); C.to_csv(f"{A}/simulacoes_conferencia.csv", index=False); print("simulação reproduzida igual:", bool(C.igual.all()))
S = P[P.sorteado]; M = pd.read_csv(f"{O}/mapa_documentos_v2_NAO_ENVIAR.csv", keep_default_na=False)
rows = []
for d, g in list(S.groupby("dominio")) + [("total", S)]:
    k = g.groupby("jid").agg(oc=("lista", "size"), est=("estrategia", "nunique"), jul=("ja_julgado_top10", "first"))
    mg = M if d == "total" else M[M.dominio == d]
    rows.append({"dominio": d, "posicoes_sorteadas": len(g), "documentos_distintos": len(k),
                 "ocorrencias_repetidas (posicoes - distintos)": len(g) - len(k), "docs_em_>1_estrato": int((k.oc > 1).sum()),
                 "docs_em_>1_estrategia": int((k.est > 1).sum()), "posicoes_ja_julgadas_top10": int(g.ja_julgado_top10.sum()),
                 "docs_distintos_ja_julgados": int(k.jul.sum()), "docs_distintos_novos": int((~k.jul).sum()),
                 "posicoes_de_docs_novos": int((~g.ja_julgado_top10).sum()),
                 "folha_v2_amostra": int((mg.tipo == "amostra").sum()), "folha_v2_calibracao": int((mg.tipo == "calibracao").sum()),
                 "novos_iguais_ao_mapa": set(k[~k.jul].index) == set(mg[mg.tipo == "amostra"].jid)})
Rc = pd.DataFrame(rows); Rc.to_csv(f"{A}/reconciliacao.csv", index=False); print(Rc.T.to_string())
fl = []
for f in sorted(os.listdir(f"{O}/folhas_v2")):
    x = pd.read_excel(f"{O}/folhas_v2/{f}"); d = {"Microarranjos": "microarranjos", "Radiomica": "radiomica", "Metamateriais": "metamateriais"}[f.split("_")[2]]
    ids = set(x.doc_id); mi = set(M[M.dominio == d].doc_id)
    fl.append({"folha": f, "linhas": len(x), "doc_id_unicos": len(ids), "iguais_ao_mapa_do_dominio": ids == mi, "sem_resumo": int((x.resumo == "(sem resumo)").sum()),
               "colunas": "|".join(x.columns)})
F = pd.DataFrame(fl); F.to_csv(f"{A}/reconciliacao_folhas.csv", index=False); print(F.to_string(index=False))
