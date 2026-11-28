#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F008r2_figura9_v60.py

File type:
    Script

Purpose:
    Regenerates Figure 9 (PCA scatter panels, three PDFs) with the final marker order, opacity and outline settings.

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
    - See docs/file_level_documentation.md (entry F008r2_figura9_v60.py).

Outputs:
    - See docs/file_level_documentation.md (entry F008r2_figura9_v60.py).

Dependencies:
    - matplotlib
    - numpy
    - pandas
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F008r2_figura9_v60.py

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
OUT = f"{R}/F008_reparacao_R2_20261123"; os.makedirs(OUT, exist_ok=False); MAN = []
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
        if e == "A":
            ax.scatter(z[:, 0], z[:, 1], s=10, alpha=0.85, color=cor, marker=mk, rasterized=True, linewidths=0.2, edgecolors=E.TINTA)
        else:
            ax.scatter(z[:, 0], z[:, 1], s=10, alpha=0.45, color=cor, marker=mk, rasterized=True, linewidths=0)
        mu, cov = z.mean(0), np.cov(z.T); v, w = np.linalg.eigh(cov); o = v.argsort()[::-1]; v, w = v[o], w[:, o]
        ax.add_patch(mp.Ellipse(mu, 2 * 2.447 * np.sqrt(v[0]), 2 * 2.447 * np.sqrt(v[1]), angle=np.degrees(np.arctan2(w[1, 0], w[0, 0])),
                                fill=False, color=cor, lw=3, ls=["-", "--", ":"]["ABC".index(e)]))
        CTRL.append(dict(figura=f"fig_pca_{d}", estrategia=e, n_pontos=len(z), mu1=mu[0], mu2=mu[1], eixo1=2*2.447*np.sqrt(v[0]), eixo2=2*2.447*np.sqrt(v[1])))
    ev = p.explained_variance_ratio_ * 100
    CTRL.append(dict(figura=f"fig_pca_{d}", estrategia="PC", n_pontos=len(m), mu1=ev[0], mu2=ev[1]))
    ax.set_xlabel(f"PC1 ({ev[0]:.1f}%) [-]"); ax.set_ylabel(f"PC2 ({ev[1]:.1f}%) [-]")
    gravar(fig, f"{OUT}/fig_pca_{d}.pdf")


pd.DataFrame(CTRL).to_csv(f"{OUT}/controle_pca_parametros.csv", index=False)
with open(f"{OUT}/MANIFESTO_figuras.txt", "w") as f:
    for p in MAN: f.write(os.path.basename(p) + "\n")
print(len(MAN), "figuras:", " ".join(os.path.basename(p) for p in MAN))
