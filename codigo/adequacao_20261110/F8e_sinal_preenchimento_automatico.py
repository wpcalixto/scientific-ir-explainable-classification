#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F8e_sinal_preenchimento_automatico.py

File type:
    Script

Purpose:
    Checks the returned human sheets for signs of automatic filling.

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
    - See docs/file_level_documentation.md (entry F8e_sinal_preenchimento_automatico.py).

Outputs:
    - See docs/file_level_documentation.md (entry F8e_sinal_preenchimento_automatico.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F8e_sinal_preenchimento_automatico.py

Portability notes:
    All paths are resolved relative to the package base directory given by the BIBLIO_BASE environment variable
    (default: the package root, two levels above codigo/adequacao_20261110/). No machine-specific path is required.
    API keys, when needed, are read from ~/.config/bibliogenre/ and ~/.config/bibliometria/ and are not part of the package.

Reproducibility notes:
    Environment pinned in requirements.txt and environment/. Seeds and frozen parameters are written in the code and
    summarized in docs/parameters.md.

Warnings:
    Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.
"""

import os as _bb_os
BIBLIO_BASE = _bb_os.environ.get("BIBLIO_BASE") or _bb_os.path.abspath(
    _bb_os.path.join(_bb_os.path.dirname(_bb_os.path.abspath(__file__)), "..", ".."))

import pandas as pd, numpy as np, hashlib, itertools
R=BIBLIO_BASE + "/resultados/adequacao_20261110"; F=f"{R}/F8_julgamento/fichas_reais_20261111"
mapa=pd.read_csv(f"{R}/F8_julgamento/pool_mapa_NAO_ENVIAR.csv",keep_default_na=False)
D=mapa[["doc_id","dominio","chave"]].copy()
for k in "WUVTSR": D=D.merge(pd.read_csv(f"{F}/ficha_{k}.csv",keep_default_na=False)[["doc_id","nota"]].rename(columns={"nota":k}),on="doc_id",how="left")
D["jid"]=[f"{d[:2]}_{hashlib.md5(c.encode()).hexdigest()[:12]}" for d,c in zip(D.dominio,D.chave)]
L=pd.read_csv(f"{R}/F7_painel_llm/analise/J_notas_3llm.csv",keep_default_na=False)
D=D.merge(L[["jid","haiku","gpt","gemini","consenso"]],on="jid",how="left")
for c in ["haiku","gpt","gemini","consenso"]: D[c]=pd.to_numeric(D[c]).round()
def kw(a,b):
    a=np.asarray(a,int);b=np.asarray(b,int);O=np.zeros((3,3))
    for x,y in zip(a,b):O[x,y]+=1
    W=np.array([[(i-j)**2 for j in range(3)] for i in range(3)])/4;E=np.outer(O.sum(1),O.sum(0))/O.sum()
    return 1-(W*O).sum()/(W*E).sum()
rows=[]
for k in "WUVTSR":
    g=D.dropna(subset=[k]); r={"ficha":k,"n":len(g)}
    for c in ["haiku","gpt","gemini","consenso"]: r[f"igual_{c}"]=round((g[k]==g[c]).mean(),3); r[f"kw_{c}"]=round(kw(g[k],g[c]),3)
    r["dist_0/1/2"]="/".join(str(int((g[k]==v).sum())) for v in (0,1,2)); rows.append(r)
print(pd.DataFrame(rows).to_string(index=False))
print("pares humanos kw:"); print({f"{a}{b}":round(kw(*[D.dropna(subset=[a,b])[x] for x in (a,b)]),3) for a,b in itertools.combinations("WUVTSR",2)})
for c in ["haiku","gpt","gemini","consenso"]: print(c,"/".join(str(int((D[c]==v).sum())) for v in (0,1,2)))
