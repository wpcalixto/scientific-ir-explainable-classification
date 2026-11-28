#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    02_preprocessamento_lda.py

File type:
    Script

Purpose:
    Preprocessing and LDA topic modelling of each domain corpus (F10 re-execution).

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
    - See docs/file_level_documentation.md (entry 02_preprocessamento_lda.py).

Outputs:
    - See docs/file_level_documentation.md (entry 02_preprocessamento_lda.py).

Dependencies:
    - gensim
    - matplotlib
    - numpy
    - pandas
    - sklearn

Execution:
    python resultados/adequacao_20261110/F10_reexec/02_preprocessamento_lda.py  (paths relative to this folder)

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

import html as _html
import os, re, warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import gensim
from gensim import corpora
from gensim.models import LdaModel, CoherenceModel
from gensim.parsing.preprocessing import (
    strip_punctuation, strip_numeric, strip_multiple_whitespaces,
    remove_stopwords, stem_text,
)
warnings.filterwarnings("ignore")


INPUT_FILE  = "dados_openalex/consolidado_todos_dominios.csv"
OUTPUT_DIR  = "dados_processados"
RANDOM_SEED = 42
os.makedirs(OUTPUT_DIR, exist_ok=True)

STOPWORDS_EXTRA = {
    "study", "paper", "method", "approach", "result", "using", "used",
    "proposed", "based", "data", "analysis", "show", "shown", "use",
    "also", "however", "thus", "therefore", "two", "three", "one",
    "new", "different", "high", "low", "large", "small", "et", "al",
    "doi", "http", "www", "fig", "table", "figure",
    "mml", "math", "mathml", "xmlns", "xlink", "xml",
    "html", "w3", "w3c", "org", "sup", "sub", "inline",
    "tex", "mrow", "formula",
}

_FORBIDDEN_TOKENS = frozenset({
    "mml", "math", "mathml", "xmlns", "xlink", "xml",
    "org", "tex", "mrow", "formula",
})

LDA_K_RANGE   = list(range(5, 31, 2))
LDA_PASSES    = 20
LDA_ALPHA     = "auto"
LDA_ETA       = "auto"


def limpar_texto(texto):
    """Pipeline de limpeza: unescape HTML → strip tags/entities → lower → remove punct/nums → stopwords."""
    if not isinstance(texto, str) or len(texto.strip()) < 10:
        return []
    t = _html.unescape(texto)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"&[a-zA-Z]+;", " ", t)
    t = t.lower()
    t = strip_punctuation(t)
    t = strip_numeric(t)
    t = strip_multiple_whitespaces(t)
    t = remove_stopwords(t)
    tokens = [w for w in t.split() if len(w) > 2 and w not in STOPWORDS_EXTRA]
    return tokens


def preprocessar_corpus(df):
    """Gera coluna 'tokens' a partir de título + abstract."""
    df = df.copy()
    df["texto_combinado"] = (
        df["title"].fillna("") + " " + df["abstract"].fillna("")
    )
    df["tokens"] = df["texto_combinado"].apply(limpar_texto)
    leaked = [tok for toks in df["tokens"] for tok in toks if tok in _FORBIDDEN_TOKENS]
    assert not leaked, f"MathML tokens still present after cleaning: {set(leaked)}"
    df = df[df["tokens"].apply(len) >= 5].reset_index(drop=True)
    print(f"  Documentos com tokens suficientes: {len(df):,}")
    return df



def treinar_lda(corpus_bow, dicionario, k, passes=LDA_PASSES):
    """Treina LDA com k tópicos."""
    return LdaModel(
        corpus=corpus_bow,
        id2word=dicionario,
        num_topics=k,
        random_state=RANDOM_SEED,
        passes=passes,
        alpha=LDA_ALPHA,
        eta=LDA_ETA,
        per_word_topics=False,
    )


