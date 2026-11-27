#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F18_matriz_artefatos.py

File type:
    Script

Purpose:
    Builds the matrix linking the result tables and figures to the generating artefacts.

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
    - See docs/file_level_documentation.md (entry F18_matriz_artefatos.py).

Outputs:
    - See docs/file_level_documentation.md (entry F18_matriz_artefatos.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F18_matriz_artefatos.py

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

import os, re, sys, glob, hashlib, pandas as pd, numpy as np
TEX, FIGDIR, OUT = sys.argv[1:4]
B = BIBLIO_BASE + ""; RES = f"{B}/resultados/adequacao_20261110"
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
t = open(TEX, encoding="utf8").read()
s3 = t[t.index(r"\section{Resultados}"):t.index(r"\section{Discussion}")]
subs = [(m.start(), m.group(1)) for m in re.finditer(r"\\subsection\{([^}]*)\}", s3)]
sub_de = lambda pos: next((f"3.{i+1} {n[:40]}" for i, (p, n) in reversed(list(enumerate(subs))) if p <= pos), "3.0")
idx = {}
for p in glob.glob(f"{RES}/**/*.csv", recursive=True):
    if os.path.getsize(p) > 20e6 or re.search(r"replica|doc_topics|edges|NAO_ENVIAR|/auditoria_P01_|/pacote/|saidas_geradas|/pkg/", p): continue
    try: df = pd.read_csv(p, low_memory=False)
    except Exception: continue
    num = df.select_dtypes(include="number").select_dtypes(exclude="bool")
    vals = num.stack().astype(float).to_numpy() if num.shape[1] else np.array([])
    if vals.size == 0 or vals.size > 20000: continue
    reps = set()
    for k in range(0, 5): reps |= set(np.round(vals, k).astype(str)); reps |= set(np.round(vals * 100, k).astype(str))
    idx[p] = reps
def nums(txt):
    out = []
    for m in re.finditer(r"(?<![\w.])(\d{1,3}(?:\.\d{3})+|\d+)(?:\{?,\}?(\d+))?(?![\w])", txt.replace("{,}", ",")):
        ip, dp = m.group(1).replace(".", ""), m.group(2)
        v = float(ip + ("." + dp if dp else ""))
        if dp: out.append(str(round(v, len(dp))))
        elif v >= 100 and not (1990 <= v <= 2030): out.append(str(float(v)))
    return out
CODE = {}
for p in glob.glob(f"{B}/codigo/**/*.py", recursive=True) + glob.glob(f"{B}/resultados/**/*.py", recursive=True):
    try: CODE[p] = open(p, encoding="utf8", errors="ignore").read()
    except Exception: pass
FIGS = {}
for p in glob.glob(f"{B}/resultados/**/*.pdf", recursive=True): FIGS.setdefault(os.path.basename(p), []).append(p)
rows = []
for m in re.finditer(r"\\begin\{(table\*?|figure\*?)\}(.*?)\\end\{\1\}", s3, re.S):
    env, body = m.group(1), m.group(2)
    lab = re.findall(r"\\label\{([^}]*)\}", body); cap = re.search(r"\\caption\{(.*?)\}\s*\n", body, re.S)
    r = {"id": ";".join(lab) or "(sem label)", "tipo": "Tabela" if env.startswith("table") else "Figura", "subseccao": sub_de(m.start()),
         "resultado": re.sub(r"\s+", " ", cap.group(1))[:120] if cap else ""}
    if r["tipo"] == "Figura":
        fs = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]*)\}", body); ests, arts, cods, hs = [], [], [], []
        for f in fs:
            f = f if f.endswith(".pdf") else f + ".pdf"; pm = os.path.join(FIGDIR, os.path.basename(f))
            if not os.path.exists(pm): ests.append("NÃO CONFERIDO"); continue
            hm = h(pm); cand = FIGS.get(os.path.basename(f), [])
            igual = [p for p in cand if h(p) == hm]
            cod = [p for p, c in CODE.items() if os.path.basename(f).replace(".pdf", "") in c][:2]
            ests.append("CONFIRMADO" if igual else ("PARCIAL" if cand else "NÃO CONFERIDO")); arts.append((igual or cand or ["—"])[0]); cods += cod; hs.append(hm[:16])
        r.update({"arquivo_origem": " | ".join(arts), "codigo": " | ".join(sorted(set(cods))) or "—", "hash": " | ".join(hs),
                  "verificacao": "CONFIRMADO" if ests and all(e == "CONFIRMADO" for e in ests) else ("PARCIAL" if any(e != "NÃO CONFERIDO" for e in ests) else "NÃO CONFERIDO"),
                  "divergencia": "" if all(e == "CONFIRMADO" for e in ests) else "figura do manuscrito sem artefato de hash idêntico" if ests else "sem includegraphics"})
    else:
        ns = nums(body[body.find(r"\begin{tabular"):] if r"\begin{tabular" in body else body); u = sorted(set(ns))
        rest, esc = set(u), []
        while rest and len(esc) < 3:
            best, bs, bk = None, 0, 0
            for p, reps in idx.items():
                k = len(rest & reps)
                if k >= 2:
                    s = k / np.log2(2 + len(reps))
                    if s > bs: best, bs, bk = p, s, k
            if not best: break
            esc.append((best, bk)); rest -= idx[best]
        cob = (len(u) - len(rest)) / len(u) if u else 0
        r.update({"arquivo_origem": " | ".join(p for p, _ in esc) or "—", "codigo": "—", "hash": " | ".join(h(p)[:16] for p, _ in esc),
                  "verificacao": "PARCIAL" if (u and len(u) - len(rest) >= 3 and cob >= 0.8) else "NÃO CONFERIDO",
                  "divergencia": (f"{len(u)-len(rest)}/{len(u)} números da tabela localizados nos ficheiros indicados" if u else "tabela sem números distintivos (só texto)")})
    rows.append(r)
M = pd.DataFrame(rows); M.to_csv(OUT, index=False)
print(M.verificacao.value_counts().to_string()); print(len(M), "elementos")
