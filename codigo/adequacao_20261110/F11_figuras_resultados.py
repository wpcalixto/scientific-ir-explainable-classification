#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F11_figuras_resultados.py

File type:
    Script

Purpose:
    Regenerates the result figures with a single visual identity (one panel per PDF).

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
    - See docs/file_level_documentation.md (entry F11_figuras_resultados.py).

Outputs:
    - See docs/file_level_documentation.md (entry F11_figuras_resultados.py).

Dependencies:
    - matplotlib
    - networkx
    - numpy
    - pandas
    - shap
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F11_figuras_resultados.py

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

import os, sys, json, importlib.util, textwrap, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo_figuras as E
import matplotlib.pyplot as plt, matplotlib.patches as mp
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D
E.aplicar()
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; S = f"{R}/F10_reexec"
D, DC, CL = f"{S}/dados_processados", f"{S}/dados_classificacao", f"{S}/classificacao"
OUT = f"{R}/F11_figuras"; os.makedirs(OUT, exist_ok=True); MAN = []
milhar = FuncFormatter(lambda x, p: f"{x:,.0f}")
nome_dom = lambda d: E.DOMINIO[d][0]
so = sys.argv[1:]
def corre(g): return not so or g in so

import re as _re
def _conjuntos():
    rep = {}; g = {}
    for d in E.ORDEM_DOM:
        t = pd.read_csv(f"{D}/lda_topics_{d}.csv"); tops = sorted(t[t["rank"] == 1].sort_values("peso", ascending=False).head(2).topico.tolist()); rep[d] = tops
        for k in tops: g.setdefault("lda", set()).update(t[t.topico == k].nsmallest(10, "rank").termo.astype(str))
        e = pd.read_csv(f"{DC}/kcna_edges_{d}.csv"); g.setdefault("kcna", set()).update(set(e.source) | set(e.target))
    g["shap"] = set(pd.read_csv(f"{CL}/shap_global_top30.csv", index_col=0).index[:20].astype(str))
    if os.path.exists(f"{OUT}/shap_top10_classe_valores.csv"): g["shap"] |= set(pd.read_csv(f"{OUT}/shap_top10_classe_valores.csv").termo.astype(str))
    g["lime"] = set(pd.read_csv(f"{CL}/lime_casos.csv").termo.astype(str)); return g
GRUPOS = _conjuntos(); TODOS = sorted(set().union(*GRUPOS.values()), key=lambda x: (x.lower(), x))
def _cod(t, i):
    al = _re.sub(r"[^A-Za-z0-9]", "", t); return f"{al[0].upper()}{al[-1].upper()}{i:03d}"
COD = {t: _cod(t, i) for i, t in enumerate(TODOS)}
assert len(set(COD.values())) == len(COD)
pd.DataFrame([{"termo": t, "codigo": c, **{k: t in v for k, v in GRUPOS.items()}} for t, c in COD.items()]).to_csv(f"{OUT}/codigos_termos.csv", index=False)
def _esc(t): return t.replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")
for k, v in GRUPOS.items():
    lst = sorted(v, key=lambda x: (x.lower(), x)); NC = 5; n = int(np.ceil(len(lst) / NC)); cols = [lst[i * n:(i + 1) * n] for i in range(NC)]
    linhas = []
    for r in range(n):
        cel = []
        for c in cols: cel += ([_esc(c[r]), f"\\texttt{{{COD[c[r]]}}}"] if r < len(c) else ["", ""])
        linhas.append(" & ".join(cel) + " \\\\")
    open(f"{OUT}/tab_codigos_{k}.tex", "w").write("\n".join(linhas) + "\n")

if corre("temporal"):
    T = pd.read_csv(f"{S}/caracterizacao/serie_anual.csv", index_col=0)
    fig, ax = E.figura(altura=5.0)
    for d in E.ORDEM_DOM:
        n, c, m = E.DOMINIO[d]; ax.plot(T.index, T[d], color=c, marker=m, label=n)
    ax.set_xlabel("Year"); ax.set_ylabel("Documents [count]"); ax.yaxis.set_major_formatter(milhar)
    ax.set_xticks(T.index[::1]); ax.tick_params(axis="x", rotation=45); ax.grid(axis="y"); ax.legend(loc="upper left")
    E.gravar(fig, f"{OUT}/fig_temporal.pdf", MAN)

