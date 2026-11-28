#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    F19_matriz_rastreabilidade.py

File type:
    Script

Purpose:
    Builds the traceability matrix of the result tables and figures to their source files and scripts.

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
    - See docs/file_level_documentation.md (entry F19_matriz_rastreabilidade.py).

Outputs:
    - See docs/file_level_documentation.md (entry F19_matriz_rastreabilidade.py).

Dependencies:
    - numpy
    - pandas

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/F19_matriz_rastreabilidade.py

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

import os, re, sys, glob, json, hashlib, unicodedata, pandas as pd, numpy as np
TEX, FIGDIR, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
B = BIBLIO_BASE + ""; R = f"{B}/resultados/adequacao_20261110"; V = f"{R}/F14_complementares_01A/validacao_P100"
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
F10 = "F10_reexec"; D3 = ["microarranjos", "metamateriais", "radiomica"]
FONTES = {
 "corpus": ("Volume recuperado por domínio e estratégia", ["F2_corpus/fluxo_corpus.csv", "F2_corpus/corpus_canonico.csv"], "num"),
 "tab_temporal": ("Publicações por ano e domínio", [f"{F10}/caracterizacao/serie_anual.csv"], "num"),
 "crescimento_anual": ("Crescimento anual por domínio", [f"{F10}/dados_classificacao/crescimento_anual.csv"], "num"),
 "overlap": ("Interseções entre estratégias", ["F2_corpus/sobreposicao_estrategias.csv"], "num"),
 "hst_overlap": ("δ por base e contenção A/B", ["F4_F5/delta_por_base.csv", "F4_F5/delta_variacao_entre_bases.csv", f"{F10}/dados_classificacao/hst_sobreposicao.csv", "F4_F5/reintegracao_hst.csv"], "num"),
 "facetas_exp": ("Experimento controlado das facetas", ["F14_complementares_01A/facetas/desenho_2x2.csv", "F14_complementares_01A/facetas/literal_vs_radicais.csv", "F14_complementares_01A/facetas/temporal.csv"], "num"),
 "verif_filtro": ("Verificação a posteriori do filtro booleano", ["F13_complementares/verificacao_filtro_local.csv"], "num"),
 "comparacao_bases": ("Sobreposição OAL × SCO", ["F2_corpus/cobertura_oal_scopus.csv"], "num"),
 "paises": ("Países mais produtivos", [f"{F10}/caracterizacao/top5_countries.csv"], "num"),
 "instituicoes": ("Instituições mais produtivas", [f"{F10}/caracterizacao/top5_institutions.csv"], "num"),
 "journals": ("Periódicos mais produtivos", [f"{F10}/caracterizacao/top5_journals.csv"], "num"),
 "hst_freq": ("Frequência documental dos termos HST e gerais", [f"{F10}/dados_classificacao/hst_frequencia_tabela.csv", "P02_conciliacao_denominadores_20261113/conciliacao_resumo.csv"], "num"),
 "hst_stats": ("Estatísticas das frequências por grupo", [f"{F10}/dados_classificacao/hst_estatisticas.csv"], "num"),
 "contrib": ("Contribuição das estratégias (novidade, revocação, reintegração, entropia)", ["F4_F5/novidade_redundancia.csv", "F4_F5/reintegracao_hst.csv", "F4_F5/diversidade_tematica.csv"], "num"),
 "crescimento_estrategias": ("Crescimento das estratégias por quinquénio e δ", ["F13_complementares/crescimento_por_estrategia.csv", "F13_complementares/delta_por_periodo.csv"], "num"),
 "tab_labels": ("Distribuição dos rótulos por domínio", ["DERIVADO:rotulos"], "num"),
 "tab_kappa": ("Concordância par a par entre LLM", ["F7_painel_llm/analise/R_concordancia_rotulos.csv"], "num"),
 "kappa_dominio": ("κ por domínio e κ de Fleiss", ["F7_painel_llm/analise/R_concordancia_rotulos.csv"], "num"),
 "dist_rotulos_modelo": ("Categorias atribuídas por cada LLM", ["F13_complementares/distribuicao_rotulos_por_modelo.csv", "F7_painel_llm/analise/R_distribuicao_rotulos.csv"], "num"),
 "tab_lda": ("Parâmetros, K* e coerência da LDA", ["P02_conciliacao_denominadores_20261113/conciliacao_resumo.csv", f"{F10}/F10_lda_microarranjos.log", f"{F10}/F10_lda_metamateriais.log", f"{F10}/F10_lda_radiomica.log"] + [f"{F10}/dados_processados/coherence_scores_{d}.csv" for d in D3], "num"),
 "lda_topics_dominios": ("Tópicos LDA por domínio", [f"{F10}/dados_processados/lda_topics_{d}.csv" for d in D3], "txt"),
 "tab_cod_lda": ("Códigos dos termos β dos tópicos", [f"{F10}/dados_processados/lda_topics_{d}.csv" for d in D3], "txt"),
 "pca_variance": ("Variância explicada pela PCA dos tópicos", [f"{F10}/dados_processados/pca_variance_{d}.csv" for d in D3], "num"),
 "tab_cod_kcna": ("Códigos dos conceitos da KCNA", [f"F14_complementares_01A/callon_equivalencia/particao_nova_{d}.csv" for d in D3], "txt"),
 "tab_cod_kcna2": ("Códigos dos conceitos da KCNA (cont.)", [f"F14_complementares_01A/callon_equivalencia/particao_nova_{d}.csv" for d in D3], "txt"),
 "comunidades_callon": ("Comunidades de Louvain e quadrantes", ["F14_complementares_01A/figuras/quadrantes_estritos.csv"] + [f"F14_complementares_01A/callon_equivalencia/mapa_{d}_nova.csv" for d in D3], "num"),
 "sens_agrup": ("Sensibilidade e estabilidade dos agrupamentos", ["F13_complementares/sensibilidade_agrupamentos.json", "F14_complementares_01A/callon_equivalencia/resumo.json"], "num"),
 "mca_clusters": ("Agrupamentos da ACP-MI", [f"{F10}/dados_classificacao/mca_coordenadas_{d}.csv" for d in D3], "txt"),
 "classificadores": ("Métricas dos 4 classificadores", [f"{F10}/classificacao/metricas_4modelos_dp.csv"], "num"),
 "classificadores_cenarios": ("Classificação por cenário", ["F3_classificacao/metricas_cenarios.csv", "F3_classificacao/testes_pareados.csv"], "num"),
 "tab_cod_shap": ("Códigos dos atributos SHAP", [f"{F10}/classificacao/shap_global_top30.csv", f"{F10}/classificacao/shap_top10_classe.csv"], "txt"),
 "tab_cod_lime": ("Códigos dos termos LIME", [f"{F10}/classificacao/lime_casos.csv"], "txt"),
 "shap_terms": ("Termos SHAP por classe", [f"{F10}/classificacao/shap_top10_classe.csv", "F3_classificacao/shap_top25_dominio_classe.csv"], "txt"),
 "ablacao": ("Estudo de ablação", [f"{F10}/classificacao/ablacao.csv", "F13_complementares/ablacao_resumo.csv", f"{F10}/classificacao/ablacao_lda_por_dominio.csv"], "num"),
 "wss_publicados": ("WSS@95% e comparação publicada", ["F6_benchmarks/comparacao_wss95_resumo.csv", "F6_benchmarks/comparacao_wss95_publicados.csv", "F13_complementares/wss_ic.csv"], "num"),
 "retrieval_dominios": ("Métricas de recuperação (citações)", ["F7_painel_llm/analise/J_metricas_cortes.csv"], "num"),
 "baseline_dominios": ("Métricas de recuperação (BM25)", ["F7_painel_llm/analise/J_metricas_cortes.csv"], "num"),
 "sintese_baseline": ("Síntese nDCG@100 por lista", ["F7_painel_llm/analise/J_metricas_por_lista.csv", "F7_painel_llm/analise/J_metricas_cortes.csv", "F7_painel_llm/analise/J_metricas_cortes_s2.csv"], "num"),
 "concordancia_rel": ("Concordância do painel de LLM", ["F7_painel_llm/analise/R_concordancia_rotulos.csv", "F7_painel_llm/analise/J_concordancia_relevancia.csv"], "num"),
 "externos_dominios": ("Métricas nas plataformas externas", ["F7_painel_llm/analise/J_metricas_cortes.csv", "F7_painel_llm/analise/J_metricas_cortes_s2.csv"], "num"),
 "sintese_externos": ("Síntese da P@100 por lista", ["F7_painel_llm/analise/J_metricas_por_lista.csv", "F13_complementares/P_k_por_lista.csv", "F7_painel_llm/analise/J_metricas_cortes_s2.csv"], "num"),
 "precisao_estrategia": ("P@100 e nDCG@100 por estratégia", ["F13_complementares/P_k_por_estrategia.csv", "F7_painel_llm/analise/J_metricas_por_lista.csv", "F13_complementares/P_k_por_lista.csv"], "num"),
 "sobreposicao_externas": ("Presença dos top-100 externos no OAL", ["F13_complementares/sobreposicao_externas_top100.csv"], "num"),
 "validacao_humana": ("Validação humana dos LLM (322 documentos)", [f"F8_julgamento/analise_fichas_reais_20261112_13fichas/{f}" for f in ["concordancia.csv", "P10_por_estrategia.csv", "ordenacao_humanos_vs_LLM.csv", "conferencia.json"]], "num"),
 "concordancia_fichas": ("Concordância de cada ficha com os LLM", [f"F8_julgamento/analise_fichas_reais_20261112_13fichas/{f}" for f in ["discordancia_por_ficha_dominio.csv", "por_avaliador.csv"]], "num"),
 "juiz_vs_humanos": ("Cada LLM × mediana humana", ["F13_complementares/juiz_LLM_vs_mediana_humana.csv"], "num"),
 "p100_humana": ("P@100 humana (Protocolo 01)", ["F14_complementares_01A/validacao_P100/F15_resultados_20261112/analise/P100_estrategias.csv", "F14_complementares_01A/validacao_P100/F15_resultados_20261112/analise/humano_menos_LLM.csv", "F14_complementares_01A/validacao_P100/F15e_bootstrap_20261113/B_intervalos_dados_reais.csv"], "num"),
 "p100_humana_dif": ("Diferenças de P@100 humana (Protocolo 01)", ["F14_complementares_01A/validacao_P100/F15_resultados_20261112/analise/P100_diferencas.csv", "F14_complementares_01A/validacao_P100/F15e_bootstrap_20261113/B_intervalos_dados_reais.csv"], "num"),
 "p100_replicacao": ("Replicação: P@100 R_old/R_new e mudança (Protocolo 01)", ["F14_complementares_01A/validacao_P100/replicacao_doutorandos_20261113/reproducao_F16c/C_P100_e_mudancas_entre_referencias.csv"], "num"),
 "concordancia_replicacao": ("Replicação: concordância e calibração (Protocolo 01)", ["F14_complementares_01A/validacao_P100/replicacao_doutorandos_20261113/analise/A_comparacao_old_new.csv", "F14_complementares_01A/validacao_P100/replicacao_doutorandos_20261113/analise/B_calibracao.csv"], "num"),
}
HOMOLOG_P01 = {"p100_humana", "p100_humana_dif", "p100_replicacao", "concordancia_replicacao"}
def valores(path):
    if path == "DERIVADO:rotulos":
        r = pd.read_csv(f"{R}/F2_rotulacao_v2/rotulos_v2_final.csv"); r = r[r.label.isin(["Applied", "Methodological", "General"])]
        ct = pd.crosstab(r.dominio, r.label, margins=True); pc = ct.div(ct["All"], axis=0) * 100
        return np.concatenate([ct.to_numpy().ravel().astype(float), pc.to_numpy().ravel()]), " ".join(r.label.unique())
    p = f"{R}/{path}"; txt = open(p, encoding="utf8", errors="ignore").read()
    nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", txt.replace(",", ""))] if not p.endswith(".csv") else []
    if p.endswith(".csv"):
        df = pd.read_csv(p, low_memory=False); num = df.select_dtypes(include="number").select_dtypes(exclude="bool")
        nums = list(num.stack().astype(float).to_numpy())
        for c in df.select_dtypes(include="object"):
            for s in df[c].dropna().astype(str).head(20000):
                nums += [float(x) for x in re.findall(r"-?\d+\.\d+|-?\d+", s.replace(",", "."))[:20]]
    return np.array(nums, float), txt.lower()
