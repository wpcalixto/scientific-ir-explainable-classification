#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F17_conciliacao_denominadores.py

File type:
    Script

Purpose:
    Document-level reconciliation of the denominators of the retrieval metrics.

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
    - See docs/file_level_documentation.md (entry F17_conciliacao_denominadores.py).

Outputs:
    - See docs/file_level_documentation.md (entry F17_conciliacao_denominadores.py).

Dependencies:
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F17_conciliacao_denominadores.py

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

import os, sys, re, glob, hashlib, importlib.util, pandas as pd
OUT, TEX = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
F = BIBLIO_BASE + "/resultados/adequacao_20261110/F10_reexec"
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
src = open(f"{F}/13_hst_analise.py", encoding="utf8").read()
ns = {"__file__": f"{F}/13_hst_analise.py"}; exec(compile(src.split("def make_freq_table")[0].split("if __name__")[0], "13_hst_analise.py", "exec"), ns)
count, HST, GEN = ns["_count_term"], ns["HST_TERMS"], ns["GENERAL_TERMS"]
tab = pd.read_csv(f"{F}/dados_classificacao/hst_frequencia_tabela.csv")
tex = open(TEX, encoding="utf8").read(); blk = tex[tex.index(r"\label{hst_freq}"):tex.index(r"\end{tabular}", tex.index(r"\label{hst_freq}"))]
man_N = {d: int(re.search(rf"{lab} \(\$N\$=([\d.]+)\)", blk).group(1).replace(".", "")) for d, lab in [("microarranjos", "Microarranjos"), ("metamateriais", "Metamateriais"), ("radiomica", "Radiômica")]}
res, fontes, conc = [], [], []
for d in ["microarranjos", "metamateriais", "radiomica"]:
    pc, pl = f"{F}/dados_processados/corpus_{d}.csv", f"{F}/dados_processados/lda_doc_topics_{d}.csv"
    C = pd.read_csv(pc, usecols=["openalex_id", "texto_combinado"]); Lr = pd.read_csv(pl, usecols=["openalex_id"])
    fontes += [{"ficheiro": pc, "sha256": h(pc), "linhas": len(C)}, {"ficheiro": pl, "sha256": h(pl), "linhas": len(Lr)}]
    sc, sl = set(C.openalex_id), set(Lr.openalex_id)
    for i in sorted(sc - sl): conc.append({"dominio": d, "openalex_id": i, "presente_em": "só no corpus lido pelo HST"})
    for i in sorted(sl - sc): conc.append({"dominio": d, "openalex_id": i, "presente_em": "só no corpus da LDA"})
    texts = C.texto_combinado.fillna("").str.lower(); g = tab[tab.dominio == d]
    rec = {t: count(texts, t) for t in g.term}
    man_rows = {}
    for t in g.term:
        lab = {"microarranjos": "Microarranjos", "metamateriais": "Metamateriais", "radiomica": "Radiômica"}[d]
        sb = blk[blk.index(lab + " ($N$"):]; nxt = [sb.find(x + " ($N$", 1) for x in ("Microarranjos", "Metamateriais", "Radiômica") if sb.find(x + " ($N$", 1) > 0]; sb = sb[:min(nxt)] if nxt else sb
        m = re.search(rf"& {re.escape(t)}\s*& *([\d.]+) *\\\\", sb); man_rows[t] = int(m.group(1).replace(".", "")) if m else None
    rep = {N: int(((g.freq / N * 100).round(2) == g.freq_pct).sum()) for N in sorted({len(C), man_N[d]})}
    res.append({"dominio": d, "N_manuscrito_hst_freq": man_N[d], "N_corpus_HST_len": len(C), "N_LDA_doc_topics": len(Lr), "ids_unicos_corpus": len(sc), "ids_unicos_LDA": len(sl),
                "ids_so_corpus": len(sc - sl), "ids_so_LDA": len(sl - sc), "freq_recontada_igual_tabela_csv": f"{sum(rec[t] == f for t, f in zip(g.term, g.freq))}/{len(g)}",
                "freq_manuscrito_igual_tabela_csv": f"{sum(man_rows[t] == f for t, f in zip(g.term, g.freq))}/{len(g)}",
                **{f"freq_pct_reproduzida_com_N={N}": f"{v}/{len(g)}" for N, v in rep.items()}})
alvo = {7874, 9965}; achados = []
for p in glob.glob(f"{F}/**/*.csv", recursive=True):
    try:
        n = len(pd.read_csv(p, usecols=[0]))
        if n in alvo: achados.append({"ficheiro": p, "linhas": n})
    except Exception: pass
R = pd.DataFrame(res); R.to_csv(f"{OUT}/conciliacao_resumo.csv", index=False)
pd.DataFrame(conc, columns=["dominio", "openalex_id", "presente_em"]).to_csv(f"{OUT}/conciliacao_por_id.csv", index=False)
pd.DataFrame(fontes).to_csv(f"{OUT}/fontes_sha256.csv", index=False)
pd.DataFrame(achados, columns=["ficheiro", "linhas"]).to_csv(f"{OUT}/artefatos_com_7874_ou_9965_linhas.csv", index=False)
print(R.T.to_string()); print("IDs divergentes:", len(conc)); print("artefatos com 7.874/9.965 linhas:", len(achados), achados[:5])
