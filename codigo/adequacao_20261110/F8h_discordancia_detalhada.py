#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F8h_discordancia_detalhada.py

File type:
    Script

Purpose:
    Detailed human-LLM disagreement by sheet, domain and type of disagreement.

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
    - See docs/file_level_documentation.md (entry F8h_discordancia_detalhada.py).

Outputs:
    - See docs/file_level_documentation.md (entry F8h_discordancia_detalhada.py).

Dependencies:
    - numpy
    - pandas
    - sklearn

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F8h_discordancia_detalhada.py

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

import pandas as pd, numpy as np
from sklearn.metrics import cohen_kappa_score as ck
B=BIBLIO_BASE + "/resultados/adequacao_20261110/F8_julgamento"
O=f"{B}/analise_fichas_reais_20261112_13fichas"
D=pd.read_csv(f"{O}/notas_humanos_LLM.csv"); AV=list("WUVTSRQPONMLK")
area={**{k:"Bio" for k in "TSRQ"},**{k:"Fís" for k in "PON"},**{k:"Eng" for k in "MLK"},**{k:"WUV" for k in "WUV"}}
kw=lambda a,b:ck(a,b,weights="quadratic") if len(set(a)|set(b))>1 else np.nan
D["estr"]=D.listas.str.extract(r"_([ABC])(?:_|$)")[0]
rows=[]
for k in AV:
    for dom,g in [("todos",D)]+list(D.groupby("dominio")):
        s=g[g[k].notna()]
        if len(s)==0: continue
        h=s[k].astype(int); l=s.consenso; o=s[[x for x in AV if x!=k]].median(axis=1).apply(np.floor).astype(int); d=h-l
        rows.append({"ficha":k,"area":area[k],"dominio":dom,"n":len(s),"kw_LLM":kw(h,l),"kw_outros":kw(h,o),"iguais_LLM":(d==0).mean(),
            "mais_severo_1":((d==-1)).mean(),"mais_generoso_1":(d==1).mean(),"inv_2para0":(d==-2).sum(),"inv_0para2":(d==2).sum(),
            "media_humano":h.mean(),"media_LLM":l.mean(),"pct2":(h==2).mean(),"pct0":(h==0).mean()})
T=pd.DataFrame(rows); T.round(3).to_csv(f"{O}/discordancia_por_ficha_dominio.csv",index=False)
pd.set_option("display.width",250)
print(T[T.dominio=="todos"].sort_values("kw_LLM").round(2).to_string(index=False))
print(T[T.dominio!="todos"].pivot(index="ficha",columns="dominio",values="kw_LLM").loc[AV].round(2).to_string())
inv=pd.DataFrame({k:((D[k]==0)&(D.consenso==2)) for k in AV}).sum(1)
top=D.assign(n_inv=inv,n0=(D[AV]==0).sum(1)).sort_values("n_inv",ascending=False).head(8)
print(top[["doc_id","dominio","consenso","H_med","n_inv","n0","titulo"]].assign(titulo=lambda x:x.titulo.str[:60]).to_string(index=False))
for excl in ["","SQNL","WU"]:
    ks=[k for k in AV if k not in excl]; m=D[ks].median(axis=1).apply(np.floor).astype(int)
    print("sem",excl or "-","kw",round(kw(m,D.consenso),3),"iguais",round((m==D.consenso).mean(),3))