def derivados(path):
    """Somas, médias e percentagens por linha e por coluna das colunas numéricas (só CSV com ≤ 5.000 linhas)."""
    if path.startswith("DERIVADO") or not path.endswith(".csv"): return np.array([])
    df = pd.read_csv(f"{R}/{path}", low_memory=False)
    if len(df) > 5000: return np.array([])
    X = df.select_dtypes(include="number").select_dtypes(exclude="bool").astype(float)
    if X.empty: return np.array([])
    out = [X.sum(0), X.mean(0), X.sum(1), X.mean(1)]
    rs = X.sum(1).replace(0, np.nan); cs = X.sum(0).replace(0, np.nan)
    out += [X.div(rs, axis=0).stack() * 100, X.div(cs, axis=1).stack() * 100]
    for _, g in df.groupby(df.columns[0]) if df.shape[1] > 1 and df[df.columns[0]].dtype == object else []:
        Xg = g.select_dtypes(include="number").select_dtypes(exclude="bool").astype(float); out += [Xg.sum(0), Xg.mean(0)]
    return np.concatenate([np.asarray(o, float).ravel() for o in out])
def reps(vals):
    s = set()
    for k in range(0, 5):
        for f in (1, 100, 0.01):
            s |= set(np.round(vals * f, k).astype(str)); s |= set(np.round(-vals * f, k).astype(str))
    return s
