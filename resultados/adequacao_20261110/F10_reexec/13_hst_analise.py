#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    13_hst_analise.py

File type:
    Script

Purpose:
    Comparative analyses of HST versus general terms (Venn diagrams, overlap and boxplots).

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
    - See docs/file_level_documentation.md (entry 13_hst_analise.py).

Outputs:
    - See docs/file_level_documentation.md (entry 13_hst_analise.py).

Dependencies:
    - matplotlib
    - numpy
    - pandas

Execution:
    python resultados/adequacao_20261110/F10_reexec/13_hst_analise.py  (paths relative to this folder)

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

import os, shutil, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle

warnings.filterwarnings("ignore")

BASE        = os.path.dirname(os.path.abspath(__file__))
OPENALEX    = os.path.join(BASE, "dados_openalex")
PROC_DIR    = os.path.join(BASE, "dados_processados")
OUT_FIG     = os.path.join(BASE, "figuras_pdf")
OUT_DAT     = os.path.join(BASE, "dados_classificacao")
ZENODO      = os.path.join(BASE, "zenodo")
os.makedirs(OUT_FIG, exist_ok=True)
os.makedirs(OUT_DAT, exist_ok=True)

FS = 18
plt.rcParams.update({
    'font.size': FS, 'axes.titlesize': FS - 1, 'axes.labelsize': FS - 1,
    'xtick.labelsize': FS - 2, 'ytick.labelsize': FS - 2,
    'legend.fontsize': FS - 3, 'figure.dpi': 150,
    'axes.spines.top': False, 'axes.spines.right': False,
    'savefig.dpi': 200,
})

DOMAINS    = ["microarranjos", "metamateriais", "radiomica"]
DOMAINS_EN = {"microarranjos": "Microarrays", "metamateriais": "Metamaterials",
               "radiomica": "Radiomics"}

HST_TERMS = {
    "microarranjos": ["microarray", "microarrays"],
    "metamateriais": ["metamaterial", "metamaterials", "metasurface", "metasurfaces"],
    "radiomica":     ["radiomics", "radiomic"],
}

GENERAL_TERMS = {
    "microarranjos": ["machine learning", "feature selection", "variable selection",
                      "classification", "auc-roc", "roc curve", "area under curve"],
    "metamateriais": ["machine learning", "deep learning", "neural network",
                      "simulation", "optimization", "design"],
    "radiomica":     ["machine learning", "feature selection", "classification",
                      "auc-roc", "roc curve", "feature extraction", "deep learning"],
}


def doc_keys(df: pd.DataFrame) -> set:
    """Retorna conjunto de chaves únicas: DOI normalizado (preferencial) ou OpenAlex ID."""
    doi = df["doi"].fillna("").astype(str).str.strip().str.lower()
    oid = df["openalex_id"].fillna("").astype(str).str.strip()
    key = doi.where(doi != "", oid)
    return set(key[key != ""])


