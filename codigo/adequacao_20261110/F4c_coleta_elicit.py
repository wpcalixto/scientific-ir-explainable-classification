#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F4c_coleta_elicit.py

File type:
    Script

Purpose:
    Elicit API v2 collection (semantic and keyword modes).

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
    - See docs/file_level_documentation.md (entry F4c_coleta_elicit.py).

Outputs:
    - See docs/file_level_documentation.md (entry F4c_coleta_elicit.py).

Dependencies:
    - requests

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F4c_coleta_elicit.py

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

import os, json, csv, time, datetime as dt, requests
OUT = BIBLIO_BASE + "/dados/coleta_v2_20261110/externas"
K = open(os.path.expanduser("~/.config/bibliogenre/elicit_api_key")).read().strip()
H = {"Authorization": f"Bearer {K}", "Content-Type": "application/json"}
URL = "https://elicit.com/api/v2/search/papers"
LOG = open(f"{OUT}/coleta_elicit.log", "a", encoding="utf-8")
def log(m):
    s = f"{dt.datetime.now().isoformat(timespec='seconds')} {m}"; print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
FS = '("feature selection" OR "variable selection" OR "feature ranking" OR "gene selection")'
FSR = '("feature selection" OR "variable selection" OR "feature extraction" OR "feature reduction")'
EV = '(AUC OR ROC OR "area under the curve" OR "area under curve" OR "receiver operating characteristic")'
EVB = '(AUC OR ROC OR "area under the curve" OR "area under curve" OR "receiver operating characteristic" OR classification OR prediction)'
ML = '("machine learning" OR "deep learning" OR "neural network" OR "neural networks" OR "inverse design" OR "surrogate model" OR "surrogate models")'
MLB = '("machine learning" OR "deep learning" OR "neural network" OR "neural networks" OR "inverse design" OR "surrogate model" OR "surrogate models" OR optimization OR optimisation OR "genetic algorithm" OR "evolutionary algorithm")'
EM = '(electromagnetic OR optical OR photonic OR acoustic OR microwave OR terahertz OR plasmonic OR antenna OR antennas OR wave OR waves)'
MOD = '("computed tomography" OR "magnetic resonance imaging" OR MRI OR "positron emission tomography" OR ultrasound OR mammography OR "medical imaging" OR "medical image" OR "medical images")'
E = {
 "microarranjos_busca_A": (
  "Which studies apply feature selection to microarray data and evaluate performance with AUC or ROC curves?",
  f'(microarray OR microarrays) AND {FS} AND {EV}'),
 "microarranjos_busca_B": (
  "Which studies apply feature selection to gene expression, transcriptomic or omics data for classification or prediction?",
  f'("gene expression" OR "expression profiling" OR "expression profile" OR "expression profiles" OR transcriptome OR transcriptomic OR transcriptomics OR "RNA-seq" OR "RNA sequencing" OR omics OR genomic OR genomics OR "expression data") AND {FS} AND {EVB}'),
 "microarranjos_busca_C": (
  "Which studies apply feature or gene selection to gene expression or transcriptomic data and evaluate performance with AUC or ROC curves?",
  f'("gene expression" OR "expression profiling" OR "expression profile" OR "expression profiles" OR transcriptomic OR transcriptomics OR transcriptome OR "RNA-seq" OR "gene signature" OR "gene signatures" OR "omics data") AND {FS} AND {EV}'),
 "radiomica_busca_A": (
  "Which radiomics studies use feature selection or extraction and evaluate performance with AUC or ROC curves?",
  f'(radiomics OR radiomic) AND {FSR} AND {EV}'),
 "radiomica_busca_B": (
  "Which medical imaging studies (CT, MRI, PET, ultrasound, mammography) use feature selection or extraction for classification or prediction?",
  f'("medical imaging" OR "medical image" OR "medical images" OR radiology OR "computed tomography" OR "magnetic resonance imaging" OR MRI OR "positron emission tomography" OR ultrasound OR mammography OR "texture analysis" OR "imaging biomarker" OR "imaging biomarkers" OR "quantitative imaging") AND {FSR} AND {EVB}'),
 "radiomica_busca_C": (
  "Which studies use quantitative image or texture features from CT, MRI, PET, ultrasound or mammography with feature selection and evaluate AUC or ROC?",
  f'(texture OR textural OR "quantitative imaging" OR "imaging biomarker" OR "imaging biomarkers" OR "imaging feature" OR "imaging features" OR "image feature" OR "image features" OR "handcrafted feature" OR "handcrafted features" OR "image-derived") AND {MOD} AND {FSR} AND {EV}'),
 "metamateriais_busca_A": (
  "Which studies use machine learning or deep learning to design electromagnetic, optical or acoustic metamaterials or metasurfaces?",
  f'(metamaterial OR metamaterials OR metasurface OR metasurfaces) AND {EM} AND {ML}'),
 "metamateriais_busca_B": (
  "Which studies use machine learning or optimization algorithms to design periodic, subwavelength or engineered electromagnetic structures such as photonic crystals or frequency selective surfaces?",
  f'("artificial electromagnetic material" OR "artificial electromagnetic materials" OR "engineered material" OR "engineered materials" OR "periodic structure" OR "periodic structures" OR "subwavelength structure" OR "subwavelength structures" OR "frequency selective surface" OR "frequency selective surfaces" OR "photonic crystal" OR "photonic crystals" OR "split-ring resonator" OR "split-ring resonators" OR "electromagnetic structure" OR "electromagnetic structures") AND {EM} AND {MLB}'),
 "metamateriais_busca_C": (
  "Which studies use machine learning or deep learning for the inverse design of subwavelength or resonant electromagnetic structures such as split-ring resonators or frequency selective surfaces?",
  f'("subwavelength structure" OR "subwavelength structures" OR "periodic structure" OR "periodic structures" OR "frequency selective surface" OR "frequency selective surfaces" OR "split-ring resonator" OR "split-ring resonators" OR "artificial electromagnetic material" OR "artificial electromagnetic materials" OR "unit cell" OR "unit cells" OR "electromagnetic response" OR "resonant structure" OR "resonant structures") AND {EM} AND {ML}'),
}
def buscar(body):
    for n in (1000, 500, 300, 100):
        body["maxResults"] = n
        for t in range(5):
            try:
                r = requests.post(URL, headers=H, json=body, timeout=300)
            except Exception as e:
                log(f"  ERRO {type(e).__name__} (tentativa {t+1})"); time.sleep(10 * (t + 1)); continue
            if r.status_code == 200: return n, r.json()
            if r.status_code == 400: break
            log(f"  HTTP {r.status_code} (tentativa {t+1}) {r.text[:150]}")
            time.sleep(330 if r.status_code == 429 else 10 * (t + 1))
        else:
            return n, None
    return None, None
