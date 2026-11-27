#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F16_replicacao_portatil.py

File type:
    Script

Purpose:
    Portable version of F16 (paths given as command-line arguments).

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
    - See docs/file_level_documentation.md (entry F16_replicacao_portatil.py).

Outputs:
    - See docs/file_level_documentation.md (entry F16_replicacao_portatil.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F16_replicacao_portatil.py

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

import os, sys, re, json, numpy as np, pandas as pd
PKG, D, FASE = sys.argv[1], sys.argv[2], sys.argv[3]
M = pd.read_csv(f"{PKG}/desenho/mapa_documentos_v2_NAO_ENVIAR.csv", keep_default_na=False)
OLD = pd.read_csv(f"{PKG}/referencias/notas_R_old_consolidadas.csv", keep_default_na=False, dtype=str)
pref = {"MJ": "microarranjos", "EJ": "metamateriais", "RJ": "radiomica"}
rows = []
for i, l in enumerate(open(f"{PKG}/recebido/notas_replicacao_coladas_20261113_1245.txt", encoding="utf8"), 1):
    if l.startswith("#"): continue
    m = re.match(r"^([A-Z]{2}\d{4})\t(\S*)\s*$", l.rstrip("\n"))
    rows.append({"linha": i, "doc_id": m.group(1) if m else None, "nota": m.group(2) if m else None, "bruto": l.rstrip("\n")})
X = pd.DataFrame(rows)
if FASE == "a":
    os.makedirs(f"{D}/controlo", exist_ok=True); prob = []
    for _, r in X[X.doc_id.isna()].iterrows(): prob.append({"tipo": "linha ilegível", "doc_id": "", "detalhe": f"linha {r.linha}: {r.bruto[:40]}"})
    X = X.dropna(subset=["doc_id"]); res = []
    for p, d in pref.items():
        x = X[X.doc_id.str.startswith(p)]; mapa = set(M[M.dominio == d].doc_id); ids = list(x.doc_id)
        dup = sorted({a for a in ids if ids.count(a) > 1}); fora = sorted(set(ids) - mapa); falta = sorted(mapa - set(ids))
        inval = x[~x.nota.isin(["0", "1", "2", "NA"])]
        for a in dup: prob.append({"tipo": "duplicado", "doc_id": a, "detalhe": ";".join(x[x.doc_id == a].nota)})
        for a in fora: prob.append({"tipo": "fora do mapa", "doc_id": a, "detalhe": ""})
        for a in falta: prob.append({"tipo": "em falta", "doc_id": a, "detalhe": ""})
        for _, r in inval.iterrows(): prob.append({"tipo": "nota inválida", "doc_id": r.doc_id, "detalhe": r.nota})
        ordem_ficha = list(OLD[OLD.dominio == d].doc_id)
        res.append({"dominio": d, "linhas": len(x), "esperadas": len(mapa), "validas_0_1_2": int(x.nota.isin(["0", "1", "2"]).sum()), "NA": int((x.nota == "NA").sum()),
                    "duplicados": len(dup), "fora_mapa": len(fora), "em_falta": len(falta), "invalidas": len(inval),
                    "mesma_ordem_da_ficha": ids == ordem_ficha, "amostra": int(M[(M.dominio == d) & M.doc_id.isin(ids)].tipo.eq("amostra").sum()),
                    "calibracao": int(M[(M.dominio == d) & M.doc_id.isin(ids)].tipo.eq("calibracao").sum())})
    pd.DataFrame(res).to_csv(f"{D}/controlo/controlo_replicacao.csv", index=False); pd.DataFrame(prob, columns=["tipo", "doc_id", "detalhe"]).to_csv(f"{D}/controlo/controlo_problemas.csv", index=False)
    j = M.set_index("doc_id"); X["dominio"] = X.doc_id.str[:2].map(pref); X["jid"] = X.doc_id.map(j.jid); X["tipo"] = X.doc_id.map(j.tipo); X["sem_resumo"] = X.doc_id.map(j.sem_resumo)
    X[["dominio", "doc_id", "jid", "tipo", "sem_resumo", "nota", "linha"]].to_csv(f"{D}/controlo/notas_replicacao_consolidadas.csv", index=False)
    print(pd.DataFrame(res).to_string(index=False)); print("problemas:", len(prob)); sys.exit()

OUT = f"{D}/analise"; os.makedirs(OUT, exist_ok=True)
NEW = pd.read_csv(f"{D}/controlo/notas_replicacao_consolidadas.csv", keep_default_na=False, dtype=str)
C = NEW.merge(OLD[["doc_id", "nota"]].rename(columns={"nota": "nota_old"}), on="doc_id").rename(columns={"nota": "nota_new"})
assert len(C) == 902
H = pd.read_csv(f"{PKG}/referencias/notas_humanos_LLM.csv").set_index("jid").H_med
J = pd.read_csv(f"{PKG}/referencias/J_notas_3llm.csv").set_index("jid").consenso
def kw(a, b, k=3):
    a = np.asarray(a, int); b = np.asarray(b, int); O = np.zeros((k, k))
    for i, j in zip(a, b): O[i, j] += 1
    E = np.outer(O.sum(1), O.sum(0)) / O.sum(); W = np.array([[(i - j) ** 2 for j in range(k)] for i in range(k)]) / (k - 1) ** 2
    return 1 - (W * O).sum() / (W * E).sum()
def alpha_ord2(a, b):
    v = np.concatenate([a, b]).astype(int); n = np.bincount(v, minlength=3).astype(float); N = n.sum()
    cum = np.cumsum(n)
    def d(c, k):
        lo, hi = min(c, k), max(c, k); s = n[lo:hi + 1].sum() - (n[lo] + n[hi]) / 2; return s ** 2
    Do = np.mean([d(x, y) for x, y in zip(a, b)])
    De = sum(n[c] * n[k] * d(c, k) for c in range(3) for k in range(3)) / (N * (N - 1))
    return 1 - Do / De
A_ = []; mats = []
v = C[C.nota_new.isin(["0", "1", "2"]) & C.nota_old.isin(["0", "1", "2"])].copy(); v["n"] = v.nota_new.astype(int); v["o"] = v.nota_old.astype(int)
for (d, t), g in v.groupby(["dominio", "tipo"]):
    A_.append({"dominio": d, "tipo": t, "n": len(g), "iguais": (g.n == g.o).mean(), "kw": kw(g.o, g.n), "alfa_ord": alpha_ord2(g.o.values, g.n.values),
               "new_acima": (g.n > g.o).mean(), "new_abaixo": (g.n < g.o).mean(), "dif_media_new_menos_old": (g.n - g.o).mean(),
               "estrita_old_nao_new": ((g.o == 2) & (g.n < 2)).sum(), "estrita_new_nao_old": ((g.n == 2) & (g.o < 2)).sum(),
               "inversoes_0_2": ((abs(g.n - g.o)) == 2).sum(), "prop_2_old": (g.o == 2).mean(), "prop_2_new": (g.n == 2).mean()})
    m = pd.crosstab(g.o, g.n).reindex(index=[0, 1, 2], columns=[0, 1, 2], fill_value=0); m.index = [f"old{i}" for i in m.index]; m.columns = [f"new{i}" for i in m.columns]
    mats.append(m.assign(dominio=d, tipo=t))
pd.DataFrame(A_).round(4).to_csv(f"{OUT}/A_comparacao_old_new.csv", index=False); pd.concat(mats).to_csv(f"{OUT}/A_matrizes_old_new.csv")
B_ = []
for d, g in v[v.tipo == "calibracao"].groupby("dominio"):
    r = H.reindex(g.jid).to_numpy().astype(int)
    for ref, col in [("new", "n"), ("old", "o")]:
        h = g[col].to_numpy(); k = kw(r, h)
        B_.append({"dominio": d, "referencia": ref, "n": len(g), "kw_vs_mediana_1a_fase": k, "iguais": (h == r).mean(), "dif_media": (h - r).mean(), "criterio": "substituir" if k < 0.2 else ("ressalva" if k < 0.4 else "ok")})
pd.DataFrame(B_).round(4).to_csv(f"{OUT}/B_calibracao.csv", index=False)
P = pd.read_csv(f"{PKG}/desenho/amostra_posicoes_NAO_ENVIAR.csv"); S = P[P.sorteado].reset_index(drop=True); S["reuso"] = S.ja_julgado_top10.astype(bool)
L = pd.read_csv(f"{PKG}/referencias/listas_p100_com_jid.csv"); L = L[L.lista.isin(S.lista.unique()) & (L["rank"] <= 10)]
h10h = {k: float((H.reindex(g.jid).to_numpy() >= 2).sum()) for k, g in L.groupby(["dominio", "lista"])}
h10l = {k: float((J.reindex(g.jid).to_numpy() >= 2).sum()) for k, g in L.groupby(["dominio", "lista"])}
semres = set(M[M.sem_resumo.astype(str) == "True"].jid)
def notas(col, na=None):
    d = {}
    for j, t, x in zip(C.jid, C.tipo, C[col]):
        if t == "amostra": d[j] = float(x) if x in ("0", "1", "2") else (na if (x == "NA" and na is not None) else np.nan)
    return np.array([H[j] if r else d.get(j, np.nan) for j, r in zip(S.jid, S.reuso)], float)
def rel(y): return np.where(np.isnan(y), np.nan, (y >= 2).astype(float))
DOMS = ["microarranjos", "radiomica", "metamateriais"]
def lista_est(relv, h10, w=None):
    w = np.ones(len(S)) if w is None else w; res = {}
    for (d, l), g in S.groupby(["dominio", "lista"]):
        tot = h10[(d, l)]; var = 0.0
        for f, gg in g.groupby("faixa"):
            idx = gg.index.to_numpy(); k = ~np.isnan(relv[idx]); ww = w[idx][k]; yy = relv[idx][k]; Nf = gg.N_estrato.iloc[0]; m = ww.sum()
            p = (ww * yy).sum() / m; tot += Nf * p; s2 = m / (m - 1) * p * (1 - p) if m > 1 else 0.0; var += Nf ** 2 * (1 - min(m, Nf) / Nf) * s2 / m
        res[(d, l)] = (tot / 100, var / 1e4, g.estrategia.iloc[0])
    df = pd.DataFrame([{"dominio": d, "lista": l, "estrategia": e, "P": p, "v": vv} for (d, l), (p, vv, e) in res.items()])
    return df.groupby(["dominio", "estrategia"]).agg(P=("P", "mean"), v=("v", lambda s: s.sum() / len(s) ** 2))
def difs(st):
    o = {}
    for d in DOMS:
        for a, b in [("A", "B"), ("A", "C"), ("C", "B")]:
            x = st.loc[(d, a), "P"] - st.loc[(d, b), "P"]; se = np.sqrt(st.loc[(d, a), "v"] + st.loc[(d, b), "v"]); o[(d, f"{a}-{b}")] = (x, x - 1.96 * se, x + 1.96 * se)
    return o
def pareado(r1, r2, h1, h2):
    out = {}; dd = r1 - r2
    for (d, e), g in S.assign(dd=dd).groupby(["dominio", "estrategia"]):
        tot, var, nl = 0.0, 0.0, g.lista.nunique()
        for l, gl in g.groupby("lista"):
            tot += h1[(d, l)] - h2[(d, l)]
            for f, gg in gl.groupby("faixa"):
                z = gg.dd.dropna().to_numpy(); m = len(z); Nf = gg.N_estrato.iloc[0]; tot += Nf * z.mean(); var += Nf ** 2 * (1 - m / Nf) * (z.var(ddof=1) if m > 1 else 0) / m
        x = tot / 100 / nl; se = np.sqrt(var / 1e4 / nl ** 2); out[(d, e)] = (x, x - 1.96 * se, x + 1.96 * se)
    return out
def bayes(relv, h10, seed=4242, B=2000):
    rng = np.random.default_rng(seed); u, inv = np.unique(S.jid, return_inverse=True); reps = []
    for _ in range(B):
        w = rng.exponential(1.0, len(u))[inv]; st = lista_est(relv, h10, w); dd = difs(st)
        reps.append({**{f"{d}|{e}": st.loc[(d, e), "P"] for d, e in st.index}, **{f"{d}|{c}": x[0] for (d, c), x in dd.items()}})
    return pd.DataFrame(reps)
r_new = rel(notas("nota_new")); r_old = rel(notas("nota_old")); r_llm = (J.reindex(S.jid).to_numpy() >= 2).astype(float)
St_new = lista_est(r_new, h10h); St_old = lista_est(r_old, h10h); St_llm = lista_est(r_llm, h10l)
D_new = difs(St_new); D_old = difs(St_old)
Bn = bayes(r_new, h10h); Bn.round(5).to_csv(f"{OUT}/C_replicas_M3_R_new.csv", index=False)
hn_old = pareado(r_new, r_old, h10h, h10h); hn_llm = pareado(r_new, r_llm, h10h, h10l)
est = []
for d, e in St_new.index:
    k = (d, e); se = np.sqrt(St_new.loc[k, "v"])
    est.append({"dominio": d, "estrategia": e, "P100_R_new": St_new.loc[k, "P"], "M1_inf": St_new.loc[k, "P"] - 1.96 * se, "M1_sup": St_new.loc[k, "P"] + 1.96 * se,
                "M3_inf": Bn[f"{d}|{e}"].quantile(.025), "M3_sup": Bn[f"{d}|{e}"].quantile(.975), "P100_R_old": St_old.loc[k, "P"], "LLM_mesmas_posicoes": St_llm.loc[k, "P"],
                "new_menos_old": hn_old[k][0], "nmo_inf": hn_old[k][1], "nmo_sup": hn_old[k][2], "new_menos_LLM": hn_llm[k][0], "nml_inf": hn_llm[k][1], "nml_sup": hn_llm[k][2]})
pd.DataFrame(est).round(4).to_csv(f"{OUT}/C1_P100_estrategias.csv", index=False)
dif = []
for (d, c), x in D_new.items():
    dif.append({"dominio": d, "comparacao": c, "R_new": x[0], "M1_inf": x[1], "M1_sup": x[2], "M3_inf": Bn[f"{d}|{c}"].quantile(.025), "M3_sup": Bn[f"{d}|{c}"].quantile(.975),
                "R_old": D_old[(d, c)][0], "R_old_M1_inf": D_old[(d, c)][1], "R_old_M1_sup": D_old[(d, c)][2]})
DF = pd.DataFrame(dif); DF.round(4).to_csv(f"{OUT}/C1_P100_diferencas.csv", index=False)
c2 = []
for (d, e), g in S[~S.reuso].assign(y=r_new[~S.reuso.to_numpy()], yo=r_old[~S.reuso.to_numpy()]).groupby(["dominio", "estrategia"]):
    w = g.N_estrato / g.groupby(["lista", "faixa"]).jid.transform("size"); ok = ~g.y.isna()
    c2.append({"dominio": d, "estrategia": e, "posicoes": int(ok.sum()), "prop2_R_new_ponderada": (w[ok] * g.y[ok]).sum() / w[ok].sum(), "prop2_R_old_ponderada": (w[ok] * g.yo[ok]).sum() / w[ok].sum()})
pd.DataFrame(c2).round(4).to_csv(f"{OUT}/C2_restrita_documentos_novos.csv", index=False)
crit = []
for d in DOMS:
    ab, cb, ac = D_new[(d, "A-B")], D_new[(d, "C-B")], D_new[(d, "A-C")]
    crit.append({"dominio": d, "i_AB_CB_positivos_IC_sem_zero": bool(ab[1] > 0 and cb[1] > 0), "AC": round(ac[0], 4), "AC_IC": f"[{ac[1]:.4f}; {ac[2]:.4f}]",
                 "ii_AC_IC_inclui_zero": bool(ac[1] <= 0 <= ac[2]) if d != "radiomica" else None,
                 "iii_radiomica": (("positivo, IC exclui zero → frágil" if ac[1] > 0 else "IC inclui zero → não confirmada") if d == "radiomica" else None)})
llm_abaixo = sum(St_new.loc[k, "P"] < St_llm.loc[k, "P"] for k in St_new.index)
crit.append({"dominio": "todos", "iv_humano_abaixo_LLM": f"{llm_abaixo}/9"})
pd.DataFrame(crit).to_csv(f"{OUT}/E_estabilidade.csv", index=False)
sens = []
for nome, rr in [("sem_documentos_sem_resumo", np.where(S.jid.isin(semres), np.nan, r_new)),
                 ("referencia_ambas_nota2", np.where(np.isnan(r_new) | np.isnan(r_old), np.nan, r_new * r_old))]:
    st = lista_est(rr, h10h); dd = difs(st)
    for (d, c), x in dd.items(): sens.append({"tratamento": nome, "dominio": d, "alvo": c, "valor": x[0], "inf": x[1], "sup": x[2]})
if (C.nota_new == "NA").any():
    for na in (0.0, 2.0):
        st = lista_est(rel(notas("nota_new", na)), h10h); dd = difs(st)
        for (d, c), x in dd.items(): sens.append({"tratamento": f"NA={na:.0f}", "dominio": d, "alvo": c, "valor": x[0], "inf": x[1], "sup": x[2]})
pd.DataFrame(sens).round(4).to_csv(f"{OUT}/F_sensibilidade.csv", index=False)
print(pd.DataFrame(A_).round(3).to_string(index=False)); print(pd.DataFrame(B_).round(3).to_string(index=False))
print(pd.DataFrame(est).round(3).to_string(index=False)); print(DF.round(3).to_string(index=False)); print(pd.DataFrame(crit).to_string(index=False))
print(pd.DataFrame(c2).round(3).to_string(index=False)); print(pd.DataFrame(sens).round(3).to_string(index=False))
