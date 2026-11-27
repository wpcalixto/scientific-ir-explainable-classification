#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F11b_mapa_tres_comunidades.py

File type:
    Script

Purpose:
    Builds the thematic map with three communities per domain from the keyword co-occurrence graph.

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
    - See docs/file_level_documentation.md (entry F11b_mapa_tres_comunidades.py).

Outputs:
    - See docs/file_level_documentation.md (entry F11b_mapa_tres_comunidades.py).

Dependencies:
    - community
    - networkx
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F11b_mapa_tres_comunidades.py

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

import os, json, importlib.util, numpy as np, pandas as pd
import community as community_louvain, networkx as nx
S = BIBLIO_BASE + "/resultados/adequacao_20261110/F10_reexec"
OUT = BIBLIO_BASE + "/resultados/adequacao_20261110/F11_figuras/mapa3"; os.makedirs(OUT, exist_ok=True)
sp = importlib.util.spec_from_file_location("m17", f"{S}/17_mapa_tematico.py"); m17 = importlib.util.module_from_spec(sp); sp.loader.exec_module(m17)
al = pd.read_csv(f"{S}/dados_openalex/consolidado_todos_dominios.csv", low_memory=False).drop_duplicates(["dominio", "openalex_id"])
info = {}
for d in m17.DOMAINS:
    G0, _ = m17.build_graph(m17.parse_concepts(al[al.dominio == d]["concepts"]))
    G = nx.Graph(); G.add_nodes_from(sorted(G0.nodes(data=True))); G.add_edges_from(sorted((min(u, v), max(u, v), w) for u, v, w in G0.edges(data=True)))
    grade = sorted(np.round(np.arange(0.5, 3.0001, 0.05), 2), key=lambda g: (abs(g - 1), g)); esc = None
    for g in grade:
        p = community_louvain.best_partition(G, weight="weight", resolution=float(g), random_state=42)
        if len(set(p.values())) == 3: esc = (float(g), p); break
    assert esc, f"nenhuma resolução dá 3 comunidades em {d}"
    g, p = esc; M = m17.callon_metrics(G, p).sort_values("freq_total", ascending=False).reset_index(drop=True)
    ren = {old: i for i, old in enumerate(M.community)}; M["community"] = range(3); M.to_csv(f"{OUT}/mapa_tematico_{d}.csv", index=False)
    pd.DataFrame({"conceito": list(p), "comunidade": [ren[p[n]] for n in p]}).sort_values(["comunidade", "conceito"]).to_csv(f"{OUT}/particao_{d}.csv", index=False)
    info[d] = {"resolucao": g, "modularidade": float(community_louvain.modularity(p, G, weight="weight")), "nos": G.number_of_nodes(),
               "arestas": G.number_of_edges(), "tamanhos": M.n_nodes.tolist()}
    print(d, info[d]); print(M[["community", "label", "centrality", "density", "n_nodes"]].to_string(index=False))
json.dump(info, open(f"{OUT}/resolucao.json", "w"), indent=1)