if corre("venn"):
    can = pd.read_csv(f"{R}/F2_corpus/corpus_canonico.csv", usecols=["dominio", "em_A", "em_B"], low_memory=False)
    b = lambda s: s.astype(str).isin(["1", "True", "true"])
    def lente(r1, r2, d):
        if d >= r1 + r2: return 0.0
        if d <= abs(r1 - r2): return np.pi * min(r1, r2) ** 2
        a1 = r1 ** 2 * np.arccos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1)); a2 = r2 ** 2 * np.arccos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2))
        return a1 + a2 - 0.5 * np.sqrt((-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2))
    rows = []
    for d in E.ORDEM_DOM:
        g = can[can.dominio == d]; A, B = b(g.em_A), b(g.em_B); nA, nB, i = int(A.sum()), int(B.sum()), int((A & B).sum())
        rows.append({"dominio": d, "n_A": nA, "n_B": nB, "A_so": nA - i, "B_so": nB - i, "A_e_B": i})
        rA, rB = np.sqrt(nA / np.pi), np.sqrt(nB / np.pi); lo, hi = abs(rA - rB), rA + rB
        for _ in range(200):
            m = (lo + hi) / 2; lo, hi = (m, hi) if lente(rA, rB, m) > i else (lo, m)
        dist = (lo + hi) / 2; s = 1 / rB
        fig, ax = E.figura(altura=5.0); ax.set_aspect("equal"); ax.axis("off")
        _, cA, _ = E.ESTRATEGIA["A"]; _, cB, _ = E.ESTRATEGIA["B"]
        xa, xb = -dist * s / 2, dist * s / 2
        ax.add_patch(mp.Circle((xb, 0), rB * s, facecolor=cB, alpha=0.30, edgecolor=cB, lw=2.5))
        ax.add_patch(mp.Circle((xa, 0), rA * s, facecolor=cA, alpha=0.45, edgecolor=cA, lw=2.5))
        x0 = min(xa - rA * s, xb - rB * s); x1 = max(xa + rA * s, xb + rB * s)
        ax.set_xlim(x0 - 0.05, x1 + 1.75); ax.set_ylim(-1.05, 1.05)
        for k, t in enumerate([f"A only: {nA - i:,}", f"A ∩ B: {i:,}", f"B only: {nB - i:,}"]):
            ax.text(x1 + 0.12, -1.0 + 0.27 * (2 - k), t, ha="left", va="bottom")
        E.gravar(fig, f"{OUT}/fig_venn_hst_{d}.pdf", MAN)
    pd.DataFrame(rows).to_csv(f"{OUT}/venn_contagens.csv", index=False)
    fig, ax = E.figura(altura=5.0); ax.axis("off")
    ax.legend(handles=[mp.Patch(facecolor=E.ESTRATEGIA[k][1], alpha=0.5, edgecolor=E.ESTRATEGIA[k][1], lw=2.5, label=E.ESTRATEGIA[k][0]) for k in "AB"],
              loc="center", handlelength=2.2, handleheight=1.4)
    E.gravar(fig, f"{OUT}/fig_venn_hst_legenda.pdf", MAN)

if corre("hst"):
    F = pd.read_csv(f"{DC}/hst_frequencia_tabela.csv")
    ymax = {}
    for d in E.ORDEM_DOM:
        g = F[F.dominio == d]
        fig, ax = E.figura(altura=5.4)
        dados = [g[g.category == k].freq.values for k in ("HST", "General")]
        bp = ax.boxplot(dados, tick_labels=[E.GRUPO_TERMO[k][0] for k in ("HST", "General")], patch_artist=True, widths=0.5,
                        medianprops=dict(color=E.TINTA, lw=2.5), whiskerprops=dict(lw=2), capprops=dict(lw=2), boxprops=dict(lw=2), showfliers=False)
        for p, k in zip(bp["boxes"], ("HST", "General")): p.set_facecolor(E.GRUPO_TERMO[k][1]); p.set_alpha(0.35)
        rng = np.random.default_rng(42)
        for j, k in enumerate(("HST", "General")):
            v = dados[j]; ax.scatter(np.full(len(v), j + 1) + rng.uniform(-0.12, 0.12, len(v)), v, color=E.GRUPO_TERMO[k][1],
                                      marker=E.GRUPO_TERMO[k][2], s=110, edgecolor="white", linewidth=1.2, zorder=3)
        ax.set_ylabel("Documents [count]"); ax.yaxis.set_major_formatter(milhar); ax.grid(axis="y"); ax.set_ylim(bottom=0)
        E.gravar(fig, f"{OUT}/fig_hst_box_{d}.pdf", MAN)
        h = g.sort_values("freq"); fig, ax = E.figura(altura=5.4)
        for k in ("HST", "General"):
            q = h[h.category == k]; ax.scatter(q.freq, q.term, color=E.GRUPO_TERMO[k][1], marker=E.GRUPO_TERMO[k][2], s=140, label=E.GRUPO_TERMO[k][0], zorder=3)
        ax.hlines(h.term, 0, h.freq, color=E.GRADE, lw=2, zorder=1)
        ax.set_xlabel("Documents [count]"); ax.xaxis.set_major_formatter(milhar); ax.set_xlim(left=0); ax.legend(loc="lower right")
        E.gravar(fig, f"{OUT}/fig_hst_termos_{d}.pdf", MAN)

