#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F15b_analise_P100.py

File type:
    Script

Purpose:
    Pre-specified analysis of the human P@100 (stratified estimator, confidence intervals and comparison with the LLM judges).

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
    - See docs/file_level_documentation.md (entry F15b_analise_P100.py).

Outputs:
    - See docs/file_level_documentation.md (entry F15b_analise_P100.py).

Dependencies:
    - numpy
    - pandas
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F15b_analise_P100.py

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

import os, sys, json, numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score as ck
NOT, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; V = f"{R}/F14_complementares_01A/validacao_P100"
P = pd.read_csv(f"{V}/amostra_posicoes_NAO_ENVIAR.csv"); S = P[P.sorteado].copy()
L = pd.read_csv(f"{R}/F7_painel_llm/listas_p100_com_jid.csv"); L = L[L.lista.isin(P.lista.unique())]
J = pd.read_csv(f"{R}/F7_painel_llm/analise/J_notas_3llm.csv").set_index("jid").consenso
H = pd.read_csv(f"{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv").set_index("jid").H_med
N = pd.read_csv(NOT, keep_default_na=False, dtype={"nota": str}); M = pd.read_csv(f"{V}/mapa_documentos_v2_NAO_ENVIAR.csv", keep_default_na=False)
kw = lambda a, b: ck(a, b, weights="quadratic", labels=[0, 1, 2])
COL = "nota"
def ref_novos(trat):
    x = N[N.tipo == "amostra"].copy(); x["v"] = x[COL].map(lambda s: float(s) if s in ("0", "1", "2") else (trat if s == "NA" and trat is not None else np.nan))
    return x.groupby("jid").v.apply(lambda s: np.floor(s.dropna().median()) if s.notna().any() else np.nan)
def notas_posicao(trat=None, excluir_sem_resumo=False):
    rn = ref_novos(trat); y = np.where(S.ja_julgado_top10, H.reindex(S.jid).to_numpy(), rn.reindex(S.jid).to_numpy()).astype(float)
    if excluir_sem_resumo: y[S.jid.isin(M[M.sem_resumo.astype(str) == "True"].jid).to_numpy()] = np.nan
    return y
top10 = L[L["rank"] <= 10].assign(h=lambda t: (H.reindex(t.jid).to_numpy() >= 2).astype(float), l=lambda t: (J.reindex(t.jid).to_numpy() >= 2).astype(float))
H10 = top10.groupby(["dominio", "lista"]).h.sum(); L10 = top10.groupby(["dominio", "lista"]).l.sum()
def estimar(y, h10, peso=None):
    S2 = S.assign(y=(y >= 2).astype(float), ok=~np.isnan(y), w=1.0 if peso is None else peso); S2.loc[~S2.ok, "y"] = np.nan
    lst = []
    for (d, l, f), g in S2.groupby(["dominio", "lista", "faixa"]):
        g = g[g.ok]; Nf = int(g.N_estrato.iloc[0]) if len(g) else int(S2[(S2.lista == l) & (S2.faixa == f) & (S2.dominio == d)].N_estrato.iloc[0])
        m = g.w.sum(); p = (g.y * g.w).sum() / m if m > 0 else np.nan
        v = (1 - min(m, Nf) / Nf) * (m / (m - 1) * p * (1 - p) if m > 1 else 0) / max(m, 1)
        lst.append({"dominio": d, "lista": l, "estrategia": g.estrategia.iloc[0] if len(g) else S2[S2.lista == l].estrategia.iloc[0], "faixa": f, "N": Nf, "m": m, "p": p, "v": v})
    E = pd.DataFrame(lst); E["tot"] = E.N * E.p; E["vt"] = E.N ** 2 * E.v
    Lc = E.groupby(["dominio", "lista", "estrategia"]).agg(tot=("tot", "sum"), vt=("vt", "sum")).reset_index()
    Lc["P100"] = (Lc.apply(lambda r: h10.get((r.dominio, r.lista), 0), axis=1) + Lc.tot) / 100; Lc["var"] = Lc.vt / 100 ** 2
    Sg = Lc.groupby(["dominio", "estrategia"]).agg(P100=("P100", "mean"), var=("var", lambda v: v.sum() / 25)).reset_index()
    return Lc, Sg
def difs(Sg):
    out = []
    for d in sorted(Sg.dominio.unique()):
        g = Sg[Sg.dominio == d].set_index("estrategia")
        for a, b in [("A", "B"), ("A", "C"), ("C", "B")]:
            dif = g.loc[a, "P100"] - g.loc[b, "P100"]; se = np.sqrt(g.loc[a, "var"] + g.loc[b, "var"])
            out.append({"dominio": d, "comparacao": f"{a}-{b}", "diferenca": dif, "ic95_inf": dif - 1.96 * se, "ic95_sup": dif + 1.96 * se, "sustentada": (dif - 1.96 * se > 0) or (dif + 1.96 * se < 0)})
    return pd.DataFrame(out)
