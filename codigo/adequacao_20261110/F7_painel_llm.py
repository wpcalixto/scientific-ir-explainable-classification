#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F7_painel_llm.py

File type:
    Script

Purpose:
    Panel of three LLM judges at temperature 0: labelling task (R) and relevance judgement task (J).

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
    - See docs/file_level_documentation.md (entry F7_painel_llm.py).

Outputs:
    - See docs/file_level_documentation.md (entry F7_painel_llm.py).

Dependencies:
    - anthropic
    - numpy
    - pandas
    - requests

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F7_painel_llm.py

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

import os, re, json, time, threading, urllib.request, urllib.parse, hashlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd, requests, anthropic
BASE = BIBLIO_BASE + ""; R = f"{BASE}/resultados/adequacao_20261110"
EXT = f"{BASE}/dados/coleta_v2_20261110/externas"
OUT = f"{R}/F7_painel_llm"; os.makedirs(OUT, exist_ok=True)
key = lambda n: open(os.path.expanduser(f"~/.config/bibliometria/{n}")).read().strip()
KA, KO, KG = key("anthropic_api_key"), key("openai_api_key"), key("gemini_api_key")
M = {"haiku": "claude-haiku-4-5-20251001", "gpt": "gpt-5.4-mini", "gemini": "gemini-3.5-flash"}
LOG = open(f"{OUT}/painel.log", "a"); LK = threading.RLock()
def log(m):
    s = time.strftime("%Y-%m-%dT%H:%M:%S ") + m
    with LK: print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
SYS_R = open(f"{R}/F2_rotulacao_v2/prompt_system_v2.txt").read()
TEMAS = {
 "microarranjos": "Studies that develop, compare or apply feature (gene) selection methods on gene expression data (microarrays or other transcriptomic profiles) for classification or prediction, evaluating discriminative performance (e.g., AUC/ROC).",
 "radiomica": "Studies that extract and select quantitative features from medical images (CT, MRI, PET, ultrasound, mammography) — radiomics, texture or image features — to build classification or prediction models, evaluating discriminative performance (AUC/ROC).",
 "metamateriais": "Studies that use machine learning (including deep learning, surrogate models and inverse design) to design, model or optimise metamaterials, metasurfaces or other subwavelength electromagnetic, optical or acoustic structures (e.g., frequency selective surfaces, resonators, photonic crystals)."}
SYS_J = ("You are an expert assessor of the relevance of scientific documents to an information need.\n\nTOPIC\n{tema}\n\n"
         "GRADES\n- 2 = highly relevant: meets all elements of the topic.\n- 1 = partially relevant: in the domain and uses the method, "
         "but one element is missing (e.g., no performance evaluation, or data not from the domain); a review on the topic is also 1.\n"
         "- 0 = not relevant.\n\nJudge only from the title and abstract. Answer with exactly one digit: 0, 1 or 2.")
DOM = {"microarranjos": "Gene expression (microarray)", "radiomica": "Radiomics", "metamateriais": "Metamaterials"}
ca = anthropic.Anthropic(api_key=KA)
def chamar(mod, system, user, tries=6):
    for i in range(tries):
        try:
            if mod == "haiku":
                r = ca.messages.create(model=M[mod], max_tokens=5, temperature=0, system=system, messages=[{"role": "user", "content": user}])
                return next((c.text for c in r.content if c.type == "text"), ""), M[mod]
            if mod == "gpt":
                r = requests.post("https://api.openai.com/v1/responses", timeout=120, headers={"Authorization": f"Bearer {KO}"},
                                  json={"model": M[mod], "temperature": 0, "reasoning": {"effort": "none"}, "max_output_tokens": 16,
                                        "input": [{"role": "developer", "content": system}, {"role": "user", "content": user}]})
                j = r.json()
                if r.status_code != 200: raise RuntimeError(f"{r.status_code} {str(j.get('error'))[:120]}")
                return "".join(c["text"] for o in j["output"] if o["type"] == "message" for c in o["content"]), j.get("model")
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{M[mod]}:generateContent", timeout=120,
                              headers={"x-goog-api-key": KG},
                              json={"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"parts": [{"text": user}]}],
                                    "generationConfig": {"temperature": 0, "maxOutputTokens": 16, "thinkingConfig": {"thinkingBudget": 0}}})
            j = r.json()
            if r.status_code != 200: raise RuntimeError(f"{r.status_code} {str(j.get('error', {}).get('message'))[:120]}")
            c = j.get("candidates", [{}])[0]
            return "".join(p.get("text", "") for p in c.get("content", {}).get("parts", [])), j.get("modelVersion")
        except Exception as e:
            log(f"  {mod} erro {type(e).__name__}: {str(e)[:120]} (tentativa {i+1})"); time.sleep(min(120, 5 * 2 ** i))
    return "ERRO", M[mod]
THREADS = {"haiku": 8, "gpt": 4, "gemini": 2}
def correr(nome, tarefas, fich):
    feito = set()
    if os.path.exists(fich):
        for l in open(fich): feito.add(json.loads(l)["id"])
    f = open(fich, "a")
    def por_modelo(mod):
        pend = [t for t in tarefas if t["id"] not in feito and t["mod"] == mod]
        log(f"[{nome}/{mod}] a fazer={len(pend)}"); n = [0, 0]
        def um(t):
            txt, mv = chamar(t["mod"], t["system"], t["user"])
            with LK:
                if txt == "ERRO": n[1] += 1; return
                f.write(json.dumps({"id": t["id"], "mod": t["mod"], "model_version": mv, "resposta": txt}, ensure_ascii=False) + "\n"); f.flush()
                n[0] += 1
                if n[0] % 500 == 0: log(f"[{nome}/{mod}] {n[0]}/{len(pend)}")
        with ThreadPoolExecutor(THREADS[mod]) as ex: list(ex.map(um, pend))
        log(f"[{nome}/{mod}] FIM ok={n[0]} falhas={n[1]}")
    mods = sorted({t["mod"] for t in tarefas})
    with ThreadPoolExecutor(len(mods)) as ex: list(ex.map(por_modelo, mods))
    f.close()

