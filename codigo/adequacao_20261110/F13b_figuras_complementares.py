#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F13b_figuras_complementares.py

File type:
    Script

Purpose:
    Draws the complementary figures: growth by strategy and annual delta, P@k by strategy and weighted kappa matrix between assessors.

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
    - See docs/file_level_documentation.md (entry F13b_figuras_complementares.py).

Outputs:
    - See docs/file_level_documentation.md (entry F13b_figuras_complementares.py).

Dependencies:
    - matplotlib
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F13b_figuras_complementares.py

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

import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo_figuras as E
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
E.aplicar()
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; I = f"{R}/F13_complementares"
OUT = f"{I}/figuras"; os.makedirs(OUT, exist_ok=True); MAN = []
milhar = FuncFormatter(lambda x, p: f"{x:,.0f}")

S = pd.read_csv(f"{I}/serie_anual_por_estrategia.csv"); S = S[(S.ano >= 2000) & (S.ano <= 2025)]
assert S.n.min() > 0
for d in E.ORDEM_DOM:
    fig, ax = E.figura(altura=5.4)
    for e in "ABC":
        g = S[(S.dominio == d) & (S.estrategia == e)].set_index("ano").n.reindex(range(2000, 2026))
        nm, c, mk = E.ESTRATEGIA[e]; ax.plot(g.index, g.values, color=c, marker=mk, markersize=7, label=nm)
    ax.set_yscale("log"); ax.yaxis.set_major_formatter(milhar); ax.set_xlim(1999.5, 2025.5); ax.set_xticks(range(2000, 2026, 5))
    ax.set_xlabel("Publication year"); ax.set_ylabel("Documents per year [-]"); ax.grid(axis="y", which="major")
    E.gravar(fig, f"{OUT}/fig_crescimento_{d}.pdf", MAN)
fig, ax = E.figura(altura=5.4)
for d in E.ORDEM_DOM:
    p = S[S.dominio == d].pivot(index="ano", columns="estrategia", values="n").reindex(range(2000, 2026))
    p = p[p.B >= 20]; dt = (p.A.fillna(0) / p.B)
    nm, c, mk = E.DOMINIO[d]; ax.plot(dt.index, dt.values, color=c, marker=mk, markersize=7, label=nm)
ax.set_xlim(1999.5, 2025.5); ax.set_xticks(range(2000, 2026, 5)); ax.set_ylim(0, None)
ax.set_xlabel("Publication year"); ax.set_ylabel(r"Annual $\delta_t = |A_t|/|B_t|$ [-]"); ax.grid(axis="y"); ax.legend(loc="upper left")
E.gravar(fig, f"{OUT}/fig_delta_anual.pdf", MAN)

P = pd.read_csv(f"{I}/P_k_por_estrategia.csv"); assert (P["count"] == 5).all()
ks = [10, 20, 50, 100]; off = {"A": -0.06, "B": 0.0, "C": 0.06}
for d in E.ORDEM_DOM:
    fig, ax = E.figura(altura=5.4)
    for e in "ABC":
        g = P[(P.dominio == d) & (P.estrategia == e)].set_index("k").loc[ks]; nm, c, mk = E.ESTRATEGIA[e]
        x = np.log10(ks) + off[e]
        ax.errorbar(x, g["mean"], yerr=[g["mean"] - g["min"], g["max"] - g["mean"]], color=c, marker=mk, capsize=5, elinewidth=2, label=nm)
    ax.set_xticks(np.log10(ks), [str(k) for k in ks]); ax.set_xlabel("Cut-off $k$ [documents]"); ax.set_ylabel("Strict P@$k$ [-]")
    ax.set_ylim(0, 1.02); ax.grid(axis="y")
    E.gravar(fig, f"{OUT}/fig_pk_{d}.pdf", MAN)
fig, ax = E.figura(altura=5.0); ax.axis("off")
ax.legend(handles=[Line2D([], [], color=E.ESTRATEGIA[e][1], marker=E.ESTRATEGIA[e][2], lw=3, label=E.ESTRATEGIA[e][0]) for e in "ABC"], loc="center")
E.gravar(fig, f"{OUT}/fig_estrategias_legenda.pdf", MAN)

M = pd.read_csv(f"{I}/kw_matriz_avaliadores.csv", index_col=0)
ordem = ["W", "U", "V", "T", "S", "R", "Q", "P", "O", "N", "M", "L", "K"]; M = M.loc[ordem, ordem]
grupo = {"W": "W, U, V", "U": "W, U, V", "V": "W, U, V", "T": "Biomed.", "S": "Biomed.", "R": "Biomed.", "Q": "Biomed.",
         "P": "Physics", "O": "Physics", "N": "Physics", "M": "Comp. eng.", "L": "Comp. eng.", "K": "Comp. eng."}
fig, ax = E.figura(E.INTEIRA, 11.0)
Mv = M.values.copy(); np.fill_diagonal(Mv, np.nan)
im = ax.imshow(Mv, cmap="Blues", vmin=0, vmax=1)
for (i, j), v in np.ndenumerate(Mv):
    if not np.isnan(v): ax.text(j, i, f"{v:.2f}".replace("0.", "."), ha="center", va="center", color="white" if v > 0.6 else E.TINTA)
ax.set_xticks(range(13), ordem); ax.set_yticks(range(13), ordem); ax.tick_params(length=0)
for b in [2.5, 6.5, 9.5]: ax.axhline(b, color=E.TINTA, lw=2.5); ax.axvline(b, color=E.TINTA, lw=2.5)
for c0, c1, t in [(0, 2, "W, U, V"), (3, 6, "Biomedicine"), (7, 9, "Physics"), (10, 12, "Comp. eng.")]:
    ax.text((c0 + c1) / 2, -0.95, t, ha="center", va="bottom")
[sp.set_visible(False) for sp in ax.spines.values()]
cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02, ticks=[0, 0.25, 0.5, 0.75, 1]); cb.set_label(r"Quadratic-weighted $\kappa_w$ [-]"); cb.outline.set_visible(False)
E.gravar(fig, f"{OUT}/fig_kw_avaliadores.pdf", MAN)

pd.DataFrame([{"figura": os.path.basename(p), "script": "F13b_figuras_complementares.py", "fonte": "F13_complementares/*.csv",
               "estilo": "estilo_figuras.py", "status": "gerada"} for p in MAN]).to_csv(f"{OUT}/MANIFESTO_figuras.csv", index=False)
print(len(MAN), "figuras")
