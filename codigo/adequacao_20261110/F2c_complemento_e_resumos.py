#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F2c_complemento_e_resumos.py

File type:
    Script

Purpose:
    Complementary collection pass for strategies with cursor losses and abstract completion.

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
    - See docs/file_level_documentation.md (entry F2c_complemento_e_resumos.py).

Outputs:
    - See docs/file_level_documentation.md (entry F2c_complemento_e_resumos.py).

Dependencies:
    - requests

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F2c_complemento_e_resumos.py

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

import csv, os, sys, json, gzip, glob, time, shutil, importlib.util, urllib.parse, datetime as dt
import requests
S = BIBLIO_BASE + "/codigo/adequacao_20261110"
spec = importlib.util.spec_from_file_location("f2a", f"{S}/F2a_coleta_openalex_v2.py")
f2a = importlib.util.module_from_spec(spec); spec.loader.exec_module(f2a)
OUT, CFG, log, get, row, SELECT = f2a.OUT, f2a.CFG, f2a.log, f2a.get, f2a.row, f2a.SELECT
csv.field_size_limit(10**9)
S2KEY = open(os.path.expanduser("~/.config/bibliogenre/s2_api_key")).read().strip()

def ler(f): return list(csv.DictReader(open(f, encoding="utf-8")))
def gravar(f, rows):
    with open(f, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

log("=" * 70); log("F2c — COMPLEMENTO E RESUMOS — INÍCIO")
resumo = json.load(open(f"{OUT}/resumo_coleta_v2.json"))
dados = {}
for dom, ests in CFG["consultas"].items():
    for est, q in ests.items():
        f = f"{OUT}/{dom}_{est}.csv"
        shutil.copy(f, f.replace(".csv", "_antes_F2c.csv"))
        rows, vistos = [], set()
        for r in ler(f):
            if r["openalex_id"] not in vistos: vistos.add(r["openalex_id"]); rows.append(r)
        filt = f"title_and_abstract.search:{q},{CFG['filtros_comuns']}"
        esperado = get({"filter": filt, "per-page": 1})["meta"]["count"]
        passagem = 0
        while len(vistos) < esperado and passagem < 3:
            passagem += 1; novos = 0; cursor = "*"
            with gzip.open(f"{OUT}/raw_{dom}_{est}_complemento{passagem}.jsonl.gz", "wt", encoding="utf-8") as raw:
                while cursor:
                    d = get({"filter": filt, "per-page": 200, "cursor": cursor, "select": SELECT})
                    for w in d["results"]:
                        if w["id"] not in vistos:
                            raw.write(json.dumps(w, ensure_ascii=False) + "\n")
                            vistos.add(w["id"]); rows.append({k: ("" if v is None else v) for k, v in row(w, dom, est).items()}); novos += 1
                    cursor = d["meta"].get("next_cursor")
                    if not d["results"]: break
                    time.sleep(0.12)
            log(f"[{dom}/{est}] passagem {passagem}: +{novos} novos -> {len(vistos)} de {esperado}")
        estado = "OK" if len(vistos) == esperado else ("ACIMA" if len(vistos) > esperado else "ABAIXO")
        log(f"[{dom}/{est}] final unicos={len(vistos)} esperado={esperado} {estado}")
        resumo["estrategias"][f"{dom}/{est}"].update({"unicos_final": len(vistos), "esperado_F2c": esperado, "estado_F2c": estado})
        dados[f] = rows

falta = sorted({r["doi"] for rows in dados.values() for r in rows if not r["abstract"] and r["doi"]})
log(f"Resumos: DOIs sem resumo = {len(falta)}")
achados = {}
for i in range(0, len(falta), 200):
    lote = falta[i:i + 200]
    for t in range(8):
        try:
            r = requests.post("https://api.semanticscholar.org/graph/v1/paper/batch", params={"fields": "abstract"},
                              json={"ids": [f"DOI:{d}" for d in lote]}, headers={"x-api-key": S2KEY}, timeout=120)
            if r.status_code == 200:
                for d, p in zip(lote, r.json()):
                    if p and p.get("abstract"): achados[d] = ("semantic_scholar", p["abstract"])
                break
            log(f"  S2 HTTP {r.status_code} lote {i // 200} tentativa {t + 1}")
        except Exception as e:
            log(f"  S2 ERRO {type(e).__name__} lote {i // 200} tentativa {t + 1}")
        time.sleep(min(120, 5 * 2 ** t))
    time.sleep(3)
log(f"Resumos: Semantic Scholar encontrou {len(achados)}")
resto = [d for d in falta if d not in achados]
n_epmc = 0
for k, d in enumerate(resto):
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&pageSize=1&query="
           + urllib.parse.quote(f'DOI:"{d}"'))
    for t in range(4):
        try:
            r = requests.get(url, timeout=60, headers={"User-Agent": "bibliometria-coleta/2.0"})
            if r.status_code == 200:
                res = r.json().get("resultList", {}).get("result", [])
                if res and res[0].get("abstractText"):
                    achados[d] = ("europe_pmc", res[0]["abstractText"]); n_epmc += 1
                break
        except Exception:
            pass
        time.sleep(2 * (t + 1))
    time.sleep(0.15)
    if k % 500 == 0: log(f"  Europe PMC {k}/{len(resto)} (encontrados {n_epmc})")
log(f"Resumos: Europe PMC encontrou {n_epmc}")
tot = {}
for f, rows in dados.items():
    for r in rows:
        if not r["abstract"] and r["doi"] in achados:
            r["abstract_fonte"], r["abstract"] = achados[r["doi"]]
    gravar(f, rows)
    sem = sum(1 for r in rows if not r["abstract"])
    tot[os.path.basename(f)] = {"linhas": len(rows), "sem_resumo": sem}
    log(f"  {os.path.basename(f)}: linhas={len(rows)} sem resumo={sem} ({sem / len(rows):.1%})")
resumo["resumos_F2c"] = tot; resumo["fim_F2c"] = dt.datetime.now().isoformat(timespec="seconds")
json.dump(resumo, open(f"{OUT}/resumo_coleta_v2.json", "w"), indent=1, ensure_ascii=False)
log("F2c — FIM")