if corre("coerencia"):
    for d in E.ORDEM_DOM:
        c = pd.read_csv(f"{D}/coherence_scores_{d}.csv"); k = int(c.k[c.coherence.idxmax()]); n, cor, m = E.DOMINIO[d]
        fig, ax = E.figura(altura=4.6)
        ax.plot(c.k, c.coherence, color=cor, marker=m); ax.axvline(k, color=E.TINTA2, ls="--", lw=2)
        ax.annotate(f"k* = {k}", (k, 1), xycoords=("data", "axes fraction"), xytext=(0, 6), textcoords="offset points", ha="center", va="bottom", annotation_clip=False)
        ax.set_xlabel("Number of topics k [-]"); ax.set_ylabel("Coherence $c_v$ [-]"); ax.set_xticks(range(5, 30, 4)); ax.grid(axis="y")
        E.gravar(fig, f"{OUT}/fig_coerencia_{d}.pdf", MAN)

if corre("beta"):
    rep = {}
    for d in E.ORDEM_DOM:
        t = pd.read_csv(f"{D}/lda_topics_{d}.csv"); tops = sorted(t[t["rank"] == 1].sort_values("peso", ascending=False).head(2).topico.tolist()); rep[d] = tops
        for tid in tops:
            s = t[t.topico == tid].nsmallest(10, "rank").sort_values("peso"); fig, ax = E.figura(altura=5.6)
            ax.barh([COD[x] for x in s.termo.astype(str)], s.peso, color=E.DOMINIO[d][1]); ax.set_xlabel(r"Term weight $\beta$ [-]"); ax.grid(axis="x")
            E.gravar(fig, f"{OUT}/fig_lda_beta_{d}_t{tid}.pdf", MAN)
    json.dump(rep, open(f"{OUT}/lda_topicos_representativos.json", "w"))

if corre("pca"):
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    long = pd.read_csv(f"{S}/dados_openalex/consolidado_todos_dominios.csv", usecols=["openalex_id", "dominio", "estrategia"], low_memory=False)
    for j, d in enumerate(E.ORDEM_DOM):
        t = pd.read_csv(f"{D}/lda_doc_topics_{d}.csv", low_memory=False); cols = [x for x in t.columns if x.startswith("topic_")]
        m = long[long.dominio == d].merge(t[["openalex_id"] + cols], on="openalex_id")
        p = PCA(2, random_state=42); Z = p.fit_transform(StandardScaler().fit_transform(m[cols])); fig, ax = E.figura(altura=5.6)
        for e in "BCA":
            n, cor, mk = E.ESTRATEGIA[e]; z = Z[m.estrategia == f"busca_{e}"]
            ax.scatter(z[:, 0], z[:, 1], s=6, alpha=0.25, color=cor, marker=mk, rasterized=True, linewidths=0)
            mu, cov = z.mean(0), np.cov(z.T); v, w = np.linalg.eigh(cov); o = v.argsort()[::-1]; v, w = v[o], w[:, o]
            ax.add_patch(mp.Ellipse(mu, 2 * 2.447 * np.sqrt(v[0]), 2 * 2.447 * np.sqrt(v[1]), angle=np.degrees(np.arctan2(w[1, 0], w[0, 0])),
                                    fill=False, color=cor, lw=3, ls=["-", "--", ":"]["ABC".index(e)]))
        ev = p.explained_variance_ratio_ * 100
        ax.set_xlabel(f"PC1 ({ev[0]:.1f}%) [-]"); ax.set_ylabel(f"PC2 ({ev[1]:.1f}%) [-]")
        E.gravar(fig, f"{OUT}/fig_pca_{d}.pdf", MAN)
    fig, ax = E.figura(altura=5.6); ax.axis("off")
    ax.legend(handles=[Line2D([], [], color=E.ESTRATEGIA[e][1], ls=["-", "--", ":"][i], lw=3, marker=E.ESTRATEGIA[e][2], ms=9, label=E.ESTRATEGIA[e][0]) for i, e in enumerate("ABC")],
              loc="center", handlelength=3)
    E.gravar(fig, f"{OUT}/fig_pca_legenda.pdf", MAN)

