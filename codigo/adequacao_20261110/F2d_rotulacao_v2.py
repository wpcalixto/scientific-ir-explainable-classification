#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F2d_rotulacao_v2.py

File type:
    Script

Purpose:
    Labels the documents as Applied, Methodological or General with Claude Haiku 4.5 through the Message Batches API.

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
    - See docs/file_level_documentation.md (entry F2d_rotulacao_v2.py).

Outputs:
    - See docs/file_level_documentation.md (entry F2d_rotulacao_v2.py).

Dependencies:
    - anthropic

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F2d_rotulacao_v2.py

Portability notes:
    All paths are resolved relative to the package base directory given by the BIBLIO_BASE environment variable
    (default: the package root, two levels above codigo/adequacao_20261110/). No machine-specific path is required.
    API keys, when needed, are read from ~/.config/bibliogenre/ and ~/.config/bibliometria/ and are not part of the package.

Reproducibility notes:
    Environment pinned in requirements.txt and environment/. Seeds and frozen parameters are written in the code and
    summarized in docs/parameters.md.

Warnings:
    Calls paid LLM APIs and needs API keys; re-running incurs costs and may not return identical outputs (the archived outputs are in resultados/).
"""

import os as _bb_os
BIBLIO_BASE = _bb_os.environ.get("BIBLIO_BASE") or _bb_os.path.abspath(
    _bb_os.path.join(_bb_os.path.dirname(_bb_os.path.abspath(__file__)), "..", ".."))

import os, csv, json, glob, time, hashlib, datetime as dt
import anthropic
BASE = BIBLIO_BASE + ""
COL = f"{BASE}/dados/coleta_v2_20261110"
OUT = f"{BASE}/resultados/adequacao_20261110/F2_rotulacao_v2"; os.makedirs(OUT, exist_ok=True)
MODEL = "claude-haiku-4-5-20251001"
LOG = open(f"{OUT}/rotulacao_v2.log", "a", encoding="utf-8")
def log(m):
    s = f"{dt.datetime.now().isoformat(timespec='seconds')} {m}"; print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
SYSTEM = """You are an expert in scientometrics. Classify the scientific document below into exactly one of three categories, considering the research domain indicated.

CATEGORIES
- Applied: the central contribution is the use of computational or data-driven methods to solve a concrete problem of the domain.
    * Gene expression (microarray) and radiomics domains: clinical, diagnostic, prognostic or biological applications (e.g., disease classification, outcome prediction, biomarker discovery in patient data).
    * Metamaterials domain: design, fabrication or characterisation of a specific device, structure or engineering application (e.g., an absorber, antenna, metasurface or sensor).
- Methodological: the central contribution is the development, comparison or evaluation of methods themselves (feature selection, machine learning models, evaluation metrics such as AUC-ROC, design/optimisation algorithms), with the application playing a secondary or illustrative role.
- General: reviews, surveys, tutorials, perspectives, bibliometric studies, or documents that fit neither of the other categories.