def make_venn():
    """Painel 1×3 com um Venn por domínio (Strategy A vs Strategy B)."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    records = []

    for ax, dom in zip(axes, DOMAINS):
        fa = os.path.join(OPENALEX, f"{dom}_busca_A.csv")
        fb = os.path.join(OPENALEX, f"{dom}_busca_B.csv")
        if not os.path.exists(fa) or not os.path.exists(fb):
            ax.set_title(f"{DOMAINS_EN[dom]}\n(data not found)")
            continue

        df_a = pd.read_csv(fa)
        df_b = pd.read_csv(fb)
        keys_a = doc_keys(df_a)
        keys_b = doc_keys(df_b)

        only_a = len(keys_a - keys_b)
        only_b = len(keys_b - keys_a)
        inter  = len(keys_a & keys_b)
        total  = len(keys_a | keys_b)

        assert only_a + inter == len(keys_a), \
            f"{dom}: |A only| + |A∩B| ≠ |A|  ({only_a}+{inter}≠{len(keys_a)})"
        assert only_b + inter == len(keys_b), \
            f"{dom}: |B only| + |A∩B| ≠ |B|  ({only_b}+{inter}≠{len(keys_b)})"
        assert only_a + only_b + inter == total, \
            f"{dom}: cardinalidade da união inconsistente"

        records.append({"dominio": dom,
                         "n_A": len(keys_a), "n_B": len(keys_b),
                         "only_A": only_a, "only_B": only_b,
                         "intersection": inter, "union": total})

        max_r   = 1.8
        r_a = max_r * np.sqrt(len(keys_a) / max(len(keys_a), len(keys_b)))
        r_b = max_r * np.sqrt(len(keys_b) / max(len(keys_a), len(keys_b)))
        sep  = 0.80 * (r_a + r_b) / 2
        cx_a = -sep / 2
        cx_b =  sep / 2

        circ_a = Circle((cx_a, 0), r_a, alpha=0.35, color="#ef4444")
        circ_b = Circle((cx_b, 0), r_b, alpha=0.35, color="#3b82f6")
        ax.add_patch(circ_a)
        ax.add_patch(circ_b)

        ax.text(cx_a - r_a * 0.55, 0, f"{only_a:,}", ha="center", va="center",
                fontsize=FS, fontweight="bold", color="#b91c1c")
        ax.text(cx_b + r_b * 0.55, 0, f"{only_b:,}", ha="center", va="center",
                fontsize=FS, fontweight="bold", color="#1d4ed8")
        ax.text(0, 0, f"{inter:,}", ha="center", va="center",
                fontsize=FS - 1, fontweight="bold", color="#333")

        ax.set_xlim(-3.2, 3.2)
        ax.set_ylim(-2.5, 2.5)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(DOMAINS_EN[dom], fontsize=FS, fontweight="bold", pad=10)

        ax.text(cx_a - r_a, -2.3, "Strategy A (HST)", ha="center",
                fontsize=FS, color="#b91c1c")
        ax.text(cx_b + r_b, -2.3, "Strategy B (HSSS)", ha="center",
                fontsize=FS, color="#1d4ed8")

    fig.tight_layout()
    out = os.path.join(OUT_FIG, "fig_venn_hst.pdf")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"[Tópico 1] Salvo: {out}")

    df_rec = pd.DataFrame(records)
    df_rec.to_csv(os.path.join(OUT_DAT, "hst_sobreposicao.csv"), index=False)
    print(f"[Tópico 1] CSV: dados_classificacao/hst_sobreposicao.csv")


def _count_term(texts: pd.Series, term: str) -> int:
    """Conta documentos cujo texto (minúsculas) contém o termo."""
    return int(texts.str.contains(term.lower(), na=False, regex=False).sum())


def make_freq_table():
    """Calcula e exporta tabela de frequência + estatísticas descritivas."""
    rows = []
    for dom in DOMAINS:
        fp = os.path.join(PROC_DIR, f"corpus_{dom}.csv")
        if not os.path.exists(fp):
            print(f"[Tópico 2] Arquivo não encontrado: {fp}")
            continue
        df = pd.read_csv(fp, usecols=["texto_combinado"])
        texts = df["texto_combinado"].fillna("").str.lower()
        N = len(df)

        for term in HST_TERMS[dom]:
            freq = _count_term(texts, term)
            rows.append({"dominio": dom, "domain_en": DOMAINS_EN[dom],
                         "category": "HST", "term": term, "freq": freq,
                         "freq_pct": round(100 * freq / N, 2)})
        for term in GENERAL_TERMS[dom]:
            freq = _count_term(texts, term)
            rows.append({"dominio": dom, "domain_en": DOMAINS_EN[dom],
                         "category": "General", "term": term, "freq": freq,
                         "freq_pct": round(100 * freq / N, 2)})

    df_all = pd.DataFrame(rows)
    df_all.to_csv(os.path.join(OUT_DAT, "hst_frequencia_tabela.csv"), index=False)

    _export_freq_tex(df_all)

    stats_rows = []
    for dom in DOMAINS:
        for cat in ["HST", "General"]:
            sub = df_all[(df_all["dominio"] == dom) & (df_all["category"] == cat)]["freq"]
            if sub.empty:
                continue
            stats_rows.append({
                "Domain": DOMAINS_EN[dom], "Category": cat,
                "Mean": round(sub.mean(), 1), "Std": round(sub.std(), 1),
                "Min": int(sub.min()), "Q25": int(sub.quantile(.25)),
                "Median": int(sub.median()), "Q75": int(sub.quantile(.75)),
                "Max": int(sub.max()),
            })
    df_stats = pd.DataFrame(stats_rows)
    df_stats.to_csv(os.path.join(OUT_DAT, "hst_estatisticas.csv"), index=False)
    _export_stats_tex(df_stats)
    print(f"[Tópico 2] Tabelas salvas em dados_classificacao/")
    return df_all


def _export_freq_tex(df: pd.DataFrame):
    lines = [
        r"\begin{table}[ht]", r"\centering",
        r"\caption{Frequency of HST and general terms per domain. "
        r"Frequency = number of documents (title + abstract) containing the term.}",
        r"\label{tab:hst_freq}",
        r"\scriptsize",
        r"\begin{tabular}{llrr}",
        r"\hline",
        r"\textbf{Domain / Category} & \textbf{Term} & \textbf{Freq.} & \textbf{\%} \\",
        r"\hline",
    ]
    for dom in DOMAINS:
        sub = df[df["dominio"] == dom]
        dom_en = DOMAINS_EN[dom]
        for cat in ["HST", "General"]:
            csub = sub[sub["category"] == cat].sort_values("freq", ascending=False)
            first = True
            for _, row in csub.iterrows():
                label = f"{dom_en} — {cat}" if first else ""
                lines.append(f"{label} & {row['term']} & {int(row['freq']):,} & {row['freq_pct']:.1f} \\\\")
                first = False
        lines.append(r"\hline")
    lines += [r"\end{tabular}", r"\end{table}", ""]
    with open(os.path.join(OUT_DAT, "hst_frequencia_tabela.tex"), "w") as f:
        f.write("\n".join(lines))


def _export_stats_tex(df: pd.DataFrame):
    lines = [
        r"\begin{table}[ht]", r"\centering",
        r"\caption{Descriptive statistics of term frequencies: HST vs.\ general terms, per domain.}",
        r"\label{tab:hst_stats}",
        r"\scriptsize",
        r"\begin{tabular}{llrrrrrrr}",
        r"\hline",
        r"\textbf{Domain} & \textbf{Cat.} & \textbf{Mean} & \textbf{SD} & "
        r"\textbf{Min} & \textbf{Q1} & \textbf{Median} & \textbf{Q3} & \textbf{Max} \\",
        r"\hline",
    ]
    for _, row in df.iterrows():
        lines.append(
            f"{row['Domain']} & {row['Category']} & {row['Mean']:,.1f} & {row['Std']:,.1f} & "
            f"{row['Min']:,} & {row['Q25']:,} & {row['Median']:,} & {row['Q75']:,} & {row['Max']:,} \\\\"
        )
    lines += [r"\hline", r"\end{tabular}", r"\end{table}", ""]
    with open(os.path.join(OUT_DAT, "hst_estatisticas.tex"), "w") as f:
        f.write("\n".join(lines))


def make_boxplot(df_freq=None):
    """Painel 3 × 2: (a) box plot e (b) scatter por domínio."""
    if df_freq is None:
        fp = os.path.join(OUT_DAT, "hst_frequencia_tabela.csv")
        if not os.path.exists(fp):
            print("[Tópico 3] Execute make_freq_table() primeiro.")
            return
        df_freq = pd.read_csv(fp)

    fig, axes = plt.subplots(3, 2, figsize=(16, 15))

    for row_idx, dom in enumerate(DOMAINS):
        sub = df_freq[df_freq["dominio"] == dom]
        hst_vals  = sub[sub["category"] == "HST"]["freq"].values
        gen_vals  = sub[sub["category"] == "General"]["freq"].values
        hst_terms = sub[sub["category"] == "HST"]["term"].tolist()
        gen_terms = sub[sub["category"] == "General"]["term"].tolist()

        ax_box  = axes[row_idx, 0]
        ax_scat = axes[row_idx, 1]

        bp = ax_box.boxplot([hst_vals, gen_vals], tick_labels=["HST", "General"],
                            patch_artist=True, widths=0.5,
                            medianprops=dict(color="black", linewidth=2))
        bp["boxes"][0].set_facecolor("#ef444488")
        bp["boxes"][1].set_facecolor("#3b82f688")
        ax_box.set_ylabel("Document frequency")
        ax_box.set_title(f"{DOMAINS_EN[dom]} — Frequency Distribution")

        all_terms = hst_terms + gen_terms
        all_vals  = list(hst_vals) + list(gen_vals)
        all_cats  = ["HST"] * len(hst_terms) + ["General"] * len(gen_terms)
        colors    = ["#ef4444" if c == "HST" else "#3b82f6" for c in all_cats]

        x_pos = np.arange(len(all_terms))
        ax_scat.scatter(x_pos, all_vals, c=colors, s=120, zorder=3)
        for xi, yi, term in zip(x_pos, all_vals, all_terms):
            ax_scat.annotate(term, (xi, yi), textcoords="offset points",
                             xytext=(0, 7), ha="center", fontsize=7, rotation=45)
        ax_scat.set_xticks(x_pos)
        ax_scat.set_xticklabels(all_terms, rotation=55, ha="right", fontsize=7)
        ax_scat.set_ylabel("Document frequency")
        ax_scat.set_title(f"{DOMAINS_EN[dom]} — Frequency per Term")
        legend_elems = [
            mpatches.Patch(color="#ef4444", label="HST"),
            mpatches.Patch(color="#3b82f6", label="General"),
        ]
        ax_scat.legend(handles=legend_elems, fontsize=FS - 4)
        ax_scat.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    out = os.path.join(OUT_FIG, "fig_boxplot_hst.pdf")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"[Tópico 3] Salvo: {out}")


def copy_to_zenodo():
    files = [
        os.path.join(OUT_FIG, "fig_venn_hst.pdf"),
        os.path.join(OUT_FIG, "fig_boxplot_hst.pdf"),
        os.path.join(OUT_DAT, "hst_frequencia_tabela.csv"),
        os.path.join(OUT_DAT, "hst_frequencia_tabela.tex"),
        os.path.join(OUT_DAT, "hst_estatisticas.csv"),
        os.path.join(OUT_DAT, "hst_estatisticas.tex"),
        os.path.join(OUT_DAT, "hst_sobreposicao.csv"),
    ]
    for f in files:
        if os.path.exists(f):
            shutil.copy2(f, ZENODO)
    print("[Zenodo] Arquivos copiados.")


if __name__ == "__main__":
    print("=== 13_hst_analise.py ===")
    make_venn()
    df_freq = make_freq_table()
    make_boxplot(df_freq)
    copy_to_zenodo()
    print("Concluído.")