if corre("kcna"):
    import networkx as nx
    for d in E.ORDEM_DOM:
        ed = pd.read_csv(f"{DC}/kcna_edges_{d}.csv"); G = nx.Graph()
        for r in ed.itertuples(): G.add_edge(r.source, r.target, weight=r.weight)
        com = pd.read_csv(f"{OUT}/mapa3/particao_{d}.csv").set_index("conceito").comunidade.to_dict(); assert set(com) == set(G.nodes())
        G = nx.relabel_nodes(G, {}, copy=True); nodes = sorted(G.nodes()); H = nx.Graph(); H.add_nodes_from(nodes); H.add_edges_from(sorted(G.edges(data=True)))
        deg = dict(H.degree()); w = np.array([H[u][v]["weight"] for u, v in H.edges()])
        cs = sorted(set(com.values()))
        ordem = [n for cc in cs for n in sorted([m for m in nodes if com.get(m) == cc], key=lambda m: -deg[m])]
        gap = 2; tot = len(ordem) + gap * len(cs); pos, ang, k = {}, {}, 0
        for cc in cs:
            for n in [m for m in ordem if com.get(m) == cc]:
                a = 2 * np.pi * k / tot; pos[n] = np.array([np.cos(a), np.sin(a)]); ang[n] = a; k += 1
            k += gap
        fig, ax = E.figura(E.INTEIRA, 13.0); ax.axis("off"); ax.set_aspect("equal")
        nx.draw_networkx_edges(H, pos, ax=ax, width=0.3 + 3.2 * w / w.max(), edge_color="#8A8A8A", alpha=0.30)
        for ci, cc in enumerate(cs):
            ns = [n for n in nodes if com.get(n) == cc]; cor, mk = E.AGRUPAMENTO[ci % 8]
            nx.draw_networkx_nodes(H, pos, nodelist=ns, ax=ax, node_color=cor, node_shape=mk, node_size=[90 + 6 * deg[n] for n in ns],
                                   edgecolors="white", linewidths=1.2, label=f"Community {ci + 1} ({len(ns)} concepts)")
        for n in nodes:
            a = ang[n]; dg = np.degrees(a); esq = 90 < dg < 270
            ax.text(1.07 * np.cos(a), 1.07 * np.sin(a), COD[n], rotation=dg - 180 if esq else dg, rotation_mode="anchor",
                    ha="right" if esq else "left", va="center")
        ax.set_xlim(-1.45, 1.45); ax.set_ylim(-1.75, 1.35)
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.01), ncol=3, markerscale=0.8)
        E.gravar(fig, f"{OUT}/fig_kcna_{d}.pdf", MAN)

