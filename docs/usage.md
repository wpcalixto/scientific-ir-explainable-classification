# Usage

Run from the package root with `BIBLIO_BASE` set. Stages are independent scripts; each reads the archived outputs of the previous ones,
so any analysis can be re-run without repeating the collection or the paid LLM calls.

| Order | Stage | Scripts | Needs keys / cost |
|---|---|---|---|
| 1 | Collection (OpenAlex, S2, external platforms) | F2a, F2b, F2c, F4a, F4b, F4c (`F2_correr_coleta.sh`, `F2c_correr.sh`) | yes |
| 2 | LLM labelling | F2d | yes (paid) |
| 3 | Canonical corpus | F2e | no |
| 4 | Classification, SHAP, LIME, ablation | F3, F3b, F10c, F10c2, F10c3, F13d, F14a | no |
| 5 | Retrieval, delta, purity | F4_F5, F10d, F13e, F17, F20 | no |
| 6 | Public benchmarks | F6a (download), F6b, F6c | F6a only network |
| 7 | Three-LLM panel | F7, F7c (paid); F7d, F7e, F7f, F7g | F7, F7c, F7f |
| 8 | Human judgement top-10 | F8a–F8c (sheets), F8d–F8h (analysis) | no |
| 9 | Legacy analyses on the new corpus (LDA, KCNA, thematic map, MCA, growth, HST) | `patch02.py`, `patch02b.py`, `resultados/adequacao_20261110/F10_reexec/correr_F10.sh`; F10b, F10f, F11b, F13c, F14b | no |
| 10 | Facet experiment | F14d (OpenAlex), F14g | F14d network |
| 11 | Human P@100 validation | F14e, F14f, F14h–F14k (design and sheets), F15a–F15f (analysis) | no |
| 12 | Independent replication | F16, F16c (and `_portatil` versions) | no |
| 13 | Figures and traceability | F9, F11, F13a, F13b, F14c, F008r, F008r2, F18, F19, F21 | no |

Example: `BIBLIO_BASE=$(pwd) python codigo/adequacao_20261110/F2e_corpus_canonico.py`.
