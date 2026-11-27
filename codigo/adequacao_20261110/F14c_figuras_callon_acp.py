#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F14c_figuras_callon_acp.py

File type:
    Script

Purpose:
    Draws the KCNA and thematic-map figures with the equivalence-index partition and the PCA of the indicator matrix.

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
    - See docs/file_level_documentation.md (entry F14c_figuras_callon_acp.py).

Outputs:
    - See docs/file_level_documentation.md (entry F14c_figuras_callon_acp.py).

Dependencies:
    - matplotlib
    - networkx
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F14c_figuras_callon_acp.py

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

import os, sys, json, textwrap, numpy as np, pandas as pd, networkx as nx
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo_figuras as E
import matplotlib.patches as mp
from matplotlib.lines import Line2D
E.aplicar()
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; I = f"{R}/F14_complementares_01A/callon_equivalencia"
DC = f"{R}/F10_reexec/dados_classificacao"; OUT = f"{R}/F14_complementares_01A/figuras"; os.makedirs(OUT, exist_ok=True); MAN = []
COD = pd.read_csv(f"{R}/F11_figuras/codigos_termos.csv").set_index("termo").codigo.to_dict()
FRONT = "#9A9A9A"
def quad(c, d, mc, md):
    if np.isclose(c, mc) or np.isclose(d, md): return "On a median line"
    return {(True, True): "Motor themes", (True, False): "Basic themes", (False, True): "Niche themes", (False, False): "Emerging or declining themes"}[(c > mc, d > md)]
QQ = []
for d in E.ORDEM_DOM:
    M = pd.read_csv(f"{I}/mapa_{d}_nova.csv").reset_index(drop=True); M["c"] = range(len(M))
    mc, md = M.centralidade.median(), M.densidade.median(); M["quad"] = [quad(c, x, mc, md) for c, x in zip(M.centralidade, M.densidade)]
    for r in M.itertuples(): QQ.append({"dominio": d, "comunidade": f"C{r.c + 1}", "n_conceitos": r.n_conceitos, "rotulo": r.rotulo,
                                         "centralidade": round(r.centralidade, 2), "densidade": round(r.densidade, 2), "quadrante": r.quad})
    fig, ax = E.figura(altura=5.8); sz = 350 + 1400 * M.freq_total / M.freq_total.max()
    for r, s in zip(M.itertuples(), sz):
        ax.scatter(r.centralidade, r.densidade, s=s, color=E.QUADRANTE.get(r.quad, FRONT), alpha=0.85, edgecolor="white", lw=1.5, zorder=3)
    ax.axvline(mc, color=E.TINTA2, ls="--", lw=1.8); ax.axhline(md, color=E.TINTA2, ls="--", lw=1.8)
    dx, dy = np.ptp(M.centralidade), np.ptp(M.densidade)
    ax.set_xlim(M.centralidade.min() - 0.15 * dx, M.centralidade.max() + 0.15 * dx); ax.set_ylim(M.densidade.min() - 0.2 * dy, M.densidade.max() + 0.15 * dy)
    for r in M.itertuples():
        ax.annotate(f"C{r.c + 1}", (r.centralidade, r.densidade), xytext=(10, 8), textcoords="offset points", ha="left", va="bottom", zorder=4, color=E.TINTA)
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    for t, (xa, xb, ya, yb) in {"Motor themes": (mc, x1, md, y1), "Niche themes": (x0, mc, md, y1), "Basic themes": (mc, x1, y0, md),
                                "Emerging or declining themes": (x0, mc, y0, md)}.items():
        ax.add_patch(mp.Rectangle((xa, ya), xb - xa, yb - ya, facecolor=E.QUADRANTE[t], alpha=0.10, lw=0, zorder=0))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_xlabel("Callon centrality (equivalence index) [-]"); ax.set_ylabel("Callon density (equivalence index) [-]")
    E.gravar(fig, f"{OUT}/fig_mapa_tematico_{d}.pdf", MAN)
    ed = pd.read_csv(f"{DC}/kcna_edges_{d}.csv"); G = nx.Graph()
    for r in ed.itertuples(): G.add_edge(r.source, r.target, weight=r.weight)
    com = pd.read_csv(f"{I}/particao_nova_{d}.csv").set_index("conceito").comunidade.to_dict(); assert set(com) == set(G.nodes())
    nodes = sorted(G.nodes()); H = nx.Graph(); H.add_nodes_from(nodes); H.add_edges_from(sorted(G.edges(data=True)))
    deg = dict(H.degree()); w = np.array([H[u][v]["weight"] for u, v in H.edges()]); cs = sorted(set(com.values()))
    ordem = [n for cc in cs for n in sorted([m for m in nodes if com[m] == cc], key=lambda m: -deg[m])]
    gap = 2; tot = len(ordem) + gap * len(cs); pos, ang, k = {}, {}, 0
    for cc in cs:
        for n in [m for m in ordem if com[m] == cc]:
            a = 2 * np.pi * k / tot; pos[n] = np.array([np.cos(a), np.sin(a)]); ang[n] = a; k += 1
        k += gap
    fig, ax = E.figura(E.INTEIRA, 13.0); ax.axis("off"); ax.set_aspect("equal")
    nx.draw_networkx_edges(H, pos, ax=ax, width=0.3 + 3.2 * w / w.max(), edge_color="#8A8A8A", alpha=0.30)
    for cc in cs:
        ns = [n for n in nodes if com[n] == cc]; cor, mk = E.AGRUPAMENTO[cc % 8]
        nx.draw_networkx_nodes(H, pos, nodelist=ns, ax=ax, node_color=cor, node_shape=mk, node_size=[90 + 6 * deg[n] for n in ns],
                               edgecolors="white", linewidths=1.2, label=f"C{cc + 1} ({len(ns)})")
    for n in nodes:
        a = ang[n]; dg = np.degrees(a); esq = 90 < dg < 270
        ax.text(1.07 * np.cos(a), 1.07 * np.sin(a), COD[n], rotation=dg - 180 if esq else dg, rotation_mode="anchor", ha="right" if esq else "left", va="center")
    ax.set_xlim(-1.45, 1.45); ax.set_ylim(-1.75, 1.35); ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.01), ncol=min(len(cs), 7), markerscale=0.8, columnspacing=1.0)
    E.gravar(fig, f"{OUT}/fig_kcna_{d}.pdf", MAN)
