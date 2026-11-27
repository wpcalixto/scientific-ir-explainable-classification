#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F16c_reproducao_e_mudancas_portatil.py

File type:
    Script

Purpose:
    Portable version of F16c (paths given as command-line arguments).

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
    - See docs/file_level_documentation.md (entry F16c_reproducao_e_mudancas_portatil.py).

Outputs:
    - See docs/file_level_documentation.md (entry F16c_reproducao_e_mudancas_portatil.py).

Dependencies:
    - numpy
    - pandas
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F16c_reproducao_e_mudancas_portatil.py

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

import os, sys, re, numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score
PKG, D = sys.argv[1], sys.argv[2]; OUT = f"{D}/reproducao_F16c"; os.makedirs(OUT, exist_ok=True)
new = {}
for l in open(f"{PKG}/recebido/notas_replicacao_coladas_20261113_1245.txt", encoding="utf8"):
    m = re.match(r"^([A-Z]{2}\d{4})\t(\S+)$", l.strip("\n"))
    if m: assert m.group(1) not in new; new[m.group(1)] = m.group(2)
M = pd.read_csv(f"{PKG}/desenho/mapa_documentos_v2_NAO_ENVIAR.csv", keep_default_na=False).set_index("doc_id")
OLD = pd.read_csv(f"{PKG}/referencias/notas_R_old_consolidadas.csv", keep_default_na=False, dtype=str).set_index("doc_id").nota
assert set(new) == set(M.index) == set(OLD.index) and len(new) == 902
F16 = pd.read_csv(f"{D}/controlo/notas_replicacao_consolidadas.csv", keep_default_na=False, dtype=str).set_index("doc_id").nota
chk = [("V10R2-03", "notas F16a = texto colado", int(sum(F16[k] != v for k, v in new.items())))]
H = pd.read_csv(f"{PKG}/referencias/notas_humanos_LLM.csv").set_index("jid").H_med
J = pd.read_csv(f"{PKG}/referencias/J_notas_3llm.csv").set_index("jid").consenso
DOM = {"MJ": "microarranjos", "RJ": "radiomica", "EJ": "metamateriais"}
T = pd.DataFrame({"doc_id": list(new)}); T["dominio"] = T.doc_id.str[:2].map(DOM); T["jid"] = T.doc_id.map(M.jid); T["tipo"] = T.doc_id.map(M.tipo)
T["n"] = T.doc_id.map(new).astype(int); T["o"] = T.doc_id.map(OLD).astype(int)
def alpha_coinc(a, b, k=3):
    o = np.zeros((k, k))
    for x, y in zip(a, b): o[x, y] += 1; o[y, x] += 1
    nc = o.sum(1); n = nc.sum()
    def delta(c, kk):
        lo, hi = min(c, kk), max(c, kk); return (nc[lo:hi + 1].sum() - (nc[lo] + nc[hi]) / 2) ** 2
    dl = np.array([[delta(c, kk) for kk in range(k)] for c in range(k)])
    return 1 - (n - 1) * (o * dl).sum() / (np.outer(nc, nc) * dl).sum()
A_ = []
for (d, t), g in T.groupby(["dominio", "tipo"]):
    A_.append({"dominio": d, "tipo": t, "n": len(g), "iguais": (g.n == g.o).mean(), "kw_sklearn": cohen_kappa_score(g.o, g.n, weights="quadratic", labels=[0, 1, 2]),
               "alfa_coincidencias": alpha_coinc(g.o.values, g.n.values), "dif_1nivel": (abs(g.n - g.o) == 1).mean(), "dif_2niveis": (abs(g.n - g.o) == 2).mean(),
               "1para2": ((g.o == 1) & (g.n == 2)).sum(), "2para1": ((g.o == 2) & (g.n == 1)).sum(), "0para1": ((g.o == 0) & (g.n == 1)).sum(), "1para0": ((g.o == 1) & (g.n == 0)).sum()})