if corre("mapa"):
    for d in E.ORDEM_DOM:
        M = pd.read_csv(f"{OUT}/mapa3/mapa_tematico_{d}.csv"); mc, md = M.centrality.median(), M.density.median()
        q = lambda r: ("Motor themes" if r.density >= md else "Basic themes") if r.centrality >= mc else ("Niche themes" if r.density >= md else "Emerging or declining themes")
        M["quad"] = M.apply(q, axis=1); fig, ax = E.figura(altura=5.8)
        sz = 300 + 1700 * M.freq_total / M.freq_total.max()
        for r, s in zip(M.itertuples(), sz):
            ax.scatter(r.centrality, r.density, s=s, color=E.QUADRANTE[r.quad], alpha=0.8, edgecolor="white", lw=1.5, zorder=3)
        ax.axvline(mc, color=E.TINTA2, ls="--", lw=1.8); ax.axhline(md, color=E.TINTA2, ls="--", lw=1.8)
        dx, dy = np.ptp(M.centrality) or 0.01, np.ptp(M.density) or 1
        ax.set_xlim(M.centrality.min() - 0.45 * dx, M.centrality.max() + 0.45 * dx); ax.set_ylim(M.density.min() - 0.6 * dy, M.density.max() + 0.35 * dy)
        for r in M.itertuples():
            lab = textwrap.fill(f"C{r.community + 1}: " + ", ".join(r.label.split(", ")[:2]), 24); lab = lab[:4] + lab[4].upper() + lab[5:]
            fx = (r.centrality - M.centrality.min()) / dx; ha = "left" if fx < 0.25 else ("right" if fx > 0.75 else "center")
            ax.annotate(lab, (r.centrality, r.density), xytext={"left": (-14, -22), "right": (14, -22), "center": (0, -22)}[ha], textcoords="offset points", ha=ha, va="top", zorder=4)
        x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
        for t, (xa, xb, ya, yb) in {"Motor themes": (mc, x1, md, y1), "Niche themes": (x0, mc, md, y1),
                                    "Basic themes": (mc, x1, y0, md), "Emerging or declining themes": (x0, mc, y0, md)}.items():
            ax.add_patch(mp.Rectangle((xa, ya), xb - xa, yb - ya, facecolor=E.QUADRANTE[t], alpha=0.10, lw=0, zorder=0))
        ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
        ax.set_xlabel("Callon centrality [-]"); ax.set_ylabel("Callon density [-]")
        E.gravar(fig, f"{OUT}/fig_mapa_tematico_{d}.pdf", MAN)
    fig, ax = E.figura(altura=5.8); ax.axis("off")
    ax.legend(handles=[mp.Patch(facecolor=E.QUADRANTE[t], alpha=0.35, edgecolor=E.QUADRANTE[t], lw=2, label=t) for t in ["Motor themes", "Niche themes", "Basic themes", "Emerging or declining themes"]]
              + [Line2D([], [], color=E.TINTA2, ls="--", lw=1.8, label="Median")], loc="center", handlelength=2.2, handleheight=1.4)
    E.gravar(fig, f"{OUT}/fig_mapa_tematico_legenda.pdf", MAN)

if corre("mca"):
    sp = importlib.util.spec_from_file_location("m18", f"{S}/18_mca.py"); m18 = importlib.util.module_from_spec(sp); sp.loader.exec_module(m18)
    al = pd.read_csv(f"{S}/dados_openalex/consolidado_todos_dominios.csv", low_memory=False).drop_duplicates(["dominio", "openalex_id"]); var = {}
    for j, d in enumerate(E.ORDEM_DOM):
        X = m18.build_binary_matrix(m18.parse_concepts(al[al.dominio == d]["concepts"]), min_freq=m18.MIN_FREQ); _, ex = m18.run_mca_svd(X)
        var[d] = [float(ex[0]), float(ex[1])]; C = pd.read_csv(f"{DC}/mca_coordenadas_{d}.csv"); fig, ax = E.figura(altura=5.6)
        rk = {c: i for i, c in enumerate(C.cluster.value_counts().sort_index().sort_values(ascending=False, kind="stable").index)}; C["cluster"] = C.cluster.map(rk)
        for k in sorted(C.cluster.unique()):
            g = C[C.cluster == k]; cor, mk = E.AGRUPAMENTO[k]
            ax.scatter(g.Dim1, g.Dim2, color=cor, marker=mk, s=70, alpha=0.8, edgecolor="white", lw=0.8, label=f"Cluster {k + 1}", zorder=3)
        ax.axhline(0, color=E.TINTA2, ls="--", lw=1.5); ax.axvline(0, color=E.TINTA2, ls="--", lw=1.5)
        ax.set_xlabel(f"Dimension 1 ({100 * ex[0]:.1f}%) [-]"); ax.set_ylabel(f"Dimension 2 ({100 * ex[1]:.1f}%) [-]")
        E.gravar(fig, f"{OUT}/fig_mca_{d}.pdf", MAN)
    fig, ax = E.figura(altura=5.6); ax.axis("off")
    ax.legend(handles=[Line2D([], [], ls="", marker=E.AGRUPAMENTO[k][1], color=E.AGRUPAMENTO[k][0], ms=13, markeredgecolor="white", label=f"Cluster {k + 1}") for k in range(4)],
              loc="center")
    E.gravar(fig, f"{OUT}/fig_mca_legenda.pdf", MAN)
    json.dump(var, open(f"{OUT}/mca_variancia_explicada.json", "w"), indent=1)

