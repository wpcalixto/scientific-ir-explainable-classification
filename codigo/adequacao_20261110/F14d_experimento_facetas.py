#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F14d_experimento_facetas.py

File type:
    Script

Purpose:
    Controlled facet experiment: queries derived from the original ones are executed in OpenAlex to isolate the effect of each facet.

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
    - See docs/file_level_documentation.md (entry F14d_experimento_facetas.py).

Outputs:
    - See docs/file_level_documentation.md (entry F14d_experimento_facetas.py).

Dependencies:
    - requests

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F14d_experimento_facetas.py

Portability notes:
    All paths are resolved relative to the package base directory given by the BIBLIO_BASE environment variable
    (default: the package root, two levels above codigo/adequacao_20261110/). No machine-specific path is required.
    API keys, when needed, are read from ~/.config/bibliogenre/ and ~/.config/bibliometria/ and are not part of the package.

Reproducibility notes:
    Environment pinned in requirements.txt and environment/. Seeds and frozen parameters are written in the code and
    summarized in docs/parameters.md.

Warnings:
    Re-running queries the live APIs and needs API keys; results will differ from the archived collection of 2026-11-10 (use the files in dados/).
"""

import os as _bb_os
BIBLIO_BASE = _bb_os.environ.get("BIBLIO_BASE") or _bb_os.path.abspath(
    _bb_os.path.join(_bb_os.path.dirname(_bb_os.path.abspath(__file__)), "..", ".."))

import os, re, json, gzip, time, datetime as dt, requests
B = BIBLIO_BASE + ""; OUT = f"{B}/dados/experimento_facetas_20261112"
CFG = json.load(open(f"{B}/codigo/adequacao_20261110/consultas_v2.json")); FC = CFG["filtros_comuns"]
KEY = open(os.path.expanduser("~/.config/bibliogenre/openalex")).read().strip()
LOG = open(f"{OUT}/execucao.log", "a")
def log(m): LOG.write(f"{dt.datetime.now().isoformat(timespec='seconds')} {m}\n"); LOG.flush()
def grupos(q): return [g.strip() for g in re.split(r"\)\s+AND\s+\(|(?<=[a-z\"])\s+AND\s+\(|\)\s+AND\s+(?=[a-z])", q.strip())]
def par(g): g = g.strip(); return g if g.startswith("(") and g.endswith(")") else f"({g})"
def junta(gs): return " AND ".join(par(g.strip("()")) if " OR " in g else g.strip("()") for g in gs)
V = {}
for d, e in CFG["consultas"].items():
    a, b, c = grupos(e["busca_A"]), grupos(e["busca_B"]), grupos(e["busca_C"])
    assert a[1:-1] == b[1:-1], (d, "facetas intermédias de A e B diferem")
    v = {"A_orig": e["busca_A"], "B_orig": e["busca_B"], "C_orig": e["busca_C"],
         "A_ref": junta(a),
         "A_faceta_relaxada": junta([a[0]] + a[1:-1] + [b[-1]]),
         "B_faceta_de_A": junta([b[0]] + a[1:-1] + [a[-1]]),
         "B_ref": junta(b),
         "C_objeto_de_C": junta([c[0]] + a[1:-1] + [a[-1]]),
         "uniao_HST_ou_amplos": junta(["(" + a[0].strip("()") + " OR " + b[0].strip("()") + ")"] + a[1:-1] + [a[-1]])}
    V[d] = v
json.dump(V, open(f"{OUT}/consultas.json", "w"), indent=1, ensure_ascii=False)
def get(params):
    for t in range(6):
        try:
            r = requests.get("https://api.openalex.org/works", params={**params, "api_key": KEY}, timeout=120,
                             headers={"User-Agent": "bibliometria-experimento/1.0"})
            if r.status_code == 200: return r.json()
            log(f"HTTP {r.status_code} {r.text[:120]}")
        except Exception as ex: log(f"erro {ex}")
        time.sleep(5 * (t + 1))
    raise RuntimeError("falha")
cont = {}
log("=" * 60 + " INÍCIO")
for d, v in V.items():
    for nome, q in v.items():
        filt = f"title_and_abstract.search:{q},{FC}"; cur = "*"; n = 0; total = None
        with gzip.open(f"{OUT}/{d}_{nome}.jsonl.gz", "wt", encoding="utf-8") as f:
            while cur:
                j = get({"filter": filt, "per-page": 200, "cursor": cur, "select": "id,doi,title,publication_year,abstract_inverted_index"})
                total = j["meta"]["count"]; cur = j["meta"].get("next_cursor")
                for w in j["results"]: f.write(json.dumps(w, ensure_ascii=False) + "\n"); n += 1
                if not j["results"]: break
        cont[f"{d}|{nome}"] = {"contagem_api": total, "obtidos": n, "data": dt.date.today().isoformat()}
        log(f"{d} {nome} api={total} obtidos={n}")
json.dump(cont, open(f"{OUT}/contagens.json", "w"), indent=1)
log("FIM")
