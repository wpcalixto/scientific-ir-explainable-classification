#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F008r_reparacao_figuras_v59.py

File type:
    Script

Purpose:
    Regenerates six result figures as vector PDFs with 300 dpi raster layers and enlarged markers (final graphic repair).

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
    - See docs/file_level_documentation.md (entry F008r_reparacao_figuras_v59.py).

Outputs:
    - See docs/file_level_documentation.md (entry F008r_reparacao_figuras_v59.py).

Dependencies:
    - matplotlib
    - numpy
    - pandas
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F008r_reparacao_figuras_v59.py

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

import os, sys, json, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, BIBLIO_BASE + "/codigo/adequacao_20261110")
import estilo_figuras as E
import matplotlib.pyplot as plt, matplotlib.patches as mp
E.aplicar()
DPI = 300
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; S = f"{R}/F10_reexec"
D, DC, CL = f"{S}/dados_processados", f"{S}/dados_classificacao", f"{S}/classificacao"
OUT = f"{R}/F008_reparacao_20261123"; os.makedirs(OUT, exist_ok=False); MAN = []
def gravar(fig, caminho):
    assert not os.path.exists(caminho)
    fig.savefig(caminho, format="pdf", dpi=DPI); plt.close(fig); MAN.append(caminho)
CTRL = []

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
long = pd.read_csv(f"{S}/dados_openalex/consolidado_todos_dominios.csv", usecols=["openalex_id", "dominio", "estrategia"], low_memory=False)
for j, d in enumerate(E.ORDEM_DOM):
    t = pd.read_csv(f"{D}/lda_doc_topics_{d}.csv", low_memory=False); cols = [x for x in t.columns if x.startswith("topic_")]
    m = long[long.dominio == d].merge(t[["openalex_id"] + cols], on="openalex_id")
    p = PCA(2, random_state=42); Z = p.fit_transform(StandardScaler().fit_transform(m[cols])); fig, ax = E.figura(altura=5.6)
    for e in "BCA":
        n, cor, mk = E.ESTRATEGIA[e]; z = Z[m.estrategia == f"busca_{e}"]
        ax.scatter(z[:, 0], z[:, 1], s=10, alpha=0.45, color=cor, marker=mk, rasterized=True, linewidths=0)
        mu, cov = z.mean(0), np.cov(z.T); v, w = np.linalg.eigh(cov); o = v.argsort()[::-1]; v, w = v[o], w[:, o]
        ax.add_patch(mp.Ellipse(mu, 2 * 2.447 * np.sqrt(v[0]), 2 * 2.447 * np.sqrt(v[1]), angle=np.degrees(np.arctan2(w[1, 0], w[0, 0])),
                                fill=False, color=cor, lw=3, ls=["-", "--", ":"]["ABC".index(e)]))
        CTRL.append(dict(figura=f"fig_pca_{d}", estrategia=e, n_pontos=len(z), mu1=mu[0], mu2=mu[1], eixo1=2*2.447*np.sqrt(v[0]), eixo2=2*2.447*np.sqrt(v[1])))
    ev = p.explained_variance_ratio_ * 100
    CTRL.append(dict(figura=f"fig_pca_{d}", estrategia="PC", n_pontos=len(m), mu1=ev[0], mu2=ev[1]))
    ax.set_xlabel(f"PC1 ({ev[0]:.1f}%) [-]"); ax.set_ylabel(f"PC2 ({ev[1]:.1f}%) [-]")
    gravar(fig, f"{OUT}/fig_pca_{d}.pdf")

CLS = ["Applied", "Methodological", "General"]
cm = pd.read_csv(f"{CL}/confusao_RL.csv", index_col=0).loc[CLS, CLS].values; fr = cm / cm.sum(1, keepdims=True)
fig, ax = E.figura(altura=6.0); im = ax.imshow(fr, cmap="Blues", vmin=0, vmax=1)
for (i, j), v in np.ndenumerate(cm): ax.text(j, i, f"{v:,}", ha="center", va="center", color="white" if fr[i, j] > 0.5 else E.TINTA)
ab = {"Applied": "Applied", "Methodological": "Methodo-\nlogical", "General": "General"}
ax.set_xticks(range(3), [ab[c] for c in CLS]); ax.set_yticks(range(3), [ab[c] for c in CLS], rotation=90, va="center", ha="center"); ax.tick_params(axis="y", pad=16); ax.set_xlabel("Predicted class"); ax.set_ylabel("LLM label")
ax.spines[["left", "bottom"]].set_visible(False); ax.tick_params(length=0)
cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04); cb.set_label("Row proportion [-]"); cb.outline.set_visible(False)
gravar(fig, f"{OUT}/fig_classif_confusao.pdf")

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
gravar(fig, f"{OUT}/fig_precisao_listas.pdf")

I = f"{R}/F13_complementares"
M = pd.read_csv(f"{I}/kw_matriz_avaliadores.csv", index_col=0)
ordem = ["W", "U", "V", "T", "S", "R", "Q", "P", "O", "N", "M", "L", "K"]; M = M.loc[ordem, ordem]
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
gravar(fig, f"{OUT}/fig_kw_avaliadores.pdf")

pd.DataFrame(CTRL).to_csv(f"{OUT}/controle_pca_parametros.csv", index=False)
with open(f"{OUT}/MANIFESTO_figuras.txt", "w") as f:
    for p in MAN: f.write(os.path.basename(p) + "\n")
print(len(MAN), "figuras:", " ".join(os.path.basename(p) for p in MAN))
