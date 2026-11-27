#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F6a_baixar_benchmarks.py

File type:
    Script

Purpose:
    Downloads the public screening benchmarks (Cohen 2006 and Howard 2016 through SYNERGY).

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
    - See docs/file_level_documentation.md (entry F6a_baixar_benchmarks.py).

Outputs:
    - See docs/file_level_documentation.md (entry F6a_baixar_benchmarks.py).

Dependencies:
    - Python standard library only

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F6a_baixar_benchmarks.py

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

import os, csv, io, json, time, hashlib, urllib.request, urllib.parse, xml.etree.ElementTree as ET
OUT = BIBLIO_BASE + "/dados/externos/benchmarks_triagem"
os.makedirs(f"{OUT}/ids", exist_ok=True)
RAW = "https://raw.githubusercontent.com/asreview/synergy-dataset/master/datasets"
API = "https://api.github.com/repositories/166429624/git/trees/HEAD?recursive=1"
LOG = open(f"{OUT}/baixar.log", "a")
def log(m): s = time.strftime("%Y-%m-%dT%H:%M:%S ") + m; print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
def get(url, data=None, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": "bibliometria-benchmark/1.0"})
            return urllib.request.urlopen(req, timeout=120).read()
        except Exception as e:
            log(f"  erro {type(e).__name__} {url[:80]} (tentativa {i+1})"); time.sleep(5 * (i + 1))
    return None
OAK = open(os.path.expanduser("~/.config/bibliogenre/openalex")).read().strip() if os.path.exists(os.path.expanduser("~/.config/bibliogenre/openalex")) else ""
tree = json.loads(get(API))["tree"]
fich = [x["path"] for x in tree if x["type"] == "blob" and x["path"].endswith("_ids.csv")
        and (x["path"].startswith("datasets/Cohen_2006/") or x["path"].startswith("datasets/Howard_2016/"))]
log(f"INÍCIO — {len(fich)} conjuntos")
for p in fich:
    nome = os.path.basename(p)[:-8]; dst = f"{OUT}/{nome}.csv"
    if os.path.exists(dst): log(f"[{nome}] já existe"); continue
    b = get(f"{RAW}/{p[len('datasets/'):]}"); open(f"{OUT}/ids/{nome}_ids.csv", "wb").write(b)
    rows = list(csv.DictReader(io.StringIO(b.decode())))
    pm = {r["pmid"].rsplit("/", 1)[-1]: r for r in rows if r.get("pmid")}
    info = {}
    ks = list(pm)
    for i in range(0, len(ks), 200):
        x = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                urllib.parse.urlencode({"db": "pubmed", "retmode": "xml", "id": ",".join(ks[i:i+200])}).encode())
        time.sleep(0.4)
        if not x: continue
        for a in ET.fromstring(x).iter("PubmedArticle"):
            pid = a.findtext(".//PMID")
            tit = "".join(a.find(".//ArticleTitle").itertext()) if a.find(".//ArticleTitle") is not None else ""
            ab = " ".join("".join(t.itertext()) for t in a.findall(".//Abstract/AbstractText"))
            yr = a.findtext(".//PubDate/Year") or (a.findtext(".//PubDate/MedlineDate") or "")[:4]
            info[pid] = (tit, ab, yr)
    out = []
    for r in rows:
        pid = (r.get("pmid") or "").rsplit("/", 1)[-1]
        t, ab, yr = info.get(pid, ("", "", ""))
        out.append({"pmid": pid, "doi": r.get("doi", ""), "openalex_id": r.get("openalex_id", ""), "label_included": r["label_included"],
                    "title": t, "abstract": ab, "year": yr, "fonte": "pubmed" if t else ""})
    falta = [o for o in out if not o["abstract"] and o["openalex_id"]]
    for i in range(0, len(falta), 50):
        ch = falta[i:i+50]
        q = {"filter": "openalex_id:" + "|".join(o["openalex_id"].rsplit("/", 1)[-1] for o in ch), "per-page": 50,
             "select": "id,title,abstract_inverted_index,publication_year"}
        if OAK: q["api_key"] = OAK
        x = get("https://api.openalex.org/works?" + urllib.parse.urlencode(q)); time.sleep(0.15)
        if not x: continue
        m = {w["id"]: w for w in json.loads(x).get("results", [])}
        for o in ch:
            w = m.get(o["openalex_id"])
            if not w: continue
            inv = w.get("abstract_inverted_index") or {}
            pos = sorted((p_, t_) for t_, ps in inv.items() for p_ in ps)
            ab = " ".join(t_ for _, t_ in pos)
            if ab: o["abstract"] = ab; o["fonte"] = (o["fonte"] + "+openalex").strip("+")
            if not o["title"]: o["title"] = w.get("title") or ""
            if not o["year"]: o["year"] = str(w.get("publication_year") or "")
    with open(dst, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    log(f"[{nome}] n={len(out)} incluidos={sum(o['label_included'] == '1' for o in out)} "
        f"com_titulo={sum(bool(o['title']) for o in out)} com_resumo={sum(bool(o['abstract']) for o in out)}")
with open(f"{OUT}/SHA256SUMS", "w") as f:
    for n in sorted(os.listdir(OUT)):
        if n.endswith(".csv"): f.write(hashlib.sha256(open(f"{OUT}/{n}", "rb").read()).hexdigest() + "  " + n + "\n")
log("FIM")