def curva_coherence(textos_tokenizados, dicionario, corpus_bow, dominio):
    """
    Calcula coherence (c_v) para cada k em LDA_K_RANGE.
    Salva figura e retorna k ótimo.
    """
    print(f"  Calculando coherence para k ∈ {LDA_K_RANGE}...")
    scores = []
    for k in LDA_K_RANGE:
        modelo = treinar_lda(corpus_bow, dicionario, k, passes=10)
        cm = CoherenceModel(
            model=modelo, texts=textos_tokenizados,
            dictionary=dicionario, coherence="c_v"
        )
        c = cm.get_coherence()
        scores.append(c)
        print(f"    k={k:2d}  coherence={c:.4f}")

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(LDA_K_RANGE, scores, marker="o", linewidth=2, color="#2563eb")
    k_otimo = LDA_K_RANGE[int(np.argmax(scores))]
    ax.axvline(k_otimo, color="#dc2626", linestyle="--", label=f"k ótimo = {k_otimo}")
    ax.set_xlabel("Number of topics (k)", fontsize=12)
    ax.set_ylabel("Coherence score (c_v)", fontsize=12)
    ax.set_title(f"LDA Coherence — {dominio}", fontsize=13)
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/coherence_curve_{dominio}.png", dpi=150)
    plt.close()
    print(f"  k ótimo: {k_otimo}  (coherence={max(scores):.4f})")

    pd.DataFrame({"k": LDA_K_RANGE, "coherence": scores}).to_csv(
        f"{OUTPUT_DIR}/coherence_scores_{dominio}.csv", index=False
    )
    return k_otimo


def extrair_topicos(modelo, dicionario, k, dominio):
    """Salva tabela de tópicos com top-10 termos e seus pesos."""
    rows = []
    for tid in range(k):
        termos = modelo.show_topic(tid, topn=10)
        for rank, (termo, peso) in enumerate(termos, 1):
            rows.append({"topico": tid, "rank": rank, "termo": termo, "peso": peso})
    df_top = pd.DataFrame(rows)
    df_top.to_csv(f"{OUTPUT_DIR}/lda_topics_{dominio}.csv", index=False)

    print(f"\n  Tópicos LDA ({dominio}, k={k}):")
    for tid in range(k):
        termos_str = ", ".join(
            df_top[df_top["topico"] == tid]["termo"].head(5).tolist()
        )
        print(f"    Tópico {tid:2d}: {termos_str}")
    return df_top


def distribuicao_topicos(df, modelo, corpus_bow, k):
    """Adiciona ao DataFrame a distribuição de tópicos de cada documento."""
    dist = []
    for bow in corpus_bow:
        vec = dict(modelo.get_document_topics(bow, minimum_probability=0.0))
        dist.append([vec.get(t, 0.0) for t in range(k)])
    col_names = [f"topic_{t}" for t in range(k)]
    df_dist = pd.DataFrame(dist, columns=col_names)
    return pd.concat([df.reset_index(drop=True), df_dist], axis=1)



CORES_ESTRATEGIA = {
    "busca_A": "#ef4444",
    "busca_B": "#3b82f6",
    "busca_C": "#22c55e",
}

