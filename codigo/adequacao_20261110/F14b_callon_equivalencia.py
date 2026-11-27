#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F14b_callon_equivalencia.py

File type:
    Script

Purpose:
    Thematic map with the Callon equivalence index, without new data collection.

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
    - See docs/file_level_documentation.md (entry F14b_callon_equivalencia.py).

Outputs:
    - See docs/file_level_documentation.md (entry F14b_callon_equivalencia.py).

Dependencies:
    - community
    - networkx
    - numpy
    - pandas
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F14b_callon_equivalencia.py

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

import os, json, importlib.util, numpy as np, pandas as pd, networkx as nx, community as cl
from sklearn.metrics import adjusted_rand_score as ari
R = BIBLIO_BASE + "/resultados/adequacao_20261110"; S = f"{R}/F10_reexec"
O = f"{R}/F14_complementares_01A/callon_equivalencia"; os.makedirs(O, exist_ok=True)
sp = importlib.util.spec_from_file_location("m17", f"{S}/17_mapa_tematico.py"); m17 = importlib.util.module_from_spec(sp); sp.loader.exec_module(m17)
al = pd.read_csv(f"{S}/dados_openalex/consolidado_todos_dominios.csv", low_memory=False).drop_duplicates(["dominio", "openalex_id"])
def quad(c, d, mc, md):
    return {(True, True): "Motor themes", (True, False): "Basic themes", (False, True): "Niche themes", (False, False): "Emerging or declining themes"}[(c >= mc, d >= md)]
def callon(E, part):
    rows = []
    for h in sorted(set(part.values())):
        nos = [n for n in E if part[n] == h]; ns = set(nos)
        ext = sum(d["weight"] for u, v, d in E.edges(data=True) if (u in ns) != (v in ns))
        inn = sum(d["weight"] for u, v, d in E.edges(data=True) if u in ns and v in ns)
        top = sorted(nos, key=lambda n: -E.nodes[n]["freq"])[:3]
        rows.append({"comunidade": h, "n_conceitos": len(nos), "freq_total": int(sum(E.nodes[n]["freq"] for n in nos)),
                     "centralidade": 10 * ext, "densidade": 100 * inn / len(nos), "rotulo": ", ".join(top)})
    M = pd.DataFrame(rows).sort_values("freq_total", ascending=False).reset_index(drop=True)
    mc, md = M.centralidade.median(), M.densidade.median(); M["quadrante"] = [quad(c, d, mc, md) for c, d in zip(M.centralidade, M.densidade)]
    return M
res = {}
for d in m17.DOMAINS:
    G0, _ = m17.build_graph(m17.parse_concepts(al[al.dominio == d]["concepts"]))
    E = nx.Graph(); E.add_nodes_from(sorted(G0.nodes(data=True)))
    for u, v, w in sorted((min(u, v), max(u, v), w["weight"]) for u, v, w in G0.edges(data=True)):
        E.add_edge(u, v, weight=w * w / (G0.nodes[u]["freq"] * G0.nodes[v]["freq"]), c=w)
    nodes = sorted(E)
    pub = pd.read_csv(f"{R}/F11_figuras/mapa3/particao_{d}.csv").set_index("conceito").comunidade.to_dict()
    Mp = callon(E, pub); Mp.to_csv(f"{O}/mapa_{d}_publicada.csv", index=False)
    raw = pd.read_csv(f"{R}/F11_figuras/mapa3/mapa_tematico_{d}.csv")
    ref = cl.best_partition(E, weight="weight", resolution=1.0, random_state=42)
    Mn = callon(E, ref); Mn.to_csv(f"{O}/mapa_{d}_nova.csv", index=False)
    ren = {h: i for i, h in enumerate(Mn.comunidade)}
    pd.DataFrame({"conceito": nodes, "comunidade": [ren[ref[n]] for n in nodes]}).sort_values(["comunidade", "conceito"]).to_csv(f"{O}/particao_nova_{d}.csv", index=False)
    grade = {}
    for g in np.round(np.arange(0.5, 2.0001, 0.05), 2):
        p = cl.best_partition(E, weight="weight", resolution=float(g), random_state=42); grade[str(g)] = len(set(p.values()))
    ncs, aris = [], []
    for s in range(200):
        p = cl.best_partition(E, weight="weight", resolution=1.0, random_state=s); ncs.append(len(set(p.values())))
        aris.append(ari([ref[n] for n in nodes], [p[n] for n in nodes]))
    res[d] = {"n_com_gamma1": len(set(ref.values())), "Q_equivalencia": round(cl.modularity(ref, E, weight="weight"), 4),
              "Q_particao_publicada_no_grafo_equivalencia": round(cl.modularity(pub, E, weight="weight"), 4),
              "ARI_nova_vs_publicada": round(ari([ref[n] for n in nodes], [pub[n] for n in nodes]), 3),
              "n_com_por_gamma": grade, "sementes_mesmo_n_pct": round(100 * np.mean(np.array(ncs) == len(set(ref.values()))), 1),
              "n_com_sementes": {str(k): int(v) for k, v in zip(*np.unique(ncs, return_counts=True))},
              "ARI_sementes_mediana": round(float(np.median(aris)), 3), "ARI_sementes_p10": round(float(np.percentile(aris, 10)), 3),
              "quadrantes_publicada_bruto": dict(zip(raw.community.astype(str), [m17.assign_quadrant(r, raw.centrality.median(), raw.density.median()) for _, r in raw.iterrows()])),
              "quadrantes_publicada_equivalencia": dict(zip(Mp.comunidade.astype(str), Mp.quadrante)),
              "nova": Mn[["comunidade", "n_conceitos", "rotulo", "centralidade", "densidade", "quadrante"]].round(3).to_dict("records")}
    print("==", d, {k: v for k, v in res[d].items() if k not in ("n_com_por_gamma", "nova")})
    print(Mp[["comunidade", "n_conceitos", "rotulo", "centralidade", "densidade", "quadrante"]].round(3).to_string(index=False))
    print(Mn[["comunidade", "n_conceitos", "rotulo", "centralidade", "densidade", "quadrante"]].round(3).to_string(index=False))
    print("gamma:", {k: v for k, v in grade.items() if k in ("0.5", "0.75", "1.0", "1.25", "1.5", "2.0")})
json.dump(res, open(f"{O}/resumo.json", "w"), indent=1, ensure_ascii=False)