def nums_tabela(body):
    out = []
    body = body.replace("{,}", ",").replace("$-$", "-").replace("$+$", "+")
    for m in re.finditer(r"(?<![\w.])([-+]?)(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?(?![\w])", body):
        sg, ip, dp = m.group(1), m.group(2).replace(".", ""), m.group(3)
        v = float(ip + ("." + dp if dp else "")); v = -v if sg == "-" else v
        if dp: out.append((m.group(0), str(round(v, len(dp)))))
        elif abs(v) >= 10 and not (1990 <= abs(v) <= 2030): out.append((m.group(0), str(float(v))))
    return out
def termos_tabela(body):
    body = re.sub(r"\\[a-zA-Z]+\*?(\[[^]]*\])?", " ", body); body = re.sub(r"[{}$&\\|~^_]", " ", body)
    toks = [w.lower() for w in re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\-]{3,}", body)]
    stop = {"tabela", "termo", "termos", "código", "códigos", "domínio", "conceito", "conceitos", "classe", "tópico", "tópicos", "microarranjos", "metamateriais", "radiômica", "hline", "multirow", "multicolumn", "applied", "methodological", "general", "comunidade", "agrupamento", "interpretação", "âncora", "textit", "textbf", "global"}
    return sorted({w for w in toks if w not in stop})
