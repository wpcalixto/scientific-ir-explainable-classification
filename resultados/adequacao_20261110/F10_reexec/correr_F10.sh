#!/bin/bash
# Title: correr_F10.sh
# File type: Shell script
# Purpose: Runs the F10 re-execution of the legacy analyses on the new corpus.
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
# Execution: BIBLIO_BASE=<package_dir> BIBLIO_PYTHON=<python> bash resultados/adequacao_20261110/F10_reexec/correr_F10.sh
# Portability notes: paths relative to BIBLIO_BASE (default: package root).
BIBLIO_BASE="${BIBLIO_BASE:-$(cd "$(dirname "$0")/../../.." && pwd)}"
P=${BIBLIO_PYTHON:-python3}
cd "$(dirname "$0")"
for s in 19_crescimento_anual 16_kcna 17_mapa_tematico 18_mca 02_preprocessamento_lda 13_hst_analise 15_lda_visual; do
  echo "=== $s $(date +%H:%M:%S)"; MPLBACKEND=Agg $P -I $s.py || echo "ERRO em $s"
done
echo "F10 FIM $(date +%H:%M:%S)"
