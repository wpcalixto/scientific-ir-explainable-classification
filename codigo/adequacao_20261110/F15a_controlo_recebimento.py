#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F15a_controlo_recebimento.py

File type:
    Script

Purpose:
    Quality control of the returned assessment sheets before any analysis.

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
    - See docs/file_level_documentation.md (entry F15a_controlo_recebimento.py).

Outputs:
    - See docs/file_level_documentation.md (entry F15a_controlo_recebimento.py).

Dependencies:
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F15a_controlo_recebimento.py

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

import os, re, sys, shutil, hashlib, stat, pandas as pd
CORR = re.compile(r"corrigid[oa]\s+de\s+(0|1|2|NA)\s+para\s+(0|1|2|NA)", re.I)
REC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(f"{OUT}/originais", exist_ok=True)
V = BIBLIO_BASE + "/resultados/adequacao_20261110/F14_complementares_01A/validacao_P100"
M = pd.read_csv(f"{V}/mapa_documentos_v2_NAO_ENVIAR.csv", keep_default_na=False)
DOM = {"Microarranjos": "microarranjos", "Radiomica": "radiomica", "Metamateriais": "metamateriais"}
COLS = ["doc_id", "titulo", "resumo", "relevancia_0_1_2_ou_NA", "comentario"]
def norm(v):
    s = str(v).strip().upper().replace(",", ".")
    if s in ("", "NAN", "NONE"): return ""
    if s in ("NA", "N/A", "N.A."): return "NA"
    try:
        f = float(s); return str(int(f)) if f in (0.0, 1.0, 2.0) else "INVALIDO:" + str(v)
    except ValueError: return "INVALIDO:" + str(v)
res, prob, notas = [], [], []
for f in sorted(x for x in os.listdir(REC) if x.endswith(".xlsx")):
    dom_nome, cod = f[:-5].split("_")[2], f[:-5].split("_")[3]; d = DOM[dom_nome]
    o = f"{OUT}/originais/{f}"; shutil.copy2(f"{REC}/{f}", o); os.chmod(o, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    env = pd.read_excel(f"{V}/envio_P01B2/Folha_P100_{dom_nome}_{cod}.xlsx", keep_default_na=False) if os.path.exists(f"{V}/envio_P01B2/Folha_P100_{dom_nome}_{cod}.xlsx") \
        else pd.read_excel(f"{V}/folhas_v2/Folha_P100_{dom_nome}_avaliador1.xlsx", keep_default_na=False)
    x = pd.read_excel(o, keep_default_na=False, dtype=str); md = M[M.dominio == d].set_index("doc_id")
    p = lambda tipo, det, doc="": prob.append({"ficha": f, "avaliador": cod, "dominio": d, "doc_id": doc, "problema": tipo, "detalhe": det})
    if list(x.columns) != COLS: p("colunas", "|".join(x.columns))
    ids = x.doc_id.astype(str).str.strip()
    for doc in sorted(set(ids) - set(md.index)): p("doc_id desconhecido", "", doc)
    for doc in sorted(set(md.index) - set(ids)): p("doc_id em falta", "", doc)
    for doc in ids[ids.duplicated()]: p("doc_id repetido", "", doc)
    if ids.tolist() != env.doc_id.astype(str).tolist(): p("ordem alterada", "ordem diferente da ficha enviada")
    e = env.set_index("doc_id")
    for r in x.itertuples():
        if r.doc_id in e.index and (str(r.titulo).strip() != str(e.loc[r.doc_id, "titulo"]).strip() or str(r.resumo).strip() != str(e.loc[r.doc_id, "resumo"]).strip()):
            p("texto alterado", "título ou resumo difere da ficha enviada", r.doc_id)
    x["nota"] = x["relevancia_0_1_2_ou_NA"].map(norm)
    for r in x.itertuples():
        if r.nota.startswith("INVALIDO"): p("valor inválido", r.nota, r.doc_id)
        elif r.nota == "": p("em falta", "", r.doc_id)
        elif r.nota == "NA" and r.resumo != "(sem resumo)": p("NA em documento com resumo", "mantido como NA (ausente)", r.doc_id)
    for r in x.itertuples():
        if r.doc_id in md.index:
            cs = CORR.findall(str(r.comentario)); ini = cs[0][0].upper() if cs else r.nota
            if cs and cs[-1][1].upper() != r.nota: p("correção incoerente", "última anotação 'para " + cs[-1][1] + "' diferente da nota final '" + r.nota + "'", r.doc_id)
            notas.append({"dominio": d, "avaliador": cod, "doc_id": r.doc_id, "jid": md.loc[r.doc_id, "jid"], "tipo": md.loc[r.doc_id, "tipo"],
                          "sem_resumo": md.loc[r.doc_id, "sem_resumo"], "nota_original": r.relevancia_0_1_2_ou_NA, "nota": r.nota, "comentario": r.comentario,
                          "n_correcoes": len(cs), "nota_inicial": ini, "correcoes": ";".join(x + ">" + y for x, y in cs)})
    res.append({"ficha": f, "avaliador": cod, "dominio": d, "sha256_recebida": hashlib.sha256(open(o, "rb").read()).hexdigest(), "linhas": len(x),
                "esperadas": len(md), "validas_0_1_2": int(x.nota.isin(["0", "1", "2"]).sum()), "NA": int((x.nota == "NA").sum()),
                "em_falta": int((x.nota == "").sum()), "invalidas": int(x.nota.str.startswith("INVALIDO").sum()), "comentarios": int((x.comentario.astype(str).str.strip() != "").sum()), "docs_corrigidos": int(x.comentario.astype(str).str.contains(CORR).sum()),
                "problemas": sum(1 for q in prob if q["ficha"] == f)})
pd.DataFrame(res).to_csv(f"{OUT}/controlo_fichas.csv", index=False); pd.DataFrame(prob, columns=["ficha", "avaliador", "dominio", "doc_id", "problema", "detalhe"]).to_csv(f"{OUT}/controlo_problemas.csv", index=False)
pd.DataFrame(notas).to_csv(f"{OUT}/notas_consolidadas.csv", index=False)
print(pd.DataFrame(res).to_string(index=False)); print("problemas:", len(prob)); print(pd.DataFrame(prob).problema.value_counts().to_string() if prob else "")
