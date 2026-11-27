#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    estilo_figuras.py

File type:
    Module

Purpose:
    Shared figure-style module (colours, markers, names and sizes).

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
    - See docs/file_level_documentation.md (entry estilo_figuras.py).

Outputs:
    - See docs/file_level_documentation.md (entry estilo_figuras.py).

Dependencies:
    - matplotlib

Execution:
    BIBLIO_BASE=<package_dir> python codigo/adequacao_20261110/estilo_figuras.py

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

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt

MEIA, INTEIRA, FS = 7.2299, 14.4598, 19
OI = {"azul": "#0072B2", "laranja": "#E69F00", "verde": "#009E73", "vermelhao": "#D55E00",
      "roxo": "#CC79A7", "amarelo": "#F0E442", "celeste": "#56B4E9", "preto": "#000000", "cinza": "#7F7F7F"}
DOMINIO = {"microarranjos": ("Microarrays", OI["azul"], "o"), "metamateriais": ("Metamaterials", OI["roxo"], "s"),
           "radiomica": ("Radiomics", OI["vermelhao"], "^")}
ESTRATEGIA = {"A": ("Strategy A (HST)", OI["verde"], "o"), "B": ("Strategy B (broad)", OI["laranja"], "s"),
              "C": ("Strategy C (focused)", OI["celeste"], "^")}
GRUPO_TERMO = {"HST": ("HST terms", OI["verde"], "o"), "General": ("General terms", "#555555", "s")}
CLASSE = {"Applied": (OI["azul"], "-"), "Methodological": (OI["vermelhao"], "--"), "General": (OI["verde"], ":")}
CLASSIFICADOR = {"SVM": ("SVM", OI["azul"], "o"), "RF": ("RF", OI["laranja"], "s"), "RL": ("LR", OI["verde"], "^"),
                 "NB": ("NB", OI["roxo"], "D")}
METRICA = {"acc": ("Accuracy", OI["azul"], ""), "f1": ("Macro F1", OI["vermelhao"], "//"),
           "prec": ("Macro precision", OI["verde"], ".."), "rec": ("Macro recall", OI["laranja"], "xx")}
CURVA = {"treino": ("Training", OI["azul"], "o", "-"), "valid": ("Validation", OI["vermelhao"], "s", "--")}
QUADRANTE = {"Motor themes": OI["azul"], "Basic themes": OI["laranja"], "Niche themes": OI["verde"], "Emerging or declining themes": OI["roxo"]}
AGRUPAMENTO = [(OI["azul"], "o"), (OI["vermelhao"], "s"), (OI["verde"], "^"), (OI["laranja"], "D"),
               (OI["roxo"], "v"), (OI["celeste"], "P"), (OI["amarelo"], "X"), (OI["cinza"], "h")]
LIME_SINAL = {True: OI["verde"], False: OI["vermelhao"]}
ORDEM_DOM = ["microarranjos", "metamateriais", "radiomica"]
TINTA, TINTA2, GRADE = "#111111", "#444444", "#DDDDDD"

def aplicar():
    mpl.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": FS, "axes.labelsize": FS, "axes.titlesize": FS, "xtick.labelsize": FS,
        "ytick.labelsize": FS, "legend.fontsize": FS, "pdf.fonttype": 42, "ps.fonttype": 42,
        "axes.edgecolor": TINTA2, "axes.labelcolor": TINTA, "xtick.color": TINTA2, "ytick.color": TINTA2, "text.color": TINTA,
        "axes.linewidth": 1.4, "xtick.major.width": 1.4, "ytick.major.width": 1.4, "xtick.major.size": 6, "ytick.major.size": 6,
        "lines.linewidth": 3.0, "lines.markersize": 10, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "grid.color": GRADE, "grid.linewidth": 1.0, "axes.axisbelow": True,
        "legend.frameon": False, "legend.handlelength": 1.6, "figure.facecolor": "white", "savefig.facecolor": "white"})

def figura(largura=MEIA, altura=5.4):
    return plt.subplots(figsize=(largura, altura), layout="constrained")

def gravar(fig, caminho, manifesto):
    fig.savefig(caminho, format="pdf"); plt.close(fig); manifesto.append(caminho)
