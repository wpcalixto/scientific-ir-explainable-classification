# Reproducibility package for a protocol for scientific information retrieval with explainable text classification: code, bibliographic search datasets, LLM and human relevance judgements and analysis results

## Package documentation

### 1. Identification

- **Title:** Reproducibility package for a protocol for scientific information retrieval with explainable text classification: code, bibliographic search datasets, LLM and human relevance judgements and analysis results
- **Version:** v1.0.0 (2026-11-27)
- **Resource type:** Dataset and Software (combined reproducibility package)
- **DOI:** [10.5281/zenodo.19791096](https://doi.org/10.5281/zenodo.19791096)
- **Authors:**
  - Viviane M. Gomes Pacheco; ORCID 0000-0003-3693-4377; EMC/UFG; PUC Goias; CPDT/IFG
  - Clóves Gonçalves Rodrigues; ORCID 0000-0003-0140-9847; PUC Goias
  - Antonio Paulo Coimbra; ORCID 0000-0003-3780-2405; ISR/University of Coimbra
  - Wesley Pacheco Calixto; ORCID 0000-0002-1928-4432; ISR/University of Coimbra; EMC/UFG; CPDT/IFG
- **Corresponding author:** Wesley Pacheco Calixto, wesley.pacheco@ufg.br
- **Language:** English (documentation and headers); Portuguese in file names, column names, string literals and logs
- **License:** code under MIT; data, results and documentation under CC BY 4.0 (see `LICENSE`)

### 2. General description

This record contains the complete computational pipeline, the collected bibliographic data and the derived results of the study *Protocol for scientific information retrieval with explainable text classification: design and cross-domain evaluation*.
It allows installation, minimal execution, traceability of inputs and outputs, reproduction of the analyses and citation by DOI.

### 3. Contents

- **Code** (`codigo/adequacao_20261110/`): stages F2–F21 and F008 of the pipeline — collection (OpenAlex, Semantic Scholar, Scopus, Web of Science, Elicit), LLM labelling, canonical corpus, classification with SHAP, LIME and ablation, retrieval metrics and the delta ratio, public screening benchmarks, three-LLM judge panel, human top-10 census, human P@100 validation, independent replication, figures and traceability matrices; queries (`consultas_v2.json`) and labelling prompt (`prompt_rotulacao_v2.md`). The F10 re-execution scripts (LDA, KCNA, thematic map, MCA, growth, HST) are in `resultados/adequacao_20261110/F10_reexec/`.
- **Data** (`dados/`): collections of 2026-11-10 (`coleta_v2_20261110/`, with the raw platform responses in `externas/`), facet experiment (`experimento_facetas_20261112/`) and public screening benchmarks (`externos/benchmarks_triagem/`).
- **Results** (`resultados/adequacao_20261110/`): canonical corpus, LLM labels and judgements, pseudonymized human judgements, statistics, tables and figure files of every stage.
- **Metadata** (`metadata/`: dataset metadata, file manifest, data dictionary, quality-control report), documentation (`docs/`, `documentation/`), environment (`environment/`, `requirements.txt`), smoke test (`tests/`) and checksums (`checksums/`).
- Only what is necessary for reproduction is included; manuscript-writing code, audit correspondence, superseded runs, and original assessment sheets are not.

### 4. Repository structure

```text
scientific-ir-explainable-classification_v1.0.0/
├── CHANGELOG.md
├── CITATION.cff
├── LICENSE
├── README.md
├── requirements.txt
├── checksums/  (1 files)
├── codigo/  (78 files)
├── dados/  (197 files)
├── docs/  (6 files)
├── documentation/  (4 files)
├── environment/  (3 files)
├── metadata/  (4 files)
├── resultados/  (466 files)
├── tests/  (1 files)
```

### 5. Installation and minimal execution

See `docs/installation.md` and `docs/usage.md`. Minimal check: `python tests/test_smoke.py` (add `--checksums` to verify the SHA-256 of every file).

### 6. Source data

OpenAlex (https://openalex.org, CC0), Semantic Scholar (https://www.semanticscholar.org), Scopus, Web of Science and Elicit
(records limited to identifiers and bibliographic metadata returned by each platform), and the screening benchmarks of
Cohen et al. (2006) and Howard et al. (2016) distributed through SYNERGY. Cite the original sources.

### 7. Limitations

See `docs/limitations.md`.

### 8. How to cite

Pacheco, V. M. G., Rodrigues, C. G., Coimbra, A. P., & Calixto, W. P. (2026). Reproducibility package for a protocol for scientific information retrieval with explainable text classification: code, bibliographic search datasets, LLM and human relevance judgements and analysis results (v1.0.0) [Data set and software]. Zenodo. https://doi.org/10.5281/zenodo.19791096
