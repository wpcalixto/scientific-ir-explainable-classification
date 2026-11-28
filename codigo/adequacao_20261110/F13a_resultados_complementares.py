#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F13a_resultados_complementares.py

File type:
    Script

Purpose:
    Recomputes the complementary results from the raw data and checks them against the reported values.

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
    - See docs/file_level_documentation.md (entry F13a_resultados_complementares.py).

Outputs:
    - See docs/file_level_documentation.md (entry F13a_resultados_complementares.py).

Dependencies:
    - numpy
    - pandas
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F13a_resultados_complementares.py

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

import os, re, json, numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score as ck
R = BIBLIO_BASE + "/resultados/adequacao_20261110"
EXT = BIBLIO_BASE + "/dados/coleta_v2_20261110/externas"
O = f"{R}/F13_complementares"; os.makedirs(O, exist_ok=True)
DOMS, ESTS = ["microarranjos", "metamateriais", "radiomica"], ["A", "B", "C"]
conf = {}
kw = lambda a, b: ck(a, b, weights="quadratic", labels=[0, 1, 2])

can = pd.read_csv(f"{R}/F2_corpus/corpus_canonico.csv", dtype={"year": "Int64"}, low_memory=False)
can = can.drop_duplicates(["dominio", "openalex_id"])
ser, res = [], []
for d in DOMS:
    for e in ESTS + ["União"]:
        s = can[can.dominio == d] if e == "União" else can[(can.dominio == d) & (can[f"em_{e}"] == 1)]
        vc = s.year.dropna().astype(int).value_counts().sort_index()
        for y, n in vc.items(): ser.append({"dominio": d, "estrategia": e, "ano": y, "n": int(n)})
        p1, p2 = int(vc[(vc.index >= 2016) & (vc.index <= 2020)].sum()), int(vc[(vc.index >= 2021) & (vc.index <= 2025)].sum())
        res.append({"dominio": d, "estrategia": e, "n_total": len(s), "n_2016_2020": p1, "n_2021_2025": p2,
                    "variacao_pct": round(100 * (p2 - p1) / p1, 1)})
ser, res = pd.DataFrame(ser), pd.DataFrame(res)
ant = pd.read_csv(f"{R}/F2_corpus/crescimento_resumo.csv")
m = res.merge(ant, on=["dominio", "estrategia"])
conf["1_crescimento_igual_ao_antigo"] = bool((m.n_2016_2020_x == m.n_2016_2020_y).all() and (m.n_2021_2025_x == m.n_2021_2025_y).all())
dl = []
for d in DOMS:
    g = res[res.dominio == d].set_index("estrategia")
    for per in ["n_2016_2020", "n_2021_2025"]:
        dl.append({"dominio": d, "periodo": per[2:].replace("_", "–"), "A": g.loc["A", per], "B": g.loc["B", per], "C": g.loc["C", per],
                   "delta_A_B": round(g.loc["A", per] / g.loc["B", per], 3)})
pd.DataFrame(dl).to_csv(f"{O}/delta_por_periodo.csv", index=False)
res.to_csv(f"{O}/crescimento_por_estrategia.csv", index=False); ser.to_csv(f"{O}/serie_anual_por_estrategia.csv", index=False)

ndoi = lambda x: re.sub(r"^https?://(dx\.)?doi\.org/", "", str(x).strip().lower())
ntit = lambda x: re.sub(r"[^a-z0-9]", "", str(x).lower())[:120]
can["doi_n2"] = can.doi_n.fillna("").map(ndoi); can["tit_n2"] = can.title.fillna("").map(ntit)
ck_ = []
for d in DOMS:
    dom = can[can.dominio == d]
    for e in ESTS:
        est = dom[dom[f"em_{e}"] == 1]
        for plat in ["scopus_top100", "wos_top100", "s2_top100", "elicit_semantico", "elicit_keyword"]:
            f = f"{EXT}/{plat}_{d}_busca_{e}.csv"
            if not os.path.exists(f): continue
            x = pd.read_csv(f, dtype=str, keep_default_na=False).head(100)
            dd, tt = x.doi.map(ndoi), x.title.map(ntit)
            def em(S): return (dd.isin(set(S.doi_n2) - {""}) & (dd != "")) | (tt.isin(set(S.tit_n2) - {""}) & (tt != ""))
            ck_.append({"dominio": d, "estrategia": e, "plataforma": plat, "n": len(x),
                        "pct_no_corpus_dominio": round(100 * em(dom).mean(), 1), "pct_na_mesma_estrategia": round(100 * em(est).mean(), 1)})
