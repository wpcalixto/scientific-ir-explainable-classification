#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F13c_sensibilidade_agrupamentos.py

File type:
    Script

Purpose:
    Sensitivity and stability analysis of the clustering results without new data collection.

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
    - See docs/file_level_documentation.md (entry F13c_sensibilidade_agrupamentos.py).

Outputs:
    - See docs/file_level_documentation.md (entry F13c_sensibilidade_agrupamentos.py).

Dependencies:
    - community
    - networkx
    - numpy
    - pandas
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F13c_sensibilidade_agrupamentos.py

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

import json, importlib.util, numpy as np, pandas as pd, networkx as nx, community as cl
from sklearn.metrics import adjusted_rand_score as ari, silhouette_score
from sklearn.cluster import KMeans
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; S = f"{R}/F10_reexec"
sp = importlib.util.spec_from_file_location("m17", f"{S}/17_mapa_tematico.py"); m17 = importlib.util.module_from_spec(sp); sp.loader.exec_module(m17)
al = pd.read_csv(f"{S}/dados_openalex/consolidado_todos_dominios.csv", low_memory=False).drop_duplicates(["dominio", "openalex_id"])
res = json.load(open(f"{R}/F11_figuras/mapa3/resolucao.json")); out = {}
rng = np.random.default_rng(42)
for d in m17.DOMAINS:
    G0, _ = m17.build_graph(m17.parse_concepts(al[al.dominio == d]["concepts"]))
    G = nx.Graph(); G.add_nodes_from(sorted(G0.nodes(data=True))); G.add_edges_from(sorted((min(u, v), max(u, v), w) for u, v, w in G0.edges(data=True)))
    n = G.number_of_nodes(); dens = 2 * G.number_of_edges() / (n * (n - 1))
    grade = []
    for g in np.round(np.arange(0.5, 3.0001, 0.05), 2):
        p = cl.best_partition(G, weight="weight", resolution=float(g), random_state=42)
        grade.append({"gamma": float(g), "n_com": len(set(p.values())), "Q": round(cl.modularity(p, G, weight="weight"), 4)})
    gam = res[d]["resolucao"]; ref = cl.best_partition(G, weight="weight", resolution=gam, random_state=42); nodes = sorted(G)
    ncs, aris = [], []
    for s in range(200):
        p = cl.best_partition(G, weight="weight", resolution=gam, random_state=s); ncs.append(len(set(p.values())))
        aris.append(ari([ref[x] for x in nodes], [p[x] for x in nodes]))
    p1 = cl.best_partition(G, weight="weight", resolution=1.0, random_state=42); Q1 = cl.modularity(p1, G, weight="weight")
    w = np.array([dd["weight"] for _, _, dd in G.edges(data=True)]); E = list(G.edges()); qn = []
    for _ in range(200):
        H = nx.Graph(); H.add_nodes_from(nodes); H.add_weighted_edges_from([(u, v, x) for (u, v), x in zip(E, rng.permutation(w))])
        qn.append(cl.modularity(cl.best_partition(H, weight="weight", resolution=1.0, random_state=42), H, weight="weight"))
    C = pd.read_csv(f"{S}/dados_classificacao/mca_coordenadas_{d}.csv"); X = C[["Dim1", "Dim2"]].values
    sil = {k: round(float(silhouette_score(X, KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X))), 3) for k in range(2, 9)}
    km = [KMeans(n_clusters=4, random_state=s, n_init=10).fit_predict(X) for s in range(200)]
    kari = [ari(km[0], k_) for k_ in km[1:]]
    out[d] = {"nos": n, "arestas": G.number_of_edges(), "densidade_grafo": round(dens, 3),
              "gamma_escolhida": gam, "Q_publicada": round(res[d]["modularidade"], 4),
              "n_com_gamma1_semente42": len(set(p1.values())), "Q_gamma1": round(Q1, 4),
              "Q_nulo_pesos_permutados_media": round(float(np.mean(qn)), 4), "Q_nulo_p95": round(float(np.percentile(qn, 95)), 4),
              "z_Q": round(float((Q1 - np.mean(qn)) / np.std(qn)), 1),
              "gammas_com_3_comunidades": [x["gamma"] for x in grade if x["n_com"] == 3],
              "n_com_por_gamma": {str(x["gamma"]): x["n_com"] for x in grade},
              "sementes_com_3_comunidades_pct": round(100 * np.mean(np.array(ncs) == 3), 1),
              "n_com_sementes_distrib": {str(k): int(v) for k, v in zip(*np.unique(ncs, return_counts=True))},
              "ARI_sementes_mediana": round(float(np.median(aris)), 3), "ARI_sementes_p10": round(float(np.percentile(aris, 10)), 3),
              "kmeans_silhueta_k2_8": sil, "kmeans_k4_ARI_sementes_mediana": round(float(np.median(kari)), 3),
              "kmeans_k4_ARI_sementes_min": round(float(np.min(kari)), 3), "n_conceitos_mca": len(C)}
    print(d, {k: v for k, v in out[d].items() if k != "n_com_por_gamma"})
json.dump(out, open(f"{R}/F13_complementares/sensibilidade_agrupamentos.json", "w"), indent=1, ensure_ascii=False)
