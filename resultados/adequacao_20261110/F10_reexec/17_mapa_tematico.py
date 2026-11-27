#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    17_mapa_tematico.py

File type:
    Script

Purpose:
    Thematic map (motor, niche, basic and emerging themes) from centrality and density.

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
    - See docs/file_level_documentation.md (entry 17_mapa_tematico.py).

Outputs:
    - See docs/file_level_documentation.md (entry 17_mapa_tematico.py).

Dependencies:
    - community
    - matplotlib
    - networkx
    - numpy
    - pandas

Execution:
    python resultados/adequacao_20261110/F10_reexec/17_mapa_tematico.py  (paths relative to this folder)

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

import os, shutil, itertools, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

try:
    import community as community_louvain
    HAS_LOUVAIN = True
except ImportError:
    HAS_LOUVAIN = False
    warnings.warn("python-louvain não encontrado; usando greedy_modularity_communities.")

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
MIN_FREQ  = 20
MAX_NODES = 60

QUADRANT_COLORS = {
    "Motor themes":            "#2166ac",
    "Basic themes":            "#f1a340",
    "Niche themes":            "#1a9641",
    "Emerging/Declining":      "#d01c8b",
}


def parse_concepts(series):
    result = []
    for val in series:
        if pd.isna(val) or val == "":
            result.append([])
        else:
            result.append([c.strip().lower() for c in str(val).split(";") if c.strip()])
    return result


def build_graph(concept_lists, min_freq=MIN_FREQ, max_nodes=MAX_NODES):
    freq = {}
    for doc in concept_lists:
        for c in set(doc):
            freq[c] = freq.get(c, 0) + 1
    valid = {c for c, f in freq.items() if f >= min_freq}
    if len(valid) > max_nodes:
        valid = set(sorted(valid, key=lambda c: freq[c], reverse=True)[:max_nodes])
    edge_weight = {}
    for doc in concept_lists:
        dvld = list(set(doc) & valid)
        for a, b in itertools.combinations(sorted(dvld), 2):
            key = (a, b)
            edge_weight[key] = edge_weight.get(key, 0) + 1
    G = nx.Graph()
    for c in valid:
        G.add_node(c, freq=freq[c])
    for (a, b), w in edge_weight.items():
        G.add_edge(a, b, weight=w)
    G.remove_nodes_from(list(nx.isolates(G)))
    return G, freq


def detect_communities(G):
    if HAS_LOUVAIN:
        return community_louvain.best_partition(G, weight="weight")
    comms = list(nx.algorithms.community.greedy_modularity_communities(G))
    partition = {}
    for cid, comm in enumerate(comms):
        for node in comm:
            partition[node] = cid
    return partition


def callon_metrics(G, partition):
    """
    Calcula centralidade e densidade de Callon para cada comunidade.

    centralidade(c) = soma dos pesos das arestas externas do cluster c
                      / total de pesos de arestas de todos os clusters
    densidade(c)    = soma dos pesos internos / (n*(n-1)/2) normalizado
    """
    communities = {}
    for node, cid in partition.items():
        communities.setdefault(cid, []).append(node)

    total_weight = sum(d["weight"] for _, _, d in G.edges(data=True))
    if total_weight == 0:
        total_weight = 1

    records = []
    for cid, nodes in communities.items():
        node_set = set(nodes)
        n = len(nodes)
        internal_w = 0.0
        external_w = 0.0
        for u, v, d in G.edges(data=True):
            w = d.get("weight", 1)
            u_in = u in node_set
            v_in = v in node_set
            if u_in and v_in:
                internal_w += w
            elif u_in or v_in:
                external_w += w

        max_internal = n * (n - 1) / 2 if n > 1 else 1
        density      = internal_w / max_internal if max_internal > 0 else 0
        centrality   = external_w / total_weight

        freq_total = sum(G.nodes[nd].get("freq", 1) for nd in nodes)
        label      = ", ".join(sorted(nodes, key=lambda nd: G.nodes[nd].get("freq", 0),
                                      reverse=True)[:3])
        records.append({
            "community":   cid,
            "label":       label,
            "density":     density,
            "centrality":  centrality,
            "freq_total":  freq_total,
            "n_nodes":     n,
        })
    return pd.DataFrame(records)


def assign_quadrant(row, median_c, median_d):
    if row["centrality"] >= median_c and row["density"] >= median_d:
        return "Motor themes"
    elif row["centrality"] >= median_c and row["density"] < median_d:
        return "Basic themes"
    elif row["centrality"] < median_c and row["density"] >= median_d:
        return "Niche themes"
    else:
        return "Emerging/Declining"


def plot_thematic_map(df_metrics, dom, out_path):
    med_c = df_metrics["centrality"].median()
    med_d = df_metrics["density"].median()

    df_metrics = df_metrics.copy()
    df_metrics["quadrant"] = df_metrics.apply(
        assign_quadrant, axis=1, args=(med_c, med_d))

    sizes = 200 + 600 * (df_metrics["freq_total"] / df_metrics["freq_total"].max())

    fig, ax = plt.subplots(figsize=(10, 4))
    for quad, color in QUADRANT_COLORS.items():
        sub = df_metrics[df_metrics["quadrant"] == quad]
        ax.scatter(sub["centrality"], sub["density"],
                   s=sizes.loc[sub.index], color=color,
                   alpha=0.75, label=quad, zorder=3)
        for _, row in sub.iterrows():
            ax.annotate(row["label"],
                        xy=(row["centrality"], row["density"]),
                        xytext=(4, 4), textcoords="offset points",
                        fontsize=7, wrap=True)

    ax.axvline(med_c, color="grey", linestyle="--", linewidth=1)
    ax.axhline(med_d, color="grey", linestyle="--", linewidth=1)

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    pad_x = (xlim[1] - xlim[0]) * 0.03
    pad_y = (ylim[1] - ylim[0]) * 0.03
    ax.text(med_c + pad_x, med_d + pad_y, "Motor themes",
            fontsize=FS - 3, color=QUADRANT_COLORS["Motor themes"], alpha=0.6)
    ax.text(xlim[0] + pad_x, med_d + pad_y, "Niche themes",
            fontsize=FS - 3, color=QUADRANT_COLORS["Niche themes"], alpha=0.6)
    ax.text(med_c + pad_x, ylim[0] + pad_y, "Basic themes",
            fontsize=FS - 3, color=QUADRANT_COLORS["Basic themes"], alpha=0.6)
    ax.text(xlim[0] + pad_x, ylim[0] + pad_y, "Emerging/\nDeclining",
            fontsize=FS - 3, color=QUADRANT_COLORS["Emerging/Declining"], alpha=0.6)

    ax.set_xlabel("Callon Centrality", fontsize=FS)
    ax.set_ylabel("Callon Density", fontsize=FS)
    ax.legend(fontsize=FS - 3, loc="upper left")
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

        G, freq    = build_graph(concept_lists)
        partition  = detect_communities(G)
        df_metrics = callon_metrics(G, partition)

        fig_out = os.path.join(FIG_DIR, f"fig_mapa_tematico_{dom}.pdf")
        plot_thematic_map(df_metrics, dom, fig_out)

        csv_out = os.path.join(DAD_DIR, f"mapa_tematico_{dom}.csv")
        df_metrics.to_csv(csv_out, index=False)
        print(f"[OK] {csv_out}")

        outputs += [fig_out, csv_out]

    copy_to_zenodo(outputs)
    print("Script 17 concluído.")