CODE = {}
for p in glob.glob(f"{B}/codigo/**/*.py", recursive=True) + glob.glob(f"{R}/**/*.py", recursive=True):
    if re.search(r"F1[789]_", p): continue
    try: CODE[p] = open(p, encoding="utf8", errors="ignore").read()
    except Exception: pass
def scripts_de(nome):
    base = os.path.basename(nome).replace(".csv", "").replace(".json", "").replace(".log", "")
    base = re.sub(r"_(microarranjos|metamateriais|radiomica)$", "_", base)
    return sorted({os.path.relpath(p, B) for p, c in CODE.items() if base.rstrip("_") in c})[:3]
t = open(TEX, encoding="utf8").read(); a = t.index(r"\section{Resultados}"); b = t.index(r"\section{Discussion}")
nt = len(re.findall(r"\\begin\{table\*?\}", t[:a])); nf = len(re.findall(r"\\begin\{figure\*?\}", t[:a]))
sec = t[a:b]; subs = [(m.start(), m.group(1)) for m in re.finditer(r"\\subsection\{([^}]*)\}", sec)]
sub_de = lambda pos: next((f"3.{i+1}" for i, (p, n) in reversed(list(enumerate(subs))) if p <= pos), "3")
TAB, FIG = [], []
for m in re.finditer(r"\\begin\{(table\*?|figure\*?)\}(.*?)\\end\{\1\}", sec, re.S):
    body = m.group(2); labs = re.findall(r"\\label\{([^}]*)\}", body)
    if m.group(1).startswith("table"):
        nt += 1; lab = labs[0] if labs else ""; perg, fs, tipo = FONTES.get(lab, ("?", [], "num"))
        tb = body[body.find(r"\begin{tabular"):] if r"\begin{tabular" in body else body
        S = set(); TX = ""; hs = []; scr = set()
        for f in fs:
            v, tx = valores(f); S |= reps(v); TX += " " + tx
            if not f.startswith("DERIVADO"): hs.append(f"{os.path.basename(f)}:{h(f'{R}/{f}')[:16]}"); scr |= set(scripts_de(f))
            else: hs.append(f"rotulos_v2_final.csv:{h(f'{R}/F2_rotulacao_v2/rotulos_v2_final.csv')[:16]} (agregado por domínio×rótulo)")
        if tipo == "num":
            ns = nums_tabela(tb); ok = [x for x in ns if x[1] in S]; resto = [x for x in ns if x[1] not in S]
            DS = set()
            for f in fs: DS |= reps(derivados(f))
            der = [x for x in resto if x[1] in DS]; falt = [x[0] for x in resto if x[1] not in DS]; ok = ok + der; tot = len(ns)
        else:
            if lab in ("lda_topics_dominios", "mca_clusters"):
                tb = " ".join(l.split("&")[-1] for l in re.split(r"\\\\", tb) if "&" in l)
            ws = termos_tabela(tb); TXn = unicodedata.normalize("NFKC", TX)
            ws = [w for w in ws if w not in ("tabular", "ordenados", "top-")]
            ok = [w for w in ws if w in TXn]; falt = [w for w in ws if w not in TXn]; tot = len(ws)
        frac = len(ok) / tot if tot else 0
        est = "NÃO CONFERIDO" if not fs or tot == 0 or frac < 0.5 else ("CONFIRMADO" if frac == 1 else "PARCIAL")
        TAB.append({"tabela": f"Tabela {nt}", "label": lab, "subseccao": sub_de(m.start()), "pergunta": perg, "arquivos": " | ".join(fs),
                    "script_produtor": " | ".join(sorted(scr)) or "não localizado por nome", "sha256_16": " | ".join(hs),
                    "chave": "domínio/estratégia/lista" if tipo == "num" else "termo/conceito/código", "tipo_conferencia": "valores" if tipo == "num" else "termos",
                    "encontrados": f"{len(ok)}/{tot}", "via_derivado": (len(der) if tipo == "num" else 0), "nao_encontrados": "; ".join(falt[:25]) + (" …" if len(falt) > 25 else ""),
                    "homologado_P01": lab in HOMOLOG_P01, "estado": est})
    else:
        nf += 1; files = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]*)\}", body); rows = []
        for f in files:
            f = f if f.endswith(".pdf") else f + ".pdf"; pm = os.path.join(FIGDIR, os.path.basename(f))
            hm = h(pm) if os.path.exists(pm) else ""
            cand = [p for p in glob.glob(f"{B}/resultados/**/{os.path.basename(f)}", recursive=True)]
            igual = [p for p in cand if h(p) == hm]; stem = os.path.basename(f)[:-4]
            gen = sorted({os.path.relpath(p, B) for p, c in CODE.items() if re.sub(r"_(microarranjos|metamateriais|radiomica|t\d+|applied|general|methodological|legenda)$", "", stem) in c})[:3]
            dados = set()
            for g in gen: dados |= set(re.findall(r"[\w/.-]+\.csv", CODE[f"{B}/{g}"]))
            rows.append({"painel": os.path.basename(f), "sha256_16": hm[:16], "artefato_hash_igual": os.path.relpath(igual[0], B) if igual else "—",
                         "script": " | ".join(gen) or "não localizado por nome", "dados_lidos_pelo_script": " | ".join(sorted(dados))[:300]})
        FIG.append({"figura": f"Figura {nf}", "label": labs[0] if labs else "", "subseccao": sub_de(m.start()), "paineis": len(rows), "detalhe": rows,
                    "estado_arquivo": "CONFIRMADO" if rows and all(r["artefato_hash_igual"] != "—" for r in rows) else "PARCIAL"})
