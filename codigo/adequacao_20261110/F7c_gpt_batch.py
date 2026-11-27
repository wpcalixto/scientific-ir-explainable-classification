#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F7c_gpt_batch.py

File type:
    Script

Purpose:
    GPT judgements through the OpenAI Batch API.

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
    - See docs/file_level_documentation.md (entry F7c_gpt_batch.py).

Outputs:
    - See docs/file_level_documentation.md (entry F7c_gpt_batch.py).

Dependencies:
    - requests

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F7c_gpt_batch.py

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

import os, json, time, requests
SRC = BIBLIO_BASE + "/codigo/adequacao_20261110/F7_painel_llm.py"
code = open(SRC).read().split("with ThreadPoolExecutor(2) as ex:")[0]
g = {"__name__": "f7"}; exec(compile(code, SRC, "exec"), g)
OUT, KO, M, log = g["OUT"], g["KO"], g["M"], g["log"]
feito = set()
for fn in ["respostas_R.jsonl", "respostas_J.jsonl", "respostas_gpt_batch.jsonl"]:
    p = f"{OUT}/{fn}"
    if os.path.exists(p): feito |= {json.loads(l)["id"] for l in open(p)}
H = {"Authorization": f"Bearer {KO}"}
LIM = 150_000
def feitos():
    s = set()
    for fn in ["respostas_R.jsonl", "respostas_J.jsonl", "respostas_gpt_batch.jsonl"]:
        p = f"{OUT}/{fn}"
        if os.path.exists(p): s |= {json.loads(l)["id"] for l in open(p)}
    return s
def linha(t):
    return {"custom_id": t["id"], "method": "POST", "url": "/v1/responses",
            "body": {"model": M["gpt"], "temperature": 0, "reasoning": {"effort": "none"}, "max_output_tokens": 16,
                     "input": [{"role": "developer", "content": t["system"]}, {"role": "user", "content": t["user"]}]}}
k = 0
while True:
    fe = feitos(); tar = [t for t in g["TR"] + g["TJ"] if t["mod"] == "gpt" and t["id"] not in fe]
    if not tar: break
    lote, tok = [], 0
    for t in tar:
        e = (len(t["system"]) + len(t["user"])) / 3.5 + 30
        if tok + e > LIM and lote: break
        lote.append(t); tok += e
    k += 1; log(f"[GPT batch {k}] a enviar {len(lote)} pedidos (~{int(tok)} tokens); restam {len(tar)}")
    with open(f"{OUT}/gpt_batch_input.jsonl", "w") as f:
        for t in lote: f.write(json.dumps(linha(t), ensure_ascii=False) + "\n")
    r = requests.post("https://api.openai.com/v1/files", headers=H, files={"file": open(f"{OUT}/gpt_batch_input.jsonl", "rb")}, data={"purpose": "batch"}, timeout=300)
    fid = r.json()["id"]
    r = requests.post("https://api.openai.com/v1/batches", headers=H, timeout=120, json={"input_file_id": fid, "endpoint": "/v1/responses", "completion_window": "24h"})
    if r.status_code != 200: log(f"[GPT batch {k}] ERRO criar {r.status_code} {r.text[:200]}"); time.sleep(300); continue
    bid = r.json()["id"]
    while True:
        time.sleep(60)
        b = requests.get(f"https://api.openai.com/v1/batches/{bid}", headers=H, timeout=120).json()
        if b["status"] in ("completed", "failed", "expired", "cancelled"): break
    log(f"[GPT batch {k}] {bid} estado={b['status']} {b.get('request_counts')} {str(b.get('errors'))[:150] if b['status'] == 'failed' else ''}")
    if b["status"] == "failed": time.sleep(300); continue
    n = 0
    with open(f"{OUT}/respostas_gpt_batch.jsonl", "a") as f:
        if b.get("output_file_id"):
            for l in requests.get(f"https://api.openai.com/v1/files/{b['output_file_id']}/content", headers=H, timeout=300).text.splitlines():
                j = json.loads(l); rr = j.get("response") or {}
                if rr.get("status_code") != 200: continue
                bd = rr["body"]
                out = "".join(c.get("text", "") for o in bd.get("output", []) if o.get("type") == "message" for c in o.get("content", []))
                f.write(json.dumps({"id": j["custom_id"], "mod": "gpt", "model_version": bd.get("model"), "resposta": out}, ensure_ascii=False) + "\n"); n += 1
    log(f"[GPT batch {k}] gravadas {n}")
log("[GPT batch] FIM — todas as tarefas GPT têm resposta")
