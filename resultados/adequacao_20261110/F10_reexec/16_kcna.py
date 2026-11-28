#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    16_kcna.py

File type:
    Script

Purpose:
    Keyword co-occurrence network analysis (KCNA) from OpenAlex concepts.

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
    - See docs/file_level_documentation.md (entry 16_kcna.py).

Outputs:
    - See docs/file_level_documentation.md (entry 16_kcna.py).

Dependencies:
    - community
    - matplotlib
    - networkx
    - numpy
    - pandas

Execution:
    python resultados/adequacao_20261110/F10_reexec/16_kcna.py  (paths relative to this folder)

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
import matplotlib.cm as cm
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

FS      = 16
DOMAINS = ["microarranjos", "metamateriais", "radiomica"]
DOMAINS_EN = {
    "microarranjos": "Microarrays",
    "metamateriais": "Metamaterials",
    "radiomica":     "Radiomics",
}
MIN_FREQ   = 20
MAX_NODES  = 60

DOMAIN_CMAP = {
    "microarranjos": "Blues",
    "metamateriais": "RdPu",
    "radiomica":     "Greens",
}


def parse_concepts(series):
    """Converte coluna 'concepts' (';'-separated) em lista de listas."""
    result = []
    for val in series:
        if pd.isna(val) or val == "":
            result.append([])
        else:
            concepts = [c.strip().lower() for c in str(val).split(";") if c.strip()]
            result.append(concepts)
    return result


def build_graph(concept_lists, min_freq=MIN_FREQ, max_nodes=MAX_NODES):
    """Constrói grafo de coocorrência filtrado."""
    freq = {}
    for doc in concept_lists:
        for c in set(doc):
            freq[c] = freq.get(c, 0) + 1

    valid = {c for c, f in freq.items() if f >= min_freq}

    if len(valid) > max_nodes:
        valid = set(sorted(valid, key=lambda c: freq[c], reverse=True)[:max_nodes])

    edge_weight = {}
    for doc in concept_lists:
        doc_valid = list(set(doc) & valid)
        for a, b in itertools.combinations(sorted(doc_valid), 2):
            key = (a, b)
            edge_weight[key] = edge_weight.get(key, 0) + 1

    G = nx.Graph()
    for c in valid:
        G.add_node(c, freq=freq[c])
    for (a, b), w in edge_weight.items():
        G.add_edge(a, b, weight=w)

    isolated = list(nx.isolates(G))
    G.remove_nodes_from(isolated)
    return G


def detect_communities(G):
    """Retorna dict {nó: comunidade_id}."""
    if HAS_LOUVAIN:
        partition = community_louvain.best_partition(G, weight="weight")
    else:
        comms = list(nx.algorithms.community.greedy_modularity_communities(G))
        partition = {}
        for cid, comm in enumerate(comms):
            for node in comm:
                partition[node] = cid
    return partition


def plot_kcna(G, partition, dom, out_path):
    """Plota o grafo com cor por comunidade e tamanho por grau."""
    n_comm = max(partition.values()) + 1
    cmap   = matplotlib.colormaps["tab20"].resampled(max(n_comm, 2))
    colors = [cmap(partition.get(n, 0)) for n in G.nodes()]

    degrees = dict(G.degree())
    sizes   = [30 + 8 * degrees[n] for n in G.nodes()]

    weights = [G[u][v]["weight"] for u, v in G.edges()]
    max_w   = max(weights) if weights else 1
    widths  = [0.5 + 2.5 * w / max_w for w in weights]

    fig, ax = plt.subplots(figsize=(14, 10))
    pos = nx.spring_layout(G, seed=42, k=1.2 / np.sqrt(len(G.nodes()) + 1))

    nx.draw_networkx_edges(G, pos, ax=ax, width=widths,
                           edge_color="grey", alpha=0.4)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colors,
                           node_size=sizes, alpha=0.9)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=9, font_color="black")

    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"[OK] {out_path}")


def export_edges(G, partition, dom):
    """Exporta CSV de arestas com peso e comunidades dos nós."""
    rows = []
    for u, v, data in G.edges(data=True):
        rows.append({
            "source":      u,
            "target":      v,
            "weight":      data.get("weight", 1),
            "community_u": partition.get(u, -1),
            "community_v": partition.get(v, -1),
        })
    df = pd.DataFrame(rows).sort_values("weight", ascending=False)
    out = os.path.join(DAD_DIR, f"kcna_edges_{dom}.csv")
    df.to_csv(out, index=False)
    print(f"[OK] {out}")
    return out


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
        df_dom = df_all[df_all["dominio"] == dom].copy()
        concept_lists = parse_concepts(df_dom["concepts"])

        G         = build_graph(concept_lists)
        partition = detect_communities(G)

        fig_out  = os.path.join(FIG_DIR, f"fig_kcna_{dom}.pdf")
        plot_kcna(G, partition, dom, fig_out)
        csv_out  = export_edges(G, partition, dom)

        outputs += [fig_out, csv_out]

    copy_to_zenodo(outputs)
    print("Script 16 concluído.")