def pca_topicos(df_com_topicos, k, dominio):
    """
    PCA sobre as colunas topic_0..topic_{k-1}.
    Figura de dispersão PC1×PC2 com elipses de confiança por estratégia.
    """
    cols_topico = [f"topic_{t}" for t in range(k)]
    X = df_com_topicos[cols_topico].values

    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X)

    pca = PCA(random_state=RANDOM_SEED)
    X_pca = pca.fit_transform(X_sc)

    var_exp = pca.explained_variance_ratio_
    cum_var = np.cumsum(var_exp)
    k_95 = int(np.argmax(cum_var >= 0.95)) + 1

    print(f"\n  PCA ({dominio}):")
    print(f"    PC1={var_exp[0]*100:.1f}%  PC2={var_exp[1]*100:.1f}%  "
          f"PC1+PC2={sum(var_exp[:2])*100:.1f}%")
    print(f"    Componentes para 95% da variância: {k_95}")

    pd.DataFrame({
        "componente": range(1, len(var_exp)+1),
        "variancia_explicada": var_exp,
        "variancia_acumulada": cum_var,
    }).to_csv(f"{OUTPUT_DIR}/pca_variance_{dominio}.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 7))
    patches = []
    for est, cor in CORES_ESTRATEGIA.items():
        mask = df_com_topicos["estrategia"] == est
        if mask.sum() < 5:
            continue
        X_est = X_pca[mask]
        ax.scatter(X_est[:, 0], X_est[:, 1], c=cor, alpha=0.35, s=8, label=est)

        mean = X_est[:, :2].mean(axis=0)
        cov  = np.cov(X_est[:, 0], X_est[:, 1])
        vals, vecs = np.linalg.eigh(cov)
        order = vals.argsort()[::-1]
        vals, vecs = vals[order], vecs[:, order]
        angle = np.degrees(np.arctan2(*vecs[:, 0][::-1]))
        width, height = 2 * 2.447 * np.sqrt(vals)
        ell = mpatches.Ellipse(
            mean, width, height, angle=angle,
            edgecolor=cor, facecolor="none", linewidth=2, linestyle="--"
        )
        ax.add_patch(ell)
        patches.append(mpatches.Patch(color=cor, label=est))

    ax.set_xlabel(f"PC1 ({var_exp[0]*100:.1f}% variance)", fontsize=12)
    ax.set_ylabel(f"PC2 ({var_exp[1]*100:.1f}% variance)", fontsize=12)
    ax.set_title(f"PCA of LDA topic distributions — {dominio}", fontsize=13)
    ax.legend(handles=patches, fontsize=11)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/pca_{dominio}.png", dpi=150)
    plt.close()
    print(f"  Figura salva: {OUTPUT_DIR}/pca_{dominio}.png")



def processar_dominio(df_dom, dominio):
    print(f"\n{'='*60}")
    print(f"DOMÍNIO: {dominio.upper()}  ({len(df_dom):,} documentos)")
    print(f"{'='*60}")

    df_longo = df_dom.copy()
    df_dom = df_dom.drop_duplicates("openalex_id").copy()
    print("\n[1] Pré-processamento...")
    df_dom = preprocessar_corpus(df_dom)
    df_dom.to_csv(f"{OUTPUT_DIR}/corpus_{dominio}.csv", index=False)

    textos = df_dom["tokens"].tolist()
    dicionario = corpora.Dictionary(textos)

    dicionario.filter_extremes(no_below=5, no_above=0.8)
    print(f"  Vocabulário após filtro: {len(dicionario):,} termos")

    corpus_bow = [dicionario.doc2bow(t) for t in textos]

    dicionario.save(f"{OUTPUT_DIR}/dicionario_{dominio}.gensim")

    print("\n[2] Seleção de k via coherence score...")
    k_otimo = curva_coherence(textos, dicionario, corpus_bow, dominio)

    print(f"\n[3] Treinando LDA final (k={k_otimo}, passes={LDA_PASSES})...")
    modelo = treinar_lda(corpus_bow, dicionario, k_otimo)
    modelo.save(f"{OUTPUT_DIR}/lda_model_{dominio}.gensim")

    print("\n[4] Extraindo tópicos...")
    extrair_topicos(modelo, dicionario, k_otimo, dominio)

    print("\n[5] Calculando distribuição de tópicos por documento...")
    df_com_topicos = distribuicao_topicos(df_dom, modelo, corpus_bow, k_otimo)
    df_com_topicos.drop(columns=["tokens", "texto_combinado"], errors="ignore").to_csv(
        f"{OUTPUT_DIR}/lda_doc_topics_{dominio}.csv", index=False
    )

    print("\n[6] Análise de componentes principais (PCA)...")
    cols_t = [f"topic_{t}" for t in range(k_otimo)]
    df_pca = df_longo[["openalex_id", "estrategia"]].merge(df_com_topicos[["openalex_id"] + cols_t], on="openalex_id", how="inner")
    pca_topicos(df_pca, k_otimo, dominio)

    print(f"\n  [{dominio}] Concluído.")
    return df_com_topicos


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"ERRO: {INPUT_FILE} não encontrado.")
        print("Execute primeiro: python3 01_coleta_openalex.py")
        return

    print("Carregando corpus consolidado...")
    df = pd.read_csv(INPUT_FILE, low_memory=False)
    print(f"Total de registros: {len(df):,}")
    print(f"Domínios: {df['dominio'].unique().tolist()}")
    print(f"Estratégias: {df['estrategia'].unique().tolist()}")

    resultados = {}
    import sys
    doms = sys.argv[1:] or df["dominio"].unique()
    for dominio in doms:
        df_dom = df[df["dominio"] == dominio].copy()
        resultados[dominio] = processar_dominio(df_dom, dominio)

    print(f"\n{'='*60}")
    print("PRÉ-PROCESSAMENTO E LDA CONCLUÍDOS")
    print(f"Arquivos em: {OUTPUT_DIR}/")
    print("="*60)


if __name__ == "__main__":
    main()
