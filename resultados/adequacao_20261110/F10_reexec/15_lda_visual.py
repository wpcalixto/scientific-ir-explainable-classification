#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    15_lda_visual.py

File type:
    Script

Purpose:
    Bar charts of the LDA topics per domain (beta values).

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
    - See docs/file_level_documentation.md (entry 15_lda_visual.py).

Outputs:
    - See docs/file_level_documentation.md (entry 15_lda_visual.py).

Dependencies:
    - matplotlib
    - numpy
    - pandas

Execution:
    python resultados/adequacao_20261110/F10_reexec/15_lda_visual.py  (paths relative to this folder)

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

import os, shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE    = os.path.dirname(os.path.abspath(__file__))
PROC    = os.path.join(BASE, "dados_processados")
FIG_DIR = os.path.join(BASE, "figuras_pdf")
ZEN_DIR = os.path.join(BASE, "zenodo")
os.makedirs(FIG_DIR, exist_ok=True)

FS      = 16
DOMAINS = ["microarranjos", "metamateriais", "radiomica"]
DOMAINS_EN = {
    "microarranjos": "Microarrays",
    "metamateriais": "Metamaterials",
    "radiomica":     "Radiomics",
}
K_STAR = {"microarranjos": 9, "metamateriais": 11, "radiomica": 25}

DOMAIN_COLORS = {
    "microarranjos": "#2166ac",
    "metamateriais": "#d01c8b",
    "radiomica":     "#1a9641",
}


def load_topics(dom):
    """Retorna DataFrame com colunas [topico, rank, termo, peso]."""
    path = os.path.join(PROC, f"lda_topics_{dom}.csv")
    df = pd.read_csv(path)
    return df


def load_coherence(dom):
    """Retorna dict {k: coherence} para identificar tópicos mais coerentes."""
    path = os.path.join(PROC, f"coherence_scores_{dom}.csv")
    if os.path.isfile(path):
        df = pd.read_csv(path)
        return dict(zip(df["k"].astype(int), df["coherence"]))
    return {}


def plot_domain(dom, df, color, out_path, top_k_topics=None, ncols=3):
    """Plota todos os tópicos do domínio em subplots de barras horizontais."""
    topics = sorted(df["topico"].unique())
    if top_k_topics is not None:
        topics = topics[:top_k_topics]
    n = len(topics)
    nrows = int(np.ceil(n / ncols))

    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(ncols * 4.5, nrows * 3.2))
    axes = np.array(axes).flatten()

    for ax, tid in zip(axes, topics):
        sub = df[df["topico"] == tid].nsmallest(10, "rank").sort_values("peso")
        ax.barh(sub["termo"], sub["peso"], color=color, alpha=0.85)
        ax.set_title(f"Topic {tid}", fontsize=FS - 1)
        ax.tick_params(axis="y", labelsize=FS - 3)
        ax.tick_params(axis="x", labelsize=FS - 4)
        ax.set_xlabel("β weight", fontsize=FS - 3)

    for ax in axes[n:]:
        ax.set_visible(False)

    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {out_path}")


def pick_representative_topics(dom, df, n=2):
    """Escolhe n tópicos com maior termo de maior peso (mais discriminativos)."""
    top_term_per_topic = (df[df["rank"] == 1]
                          .sort_values("peso", ascending=False)
                          .head(n))
    return sorted(top_term_per_topic["topico"].tolist())


def make_resumo(data_by_dom, out_path):
    """Painel 3×2: 2 tópicos representativos por domínio."""
    ncols = 2
    nrows = 3
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 5, nrows * 3.2))

    for row, dom in enumerate(DOMAINS):
        df, color, rep_topics = data_by_dom[dom]
        for col, tid in enumerate(rep_topics[:2]):
            ax = axes[row][col]
            sub = df[df["topico"] == tid].nsmallest(10, "rank").sort_values("peso")
            ax.barh(sub["termo"], sub["peso"], color=color, alpha=0.85)
            ax.set_title(f"{DOMAINS_EN[dom]} — Topic {tid}", fontsize=FS - 1)
            ax.tick_params(axis="y", labelsize=FS - 4)
            ax.tick_params(axis="x", labelsize=FS - 5)
            ax.set_xlabel("β weight", fontsize=FS - 4)

    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {out_path}")


def copy_to_zenodo(paths):
    os.makedirs(ZEN_DIR, exist_ok=True)
    for p in paths:
        if os.path.isfile(p):
            shutil.copy2(p, ZEN_DIR)
            print(f"[zenodo] {os.path.basename(p)}")


if __name__ == "__main__":
    outputs    = []
    data_by_dom = {}

    for dom in DOMAINS:
        df    = load_topics(dom)
        color = DOMAIN_COLORS[dom]
        rep   = pick_representative_topics(dom, df, n=2)
        data_by_dom[dom] = (df, color, rep)

        out = os.path.join(FIG_DIR, f"fig_lda_beta_{dom}.pdf")
        ncols = 5 if dom == "radiomica" else 3
        plot_domain(dom, df, color, out, ncols=ncols)
        outputs.append(out)

    resumo_out = os.path.join(FIG_DIR, "fig_lda_beta_resumo.pdf")
    make_resumo(data_by_dom, resumo_out)
    outputs.append(resumo_out)

    copy_to_zenodo(outputs)
    print("Script 15 concluído.")
