#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F15e_bootstrap_cobertura.py

File type:
    Script

Purpose:
    Re-evaluates the bootstrap of the human P@100 (coverage and intervals) without changing the data.

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
    - See docs/file_level_documentation.md (entry F15e_bootstrap_cobertura.py).

Outputs:
    - See docs/file_level_documentation.md (entry F15e_bootstrap_cobertura.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F15e_bootstrap_cobertura.py

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
OUT = sys.argv[1]; NSIM = int(sys.argv[2]) if len(sys.argv) > 2 else 500; BS = int(sys.argv[3]) if len(sys.argv) > 3 else 400
os.makedirs(OUT, exist_ok=True)
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; V = f"{R}/F14_complementares_01A/validacao_P100"
P = pd.read_csv(f"{V}/amostra_posicoes_NAO_ENVIAR.csv")
J = pd.read_csv(f"{R}/F7_painel_llm/analise/J_notas_3llm.csv").set_index("jid").consenso
H = pd.read_csv(f"{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv").set_index("jid").H_med
L = pd.read_csv(f"{R}/F7_painel_llm/listas_p100_com_jid.csv"); L = L[L.lista.isin(P.lista.unique()) & (L["rank"] <= 10)]
DOM = ["microarranjos", "radiomica", "metamateriais"]; EST = ["A", "B", "C"]; CMP = [("A", "B"), ("A", "C"), ("C", "B")]
P["skey"] = P.dominio + "|" + P.lista + "|" + P.faixa
strata = P.drop_duplicates("skey")[["skey", "dominio", "lista", "estrategia", "faixa", "N_estrato", "n_estrato"]].reset_index(drop=True)
sidx = {k: i for i, k in enumerate(strata.skey)}; NS = len(strata); P["s"] = P.skey.map(sidx)
assert NS == 135 and (P.groupby("s").size().values == strata.N_estrato.values).all()
lists = strata.drop_duplicates(["dominio", "lista"])[["dominio", "lista", "estrategia"]].reset_index(drop=True); NL = len(lists)
lidx = {(d, l): i for i, (d, l) in enumerate(zip(lists.dominio, lists.lista))}
s2l = np.array([lidx[(d, l)] for d, l in zip(strata.dominio, strata.lista)]); Ns = strata.N_estrato.to_numpy(float); ns = strata.n_estrato.to_numpy()
targets, A = [], []
for d in DOM:
    for e in EST:
        v = np.zeros(NL); v[[i for i, (dd, ee) in enumerate(zip(lists.dominio, lists.estrategia)) if dd == d and ee == e]] = 1 / 5; targets.append(f"{d}|{e}"); A.append(v)
for d in DOM:
    for a, b in CMP:
        targets.append(f"{d}|{a}-{b}"); A.append(A[targets.index(f"{d}|{a}")] - A[targets.index(f"{d}|{b}")])
A = np.array(A)
def h10(score):
    v = np.zeros(NL)
    for (d, l), g in L.groupby(["dominio", "lista"]): v[lidx[(d, l)]] = (score.reindex(g.jid).to_numpy() >= 2).sum()
    return v
def est_from(Wy, W, h):
    p = Wy / W; tot = h + np.stack([(Ns * p)[..., s2l == i].sum(-1) for i in range(NL)], -1)
    return (tot / 100) @ A.T
def analitico(y, s):
    m = np.bincount(s, minlength=NS).astype(float); sy = np.bincount(s, y, minlength=NS); p = sy / m
    s2 = np.where(m > 1, m / (m - 1) * p * (1 - p), 0); vs = Ns ** 2 * (1 - m / Ns) * s2 / m
    vl = np.array([vs[s2l == i].sum() for i in range(NL)]) / 1e4
    return np.sqrt((A ** 2) @ vl)
def boot_weights(metodo, s, doc, dom, B, rng):
    """Devolve matriz (B, n_pos) de pesos por posição."""
    n = len(s)
    if metodo == "doc-cond":
        W = np.zeros((B, n))
        for d in np.unique(dom):
            idx = np.where(dom == d)[0]; u, inv = np.unique(doc[idx], return_inverse=True)
            cnt = rng.multinomial(len(u), np.full(len(u), 1 / len(u)), size=B)
            W[:, idx] = cnt[:, inv]
        return W
    if metodo == "doc-bayes":
        u, inv = np.unique(doc, return_inverse=True); return rng.exponential(1.0, size=(B, len(u)))[:, inv]
    if metodo == "rao-wu":
        W = np.zeros((B, n))
        for k in np.unique(s):
            idx = np.where(s == k)[0]; nh = len(idx); mh = nh - 1; f = nh / Ns[k]; lam = np.sqrt(mh * (1 - f) / (nh - 1))
            r = rng.multinomial(mh, np.full(nh, 1 / nh), size=B)
            W[:, idx] = (1 - lam) + lam * (nh / mh) * r
        return W
def boot_ci(metodo, y, s, doc, dom, h, B, rng, devolver=False):
    W = boot_weights(metodo, s, doc, dom, B, rng)
    S1 = np.zeros((NS, len(s))); S1[s, np.arange(len(s))] = 1
    Wy = (W * y) @ S1.T; Ws = W @ S1.T; vazio = (Ws == 0).any(1)
    with np.errstate(invalid="ignore", divide="ignore"): T = est_from(Wy, Ws, h)
    Tk = T[~vazio]; lo, hi = np.quantile(Tk, [0.025, 0.975], axis=0)
    return (lo, hi, int(vazio.sum()), T, vazio) if devolver else (lo, hi, int(vazio.sum()), T, vazio)
MET = ["analitico", "doc-cond", "doc-bayes", "rao-wu"]
yllm_all = (J.reindex(P.jid).to_numpy() >= 2).astype(float); hL = h10(J)
true_l = (hL + np.array([yllm_all[(P.lista == l) & (P.dominio == d)].sum() for d, l in zip(lists.dominio, lists.lista)])) / 100
truth = A @ true_l
rng = np.random.default_rng(20261113); rec = []; sel = []
grp = [np.where(P.s.to_numpy() == k)[0] for k in range(NS)]
for it in range(NSIM):
    pick = np.concatenate([rng.choice(g, ns[k], replace=False) for k, g in enumerate(grp)])
    y = yllm_all[pick]; s = P.s.to_numpy()[pick]; doc = P.jid.to_numpy()[pick]; dom = P.dominio.to_numpy()[pick]
    m = np.bincount(s, minlength=NS).astype(float); est = est_from(np.bincount(s, y, minlength=NS), m, hL)
    se = analitico(y, s); rec.append({"sim": it, "metodo": "analitico", **{f"cob|{t}": float(abs(est[i] - truth[i]) <= 1.96 * se[i]) for i, t in enumerate(targets)}, **{f"larg|{t}": 2 * 1.96 * se[i] for i, t in enumerate(targets)}})
    for me in MET[1:]:
        lo, hi, nv, T, vz = boot_ci(me, y, s, doc, dom, hL, BS, rng)
        rec.append({"sim": it, "metodo": me, "vazias": nv, **{f"cob|{t}": float(lo[i] <= truth[i] <= hi[i]) for i, t in enumerate(targets)}, **{f"larg|{t}": hi[i] - lo[i] for i, t in enumerate(targets)}})
        if me == "doc-cond" and nv > 0:
            sel.append({"sim": it, "excluidas": nv, "B": BS})
Rk = pd.DataFrame(rec); Rk.to_csv(f"{OUT}/A_cobertura_por_simulacao.csv", index=False)
cob = Rk.groupby("metodo")[[c for c in Rk if c.startswith("cob|")]].mean().T; cob.index = cob.index.str[4:]
lar = Rk.groupby("metodo")[[c for c in Rk if c.startswith("larg|")]].mean().T; lar.index = lar.index.str[5:]
tab = cob.add_prefix("cobertura_").join(lar.add_prefix("largura_")); tab["verdade_pseudo"] = truth; tab.round(4).to_csv(f"{OUT}/A_cobertura_resumo.csv")
print(f"Parte A: {NSIM} simulações, B={BS}"); print(tab.round(3).to_string())
print("cobertura média (18 alvos):", cob.mean().round(3).to_dict(), "| mínima:", cob.min().round(3).to_dict())
print("réplicas excluídas doc-cond por simulação (média):", round(Rk[Rk.metodo == "doc-cond"].vazias.mean(), 2), "de", BS)
S = P[P.sorteado].reset_index(drop=True); M = pd.read_csv(f"{V}/mapa_documentos_v2_NAO_ENVIAR.csv", keep_default_na=False)
NC = pd.read_csv(f"{V}/F15_resultados_20261112/controlo/notas_consolidadas.csv", keep_default_na=False, dtype=str)
nova = {j: float(n) for j, n, t in zip(NC.jid, NC.nota, NC.tipo) if t == "amostra" and n in ("0", "1", "2")}
yh = np.array([H[j] if r else nova[j] for j, r in zip(S.jid, S.ja_julgado_top10)], float); y = (yh >= 2).astype(float)
s = S.s.to_numpy(); doc = S.jid.to_numpy(); dom = S.dominio.to_numpy(); hH = h10(H)
m = np.bincount(s, minlength=NS).astype(float); est = est_from(np.bincount(s, y, minlength=NS), m, hH); se = analitico(y, s)
rows = {t: {"estimativa": est[i], "analitico_inf": est[i] - 1.96 * se[i], "analitico_sup": est[i] + 1.96 * se[i]} for i, t in enumerate(targets)}
for me, seed in [("doc-cond", 42), ("doc-bayes", 4242), ("rao-wu", 424242)]:
    lo, hi, nv, T, vz = boot_ci(me, y, s, doc, dom, hH, 2000, np.random.default_rng(seed))
    pd.DataFrame(T, columns=targets).assign(replica=np.arange(2000), excluida_estrato_vazio=vz).round(5).to_csv(f"{OUT}/B_replicas_{me}.csv", index=False)
    for i, t in enumerate(targets): rows[t].update({f"{me}_inf": lo[i], f"{me}_sup": hi[i], f"{me}_validas": 2000 - nv})
    if me == "doc-cond":
        Wd = boot_weights("doc-cond", s, doc, dom, 2000, np.random.default_rng(42))
        ndist = (Wd > 0).sum(1)
        print("doc-cond real: réplicas excluídas", nv, "| posições com peso>0 (média) retidas vs excluídas:", round(ndist[~vz].mean(), 1), round(ndist[vz].mean(), 1))
Bt = pd.DataFrame(rows).T; Bt.index.name = "alvo"; Bt.round(4).to_csv(f"{OUT}/B_intervalos_dados_reais.csv")
pub = pd.read_csv(f"{V}/F15d_reproducao_20261113/V7_05_bootstrap_semente42_corrigido.csv").set_index("alvo")
Bt["publicado_v8_inf"] = pub.reindex(Bt.index)["inf"].values; Bt["publicado_v8_sup"] = pub.reindex(Bt.index)["sup"].values; Bt.round(4).to_csv(f"{OUT}/B_intervalos_dados_reais.csv")
print(Bt.round(3).to_string())
