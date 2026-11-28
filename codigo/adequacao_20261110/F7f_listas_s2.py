#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F7f_listas_s2.py

File type:
    Script

Purpose:
    Judges the Semantic Scholar lists with the same three LLM judges.

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
    - See docs/file_level_documentation.md (entry F7f_listas_s2.py).

Outputs:
    - See docs/file_level_documentation.md (entry F7f_listas_s2.py).

Dependencies:
    - pandas
    - requests

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F7f_listas_s2.py

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

import os, json, time, hashlib, requests, pandas as pd
from concurrent.futures import ThreadPoolExecutor
SRC = BIBLIO_BASE + "/codigo/adequacao_20261110/F7_painel_llm.py"
g = {"__name__": "f7"}; exec(compile(open(SRC).read().split("with ThreadPoolExecutor(2) as ex:")[0], SRC, "exec"), g)
OUT, KO, M, log, correr, SYS_J, TEMAS, txt, tk = g["OUT"], g["KO"], g["M"], g["log"], g["correr"], g["SYS_J"], g["TEMAS"], g["txt"], g["tk"]
R = BIBLIO_BASE + ""
L = pd.read_csv(f"{R}/resultados/adequacao_20261110/F4_F5/listas_ranqueadas.csv", keep_default_na=False)
L = L[L.lista.str.startswith("s2_top100")].copy(); L["rank"] = pd.to_numeric(L["rank"]); L = L[L["rank"] <= 100]
L["jid"] = [f"{d[:2]}_{hashlib.md5(k.encode()).hexdigest()[:12]}" for d, k in zip(L.dominio, L.chave)]
L.to_csv(f"{OUT}/listas_s2_com_jid.csv", index=False)
pool = pd.read_csv(f"{OUT}/pool_relevancia_p100.csv", keep_default_na=False)
novos = L[~L.jid.isin(set(pool.jid))].drop_duplicates("jid")[["dominio", "chave", "title", "jid"]].copy()
s2 = {}
for f in os.listdir(f"{R}/dados/coleta_v2_20261110/externas"):
    if f.startswith("s2_top100_") and f.endswith(".csv"):
        for r in pd.read_csv(f"{R}/dados/coleta_v2_20261110/externas/{f}", keep_default_na=False).itertuples():
            for k in [(r.doi or "").lower(), tk(r.title)]:
                if k and r.abstract: s2.setdefault(k, r.abstract)
novos["abstract"] = [txt.get(k, ("", ""))[1] or txt.get(tk(t), ("", ""))[1] or s2.get(k, "") or s2.get(tk(t), "") for k, t in zip(novos.chave, novos.title)]
novos.to_csv(f"{OUT}/pool_s2_novos.csv", index=False)
log(f"[F7f] listas S2: {L.lista.nunique()} x dominio; docs={L.jid.nunique()}; já julgados={L.jid.nunique() - len(novos)}; novos={len(novos)}; sem resumo={int((novos.abstract == '').sum())}")
T = [{"id": f"{m}|{r.jid}", "mod": m, "system": SYS_J.format(tema=TEMAS[r.dominio]),
      "user": f"Title: {r.title}\nAbstract: {r.abstract if r.abstract else 'not available'}"[:3000]} for r in novos.itertuples() for m in ("haiku", "gpt", "gemini")]
FJ, FB = f"{OUT}/respostas_J_s2.jsonl", f"{OUT}/respostas_gpt_batch_s2.jsonl"
def gpt_batch():
    H = {"Authorization": f"Bearer {KO}"}; k = 0
    while True:
        fe = set()
        for fn in [FJ, FB]:
            if os.path.exists(fn): fe |= {json.loads(l)["id"] for l in open(fn)}
        tar = [t for t in T if t["mod"] == "gpt" and t["id"] not in fe]
        if not tar: break
        lote, tok = [], 0
        for t in tar:
            e = (len(t["system"]) + len(t["user"])) / 3.5 + 30
            if tok + e > 150_000 and lote: break
            lote.append(t); tok += e
        k += 1; log(f"[F7f GPT batch {k}] {len(lote)} pedidos; restam {len(tar)}")
        p = f"{OUT}/gpt_batch_input_s2.jsonl"
        with open(p, "w") as f:
            for t in lote: f.write(json.dumps({"custom_id": t["id"], "method": "POST", "url": "/v1/responses", "body": {"model": M["gpt"], "temperature": 0, "reasoning": {"effort": "none"}, "max_output_tokens": 16, "input": [{"role": "developer", "content": t["system"]}, {"role": "user", "content": t["user"]}]}}, ensure_ascii=False) + "\n")
        fid = requests.post("https://api.openai.com/v1/files", headers=H, files={"file": open(p, "rb")}, data={"purpose": "batch"}, timeout=300).json()["id"]
        r = requests.post("https://api.openai.com/v1/batches", headers=H, timeout=120, json={"input_file_id": fid, "endpoint": "/v1/responses", "completion_window": "24h"})
        if r.status_code != 200: log(f"[F7f GPT] ERRO {r.status_code} {r.text[:150]}"); time.sleep(300); continue
        bid = r.json()["id"]
        while True:
            time.sleep(60); b = requests.get(f"https://api.openai.com/v1/batches/{bid}", headers=H, timeout=120).json()
            if b["status"] in ("completed", "failed", "expired", "cancelled"): break
        log(f"[F7f GPT batch {k}] {b['status']} {b.get('request_counts')}")
        if b["status"] == "failed": time.sleep(300); continue
        with open(FB, "a") as f:
            if b.get("output_file_id"):
                for l in requests.get(f"https://api.openai.com/v1/files/{b['output_file_id']}/content", headers=H, timeout=300).text.splitlines():
                    j = json.loads(l); rr = j.get("response") or {}
                    if rr.get("status_code") != 200: continue
                    bd = rr["body"]; out = "".join(c.get("text", "") for o in bd.get("output", []) if o.get("type") == "message" for c in o.get("content", []))
                    f.write(json.dumps({"id": j["custom_id"], "mod": "gpt", "model_version": bd.get("model"), "resposta": out}, ensure_ascii=False) + "\n")
with ThreadPoolExecutor(2) as ex:
    ex.submit(correr, "J_s2", [t for t in T if t["mod"] != "gpt"], FJ); ex.submit(gpt_batch)
log("[F7f] FIM")