A_ = pd.DataFrame(A_); A_.round(4).to_csv(f"{OUT}/A_concordancia_reproduzida.csv", index=False)
f16a = pd.read_csv(f"{D}/analise/A_comparacao_old_new.csv")
mx = max(abs(A_.set_index(["dominio", "tipo"]).kw_sklearn - f16a.set_index(["dominio", "tipo"]).kw).max(), abs(A_.set_index(["dominio", "tipo"]).alfa_coincidencias - f16a.set_index(["dominio", "tipo"]).alfa_ord).max(),
         abs(A_.set_index(["dominio", "tipo"]).iguais - f16a.set_index(["dominio", "tipo"]).iguais).max())
chk.append(("V10R2-03", "concordância (iguais, κw, α) F16c vs F16b: diferença máxima", round(float(mx), 5)))
cb = []
for d, g in T[T.tipo == "calibracao"].groupby("dominio"):
    r = H.reindex(g.jid).astype(int).to_numpy()
    for ref, col in [("R_new", "n"), ("R_old", "o")]:
        k = cohen_kappa_score(r, g[col], weights="quadratic", labels=[0, 1, 2])
        cb.append({"dominio": d, "referencia": ref, "kw": k, "iguais": (g[col].to_numpy() == r).mean(), "dif_media": (g[col].to_numpy() - r).mean(),
                   "classe_plano": "substituir (<0,20)" if k < 0.2 else ("ressalva (0,20–0,40)" if k < 0.4 else "ok (≥0,40)")})
cb = pd.DataFrame(cb); cb.round(4).to_csv(f"{OUT}/B_calibracao_reproduzida.csv", index=False)
f16b = pd.read_csv(f"{D}/analise/B_calibracao.csv")
chk.append(("V10R2-04", "κw calibração F16c vs F16b: diferença máxima", round(float(abs(cb[cb.referencia == "R_new"].set_index("dominio").kw - f16b[f16b.referencia == "new"].set_index("dominio").kw_vs_mediana_1a_fase).max()), 5)))
P = pd.read_csv(f"{PKG}/desenho/amostra_posicoes_NAO_ENVIAR.csv"); S = P[P.sorteado].reset_index(drop=True); reuso = S.ja_julgado_top10.astype(bool).to_numpy()
S["sk"] = S.dominio + "|" + S.lista + "|" + S.faixa; sk = pd.factorize(S.sk)[0]; NS = sk.max() + 1
st = S.groupby(sk).agg(dominio=("dominio", "first"), lista=("lista", "first"), estrategia=("estrategia", "first"), N=("N_estrato", "first"))
lists = st.drop_duplicates(["dominio", "lista"])[["dominio", "lista", "estrategia"]].reset_index(drop=True); li = {(a, b): i for i, (a, b) in enumerate(zip(lists.dominio, lists.lista))}
s2l = np.array([li[(a, b)] for a, b in zip(st.dominio, st.lista)]); Ns = st.N.to_numpy(float); NL = len(lists)
L = pd.read_csv(f"{PKG}/referencias/listas_p100_com_jid.csv"); L = L[L.lista.isin(S.lista.unique()) & (L["rank"] <= 10)]
def h10(score, thr=2):
    v = np.zeros(NL)
    for (a, b), g in L.groupby(["dominio", "lista"]): v[li[(a, b)]] = (score.reindex(g.jid).to_numpy() >= thr).sum()
    return v
tg, Am = [], []
DOMS = ["microarranjos", "radiomica", "metamateriais"]
for d in DOMS:
    for e in "ABC":
        vv = np.zeros(NL); vv[[i for i, (a, b) in enumerate(zip(lists.dominio, lists.estrategia)) if a == d and b == e]] = 0.2; tg.append(f"{d}|{e}"); Am.append(vv)
for d in DOMS:
    for a, b in [("A", "B"), ("A", "C"), ("C", "B")]: tg.append(f"{d}|{a}-{b}"); Am.append(Am[tg.index(f"{d}|{a}")] - Am[tg.index(f"{d}|{b}")])
Am = np.array(Am)
def est(y, h, w=None):
    w = np.ones(len(y)) if w is None else w
    p = np.bincount(sk, w * y, NS) / np.bincount(sk, w, NS); tot = h + np.bincount(s2l, Ns * p, NL); return Am @ (tot / 100)
