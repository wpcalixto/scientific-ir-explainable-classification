#!/bin/bash
# Title: criar_venv_gpu5070.sh
# File type: Shell script
# Purpose: Creates the Python virtual environment from requirements_adequacao_congelado.txt.
# Repository: scientific-ir-explainable-classification
# Version: v1.0.0
# Date: 2026-11-27
# Developer: Prof. Wesley Pacheco Calixto
# Authors:
#   Viviane M. Gomes Pacheco; ORCID 0000-0003-3693-4377; EMC/UFG; PUC Goias; CPDT/IFG
#   Clóves Gonçalves Rodrigues; ORCID 0000-0003-0140-9847; PUC Goias
#   Antonio Paulo Coimbra; ORCID 0000-0003-3780-2405; ISR/University of Coimbra
#   Wesley Pacheco Calixto; ORCID 0000-0002-1928-4432; ISR/University of Coimbra; EMC/UFG; CPDT/IFG
# Corresponding author: Wesley Pacheco Calixto, wesley.pacheco@ufg.br
# License: MIT
# Citation: Pacheco, V. M. G., Rodrigues, C. G., Coimbra, A. P., & Calixto, W. P. (2026). Reproducibility package for a protocol for scientific information retrieval with explainable text classification: code, bibliographic search datasets, LLM and human relevance judgements and analysis results (v1.0.0) [Data set and software]. Zenodo. https://doi.org/10.5281/zenodo.19791096
# Execution: BIBLIO_BASE=<package_dir> BIBLIO_PYTHON=<python> bash environment/criar_venv_gpu5070.sh
# Portability notes: paths relative to BIBLIO_BASE (default: package root).
BIBLIO_BASE="${BIBLIO_BASE:-$(cd "$(dirname "$0")/.." && pwd)}"
set -e
V=${BIBLIO_VENV:-$HOME/venvs/bibliometria}
R=$BIBLIO_BASE/environment
date
python3 -m venv $V
$V/bin/pip install --upgrade pip
$V/bin/pip install -r $R/requirements_adequacao.txt
$V/bin/pip freeze > $R/requirements_adequacao_congelado.txt
$V/bin/python -c "import pandas,sklearn,gensim,shap,lime,scipy,statsmodels;print(\"OK\",pandas.__version__,sklearn.__version__,gensim.__version__,shap.__version__)"
date