MANUAL = {
 "corpus": ("CONFIRMADO", "25.050 = soma de unicos_id; 22.051 = soma de resumo_ge10_tokens das 9 linhas; 21.679 = soma das uniões. OBSERVAÇÃO: a coluna 'Com resumo' contém resumo_ge10_tokens (resumo utilizável); no campo com_resumo, Metamateriais B tem 4.813 (tabela: 4.812) — rotulagem do cabeçalho, não erro de valor."),
 "facetas_exp": ("CONFIRMADO", "I = (2001/153)/(3695/589) = 2,08 e δ_obj^rel = 6135/6003 = 1,02 calculados das contagens de desenho_2x2.csv; 0,992 = Jaccard máximo (0,9924) de temporal.csv."),
 "hst_overlap": ("CONFIRMADO", "p_HST 29,8/8,8/23,2 em reintegracao_hst.csv (com_HST_%); ρ_B 2,4/1,5/18,7 = |A∩B|/|B| das contagens."),
 "sobreposicao_externas": ("CONFIRMADO", "Linha 'Média' = média por plataforma de sobreposicao_externas_top100.csv (94,9; 91,9; 87,4; 84,1; 59,4; 45,7; 44,9; 32,9; 69,9; 69,3)."),
 "validacao_humana": ("CONFIRMADO", "Iguais H=L por área recalculados de notas_humanos_LLM.csv com a mediana das fichas da área (empate → nota inferior): Biomedicina 73,9%, Física 72,0%, Eng. 75,8%."),
 "concordancia_fichas": ("DIVERGENTE", "Ficha T, '1 nível abaixo': notas_humanos_LLM.csv dá 52/322 = 16,149% → 16,1; a fonte agregada dá 0,161; o manuscrito publica 16,2. Diferença de 0,1 p.p. (arredondamento). Correção proposta, não aplicada."),
 "lda_topics_dominios": ("CONFIRMADO", "95/95 termos principais (inglês) presentes em lda_topics_<domínio>.csv; o único não encontrado é a palavra de cabeçalho 'principais'. Os nomes propostos em português são interpretação dos autores (sem artefato)."),
 "mca_clusters": ("CONFIRMADO", "36/36 conceitos presentes em mca_coordenadas_<domínio>.csv; não encontrados só 'mais representativos' (cabeçalho). A interpretação temática em português é dos autores."),
 "p100_humana": ("CONFIRMADO", "Homologado no Protocolo 01. 100, 1.080, 812 e 109 são contagens do desenho (amostra_posicoes_NAO_ENVIAR.csv)."),
 "p100_replicacao": ("CONFIRMADO", "Homologado no Protocolo 01 (emenda da v12). 933/812 e 147/109 são contagens do desenho (amostra_posicoes_NAO_ENVIAR.csv)."),
}
for r in TAB:
    if r["label"] in MANUAL: r["estado_automatico"] = r["estado"]; r["estado"], r["verificacao_manual"] = MANUAL[r["label"]]
T = pd.DataFrame(TAB); T.to_csv(f"{OUT}/matriz_tabelas_5_54.csv", index=False)
json.dump(FIG, open(f"{OUT}/matriz_figuras_3_21.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
pd.DataFrame([{"figura": x["figura"], "label": x["label"], "subseccao": x["subseccao"], "paineis": x["paineis"], "estado_arquivo": x["estado_arquivo"],
               "scripts": " | ".join(sorted({s for r in x["detalhe"] for s in r["script"].split(" | ")}))} for x in FIG]).to_csv(f"{OUT}/matriz_figuras_3_21.csv", index=False)
print(T.estado.value_counts().to_string()); print(len(T), "tabelas;", len(FIG), "figuras")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 90)
print(T[T.estado != "CONFIRMADO"][["tabela", "label", "encontrados", "nao_encontrados"]].to_string(index=False))