CLS = ["Applied", "Methodological", "General"]
if corre("classif"):
    B = pd.read_csv(f"{CL}/metricas_4modelos_dp.csv"); fig, ax = E.figura(altura=5.6); w = 0.2; xs = np.arange(len(B))
    for i, (s, (n, cor, ht)) in enumerate(E.METRICA.items()):
        ax.bar(xs + (i - 1.5) * w, B[f"{s}_media"], w * 0.92, yerr=B[f"{s}_dp"], color=cor, hatch=ht, edgecolor="white", lw=0.8,
               error_kw=dict(lw=1.8, capsize=4, capthick=1.8), label=n)
    ax.set_xticks(xs, [E.CLASSIFICADOR[m][0] for m in B.modelo]); ax.set_ylim(0.5, 1.0); ax.set_ylabel("Score [-]"); ax.grid(axis="y")
    ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.22), columnspacing=1.0)
    E.gravar(fig, f"{OUT}/fig_classif_metricas.pdf", MAN)
    cm = pd.read_csv(f"{CL}/confusao_RL.csv", index_col=0).loc[CLS, CLS].values; fr = cm / cm.sum(1, keepdims=True)
    fig, ax = E.figura(altura=6.0); im = ax.imshow(fr, cmap="Blues", vmin=0, vmax=1)
    for (i, j), v in np.ndenumerate(cm): ax.text(j, i, f"{v:,}", ha="center", va="center", color="white" if fr[i, j] > 0.5 else E.TINTA)
    ab = {"Applied": "Applied", "Methodological": "Methodo-\nlogical", "General": "General"}
    ax.set_xticks(range(3), [ab[c] for c in CLS]); ax.set_yticks(range(3), [ab[c] for c in CLS], rotation=90, va="center", ha="center"); ax.tick_params(axis="y", pad=16); ax.set_xlabel("Predicted class"); ax.set_ylabel("LLM label")
    ax.spines[["left", "bottom"]].set_visible(False); ax.tick_params(length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04); cb.set_label("Row proportion [-]"); cb.outline.set_visible(False)
    E.gravar(fig, f"{OUT}/fig_classif_confusao.pdf", MAN)
    L = pd.read_csv(f"{CL}/curva_treino_validacao.csv"); fig, ax = E.figura(altura=5.6)
    for col, (n, cor, mk, ls) in E.CURVA.items():
        ax.plot(L.n, L[col], color=cor, marker=mk, ls=ls, label=n); ax.fill_between(L.n, L[col] - L[col + "_dp"], L[col] + L[col + "_dp"], color=cor, alpha=0.2, lw=0)
    ax.set_xticks([0, 5000, 10000, 15000]); ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{x / 1000:.0f}k"))
    ax.set_xlabel("Training documents [count]"); ax.set_ylabel("Macro F1 [-]"); ax.grid(axis="y"); ax.legend(loc="center right")
    E.gravar(fig, f"{OUT}/fig_classif_aprendizagem.pdf", MAN)
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.metrics import roc_curve, auc
    c = pd.read_csv(f"{R}/F2_corpus/corpus_canonico.csv", keep_default_na=False, low_memory=False)
    c = c[(c.resumo_ok.astype(str).isin(["1", "True", "true"])) & c.label.isin(CLS)].drop_duplicates("openalex_id")
    X = (c.title + " " + c.abstract).tolist(); y = c.label.to_numpy(); assert len(c) == 18748
    TF = dict(ngram_range=(1, 2), min_df=3, max_df=0.85, max_features=10000, sublinear_tf=True); cv = StratifiedKFold(5, shuffle=True, random_state=42)
    pipe = make_pipeline(TfidfVectorizer(**TF), LogisticRegression(max_iter=2000, class_weight="balanced"))
    P = cross_val_predict(pipe, X, y, cv=cv, method="predict_proba", n_jobs=5); classes = np.array(sorted(CLS))
    pred = classes[P.argmax(1)]; from sklearn.metrics import confusion_matrix
    assert (confusion_matrix(y, pred, labels=CLS) == cm).all(), "matriz de confusão diferente da gravada"
    fig, ax = E.figura(altura=5.6); aucs = {}
    for cl in CLS:
        jj = list(classes).index(cl); fpr, tpr, _ = roc_curve(y == cl, P[:, jj]); aucs[cl] = auc(fpr, tpr); cor, ls = E.CLASSE[cl]
        ax.plot(fpr, tpr, color=cor, ls=ls, label=f"{cl} ({aucs[cl]:.3f})")
    ax.plot([0, 1], [0, 1], color=E.OI["cinza"], lw=1.5, ls=(0, (1, 2))); ax.set_xlabel("False positive rate [-]"); ax.set_ylabel("True positive rate [-]")
    ax.set_aspect("equal"); ax.legend(loc="lower right", title="Class (AUC)")
    E.gravar(fig, f"{OUT}/fig_classif_roc.pdf", MAN)
    import shap
    pipe.fit(X, y); vec, lr = pipe.steps[0][1], pipe.steps[1][1]; Xt = vec.transform(X); fn = vec.get_feature_names_out()
    rng = np.random.default_rng(42); idx = rng.choice(Xt.shape[0], 2000, replace=False)
    ex = shap.LinearExplainer(lr, Xt[rng.choice(Xt.shape[0], 500, replace=False)]); sv = ex.shap_values(Xt[idx])
    sv = np.stack(sv, -1) if isinstance(sv, list) else sv; imp = np.abs(sv).mean(0)
    glob = pd.Series(imp.sum(1), index=fn).sort_values(ascending=False)
    ref = pd.read_csv(f"{CL}/shap_global_top30.csv", index_col=0).iloc[:, 0]
    assert list(glob.head(20).index) == list(ref.head(20).index), "SHAP global diferente do gravado"
    g = glob.head(20)[::-1]; fig, ax = E.figura(altura=8.0); ax.barh(g.index, g.values, color=E.OI["azul"]); ax.set_xlabel("Mean |SHAP| summed over classes [-]"); ax.grid(axis="x")
    E.gravar(fig, f"{OUT}/fig_shap_global.pdf", MAN); rows = []
    for cl in CLS:
        v = pd.Series(imp[:, list(lr.classes_).index(cl)], index=fn).sort_values(ascending=False).head(10)
        rows += [{"classe": cl, "termo": t, "media_abs_shap": x} for t, x in v.items()]
        fig, ax = E.figura(altura=5.6); ax.barh(v.index[::-1], v.values[::-1], color=E.CLASSE[cl][0]); ax.set_xlabel("Mean |SHAP| [-]"); ax.grid(axis="x")
        E.gravar(fig, f"{OUT}/fig_shap_{cl.lower()}.pdf", MAN)
    pd.DataFrame(rows).to_csv(f"{OUT}/shap_top10_classe_valores.csv", index=False); json.dump(aucs, open(f"{OUT}/roc_auc.json", "w"), indent=1)