yh = notas_posicao(); yl = J.reindex(S.jid).to_numpy().astype(float)
Lh, Sh = estimar(yh, H10); Ll, Sl = estimar(yl, L10); Dh = difs(Sh); Dl = difs(Sl)
Sh["ic95_inf"] = Sh.P100 - 1.96 * np.sqrt(Sh["var"]); Sh["ic95_sup"] = Sh.P100 + 1.96 * np.sqrt(Sh["var"])
Sh = Sh.merge(Sl[["dominio", "estrategia", "P100"]].rename(columns={"P100": "P100_LLM_mesma_amostra"}), on=["dominio", "estrategia"])
full = pd.read_csv(f"{R}/F7_painel_llm/analise/J_metricas_cortes.csv"); full = full[(full.l == 100) & full.lista.isin(P.lista.unique())]
full["estrategia"] = full.lista.str.extract(r"_([ABC])(?:_|$)")[0]; Sh = Sh.merge(full.groupby(["dominio", "estrategia"]).P_estrita.mean().rename("P100_LLM_censo").reset_index(), on=["dominio", "estrategia"])
ok = ~np.isnan(yh); dpos = np.where(ok, (yh >= 2).astype(float) - (yl >= 2).astype(float), np.nan)
hl = []
for (d, e), g in S.assign(dd=dpos).groupby(["dominio", "estrategia"]):
    tot, var = 0.0, 0.0
    for (l, f), gg in g.groupby(["lista", "faixa"]):
        z = gg.dd.dropna(); m = len(z); Nf = gg.N_estrato.iloc[0]
        tot += Nf * z.mean() / 5 / 100; var += (Nf ** 2 * (1 - m / Nf) * z.var(ddof=1) / m) / 25 / 100 ** 2 if m > 1 else 0
    h10d = sum(H10.get((d, l), 0) - L10.get((d, l), 0) for l in g.lista.unique()) / 5 / 100
    hl.append({"dominio": d, "estrategia": e, "humano_menos_LLM": tot + h10d, "ic95_inf": tot + h10d - 1.96 * np.sqrt(var), "ic95_sup": tot + h10d + 1.96 * np.sqrt(var)})
HL = pd.DataFrame(hl)
nv = N[(N.tipo == "amostra") & N.nota.isin(["0", "1", "2"])].assign(h=lambda t: t.nota.astype(int), l=lambda t: J.reindex(t.jid).round().astype(int).to_numpy())
conc = [{"dominio": d, "n": len(g), "kw_humano_LLM": kw(g.h, g.l), "iguais": (g.h == g.l).mean(), "LLM_acima": (g.l > g.h).mean(), "LLM_abaixo": (g.l < g.h).mean(),
         "media_humano": g.h.mean(), "media_LLM": g.l.mean()} for d, g in nv.groupby("dominio")]
cal = N[(N.tipo == "calibracao") & N.nota.isin(["0", "1", "2"])].assign(h=lambda t: t.nota.astype(int), r=lambda t: H.reindex(t.jid).astype(int).to_numpy())
cb = []
for (d, a), g in cal.groupby(["dominio", "avaliador"]):
    k = kw(g.r, g.h); cb.append({"dominio": d, "avaliador": a, "n": len(g), "kw_vs_mediana_anterior": k, "iguais": (g.h == g.r).mean(), "diferenca_media": (g.h - g.r).mean(),
               "criterio": "substituir" if k < 0.20 else ("ressalva" if k < 0.40 else "ok")})
sens = []
if "nota_inicial" not in N: N["nota_inicial"] = N["nota"]
if "n_correcoes" not in N: N["n_correcoes"] = 0
N["nota_inicial"] = N["nota_inicial"].astype(str); N["n_correcoes"] = N["n_correcoes"].astype(int)
COL = "nota_inicial"; y_ini = notas_posicao(); COL = "nota"
pd.DataFrame([{"dominio": d, "tipo": t_, "documentos": len(g), "corrigidos": int((g.n_correcoes > 0).sum()),
               "correcoes_0_2": int(g.correcoes.astype(str).str.contains("0>2|2>0").sum()) if "correcoes" in g else 0}
              for (d, t_), g in N.groupby(["dominio", "tipo"])]).to_csv(f"{OUT}/correcoes_resumo.csv", index=False)
for nome, y in [("principal", yh), ("notas_iniciais_antes_da_revisao", y_ini), ("sem_documentos_sem_resumo", notas_posicao(excluir_sem_resumo=True)), ("NA=0", notas_posicao(0.0)), ("NA=2", notas_posicao(2.0))]:
    _, s = estimar(y, H10); dd = difs(s)
    for r in s.itertuples(): sens.append({"tratamento": nome, "dominio": r.dominio, "alvo": f"P@100 {r.estrategia}", "valor": r.P100})
    for r in dd.itertuples(): sens.append({"tratamento": nome, "dominio": r.dominio, "alvo": r.comparacao, "valor": r.diferenca, "ic95_inf": r.ic95_inf, "ic95_sup": r.ic95_sup, "sustentada": r.sustentada})
