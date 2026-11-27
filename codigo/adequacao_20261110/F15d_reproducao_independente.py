#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F15d_reproducao_independente.py

File type:
    Script

Purpose:
    Independent reproduction of the human P@100 validation (calibration, bootstrap and differences).

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
    - See docs/file_level_documentation.md (entry F15d_reproducao_independente.py).

Outputs:
    - See docs/file_level_documentation.md (entry F15d_reproducao_independente.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F15d_reproducao_independente.py

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

import os, sys, re, json, zipfile, warnings, numpy as np, pandas as pd
warnings.filterwarnings("ignore", category=RuntimeWarning)
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; V = f"{R}/F14_complementares_01A/validacao_P100"
F15 = f"{V}/F15_resultados_20261112"; REC = f"{V}/recebido_P100_20261112"; NU = f"{V}/recebido_20261112_nao_usado"
log = []
def reg(item, verificacao, resultado, ok): log.append({"item": item, "verificacao": verificacao, "resultado": str(resultado), "ok": bool(ok)})

def ler_txt(f):
    out = []
    for i, l in enumerate(open(f, encoding="utf8"), 1):
        m = re.match(r"^\s*([A-Z]{2}\d{4})\s+(\S*)\s*$", l)
        if m: out.append((m.group(1), m.group(2), i))
    return out
c2251 = ler_txt(f"{REC}/notas_P100_coladas_20261112_2251.txt"); rjc = ler_txt(f"{REC}/RJ_completo_311_20261112_2325.txt")
rjr = ler_txt(f"{REC}/rj_restante_colado_20261112_2325.txt"); rjf = ler_txt(f"{REC}/rj_continuacao_colada_20261112_2300.txt")
M = pd.read_csv(f"{V}/mapa_documentos_v2_NAO_ENVIAR.csv", keep_default_na=False)
pref = {"microarranjos": "MJ", "metamateriais": "EJ", "radiomica": "RJ"}
fonte = {}
for d, p in pref.items():
    lst = [(a, b) for a, b, _ in (rjc if p == "RJ" else c2251) if a.startswith(p) and b != ""]
    ids = [a for a, _ in lst]; dic = dict(lst); mapa_ids = set(M[M.dominio == d].doc_id)
    reg("V7-01", f"{d}: entradas com nota na fonte primária", len(lst), True)
    reg("V7-01", f"{d}: identificadores repetidos na fonte", len(ids) - len(set(ids)), len(ids) == len(set(ids)))
    reg("V7-01", f"{d}: identificadores fora do mapa / do mapa sem nota", f"{len(set(ids) - mapa_ids)} / {len(mapa_ids - set(ids))}", set(ids) == mapa_ids)
    reg("V7-01", f"{d}: valores fora de {{0,1,2,NA}}", sum(v not in ("0", "1", "2", "NA") for v in dic.values()), all(v in ("0", "1", "2", "NA") for v in dic.values()))
    fonte[d] = dic
ini = {a: b for a, b, _ in c2251 if a.startswith("RJ") and b != ""}
conf = sum(fonte["radiomica"].get(a) != b for a, b in ini.items())
reg("V7-01", "radiômica: notas das 154 iniciais (22:51) iguais no ficheiro completo", f"{len(ini)} iniciais; {conf} diferentes", conf == 0)
rest = {a: b for a, b, _ in rjr}
reg("V7-01", "radiômica: completo = iniciais ∪ restante (23:25), sem sobreposição em conflito",
    f"{len(ini)}+{len(rest)}; sobrepostos {len(set(ini) & set(rest))}", set(ini) | set(rest) == set(fonte["radiomica"]) and all(fonte["radiomica"][a] == b for a, b in rest.items()))
def ler_xlsx(f):
    z = zipfile.ZipFile(f); ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        ss = [re.sub(r"<[^>]+>", "", s) for s in re.findall(r"<si>(.*?)</si>", z.read("xl/sharedStrings.xml").decode("utf8"), re.S)]
    x = z.read("xl/worksheets/sheet1.xml").decode("utf8"); rows = []
    for r in re.findall(r"<row[^>]*>(.*?)</row>", x, re.S):
        cel = {}
        for ref, attrs, body in re.findall(r'<c r="([A-Z]+)\d+"([^>]*)>(.*?)</c>', r, re.S):
            v = re.search(r"<v>(.*?)</v>", body, re.S); t = re.search(r"<t[^>]*>(.*?)</t>", body, re.S)
            val = ss[int(v.group(1))] if v and 't="s"' in attrs else (v.group(1) if v else (t.group(1) if t else ""))
            cel[ref] = val
        rows.append(cel)
    h = rows[0]; cols = sorted(h, key=lambda c: (len(c), c))
    return pd.DataFrame([{h[c]: r.get(c, "") for c in cols} for r in rows[1:]])
ficha = {"microarranjos": "Microarranjos_Y", "metamateriais": "Metamateriais_Z", "radiomica": "Radiomica_X"}
NC = pd.read_csv(f"{F15}/controlo/notas_consolidadas.csv", keep_default_na=False, dtype=str)
for d, nm in ficha.items():
    x = ler_xlsx(f"{F15}/controlo/originais/Folha_P100_{nm}.xlsx"); e = ler_xlsx(f"{V}/envio_P01B2/Folha_P100_{nm}.xlsx")
    notas = dict(zip(x.doc_id, x.relevancia_0_1_2_ou_NA.astype(str)))
    reg("V7-01", f"{d}: ficha montada = fonte primária (doc_id e nota)", sum(notas.get(a) != b for a, b in fonte[d].items()), notas == fonte[d])
    mesmos = all((x[c].values == e[c].values).all() for c in e.columns if c not in ("relevancia_0_1_2_ou_NA", "comentario"))
    reg("V7-01", f"{d}: ficha montada = ficha enviada (ordem, títulos, resumos)", mesmos, mesmos)
    nc = NC[NC.dominio == d]; dif = sum(dict(zip(nc.doc_id, nc.nota)).get(a) != b for a, b in fonte[d].items())
    reg("V7-01", f"{d}: base consolidada (F15a) = fonte primária", f"{len(nc)} linhas; {dif} diferenças", dif == 0 and len(nc) == len(fonte[d]))
todos_ids = set(M.doc_id); pool = pd.read_csv(f"{R}/F8_julgamento/pool_mapa_NAO_ENVIAR.csv", keep_default_na=False)
corp_tit = set(pool.titulo.str.lower().str.strip()) | set(M.titulo.str.lower().str.strip())
ra = []
for l in open(f"{NU}/notas_coladas_alunos_20261112.txt", encoding="utf8"):
    m = re.match(r"^(RA\d{4})\s+(\S+)\s*\|\s*(.*)$", l.strip())
    if m: ra.append({"id": m.group(1), "nota": m.group(2), "titulo": m.group(3)})
RA = pd.DataFrame(ra); pm = pool.set_index("doc_id")
RA["id_existe_1a_fase"] = RA.id.isin(pm.index); RA["titulo_no_mapa_1a_fase_para_esse_id"] = RA.id.map(lambda i: pm.titulo.get(i, ""))
RA["titulo_coincide"] = [a.lower().strip() == b.lower().strip() for a, b in zip(RA.titulo, RA.titulo_no_mapa_1a_fase_para_esse_id)]
RA["titulo_existe_em_algum_corpus_julgado"] = RA.titulo.str.lower().str.strip().isin(corp_tit)
RA["titulo_em_alguma_lista_P100"] = RA.titulo.str.lower().str.strip().isin(set(pd.read_csv(f"{R}/F7_painel_llm/listas_p100_com_jid.csv").title.astype(str).str.lower().str.strip()))
RA["na_base_final"] = RA.id.isin(NC.doc_id)
RA.to_csv(f"{OUT}/V7_02_radiomica_8_registos.csv", index=False)
reg("V7-02", "8 registos RA: algum na base final?", int(RA.na_base_final.sum()), RA.na_base_final.sum() == 0)
reg("V7-02", "8 registos RA: títulos presentes em algum corpus julgado/listas", f"{int(RA.titulo_existe_em_algum_corpus_julgado.sum())} / {int(RA.titulo_em_alguma_lista_P100.sum())}", True)
F = pd.DataFrame([{"id": a, "nota": b, "linha": i} for a, b, i in rjf])
F["id_na_ficha_RJ"] = F.id.isin(fonte["radiomica"]); F["nota_igual_final"] = [fonte["radiomica"].get(a) == b for a, b in zip(F.id, F.nota)]
p1 = {}
for f in ["notas_coladas_alunos_20261112.txt", "notas_conferidas_20261112_2104.txt"]:
    for a, b, _ in ler_txt(f"{NU}/{f}"):
        if a[:2] in ("ME", "MI"): p1.setdefault(int(a[2:]), set()).add(b)
F["numero_coincide_com_ME_MI_1a_fase_mesma_nota"] = [b in p1.get(int(a[2:]), set()) for a, b in zip(F.id, F.nota)]
F["na_base_final_com_esta_nota_por_esta_entrega"] = False
F.to_csv(f"{OUT}/V7_02_RJ_continuacao_rejeitada.csv", index=False)
reg("V7-02", "continuação RJ rejeitada (23:00): entradas; IDs inexistentes; números = ME/MI 1.ª fase com a mesma nota",
    f"{len(F)}; {int((~F.id_na_ficha_RJ).sum())}; {int(F.numero_coincide_com_ME_MI_1a_fase_mesma_nota.sum())}", True)
reg("V7-02", "base final de radiômica proveniente só de 22:51 (154) + 23:25 (157)", "ver item V7-01", True)
P = pd.read_csv(f"{V}/amostra_posicoes_NAO_ENVIAR.csv"); S = P[P.sorteado.astype(str) == "True"].reset_index(drop=True)
S["reuso"] = S.ja_julgado_top10.astype(str) == "True"
est = S.groupby(["dominio", "lista", "faixa"]).size()
reg("V7-05.1", "posições sorteadas / estratos / n por estrato", f"{len(S)} / {len(est)} / {sorted(set(est))}", len(S) == 1080 and len(est) == 135 and set(est) == {8})
reg("V7-05.2", "documentos distintos / novos / reutilizados", f"{S.jid.nunique()} / {S[~S.reuso].jid.nunique()} / {S[S.reuso].jid.nunique()}",
    (S.jid.nunique(), S[~S.reuso].jid.nunique(), S[S.reuso].jid.nunique()) == (921, 812, 109))
am = M[M.tipo == "amostra"]
reg("V7-05.2", "mapa (amostra) = documentos novos sorteados, por domínio", all(set(am[am.dominio == d].jid) == set(S[(S.dominio == d) & ~S.reuso].jid) for d in pref), all(set(am[am.dominio == d].jid) == set(S[(S.dominio == d) & ~S.reuso].jid) for d in pref))
pi_ok = np.allclose(S.pi, S.n_estrato / S.N_estrato) and np.allclose(S.peso, 1 / S.pi)
reg("V7-05.3", "π = n/N e peso = 1/π em todas as posições", pi_ok, pi_ok)
Hm = pd.read_csv(f"{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv")
H = Hm.set_index("jid").H_med; J = pd.read_csv(f"{R}/F7_painel_llm/analise/J_notas_3llm.csv").set_index("jid").consenso
doc2jid = dict(zip(M.doc_id, M.jid)); tipo = dict(zip(M.doc_id, M.tipo)); semres = set(M[M.sem_resumo.astype(str) == "True"].jid)
nova = {}
for d in pref:
    for a, b in fonte[d].items():
        if tipo[a] == "amostra": nova[doc2jid[a]] = np.nan if b == "NA" else float(b)
yh = np.array([H[j] if r else nova.get(j, np.nan) for j, r in zip(S.jid, S.reuso)], float)
yl = J.reindex(S.jid).to_numpy(float)
reg("V7-05", "posições sem nota humana", int(np.isnan(yh).sum()), np.isnan(yh).sum() == 0)
L = pd.read_csv(f"{R}/F7_painel_llm/listas_p100_com_jid.csv"); L = L[L.lista.isin(S.lista.unique()) & (L["rank"] <= 10)]
h10h = {k: float((H.reindex(g.jid).to_numpy() >= 2).sum()) for k, g in L.groupby(["dominio", "lista"])}
h10l = {k: float((J.reindex(g.jid).to_numpy() >= 2).sum()) for k, g in L.groupby(["dominio", "lista"])}
reg("V7-05", "top-10: listas com 10 posições e nota humana em todas", f"{len(h10h)} listas", all(len(g) == 10 and H.reindex(g.jid).notna().all() for _, g in L.groupby(["dominio", "lista"])))
def lista_est(rel, h10, w=None):
    w = np.ones(len(S)) if w is None else w; res = {}; zeros = []
    for (d, l), g in S.groupby(["dominio", "lista"]):
        tot = h10[(d, l)]; var = 0.0
        for f, gg in g.groupby("faixa"):
            idx = gg.index.to_numpy(); k = ~np.isnan(rel[idx]) & (w[idx] > 0); ww = w[idx][k]; yy = rel[idx][k]; Nf = gg.N_estrato.iloc[0]
            m = ww.sum()
            if m == 0: zeros.append((d, l, f, "vazio")); tot = np.nan; continue
            p = (ww * yy).sum() / m; tot += Nf * p
            s2 = m / (m - 1) * p * (1 - p) if m > 1 else 0.0; var += Nf ** 2 * (1 - min(m, Nf) / Nf) * s2 / m
            if s2 == 0: zeros.append((d, l, f))
        res[(d, l)] = (tot / 100, var / 1e4, g.estrategia.iloc[0])
    return res, zeros
def agrega(res):
    df = pd.DataFrame([{"dominio": d, "lista": l, "estrategia": e, "P": p, "v": v} for (d, l), (p, v, e) in res.items()])
    return df, df.groupby(["dominio", "estrategia"]).agg(P=("P", "mean"), v=("v", lambda s: s.sum() / len(s) ** 2))
def diferencas(st):
    o = {}
    for d in pref:
        for a, b in [("A", "B"), ("A", "C"), ("C", "B")]:
            x = st.loc[(d, a), "P"] - st.loc[(d, b), "P"]; se = np.sqrt(st.loc[(d, a), "v"] + st.loc[(d, b), "v"]); o[(d, f"{a}-{b}")] = (x, x - 1.96 * se, x + 1.96 * se)
    return o
relh = np.where(np.isnan(yh), np.nan, (yh >= 2).astype(float)); rell = (yl >= 2).astype(float)
rh, zh = lista_est(relh, h10h); rl, _ = lista_est(rell, h10l); Lh, Sh = agrega(rh); Ll, Sl = agrega(rl); Dh = diferencas(Sh); Dl = diferencas(Sl)
pd.DataFrame(zh, columns=["dominio", "lista", "faixa"]).to_csv(f"{OUT}/V7_05_estratos_variancia_nula.csv", index=False)
reg("V7-05.6", "estratos com variância estimada nula (humano)", f"{len(zh)} de 135 (por domínio: {pd.Series([z[0] for z in zh]).value_counts().to_dict()})", True)
dpos = relh - rell; hl = {}
for (d, e), g in S.assign(dd=dpos).groupby(["dominio", "estrategia"]):
    tot, var, nl = 0.0, 0.0, g.lista.nunique()
    for l, gl in g.groupby("lista"):
        tot += h10h[(d, l)] - h10l[(d, l)]
        for f, gg in gl.groupby("faixa"):
            z = gg.dd.dropna().to_numpy(); m = len(z); Nf = gg.N_estrato.iloc[0]; tot += Nf * z.mean()
            var += Nf ** 2 * (1 - m / Nf) * (z.var(ddof=1) if m > 1 else 0) / m
    x = tot / 100 / nl; se = np.sqrt(var / 1e4 / nl ** 2); hl[(d, e)] = (x, x - 1.96 * se, x + 1.96 * se)
dom_idx = {d: S.index[S.dominio == d].to_numpy() for d in S.dominio.unique()}; ujid = {d: S.jid[dom_idx[d]].unique() for d in S.dominio.unique()}
def bootstrap(semente, modo):
    rng = np.random.default_rng(semente); out = []
    for _ in range(2000):
        w = np.zeros(len(S))
        for d in S.dominio.unique():
            u = ujid[d]; draw = rng.choice(u, len(u)) if modo == "choice" else u[rng.integers(0, len(u), len(u))]
            w[dom_idx[d]] = S.jid[dom_idx[d]].map(pd.Series(draw).value_counts()).fillna(0).to_numpy()
        r, zz = lista_est(relh, h10h, w)
        if any(len(z) == 4 for z in zz): out.append(None); continue
        _, st = agrega(r); dd = diferencas(st)
        out.append({**{f"{d}|{e}": st.loc[(d, e), "P"] for d, e in st.index}, **{f"{d}|{c}": v[0] for (d, c), v in dd.items()}})
    nv_ = sum(x is None for x in out); return pd.DataFrame([x for x in out if x is not None]), nv_
B, nrep_vazio = bootstrap(20261113, "integers"); B42, nrep42 = bootstrap(42, "choice")
reg("V7-05.7", "réplicas bootstrap com estrato sem documentos sorteados (excluídas; no F15b contaram como 0 relevantes)", f"semente própria: {nrep_vazio}; semente 42 do F15b: {nrep42} (de 2000)", True)
def kw(a, b, k=3):
    a = np.asarray(a, int); b = np.asarray(b, int); O = np.zeros((k, k))
    for i, j in zip(a, b): O[i, j] += 1
    E = np.outer(O.sum(1), O.sum(0)) / O.sum(); W = np.array([[(i - j) ** 2 for j in range(k)] for i in range(k)]) / (k - 1) ** 2
    return 1 - (W * O).sum() / (W * E).sum()
cal = []; aval1 = [c for c in ["W", "U", "V", "T", "S", "R", "Q", "P", "O", "N", "M", "L", "K"] if c in Hm.columns]
loo = []
for d in pref:
    ids = [a for a in fonte[d] if tipo[a] == "calibracao"]; js = [doc2jid[a] for a in ids]; h = np.array([float(fonte[d][a]) for a in ids]); r = H.reindex(js).to_numpy()
    cal.append({"dominio": d, "n": len(ids), "kw": kw(r, h), "iguais": (h == r).mean(), "diferenca_media_final_menos_ref": (h - r).mean(),
                "ref_0_1_2": np.bincount(r.astype(int), minlength=3).tolist(), "final_0_1_2": np.bincount(h.astype(int), minlength=3).tolist()})
    sub = Hm.set_index("jid").loc[js]
    for c in aval1:
        if sub[c].notna().sum() == 0: continue
        o = sub[[x for x in aval1 if x != c]].apply(pd.to_numeric, errors="coerce")
        rr = o.apply(lambda s: np.floor(s.dropna().median()) if s.notna().any() else np.nan, axis=1).to_numpy()
        loo.append({"dominio": d, "referencia_sem": c, "n_docs_com_nota_do_avaliador": int(sub[c].notna().sum()), "docs_com_referencia_alterada": int((rr != r).sum()), "kw": kw(rr, h), "iguais": (rr == h).mean()})
allm = Hm.set_index("jid")[aval1].apply(pd.to_numeric, errors="coerce").apply(lambda s: np.floor(s.dropna().median()), axis=1)
reg("V7-04", "H_med reproduzida (mediana, empate → nota inferior) nos 30×3 de calibração", int((allm.reindex(H.index) != H).sum()), (allm.reindex(H.index) == H).all())
nv = [(d, nova[doc2jid[a]], J[doc2jid[a]]) for d in pref for a in fonte[d] if tipo[a] == "amostra" and fonte[d][a] != "NA"]
nv = pd.DataFrame(nv, columns=["dominio", "h", "l"]); nv["l"] = nv.l.round().astype(int)
conc = [{"dominio": d, "n": len(g), "kw_humano_LLM": kw(g.h, g.l), "iguais": (g.h == g.l).mean(), "LLM_acima": (g.l > g.h).mean(), "LLM_abaixo": (g.l < g.h).mean()} for d, g in nv.groupby("dominio")]
rels = relh.copy(); rels[S.jid.isin(semres).to_numpy()] = np.nan
rs, _ = lista_est(rels, h10h); _, Ss = agrega(rs); Ds = diferencas(Ss)
fe = pd.read_csv(f"{F15}/analise/P100_estrategias.csv"); fd = pd.read_csv(f"{F15}/analise/P100_diferencas.csv"); fh = pd.read_csv(f"{F15}/analise/humano_menos_LLM.csv")
fb = pd.read_csv(f"{F15}/analise/bootstrap.csv").set_index("alvo"); fc = pd.read_csv(f"{F15}/analise/calibracao.csv"); fk = pd.read_csv(f"{F15}/analise/humano_vs_LLM_concordancia.csv")
fs = pd.read_csv(f"{F15}/analise/sensibilidade.csv"); fs = fs[fs.tratamento == "sem_documentos_sem_resumo"]
cmp = []
def C(alvo, nosso, deles, tol=6e-5): cmp.append({"alvo": alvo, "F15d": round(float(nosso), 4), "F15b": float(deles), "dif_abs": abs(round(float(nosso), 4) - float(deles)), "igual": abs(float(nosso) - float(deles)) <= tol})
for r in fe.itertuples():
    k = (r.dominio, r.estrategia); se = np.sqrt(Sh.loc[k, "v"])
    C(f"P100 humana {k}", Sh.loc[k, "P"], r.P100); C(f"IC inf {k}", Sh.loc[k, "P"] - 1.96 * se, r.ic95_inf); C(f"IC sup {k}", Sh.loc[k, "P"] + 1.96 * se, r.ic95_sup)
    C(f"P100 LLM mesmas posições {k}", Sl.loc[k, "P"], r.P100_LLM_mesma_amostra)
for r in fd.itertuples():
    k = (r.dominio, r.comparacao); C(f"dif humana {k}", Dh[k][0], r.diferenca); C(f"dif IC inf {k}", Dh[k][1], r.ic95_inf); C(f"dif IC sup {k}", Dh[k][2], r.ic95_sup); C(f"dif LLM {k}", Dl[k][0], r.diferenca_LLM_mesma_amostra)
for r in fh.itertuples():
    k = (r.dominio, r.estrategia); C(f"humano−LLM {k}", hl[k][0], r.humano_menos_LLM); C(f"humano−LLM inf {k}", hl[k][1], r.ic95_inf); C(f"humano−LLM sup {k}", hl[k][2], r.ic95_sup)
for c in cal:
    g = fc[fc.dominio == c["dominio"]].iloc[0]; C(f"calib κw {c['dominio']}", c["kw"], g.kw_vs_mediana_anterior); C(f"calib iguais {c['dominio']}", c["iguais"], g.iguais); C(f"calib dif média {c['dominio']}", c["diferenca_media_final_menos_ref"], g.diferenca_media)
for c in conc:
    g = fk[fk.dominio == c["dominio"]].iloc[0]; C(f"κw humano-LLM {c['dominio']}", c["kw_humano_LLM"], g.kw_humano_LLM); C(f"iguais humano-LLM {c['dominio']}", c["iguais"], g.iguais)
for r in fs.itertuples():
    if r.alvo.startswith("P@100"): C(f"sem resumo {r.dominio} {r.alvo}", Ss.loc[(r.dominio, r.alvo[-1]), "P"], r.valor)
    else: C(f"sem resumo {r.dominio} {r.alvo}", Ds[(r.dominio, r.alvo)][0], r.valor)
for col in B.columns:
    cmp.append({"alvo": f"bootstrap EP {col}", "F15d": round(B[col].std(), 4), "F15b": fb.loc[col, "ep_bootstrap"], "dif_abs": abs(round(B[col].std(), 4) - fb.loc[col, "ep_bootstrap"]), "igual": abs(B[col].std() - fb.loc[col, "ep_bootstrap"]) <= 0.004})
CMP = pd.DataFrame(cmp); CMP.to_csv(f"{OUT}/V7_05_comparacao_F15d_F15b.csv", index=False)
reg("V7-05", "valores determinísticos iguais ao F15b (tolerância 6e-5) / bootstrap (EP, tolerância 0,004)",
    f"{int(CMP[~CMP.alvo.str.startswith('bootstrap')].igual.sum())}/{int((~CMP.alvo.str.startswith('bootstrap')).sum())}; {int(CMP[CMP.alvo.str.startswith('bootstrap')].igual.sum())}/{int(CMP.alvo.str.startswith('bootstrap').sum())}", CMP.igual.all())
pd.DataFrame([{"dominio": d, "estrategia": e, "P100_humana": Sh.loc[(d, e), "P"], "ic95_inf": Sh.loc[(d, e), "P"] - 1.96 * np.sqrt(Sh.loc[(d, e), "v"]), "ic95_sup": Sh.loc[(d, e), "P"] + 1.96 * np.sqrt(Sh.loc[(d, e), "v"]),
               "P100_LLM_mesmas_posicoes": Sl.loc[(d, e), "P"], "humano_menos_LLM": hl[(d, e)][0], "hml_ic95_inf": hl[(d, e)][1], "hml_ic95_sup": hl[(d, e)][2],
               "hml_distinto_de_zero": hl[(d, e)][1] > 0 or hl[(d, e)][2] < 0} for d, e in Sh.index]).round(4).to_csv(f"{OUT}/V7_05_estrategias_e_pareado.csv", index=False)
pd.DataFrame([{"dominio": d, "comparacao": c, "humana": v[0], "ic95_inf": v[1], "ic95_sup": v[2], "boot_inf": B[f"{d}|{c}"].quantile(.025), "boot_sup": B[f"{d}|{c}"].quantile(.975),
               "boot_inf_F15b": fb.loc[f"{d}|{c}", "ic95_inf_bootstrap"], "boot_sup_F15b": fb.loc[f"{d}|{c}", "ic95_sup_bootstrap"], "boot42_corrigido_inf": B42[f"{d}|{c}"].quantile(.025), "boot42_corrigido_sup": B42[f"{d}|{c}"].quantile(.975), "LLM": Dl[(d, c)][0], "humana_menos_LLM": v[0] - Dl[(d, c)][0]}
              for (d, c), v in Dh.items()]).round(4).to_csv(f"{OUT}/V7_05_diferencas.csv", index=False)
pd.DataFrame({"alvo": B42.columns, "ep": B42.std().values, "inf": B42.quantile(.025).values, "sup": B42.quantile(.975).values}).round(4).to_csv(f"{OUT}/V7_05_bootstrap_semente42_corrigido.csv", index=False)
pd.DataFrame(cal).to_csv(f"{OUT}/V7_04_calibracao.csv", index=False); pd.DataFrame(loo).round(4).to_csv(f"{OUT}/V7_04_calibracao_referencia_sem_cada_avaliador.csv", index=False)
pd.DataFrame(conc).round(4).to_csv(f"{OUT}/V7_05_concordancia_humano_LLM.csv", index=False)
LOG = pd.DataFrame(log); LOG.to_csv(f"{OUT}/V7_verificacoes.csv", index=False)
print(LOG.to_string(index=False)); print("comparações:", int(CMP.igual.sum()), "/", len(CMP)); print(CMP[~CMP.igual].to_string(index=False))
print(pd.read_csv(f"{OUT}/V7_05_diferencas.csv").to_string(index=False)); print(pd.DataFrame(cal).round(3).to_string(index=False))
print(pd.DataFrame(loo).round(3).groupby("dominio").agg(kmin=("kw","min"),kmax=("kw","max"),n=("kw","count"),alt_max=("docs_com_referencia_alterada","max")))