EXTC = pd.DataFrame(ck_); EXTC.to_csv(f"{O}/sobreposicao_externas_top100.csv", index=False)

H = pd.read_csv(f"{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv")
jl = []
for dom in DOMS + ["todos"]:
    h = H if dom == "todos" else H[H.dominio == dom]
    for j in ["haiku", "gpt", "gemini", "consenso"]:
        a, b = h.H_med.astype(int), h[j].round().astype(int)
        jl.append({"dominio": dom, "juiz": j, "n": len(h), "kw": round(kw(a, b), 3), "iguais": round((a == b).mean(), 3),
                   "juiz_mais_alto": round((b > a).mean(), 3), "juiz_mais_baixo": round((b < a).mean(), 3)})
pd.DataFrame(jl).to_csv(f"{O}/juiz_LLM_vs_mediana_humana.csv", index=False)

Rt = pd.read_csv(f"{R}/F7_painel_llm/analise/R_rotulos_3llm.csv")
dist = pd.concat({m_: Rt.groupby("dominio")[m_].value_counts().unstack(fill_value=0) for m_ in ["haiku", "gpt", "gemini"]})
antd = pd.read_csv(f"{R}/F7_painel_llm/analise/R_distribuicao_rotulos.csv", index_col=[0, 1])
conf["4_distribuicao_igual_ao_antigo"] = bool((dist[antd.columns].values == antd.values).all())
dist.to_csv(f"{O}/distribuicao_rotulos_por_modelo.csv")

L = pd.read_csv(f"{R}/F7_painel_llm/listas_p100_com_jid.csv")
J = pd.read_csv(f"{R}/F7_painel_llm/analise/J_notas_3llm.csv").set_index("jid")["consenso"]
L = L[L.lista.str.match(r"^(OAL_[ABC]_(bm25|cit)|scopus_top100_[ABC]|wos_top100_[ABC]|elicit_semantico_[ABC])$")]
conf["5_listas_por_dominio"] = L.groupby("dominio").lista.nunique().to_dict()
pk = []
for (d, lst), g in L.groupby(["dominio", "lista"]):
    g = g.sort_values("rank"); e = re.search(r"_([ABC])(_|$)", lst).group(1)
    for k in [10, 20, 50, 100]:
        nota = J.reindex(g[g["rank"] <= k].jid).to_numpy(float)
        pk.append({"dominio": d, "lista": lst, "estrategia": e, "k": k, "n_lista": len(g), "P_estrita": (nota >= 2).sum() / k})
PK = pd.DataFrame(pk)
antk = pd.read_csv(f"{R}/F7_painel_llm/analise/J_metricas_cortes.csv").rename(columns={"l": "k"})
mk = PK.merge(antk, on=["dominio", "lista", "k"])
conf["5_Pk_igual_ao_antigo_max_dif"] = float((mk.P_estrita_x - mk.P_estrita_y).abs().max())
PK.to_csv(f"{O}/P_k_por_lista.csv", index=False)
PKe = PK.groupby(["dominio", "estrategia", "k"]).P_estrita.agg(["mean", "std", "min", "max", "count"]).round(3).reset_index()
PKe.to_csv(f"{O}/P_k_por_estrategia.csv", index=False)
pool = [{"dominio": d, "k": k, "n_listas": L[L.dominio == d].lista.nunique(), "pool_unico": L[(L.dominio == d) & (L["rank"] <= k)].jid.nunique()}
        for d in DOMS for k in [10, 20, 50, 100]]
pd.DataFrame(pool).to_csv(f"{O}/tamanho_pool_por_profundidade.csv", index=False)
conf["6_pool100"] = {p["dominio"]: p["pool_unico"] for p in pool if p["k"] == 100}

AV = ["W", "U", "V", "T", "S", "R", "Q", "P", "O", "N", "M", "L", "K"]
M = pd.DataFrame(np.nan, index=AV, columns=AV)
for i, a in enumerate(AV):
    M.loc[a, a] = 1.0
    for b in AV[i + 1:]:
        s = H[[a, b]].dropna()
        M.loc[a, b] = M.loc[b, a] = round(kw(s[a].astype(int), s[b].astype(int)), 3)
M.to_csv(f"{O}/kw_matriz_avaliadores.csv")
kp = pd.read_csv(f"{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/kw_pares.csv")
conf["7_kw_pares_max_dif"] = float(max(abs(M.loc[p[0], p[1]] - v) for p, v in zip(kp.par, kp.kw)))
json.dump(conf, open(f"{O}/conferencia.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(conf, ensure_ascii=False))
