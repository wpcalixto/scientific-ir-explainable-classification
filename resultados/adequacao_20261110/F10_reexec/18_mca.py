#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    18_mca.py

File type:
    Script

Purpose:
    Multiple correspondence analysis of the presence matrix of concepts.

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
    - See docs/file_level_documentation.md (entry 18_mca.py).

Outputs:
    - See docs/file_level_documentation.md (entry 18_mca.py).

Dependencies:
    - matplotlib
    - numpy
    - pandas
    - prince
    - sklearn

Execution:
    python resultados/adequacao_20261110/F10_reexec/18_mca.py  (paths relative to this folder)

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

import os, shutil, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD

try:
    import prince
    HAS_PRINCE = True
except ImportError:
    HAS_PRINCE = False
    warnings.warn("prince não encontrado; usando SVD sobre matriz de Burt como fallback.")

BASE    = os.path.dirname(os.path.abspath(__file__))
OA_DIR  = os.path.join(BASE, "dados_openalex")
FIG_DIR = os.path.join(BASE, "figuras_pdf")
DAD_DIR = os.path.join(BASE, "dados_classificacao")
ZEN_DIR = os.path.join(BASE, "zenodo")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(DAD_DIR, exist_ok=True)

FS         = 16
DOMAINS    = ["microarranjos", "metamateriais", "radiomica"]
DOMAINS_EN = {
    "microarranjos": "Microarrays",
    "metamateriais": "Metamaterials",
    "radiomica":     "Radiomics",
}
MIN_FREQ = 50
N_CLUSTERS = 4

CLUSTER_COLORS = ["#2166ac", "#d01c8b", "#1a9641", "#f1a340"]


def parse_concepts(series):
    result = []
    for val in series:
        if pd.isna(val) or val == "":
            result.append([])
        else:
            result.append([c.strip().lower() for c in str(val).split(";") if c.strip()])
    return result


def build_binary_matrix(concept_lists, min_freq=MIN_FREQ):
    """Retorna DataFrame binário documentos × conceitos (filtrado)."""
    freq = {}
    for doc in concept_lists:
        for c in set(doc):
            freq[c] = freq.get(c, 0) + 1
    valid = sorted(c for c, f in freq.items() if f >= min_freq)

    rows = []
    for doc in concept_lists:
        doc_set = set(doc)
        rows.append({c: int(c in doc_set) for c in valid})
    return pd.DataFrame(rows, columns=valid)


def run_mca_prince(X):
    """MCA com prince; retorna coordenadas dos conceitos e variância explicada."""
    mca = prince.MCA(n_components=2, random_state=42)
    mca.fit(X.astype(str))
    coords = mca.column_coordinates(X.astype(str))
    coords.columns = ["Dim1", "Dim2"]
    try:
        explained = list(mca.percentage_of_variance_[:2] / 100)
    except Exception:
        try:
            explained = list(mca.eigenvalues_[:2] / mca.eigenvalues_.sum())
        except Exception:
            explained = [0.0, 0.0]
    return coords, explained


def run_mca_svd(X):
    """Fallback: SVD sobre a matriz de Burt (X.T @ X)."""
    Xb = X.values.astype(float)
    Xb_centered = Xb - Xb.mean(axis=0)
    svd = TruncatedSVD(n_components=2, random_state=42)
    svd.fit(Xb_centered)
    coords_mat = svd.components_.T
    coords = pd.DataFrame(coords_mat, index=X.columns, columns=["Dim1", "Dim2"])
    total  = Xb_centered.var(axis=0).sum()
    explained = svd.explained_variance_ / total if total > 0 else [0, 0]
    return coords, explained


def plot_mca(coords, clusters, dom, explained, out_path):
    fig, ax = plt.subplots(figsize=(10, 8))
    n_clusters = len(set(clusters))
    for k in range(n_clusters):
        idx = [i for i, c in enumerate(clusters) if c == k]
        ax.scatter(coords.iloc[idx]["Dim1"], coords.iloc[idx]["Dim2"],
                   color=CLUSTER_COLORS[k % len(CLUSTER_COLORS)],
                   alpha=0.75, s=60, label=f"Cluster {k + 1}", zorder=3)
        for i in idx:
            ax.annotate(coords.index[i],
                        xy=(coords.iloc[i]["Dim1"], coords.iloc[i]["Dim2"]),
                        xytext=(3, 3), textcoords="offset points",
                        fontsize=6, color="black")

    ax.axhline(0, color="grey", linestyle="--", linewidth=0.8)
    ax.axvline(0, color="grey", linestyle="--", linewidth=0.8)

    var1 = f"{explained[0] * 100:.1f}%" if len(explained) >= 1 else ""
    var2 = f"{explained[1] * 100:.1f}%" if len(explained) >= 2 else ""
    ax.set_xlabel(f"Dimension 1 ({var1})", fontsize=FS)
    ax.set_ylabel(f"Dimension 2 ({var2})", fontsize=FS)
    ax.legend(fontsize=FS - 3)
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
    consol = os.path.join(OA_DIR, "consolidado_todos_dominios.csv")
    df_all = pd.read_csv(consol, low_memory=False)
    df_all = df_all.drop_duplicates(["dominio", "openalex_id"])

    outputs = []
    for dom in DOMAINS:
        df_dom        = df_all[df_all["dominio"] == dom].copy()
        concept_lists = parse_concepts(df_dom["concepts"])
        X             = build_binary_matrix(concept_lists, min_freq=MIN_FREQ)

        if X.shape[1] < 4:
            print(f"[AVISO] {dom}: apenas {X.shape[1]} conceitos após filtro; pulando MCA.")
            continue

        if HAS_PRINCE:
            coords, explained = run_mca_prince(X)
        else:
            coords, explained = run_mca_svd(X)

        n_k = min(N_CLUSTERS, len(coords))
        km  = KMeans(n_clusters=n_k, random_state=42, n_init=10)
        clusters = km.fit_predict(coords[["Dim1", "Dim2"]].values)
        coords["cluster"] = clusters

        fig_out = os.path.join(FIG_DIR, f"fig_mca_{dom}.pdf")
        plot_mca(coords, clusters, dom, explained, fig_out)

        csv_out = os.path.join(DAD_DIR, f"mca_coordenadas_{dom}.csv")
        coords.index.name = "conceito"
        coords.to_csv(csv_out)
        print(f"[OK] {csv_out}")

        outputs += [fig_out, csv_out]

    copy_to_zenodo(outputs)
    print("Script 18 concluído.")
