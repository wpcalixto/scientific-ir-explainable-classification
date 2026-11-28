#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F14h_verificacao_amostra_folhas_v2.py

File type:
    Script

Purpose:
    Pre-dispatch checks of the P@100 sample and blind sheets (version 2); does not change the sample.

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
    - See docs/file_level_documentation.md (entry F14h_verificacao_amostra_folhas_v2.py).

Outputs:
    - See docs/file_level_documentation.md (entry F14h_verificacao_amostra_folhas_v2.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F14h_verificacao_amostra_folhas_v2.py

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

import os, json, numpy as np, pandas as pd
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; O = f"{R}/F14_complementares_01A/validacao_P100"
P = pd.read_csv(f"{O}/amostra_posicoes_NAO_ENVIAR.csv"); n = int(P.n_estrato.max())
J = pd.read_csv(f"{R}/F7_painel_llm/analise/J_notas_3llm.csv").set_index("jid").consenso
L = pd.read_csv(f"{R}/F7_painel_llm/listas_p100_com_jid.csv")
L = L[L.lista.isin(P.lista.unique()) & (L["rank"] <= 10)]
H = pd.read_csv(f"{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv")
S = P[P.sorteado]; k = S.groupby("jid").agg(estratos=("lista", "size"), estrategias=("estrategia", "nunique"), dominio=("dominio", "first"))
part = {"posicoes_sorteadas": int(len(S)), "documentos_unicos_sorteados": int(len(k)), "docs_em_mais_de_um_estrato": int((k.estratos > 1).sum()),
        "docs_em_mais_de_uma_estrategia": int((k.estrategias > 1).sum()), "posicoes_com_doc_partilhado_%": round(100 * S.jid.map(k.estratos).gt(1).mean(), 1)}
P["y"] = (J.reindex(P.jid).to_numpy() >= 2).astype(float); L = L.assign(y=(J.reindex(L.jid).to_numpy() >= 2).astype(float))
top = L.groupby(["dominio", "lista"]).y.sum(); grp = P.groupby(["dominio", "lista", "faixa"]); est = list(grp.groups.keys())
estr = {g: P.loc[idx, "estrategia"].iloc[0] for g, idx in grp.groups.items()}
def estimar(amostra):
    lst = {}
    for (d, l, f), p in amostra.items(): lst.setdefault((d, l), top.get((d, l), 0.0)); lst[(d, l)] += grp.get_group((d, l, f)).shape[0] * p
    out = {}
    for (d, l), v in lst.items(): out.setdefault((d, l.split("_")[-1] if l.split("_")[-1] in "ABC" else l.split("_")[1]), []).append(v / 100)
    return {k_: np.mean(v) for k_, v in out.items()}
rng = np.random.default_rng(42); sims = []
ys = {g: grp.get_group(g).y.to_numpy() for g in est}
for _ in range(2000):
    sims.append(estimar({g: rng.choice(ys[g], min(n, len(ys[g])), replace=False).mean() for g in est}))
Sm = pd.DataFrame(sims); verdade = estimar({g: ys[g].mean() for g in est})
an = {}
for (d, l, f), y in ys.items():
    N = len(y); m = min(n, N); p = y.mean(); e = estr[(d, l, f)]
    an[(d, e)] = an.get((d, e), 0) + (N ** 2 * p * (1 - p) / m * (N - m) / max(N - 1, 1) / 100 ** 2) / 25
rows = []
for d in sorted({k_[0] for k_ in Sm.columns}):
    for e in "ABC":
        rows.append({"dominio": d, "alvo": f"P@100 {e}", "valor_pseudo": round(verdade[(d, e)], 3), "vies_sim": round(Sm[(d, e)].mean() - verdade[(d, e)], 4),
                     "dp_simulado": round(Sm[(d, e)].std(), 4), "ep_analitico": round(np.sqrt(an[(d, e)]), 4)})
    for a, b in [("A", "B"), ("A", "C"), ("C", "B")]:
        dif = Sm[(d, a)] - Sm[(d, b)]
        rows.append({"dominio": d, "alvo": f"{a}-{b}", "valor_pseudo": round(verdade[(d, a)] - verdade[(d, b)], 3), "vies_sim": round(dif.mean() - (verdade[(d, a)] - verdade[(d, b)]), 4),
                     "dp_simulado": round(dif.std(), 4), "ep_analitico": round(np.sqrt(an[(d, a)] + an[(d, b)]), 4)})
V = pd.DataFrame(rows); V["semiamplitude_IC95_sim"] = (1.96 * V.dp_simulado).round(3); V.to_csv(f"{O}/verificacao_desenho.csv", index=False)
print(json.dumps(part)); print(V.to_string(index=False)); json.dump(part, open(f"{O}/partilha.json", "w"), indent=1)
M = pd.read_csv(f"{O}/mapa_documentos_NAO_ENVIAR.csv", keep_default_na=False).assign(tipo="amostra")
pool = pd.read_csv(f"{R}/F7_painel_llm/pool_relevancia_p100.csv", keep_default_na=False).drop_duplicates("jid").set_index("jid")
cal = []
for d, g in H.groupby("dominio"):
    g = g[~g.jid.isin(M.jid)]
    pick = pd.concat([x.sample(min(10, len(x)), random_state=42) for _, x in g.groupby("H_med")])
    if len(pick) < 30: pick = pd.concat([pick, g[~g.jid.isin(pick.jid)].sample(30 - len(pick), random_state=42)])
    for r in pick.itertuples(): cal.append({"dominio": d, "jid": r.jid, "titulo": pool.loc[r.jid, "title"], "resumo": pool.loc[r.jid, "abstract"],
                                           "estratos": "calibracao", "tipo": "calibracao", "H_med_referencia": r.H_med, "n_aval_referencia": r.n_aval})
M2 = pd.concat([M.drop(columns="doc_id"), pd.DataFrame(cal)], ignore_index=True); M2["sem_resumo"] = M2.resumo.str.strip().eq("")
pref = {"microarranjos": "MJ", "radiomica": "RJ", "metamateriais": "EJ"}; rng = np.random.default_rng(4242); ids = []
for d, g in M2.groupby("dominio", sort=False):
    perm = rng.permutation(len(g)); ids += list(zip(g.index, [f"{pref[d]}{i + 1:04d}" for i in perm]))
M2.loc[[i for i, _ in ids], "doc_id"] = [x for _, x in ids]
M2.to_csv(f"{O}/mapa_documentos_v2_NAO_ENVIAR.csv", index=False)
os.makedirs(f"{O}/folhas_v2", exist_ok=True); nome = {"microarranjos": "Microarranjos", "radiomica": "Radiomica", "metamateriais": "Metamateriais"}
for d, g in M2.groupby("dominio"):
    for a in (1, 2, 3):
        f = g.iloc[rng.permutation(len(g))][["doc_id", "titulo", "resumo"]].copy(); f["resumo"] = f.resumo.where(f.resumo.str.strip() != "", "(sem resumo)")
        f = f.assign(relevancia_0_1_2_ou_NA="", comentario="")
        with pd.ExcelWriter(f"{O}/folhas_v2/Folha_P100_{nome[d]}_avaliador{a}.xlsx", engine="openpyxl") as xw: f.to_excel(xw, sheet_name=nome[d], index=False)
print(M2.groupby(["dominio", "tipo"]).size().to_dict(), "| sem resumo:", M2.groupby("dominio").sem_resumo.sum().to_dict(),
      "| calibração por mediana:", pd.DataFrame(cal).groupby(["dominio", "H_med_referencia"]).size().to_dict())