pd.DataFrame(QQ).to_csv(f"{OUT}/quadrantes_estritos.csv", index=False); print(pd.DataFrame(QQ).to_string(index=False))
fig, ax = E.figura(altura=5.8); ax.axis("off")
ax.legend(handles=[mp.Patch(facecolor=E.QUADRANTE[t], alpha=0.35, edgecolor=E.QUADRANTE[t], lw=2, label=t) for t in ["Motor themes", "Niche themes", "Basic themes", "Emerging or declining themes"]]
          + [mp.Patch(facecolor=FRONT, alpha=0.85, edgecolor=FRONT, lw=2, label="On a median line"), Line2D([], [], color=E.TINTA2, ls="--", lw=1.8, label="Median")],
          loc="center", handlelength=2.2, handleheight=1.4)
E.gravar(fig, f"{OUT}/fig_mapa_tematico_legenda.pdf", MAN)
var = json.load(open(f"{R}/F11_figuras/mca_variancia_explicada.json"))
for d in E.ORDEM_DOM:
    C = pd.read_csv(f"{DC}/mca_coordenadas_{d}.csv"); ex = var[d]; fig, ax = E.figura(altura=5.6)
    rk = {c: i for i, c in enumerate(C.cluster.value_counts().sort_index().sort_values(ascending=False, kind="stable").index)}; C["cluster"] = C.cluster.map(rk)
    for k in sorted(C.cluster.unique()):
        g = C[C.cluster == k]; cor, mk = E.AGRUPAMENTO[k]
        ax.scatter(g.Dim1, g.Dim2, color=cor, marker=mk, s=70, alpha=0.8, edgecolor="white", lw=0.8, zorder=3)
    ax.axhline(0, color=E.TINTA2, ls="--", lw=1.5); ax.axvline(0, color=E.TINTA2, ls="--", lw=1.5)
    ax.set_xlabel(f"Principal component 1 ({100 * ex[0]:.1f}% of variance) [-]"); ax.set_ylabel(f"Principal component 2 ({100 * ex[1]:.1f}%) [-]")
    E.gravar(fig, f"{OUT}/fig_mca_{d}.pdf", MAN)
fig, ax = E.figura(altura=5.6); ax.axis("off")
ax.legend(handles=[Line2D([], [], ls="", marker=E.AGRUPAMENTO[k][1], color=E.AGRUPAMENTO[k][0], ms=13, markeredgecolor="white", label=f"Cluster {k + 1}") for k in range(4)], loc="center")
E.gravar(fig, f"{OUT}/fig_mca_legenda.pdf", MAN)
pd.DataFrame([{"figura": os.path.basename(p), "script": "F14c_figuras_callon_acp.py", "estilo": "estilo_figuras.py", "status": "gerada"} for p in MAN]).to_csv(f"{OUT}/MANIFESTO_figuras.csv", index=False)
print(len(MAN), "figuras")