def se_m1(z):
    m = np.bincount(sk, minlength=NS).astype(float); mu = np.bincount(sk, z, NS) / m
    s2 = np.bincount(sk, (z - mu[sk]) ** 2, NS) / (m - 1); vs = Ns ** 2 * (1 - m / Ns) * s2 / m
    return np.sqrt((Am ** 2) @ (np.bincount(s2l, vs, NL) / 1e4))
nmap = dict(zip(T.jid, T.n)); omap = dict(zip(T.jid, T.o))
def y_of(mp, thr): return np.array([(H[j] >= thr) if r else (mp[j] >= thr) for j, r in zip(S.jid, reuso)], float)
u, inv = np.unique(S.jid, return_inverse=True); rng = np.random.default_rng(4242); Wb = rng.exponential(1.0, (2000, len(u)))[:, inv]
res = []
for nome, thr in [("estrita (nota 2)", 2), ("branda (nota ≥1)", 1)]:
    yn, yo = y_of(nmap, thr), y_of(omap, thr); h = h10(H, thr)
    en, eo = est(yn, h), est(yo, h); sen, seo, sed = se_m1(yn), se_m1(yo), se_m1(yn - yo)
    bn = np.array([est(yn, h, w) for w in Wb]); bo = np.array([est(yo, h, w) for w in Wb]); bd = bn - bo
    for i, t in enumerate(tg):
        res.append({"relevancia": nome, "alvo": t, "R_new": en[i], "R_new_M1_inf": en[i] - 1.96 * sen[i], "R_new_M1_sup": en[i] + 1.96 * sen[i],
                    "R_new_M3_inf": np.quantile(bn[:, i], .025), "R_new_M3_sup": np.quantile(bn[:, i], .975), "R_old": eo[i],
                    "mudanca": en[i] - eo[i], "mud_M1_inf": en[i] - eo[i] - 1.96 * sed[i], "mud_M1_sup": en[i] - eo[i] + 1.96 * sed[i],
                    "mud_M3_inf": np.quantile(bd[:, i], .025), "mud_M3_sup": np.quantile(bd[:, i], .975)})
RS = pd.DataFrame(res); RS.round(4).to_csv(f"{OUT}/C_P100_e_mudancas_entre_referencias.csv", index=False)
f1 = pd.read_csv(f"{D}/analise/C1_P100_estrategias.csv"); f2 = pd.read_csv(f"{D}/analise/C1_P100_diferencas.csv")
e = RS[RS.relevancia.str.startswith("estrita")].set_index("alvo"); dmax = 0
for r in f1.itertuples():
    k = f"{r.dominio}|{r.estrategia}"; dmax = max(dmax, abs(e.loc[k, "R_new"] - r.P100_R_new), abs(e.loc[k, "R_new_M1_inf"] - r.M1_inf), abs(e.loc[k, "R_old"] - r.P100_R_old), abs(e.loc[k, "mudanca"] - r.new_menos_old), abs(e.loc[k, "mud_M1_inf"] - r.nmo_inf))
for r in f2.itertuples():
    k = f"{r.dominio}|{r.comparacao}"; dmax = max(dmax, abs(e.loc[k, "R_new"] - r.R_new), abs(e.loc[k, "R_new_M1_inf"] - r.M1_inf), abs(e.loc[k, "R_new_M1_sup"] - r.M1_sup), abs(e.loc[k, "R_old"] - r.R_old))
chk.append(("V10R2-03/06", "P@100, diferenças e IC M1 (estrita) F16c vs F16b: diferença máxima", round(float(dmax), 5)))
m3 = max(max(abs(e.loc[f"{r.dominio}|{r.comparacao}", "R_new_M3_inf"] - r.M3_inf), abs(e.loc[f"{r.dominio}|{r.comparacao}", "R_new_M3_sup"] - r.M3_sup)) for r in f2.itertuples())
chk.append(("V10R2-06", "IC M3 das diferenças F16c vs F16b (mesma semente, pesos gerados de outra forma): diferença máxima", round(float(m3), 4)))
pd.DataFrame(chk, columns=["item", "verificacao", "resultado"]).to_csv(f"{OUT}/verificacoes.csv", index=False)
print(pd.DataFrame(chk, columns=["item", "verificacao", "resultado"]).to_string(index=False)); print(cb.round(3).to_string(index=False))
print(RS.round(3).to_string(index=False))