Answer with exactly one word: Applied, Methodological or General."""
DOM = {"microarranjos": "Gene expression (microarray)", "radiomica": "Radiomics", "metamateriais": "Metamaterials"}
CODE = {"microarranjos": "mi", "radiomica": "ra", "metamateriais": "me"}
CLASSES = {"applied": "Applied", "methodological": "Methodological", "general": "General"}
def norm(t):
    t = (t or "").strip().strip(".:;,!\"'*` ").lower()
    return CLASSES.get(t, "INVALID")
def texto(dom, title, abstract):
    s = f"Domain: {DOM[dom]}\nTitle: {title}\nAbstract: {abstract if abstract else 'not available'}"
    return s[:3000]

while "F2c CONCLUIDO" not in open(f"{COL}/coleta_v2.log", encoding="utf-8").read():
    time.sleep(60)
log("F2c concluída; a construir os pedidos")
csv.field_size_limit(10**9)
docs = {}
for f in sorted(glob.glob(f"{COL}/*_busca_[ABC].csv")):
    for r in csv.DictReader(open(f, encoding="utf-8")):
        k = (r["dominio"], r["openalex_id"])
        if k not in docs or (not docs[k]["abstract"] and r["abstract"]):
            docs[k] = {"title": r["title"], "abstract": r["abstract"]}
cid = {f"{CODE[d]}_{w.rsplit('/', 1)[-1]}": (d, w) for (d, w) in docs}
log(f"documentos únicos (domínio × id): {len(cid)} | sem resumo: {sum(1 for v in docs.values() if not v['abstract'])}")
reqs = [{"custom_id": c, "params": {"model": MODEL, "max_tokens": 5, "temperature": 0, "system": SYSTEM,
         "messages": [{"role": "user", "content": texto(d, docs[(d, w)]["title"], docs[(d, w)]["abstract"])}]}}
        for c, (d, w) in cid.items()]
client = anthropic.Anthropic(api_key=open(os.path.expanduser("~/.config/bibliogenre/anthropic_api_key")).read().strip())
estado = f"{OUT}/batch_id.txt"
if os.path.exists(estado):
    bid = open(estado).read().strip(); log(f"a retomar batch {bid}")
else:
    b = client.messages.batches.create(requests=reqs); bid = b.id
    open(estado, "w").write(bid); log(f"batch criado {bid} com {len(reqs)} pedidos")
while True:
    b = client.messages.batches.retrieve(bid)
    if b.processing_status == "ended": break
    time.sleep(120)
log(f"batch terminado: {b.request_counts}")
res, brutos, uso = {}, open(f"{OUT}/respostas_brutas.jsonl", "w", encoding="utf-8"), {"in": 0, "out": 0}
for r in client.messages.batches.results(bid):
    if r.result.type == "succeeded":
        m = r.result.message
        txt = next((c.text for c in m.content if c.type == "text"), "")
        uso["in"] += m.usage.input_tokens; uso["out"] += m.usage.output_tokens
        res[r.custom_id] = (norm(txt), txt)
    else:
        res[r.custom_id] = ("ERROR_" + r.result.type, "")
    brutos.write(json.dumps({"custom_id": r.custom_id, "type": r.result.type, "text": res[r.custom_id][1]}, ensure_ascii=False) + "\n")
brutos.close()
rep = [c for c, v in res.items() if v[0] not in CLASSES.values()]
log(f"a repetir {len(rep)} inválidos/erros")
for c in rep:
    d, w = cid[c]
    try:
        m = client.messages.create(model=MODEL, max_tokens=5, temperature=0, system=SYSTEM,
                                   messages=[{"role": "user", "content": texto(d, docs[(d, w)]["title"], docs[(d, w)]["abstract"])}])
        txt = next((x.text for x in m.content if x.type == "text"), "")
        res[c] = (norm(txt), txt)
    except Exception as e:
        res[c] = ("INVALID", f"erro {type(e).__name__}")
    time.sleep(0.3)
with open(f"{OUT}/rotulos_v2.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["dominio", "openalex_id", "label", "sem_resumo", "resposta_bruta", "custom_id"])
    for c, (d, wid) in cid.items():
        w.writerow([d, wid, res.get(c, ("MISSING", ""))[0], int(not docs[(d, wid)]["abstract"]), res.get(c, ("", ""))[1], c])
from collections import Counter
cont = Counter((d, res.get(c, ("MISSING",))[0]) for c, (d, _) in cid.items())
meta = {"modelo": MODEL, "sdk_anthropic": anthropic.__version__, "api_version": "2023-06-01 (padrão do SDK 0.x)",
        "temperature": 0, "max_tokens": 5, "truncamento_caracteres": 3000, "prompt_versao": "v2",
        "prompt_sha256": hashlib.sha256(SYSTEM.encode()).hexdigest(), "batch_id": bid,
        "n_pedidos": len(reqs), "tokens_entrada": uso["in"], "tokens_saida": uso["out"],
        "repetidos": len(rep), "contagens": {f"{d}|{l}": n for (d, l), n in sorted(cont.items())},
        "fim": dt.datetime.now().isoformat(timespec="seconds")}
json.dump(meta, open(f"{OUT}/metadados_rotulacao_v2.json", "w"), indent=1, ensure_ascii=False)
open(f"{OUT}/prompt_system_v2.txt", "w").write(SYSTEM)
log(f"FIM — {dict(cont)}")