if corre("shap"):
    gl = pd.read_csv(f"{CL}/shap_global_top30.csv", index_col=0).iloc[:20, 0][::-1]
    fig, ax = E.figura(altura=8.0); ax.barh([COD[str(x)] for x in gl.index], gl.values, color=E.OI["azul"]); ax.set_xlabel("Mean |SHAP| summed over classes [-]"); ax.grid(axis="x")
    E.gravar(fig, f"{OUT}/fig_shap_global.pdf", MAN); V = pd.read_csv(f"{OUT}/shap_top10_classe_valores.csv")
    for cl in CLS:
        v = V[V.classe == cl].iloc[::-1]; fig, ax = E.figura(altura=5.6)
        ax.barh([COD[str(x)] for x in v.termo], v.media_abs_shap, color=E.CLASSE[cl][0]); ax.set_xlabel("Mean |SHAP| [-]"); ax.grid(axis="x")
        E.gravar(fig, f"{OUT}/fig_shap_{cl.lower()}.pdf", MAN)
if corre("lime"):
    Lc = pd.read_csv(f"{CL}/lime_casos.csv"); conf = {}
    for cl in CLS:
        g = Lc[Lc.classe == cl].iloc[::-1]; conf[cl] = float(g.confianca.iloc[0]); fig, ax = E.figura(altura=5.6)
        ax.barh([COD[x] for x in g.termo.astype(str)], g.peso, color=[E.LIME_SINAL[p > 0] for p in g.peso], hatch=None); ax.axvline(0, color=E.TINTA2, lw=1.5)
        ax.set_xlabel("LIME weight [-]"); ax.grid(axis="x"); from matplotlib.ticker import MaxNLocator; ax.xaxis.set_major_locator(MaxNLocator(4))
        E.gravar(fig, f"{OUT}/fig_lime_{cl.lower()}.pdf", MAN)
    json.dump(conf, open(f"{OUT}/lime_confianca.json", "w"), indent=1)