can = pd.read_csv(f"{R}/F2_corpus/corpus_canonico.csv", dtype=str, keep_default_na=False)
rot = pd.read_csv(f"{R}/F2_rotulacao_v2/rotulos_v2_final.csv", dtype=str, keep_default_na=False)
rot = rot[rot["label"].isin(["Applied", "Methodological", "General"])].merge(can[["dominio", "openalex_id", "title", "abstract"]], on=["dominio", "openalex_id"])
amo = rot.sample(frac=1, random_state=42).groupby(["dominio", "label"]).head(170)
amo.drop(columns=["abstract"]).to_csv(f"{OUT}/amostra_rotulacao.csv", index=False)
def texto(d, t, a): return f"Domain: {DOM[d]}\nTitle: {t}\nAbstract: {a if a else 'not available'}"[:3000]
TR = [{"id": f"{m}|{r.custom_id}", "mod": m, "system": SYS_R, "user": texto(r.dominio, r.title, r.abstract)}
      for r in amo.itertuples() for m in ("gpt", "gemini")]

L = pd.read_csv(f"{R}/F4_F5/listas_ranqueadas.csv", keep_default_na=False)
L = L[L["lista"].str.match(r"^(OAL_[ABC]_(cit|bm25)|scopus_top100_[ABC]|wos_top100_[ABC]|elicit_semantico_[ABC])$") & (L["rank"] <= 100)]
tk = lambda t: "t:" + re.sub(r"[^a-z0-9]", "", str(t).lower())[:120]
txt = {}
for r in can.itertuples():
    for k in ([r.doi_n] if r.doi_n else []) + [tk(r.title)]:
        if k not in txt or (not txt[k][1] and r.abstract): txt[k] = (r.title, r.abstract)
for f in [f for f in os.listdir(EXT) if f.startswith(("elicit_semantico", "elicit_keyword", "s2_top100")) and f.endswith(".csv")]:
    for r in pd.read_csv(f"{EXT}/{f}", dtype=str, keep_default_na=False).itertuples():
        for k in ([r.doi.lower()] if r.doi else []) + [tk(r.title)]:
            if k not in txt or (not txt[k][1] and r.abstract): txt[k] = (r.title, r.abstract)
docs = L.groupby(["dominio", "chave"]).agg(title=("title", "first")).reset_index()
docs["abstract"] = [txt.get(r.chave, txt.get(tk(r.title), ("", "")))[1] for r in docs.itertuples()]
falta = sorted({r.chave for r in docs.itertuples() if not r.abstract and not r.chave.startswith("t:")})
log(f"pool J: {len(docs)} docs (dom×chave); sem resumo antes do OpenAlex: {len(falta)}")
extra = {}
for i in range(0, len(falta), 40):
    q = urllib.parse.urlencode({"filter": "doi:" + "|".join(falta[i:i+40]), "per-page": 50, "select": "doi,abstract_inverted_index"})
    try:
        j = json.loads(urllib.request.urlopen("https://api.openalex.org/works?" + q, timeout=60).read())
        for w in j["results"]:
            inv = w.get("abstract_inverted_index") or {}
            extra[(w.get("doi") or "").lower().replace("https://doi.org/", "")] = " ".join(t for _, t in sorted((p, t) for t, ps in inv.items() for p in ps))
    except Exception as e: log(f"openalex {type(e).__name__}")
    time.sleep(1)
docs["abstract"] = [r.abstract or extra.get(r.chave, "") for r in docs.itertuples()]
docs["jid"] = [f"{r.dominio[:2]}_{hashlib.md5(r.chave.encode()).hexdigest()[:12]}" for r in docs.itertuples()]
docs.to_csv(f"{OUT}/pool_relevancia_p100.csv", index=False)
L.merge(docs[["dominio", "chave", "jid"]], on=["dominio", "chave"]).to_csv(f"{OUT}/listas_p100_com_jid.csv", index=False)
log(f"pool J sem resumo final: {(docs['abstract'] == '').sum()}")
TJ = [{"id": f"{m}|{r.jid}", "mod": m, "system": SYS_J.format(tema=TEMAS[r.dominio]),
       "user": f"Title: {r.title}\nAbstract: {r.abstract if r.abstract else 'not available'}"[:3000]}
      for r in docs.itertuples() for m in ("haiku", "gpt", "gemini")]
json.dump({"modelos": M, "temperatura": 0, "raciocinio": {"gpt": "effort none", "gemini": "thinkingBudget 0", "haiku": "sem extended thinking"},
           "prompt_R_sha256": hashlib.sha256(SYS_R.encode()).hexdigest(), "prompt_J": SYS_J, "temas": TEMAS,
           "n_amostra_R": len(amo), "n_pool_J": len(docs), "inicio": time.strftime("%Y-%m-%dT%H:%M:%S")},
          open(f"{OUT}/metadados_F7.json", "w"), indent=1, ensure_ascii=False)
with ThreadPoolExecutor(2) as ex:
    list(ex.map(lambda a: correr(*a), [("R_rotulacao", TR, f"{OUT}/respostas_R.jsonl"), ("J_relevancia", TJ, f"{OUT}/respostas_J.jsonl")]))
log("F7 FIM")
