#!/bin/bash
# Title: F2c_correr.sh
# File type: Shell script
# Purpose: Runs the OpenAlex collection stages in sequence.
# Repository: scientific-ir-explainable-classification
# Version: v1.0.1
# Date: 2026-11-27
# Developer: Prof. Wesley Pacheco Calixto
# Authors:
#   Wesley Pacheco Calixto; ORCID 0000-0002-1928-4432; ISR/University of Coimbra; EMC/UFG; CPDT/IFG
#   Viviane M. Gomes Pacheco; ORCID 0000-0003-3693-4377; EMC/UFG; PUC Goias; CPDT/IFG
#   Clóves Gonçalves Rodrigues; ORCID 0000-0003-0140-9847; PUC Goias
#   Antonio Paulo Coimbra; ORCID 0000-0003-3780-2405; ISR/University of Coimbra
# Corresponding author: Wesley Pacheco Calixto, wesley.pacheco@ufg.br
# License: MIT
# Citation: Calixto, W. P., Pacheco, V. M. G., Rodrigues, C. G., & Coimbra, A. P. (2026). Reproducibility package for a protocol for scientific information retrieval with explainable text classification: code, bibliographic search datasets, LLM and human relevance judgements and analysis results (v1.0.1) [Data set and software]. Zenodo. https://doi.org/10.5281/zenodo.24615095
# Execution: BIBLIO_BASE=<package_dir> BIBLIO_PYTHON=<python> bash codigo/adequacao_20261110/F2c_correr.sh
# Portability notes: paths relative to BIBLIO_BASE (default: package root).
BIBLIO_BASE="${BIBLIO_BASE:-$(cd "$(dirname "$0")/../.." && pwd)}"
set -e
S=$BIBLIO_BASE/codigo/adequacao_20261110
O=$BIBLIO_BASE/dados/coleta_v2_20261110
cd $O
python3 -I $S/F2c_complemento_e_resumos.py
sha256sum *.csv *.jsonl.gz *.json $S/consultas_v2.json $S/*.py > SHA256SUMS
echo "F2c CONCLUIDO $(date -Iseconds)" >> coleta_v2.log