if corre("wss"):
    b = pd.read_csv(f"{R}/F6_benchmarks/metricas_benchmarks.csv")
    mp_ = {"SVM": "SVM", "RandomForest": "RF", "RegressaoLogistica": "RL", "NaiveBayes": "NB"}; b["m"] = b.modelo.map(mp_)
    Pv = b.pivot(index="conjunto", columns="m", values="wss95")[["RL", "RF", "SVM", "NB"]].sort_values("RL")
    REN = {"Chou_2003": "Cohen 2006 Opioids", "Chou_2004": "Cohen 2006 SkeletalMuscleRelaxants", "Nelson_2002": "Cohen 2006 Estrogens"}
    Pv = Pv.iloc[::-1]; fig, ax = E.figura(E.INTEIRA, 6.4); xx = np.arange(len(Pv))
    for m in ["RL", "RF", "SVM", "NB"]:
        n, cor, mk = E.CLASSIFICADOR[m]; ax.scatter(xx, Pv[m], color=cor, marker=mk, s=150, edgecolor="white", lw=1, label=n, zorder=3)
    FORMAL = {"ACEInhibitors": "ACE inhibitors", "ADHD": "ADHD", "Antihistamines": "Antihistamines", "AtypicalAntipsychotics": "Atypical antipsychotics",
             "BetaBlockers": "Beta blockers", "CalciumChannelBlockers": "Calcium channel blockers", "Estrogens": "Estrogens", "NSAIDS": "NSAIDs",
             "Opioids": "Opioids", "OralHypoglycemics": "Oral hypoglycemics", "ProtonPumpInhibitors": "Proton pump inhibitors",
             "SkeletalMuscleRelaxants": "Skeletal muscle relaxants", "Statins": "Statins", "Triptans": "Triptans", "UrinaryIncontinence": "Urinary incontinence"}
    lab = [FORMAL.get(x, x) for x in (REN.get(s_, s_).replace("_", " ").replace("Cohen 2006 ", "") for s_ in Pv.index)]
    ax.set_xticks(xx, lab, rotation=40, ha="right", rotation_mode="anchor"); ax.axhline(0, color=E.TINTA2, lw=1.5); ax.set_ylabel("WSS@95% [-]"); ax.grid(axis="y")
    ax.set_xlim(-0.6, len(Pv) - 0.4); ax.legend(ncol=4, loc="upper right", columnspacing=1.0, handletextpad=0.2)
    E.gravar(fig, f"{OUT}/fig_wss_benchmarks.pdf", MAN)

if corre("precisao"):
    import re
    M = pd.read_csv(f"{R}/F7_painel_llm/analise/J_metricas_por_lista.csv"); c = M[M.juiz == "consenso"]
    ordem = [f"OAL_{s}_{r}" for s in "ABC" for r in ("bm25", "cit")] + [f"{p}_{s}" for p in ("scopus_top100", "wos_top100", "elicit_semantico") for s in "ABC"]
    H = c.pivot(index="lista", columns="dominio", values="P2@100").loc[ordem, E.ORDEM_DOM]
    nome = lambda s: re.sub(r"_cit$", " (cit.)", re.sub(r"_bm25$", " (BM25)", s)).replace("scopus_top100", "Scopus").replace("wos_top100", "WoS").replace("elicit_semantico", "Elicit").replace("OAL", "OpenAlex").replace("_", " ")
    Ht = H.T; fig, ax = E.figura(E.INTEIRA, 5.2); im = ax.imshow(Ht.values, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    for (i_, j_), v in np.ndenumerate(Ht.values): ax.text(j_, i_, f"{v:.2f}", ha="center", va="center", color="white" if v > 0.55 else E.TINTA)
    ax.set_yticks(range(3), ["Microarrays", "Metamaterials", "Radiomics"]); ax.set_xticks(range(len(ordem)), [nome(s_) for s_ in ordem], rotation=40, ha="right", rotation_mode="anchor")
    ax.tick_params(length=0); [sp.set_visible(False) for sp in ax.spines.values()]
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.015, ticks=[0, 0.25, 0.5, 0.75, 1]); cb.set_label("Strict P@100 [-]"); cb.outline.set_visible(False)
    E.gravar(fig, f"{OUT}/fig_precisao_listas.pdf", MAN)

with open(f"{OUT}/MANIFESTO_figuras.txt", "a") as f:
    for p in MAN: f.write(os.path.basename(p) + "\n")
print(len(MAN), "figuras:", " ".join(os.path.basename(p) for p in MAN))