resumo = {}
log("=" * 70); log("ELICIT — INÍCIO")
for tag, (pergunta, string) in E.items():
    for modo, body in (("semantico", {"query": pergunta, "searchMode": "semantic", "corpus": "elicit", "filters": {"maxYear": 2025}}),
                       ("keyword", {"query": string, "searchMode": "keyword", "corpus": "elicit"})):
        n, j = buscar(dict(body))
        if j is None:
            log(f"[{modo} {tag}] FALHOU"); resumo[f"{modo}|{tag}"] = None; continue
        json.dump({"pedido": {k: v for k, v in body.items()}, "maxResults": n, "resposta": j},
                  open(f"{OUT}/elicit_bruto_{modo}_{tag}.json", "w"), ensure_ascii=False)
        rows = []
        for i, p in enumerate(j.get("papers", []), 1):
            rows.append({"rank": i, "elicit_id": p.get("elicitId", ""), "doi": (p.get("doi") or "").lower(),
                         "pmid": p.get("pmid") or "", "title": p.get("title") or "", "year": p.get("year") or "",
                         "venue": p.get("venue") or "", "cited_by": p.get("citedByCount") or "",
                         "quartil": p.get("journalQuartile") or "", "abstract": p.get("abstract") or ""})
        ate2025 = [r for r in rows if not r["year"] or int(r["year"]) <= 2025]
        if rows:
            with open(f"{OUT}/elicit_{modo}_{tag}.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(ate2025)
        resumo[f"{modo}|{tag}"] = {"maxResults": n, "devolvidos": len(rows), "ate_2025": len(ate2025),
                                   "com_doi": sum(1 for r in ate2025 if r["doi"]), "warnings": j.get("warnings")}
        log(f"[{modo} {tag}] maxResults={n} devolvidos={len(rows)} ate2025={len(ate2025)} warnings={j.get('warnings')}")
        time.sleep(2)
json.dump({"data": dt.datetime.now().isoformat(timespec="seconds"), "resumo": resumo}, open(f"{OUT}/contagens_elicit.json", "w"), indent=1, ensure_ascii=False)
log("ELICIT — FIM")
