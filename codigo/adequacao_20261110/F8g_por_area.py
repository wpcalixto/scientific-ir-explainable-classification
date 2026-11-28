#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F8g_por_area.py

File type:
    Script

Purpose:
    Breaks down the human-LLM agreement by assessor area.

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
    - See docs/file_level_documentation.md (entry F8g_por_area.py).

Outputs:
    - See docs/file_level_documentation.md (entry F8g_por_area.py).

Dependencies:
    - numpy
    - pandas
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F8g_por_area.py

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

import pandas as pd, numpy as np, itertools
from sklearn.metrics import cohen_kappa_score as ck
O=BIBLIO_BASE + "/resultados/adequacao_20261110/F8_julgamento/analise_fichas_reais_20261112_13fichas"
D=pd.read_csv(f"{O}/notas_humanos_LLM.csv")
AV=list("WUVTSRQPONMLK")
area={"Biomedicina":list("TSRQ"),"Física":list("PON"),"EngComp(IA)":list("MLK"),"W,U,V":list("WUV")}
kw=lambda a,b:ck(a,b,weights="quadratic")
r=[]
for k in AV:
    s=D[D[k].notna()]; outros=[x for x in AV if x!=k]
    m=s[outros].median(axis=1).apply(np.floor).astype(int)
    r.append({"av":k,"kw_vs_outros_humanos":kw(s[k].astype(int),m),"kw_vs_LLM":kw(s[k].astype(int),s.consenso),
              "exata_outros":(s[k]==m).mean(),"exata_LLM":(s[k]==s.consenso).mean()})
R=pd.DataFrame(r); print(R.round(3).to_string()); print("media",R.mean(numeric_only=True).round(3).to_dict())
for c in ["haiku","gpt","gemini","consenso"]: print(c,"vs H_med kw",round(kw(D[c],D.H_med),3),"exata",round((D[c]==D.H_med).mean(),3))
rows=[]
for a,ks in area.items():
    s=D[D[ks].notna().any(axis=1)]; m=s[ks].median(axis=1).apply(np.floor).astype(int)
    pares=[kw(*[s[[x,y]].dropna()[z].astype(int) for z in (x,y)]) for x,y in itertools.combinations(ks,2)]
    P=[]
    for _,x in s.assign(m=m).iterrows():
        for l in x.listas.split(";"): P.append({"dom":x.dominio,"lista":l.strip(),"m":x.m,"llm":x.consenso})
    P=pd.DataFrame(P); P["est"]=P.lista.str.extract(r"_([ABC])(?:_|$)")
    Q=P.groupby(["dom","lista","est"]).agg(h=("m",lambda v:(v==2).mean()),l=("llm",lambda v:(v==2).mean())).reset_index()
    S=Q.groupby(["dom","est"]).h.mean().unstack()
    rows.append({"area":a,"n_docs":len(s),"kw_intra_mediana":np.median(pares),"kw_med_vs_LLM":kw(m,s.consenso),"exata_LLM":(m==s.consenso).mean(),
                 "ordem":";".join(f"{d[:3]}:{''.join(S.loc[d].sort_values(ascending=False).index)}" for d in S.index),
                 "P10_A":S["A"].round(2).tolist(),"P10_B":S["B"].round(2).tolist(),"P10_C":S["C"].round(2).tolist()})
pd.set_option("display.width",250); print(pd.DataFrame(rows).round(3).to_string())