rng = np.random.default_rng(42); bs = []
docs = {d: S[S.dominio == d].jid.unique() for d in S.dominio.unique()}
for _ in range(2000):
    w = np.zeros(len(S))
    for d, u in docs.items():
        cnt = pd.Series(rng.choice(u, len(u))).value_counts(); w += np.where(S.dominio == d, S.jid.map(cnt).fillna(0).to_numpy(), 0)
    _, s = estimar(np.where(w > 0, yh, np.nan), H10, peso=np.where(w > 0, w, 1.0)); bs.append(pd.concat([s.set_index(["dominio", "estrategia"]).P100, difs(s).set_index(["dominio", "comparacao"]).diferenca]))
B = pd.DataFrame(bs); Bs = pd.DataFrame({"alvo": [f"{a}|{b}" for a, b in B.columns], "ep_bootstrap": B.std().values, "ic95_inf_bootstrap": B.quantile(0.025).values, "ic95_sup_bootstrap": B.quantile(0.975).values})
q = []
for d in sorted(Sh.dominio.unique()):
    g = Dh[Dh.dominio == d].set_index("comparacao"); gl = Dl[Dl.dominio == d].set_index("comparacao"); hd = HL[HL.dominio == d]
    sd = pd.DataFrame([x for x in sens if x["dominio"] == d and x["alvo"] in ("A-B", "C-B")])
    q += [{"dominio": d, "pergunta": "1 A > B (humano)", "resposta": f"{g.loc['A-B','diferenca']:+.3f} [{g.loc['A-B','ic95_inf']:+.3f}; {g.loc['A-B','ic95_sup']:+.3f}]", "sustentada": bool(g.loc["A-B", "sustentada"] and g.loc["A-B", "diferenca"] > 0)},
          {"dominio": d, "pergunta": "2 C > B (humano)", "resposta": f"{g.loc['C-B','diferenca']:+.3f} [{g.loc['C-B','ic95_inf']:+.3f}; {g.loc['C-B','ic95_sup']:+.3f}]", "sustentada": bool(g.loc["C-B", "sustentada"] and g.loc["C-B", "diferenca"] > 0)},
          {"dominio": d, "pergunta": "3 A − C humano vs LLM", "resposta": f"humano {g.loc['A-C','diferenca']:+.3f} [{g.loc['A-C','ic95_inf']:+.3f}; {g.loc['A-C','ic95_sup']:+.3f}]; LLM {gl.loc['A-C','diferenca']:+.3f}", "sustentada": bool(g.loc["A-C", "sustentada"])},
          {"dominio": d, "pergunta": "6 LLM mais generosos (humano − LLM)", "resposta": "; ".join(f"{r.estrategia} {r.humano_menos_LLM:+.3f} [{r.ic95_inf:+.3f}; {r.ic95_sup:+.3f}]" for r in hd.itertuples()), "sustentada": bool((hd.ic95_sup < 0).all())},
          {"dominio": d, "pergunta": "7 robustez a NA/sem resumo", "resposta": "; ".join(f"{r.tratamento} {r.alvo} {r.valor:+.3f}" for r in sd.itertuples()), "sustentada": bool(sd.sustentada.all() and (sd.valor > 0).all())}]
Dh["diferenca_LLM_mesma_amostra"] = Dl.diferenca.values
q.append({"dominio": "todos", "pergunta": "4 variação entre domínios (A−B)", "resposta": "; ".join(f"{r.dominio} {r.diferenca:+.3f}" for r in Dh[Dh.comparacao == "A-B"].itertuples()), "sustentada": None})
q.append({"dominio": "todos", "pergunta": "5 IC sustentam diferenças", "resposta": "; ".join(f"{r.dominio} {r.comparacao}: {'sim' if r.sustentada else 'não'}" for r in Dh.itertuples()), "sustentada": None})
for nm, df in [("P100_estrategias", Sh), ("P100_diferencas", Dh), ("P100_listas", Lh), ("humano_menos_LLM", HL), ("humano_vs_LLM_concordancia", pd.DataFrame(conc)),
               ("calibracao", pd.DataFrame(cb)), ("sensibilidade", pd.DataFrame(sens)), ("bootstrap", Bs), ("perguntas_item8", pd.DataFrame(q))]:
    df.round(4).to_csv(f"{OUT}/{nm}.csv", index=False)
json.dump({"n_posicoes": int(len(S)), "posicoes_com_nota": int(ok.sum()), "notas_avaliadores": N.groupby(["dominio", "avaliador"]).size().to_dict().__repr__()}, open(f"{OUT}/resumo.json", "w"), indent=1)
print(Sh.round(3).to_string(index=False)); print(Dh.round(3).to_string(index=False)); print(pd.DataFrame(cb).round(3).to_string(index=False)); print(pd.DataFrame(q).to_string(index=False))
