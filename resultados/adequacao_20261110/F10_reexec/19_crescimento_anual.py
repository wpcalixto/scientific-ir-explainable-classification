#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    19_crescimento_anual.py

File type:
    Script

Purpose:
    Annual percentage growth per domain.

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
    - See docs/file_level_documentation.md (entry 19_crescimento_anual.py).

Outputs:
    - See docs/file_level_documentation.md (entry 19_crescimento_anual.py).

Dependencies:
    - numpy
    - pandas

Execution:
    python resultados/adequacao_20261110/F10_reexec/19_crescimento_anual.py  (paths relative to this folder)

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

import os, shutil
import numpy as np
import pandas as pd

BASE    = os.path.dirname(os.path.abspath(__file__))
OA_DIR  = os.path.join(BASE, "dados_openalex")
DAD_DIR = os.path.join(BASE, "dados_classificacao")
ZEN_DIR = os.path.join(BASE, "zenodo")
os.makedirs(DAD_DIR, exist_ok=True)

YEAR_MIN = 2018
YEAR_MAX = 2025
DOMAINS  = ["microarranjos", "metamateriais", "radiomica"]
DOMAINS_EN = {
    "microarranjos": "Microarrays",
    "metamateriais": "Metamaterials",
    "radiomica":     "Radiomics",
}


def compute_growth(df_all):
    """
    Retorna DataFrame pivotado:
    linhas = anos, colunas = (dominio, n) e (dominio, delta_pct)
    """
    df = df_all[df_all["year"].between(YEAR_MIN, YEAR_MAX)].copy()
    counts = (df.groupby(["dominio", "year"])
               .size()
               .reset_index(name="n"))

    records = []
    for dom in DOMAINS:
        sub = (counts[counts["dominio"] == dom][["year", "n"]]
               .set_index("year")
               .reindex(range(YEAR_MIN, YEAR_MAX + 1), fill_value=0)
               .reset_index())
        sub.columns = ["year", "n"]
        sub["delta_pct"] = sub["n"].pct_change() * 100
        sub["dominio"] = dom
        records.append(sub)

    df_long = pd.concat(records, ignore_index=True)
    return df_long


def pivot_wide(df_long):
    """Formata em tabela wide para exportação: linhas=ano, col=(dom,{n,Δ%})."""
    rows = []
    for year in range(YEAR_MIN, YEAR_MAX + 1):
        row = {"year": year}
        for dom in DOMAINS:
            sub = df_long[(df_long["dominio"] == dom) & (df_long["year"] == year)]
            row[f"{dom}_n"]         = int(sub["n"].values[0]) if len(sub) else 0
            row[f"{dom}_delta_pct"] = round(sub["delta_pct"].values[0], 1) if len(sub) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def to_latex(df_wide):
    """Gera código LaTeX com \multicolumn para agrupamento por domínio."""
    header1 = " & ".join(
        [r"\multirow{2}{*}{Year}"] +
        [r"\multicolumn{2}{c}{" + DOMAINS_EN[d] + "}" for d in DOMAINS]
    ) + r" \\"
    header2 = " & " + " & ".join(["$n$ & $\\Delta\\%$"] * len(DOMAINS)) + r" \\"
    cline = r"\cline{2-" + str(1 + 2 * len(DOMAINS)) + "}"

    col_format = "r" + "rr" * len(DOMAINS)

    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\caption{Annual document count and growth rate (\%) per domain, 2018–2024.}",
        r"\label{tab:crescimento_anual}",
        r"\small",
        r"\begin{tabular}{" + col_format + "}",
        r"\hline",
        header1,
        cline,
        header2,
        r"\hline",
    ]

    for _, row in df_wide.iterrows():
        year = int(row["year"])
        parts = [str(year)]
        for dom in DOMAINS:
            n   = int(row[f"{dom}_n"])
            dp  = row[f"{dom}_delta_pct"]
            dp_str = f"{dp:.1f}" if not np.isnan(dp) else "---"
            parts += [str(n), dp_str]
        lines.append(" & ".join(parts) + r" \\")

    lines += [r"\hline", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines) + "\n"


def copy_to_zenodo(paths):
    os.makedirs(ZEN_DIR, exist_ok=True)
    for p in paths:
        if os.path.isfile(p):
            shutil.copy2(p, ZEN_DIR)
            print(f"[zenodo] {os.path.basename(p)}")


if __name__ == "__main__":
    consol = os.path.join(OA_DIR, "consolidado_todos_dominios.csv")
    df_all = pd.read_csv(consol, low_memory=False)
    df_all = df_all.drop_duplicates(["dominio", "openalex_id"])
    df_all["year"] = pd.to_numeric(df_all["year"], errors="coerce")

    df_long = compute_growth(df_all)
    df_wide = pivot_wide(df_long)

    csv_out = os.path.join(DAD_DIR, "crescimento_anual.csv")
    df_wide.to_csv(csv_out, index=False)
    print(f"[OK] {csv_out}")

    tex_out = os.path.join(DAD_DIR, "crescimento_anual.tex")
    with open(tex_out, "w", encoding="utf-8") as f:
        f.write(to_latex(df_wide))
    print(f"[OK] {tex_out}")

    copy_to_zenodo([csv_out, tex_out])
    print("Script 19 concluído.")
