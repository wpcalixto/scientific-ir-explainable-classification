# File-level documentation

## codigo/adequacao_20261110/F008r2_figura9_v60.py

- **Purpose:** Regenerates Figure 9 (PCA scatter panels, three PDFs) with the final marker order, opacity and outline settings.
- **Files referenced in the code:** `{D}/lda_doc_topics_{d}.csv`, `{OUT}/MANIFESTO_figuras.txt`, `{OUT}/controle_pca_parametros.csv`, `{OUT}/fig_pca_{d}.pdf`, `{S}/dados_openalex/consolidado_todos_dominios.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F008r_reparacao_figuras_v59.py

- **Purpose:** Regenerates six result figures as vector PDFs with 300 dpi raster layers and enlarged markers (final graphic repair).
- **Files referenced in the code:** `{CL}/confusao_RL.csv`, `{D}/lda_doc_topics_{d}.csv`, `{I}/kw_matriz_avaliadores.csv`, `{OUT}/MANIFESTO_figuras.txt`, `{OUT}/controle_pca_parametros.csv`, `{OUT}/fig_classif_confusao.pdf`, `{OUT}/fig_kw_avaliadores.pdf`, `{OUT}/fig_pca_{d}.pdf`, `{OUT}/fig_precisao_listas.pdf`, `{R}/F7_painel_llm/analise/J_metricas_por_lista.csv`, `{S}/dados_openalex/consolidado_todos_dominios.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F10b_caracterizacao.py

- **Purpose:** Characterizes the canonical corpus (one record per domain and document): annual series, main journals, countries and institutions.
- **Files referenced in the code:** `{O}/anos_resumo.csv`, `{O}/fig_temporal.pdf`, `{O}/serie_anual.csv`, `{O}/top5_journals.csv`, `{O}/top5_{col}.csv`, `{O}/{f}.csv`, `{S}/dados_openalex/consolidado_todos_dominios.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F10c2_curva.py

- **Purpose:** Computes the training versus validation learning curve of logistic regression in the three domains with shuffled training subsamples.
- **Files referenced in the code:** `{OUT}/curva_treino_validacao.csv`, `{OUT}/fig_learning.pdf`, `{R}/F2_corpus/corpus_canonico.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F10c3_fig_learning.py

- **Purpose:** Redraws the learning-curve figure from curva_treino_validacao.csv.
- **Files referenced in the code:** `{O}/curva_treino_validacao.csv`, `{O}/fig_learning.pdf`
- **Warnings:** None.

## codigo/adequacao_20261110/F10c_classif_figuras_lime_ablacao.py

- **Purpose:** Re-runs the classification analyses on the canonical corpus (unique documents with abstract): classifier comparison, SHAP, LIME, ablation and figures.
- **Files referenced in the code:** `{OUT}/ablacao.csv`, `{OUT}/confusao_RL.csv`, `{OUT}/curva_treino_validacao.csv`, `{OUT}/fig_classificadores_barras.pdf`, `{OUT}/fig_confusion.pdf`, `{OUT}/fig_learning.pdf`, `{OUT}/fig_lime.pdf`, `{OUT}/fig_roc.pdf`, `{OUT}/fig_shap_classes.pdf`, `{OUT}/fig_shap_global.pdf`, `{OUT}/lime_casos.csv`, `{OUT}/metadados_F10c.json`, `{OUT}/metricas_4modelos_dp.csv`, `{OUT}/shap_global_top30.csv`, `{OUT}/shap_top10_classe.csv`, `{R}/F2_corpus/corpus_canonico.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F10d_metricas_cortes.py

- **Purpose:** Computes retrieval metrics per list at cut-offs 10, 20, 50 and 100 with the median of the three LLM judges.
- **Files referenced in the code:** `{R}/analise/J_metricas_cortes.csv`, `{R}/analise/J_notas_3llm.csv`, `{R}/listas_p100_com_jid.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F10f_lda_figuras_ablacao.py

- **Purpose:** Builds the composite LDA figures (coherence curves and PCA by strategy) and the LDA-features row of the ablation.
- **Files referenced in the code:** `{D}/coherence_scores_{d}.csv`, `{D}/lda_doc_topics_{d}.csv`, `{D}/lda_topics_{d}.csv`, `{R}/F2_corpus/corpus_canonico.csv`, `{S}/classificacao/ablacao_lda_por_dominio.csv`, `{S}/dados_openalex/consolidado_todos_dominios.csv`, `{S}/figuras_pdf/fig_coherence.pdf`, `{S}/figuras_pdf/fig_pca.pdf`
- **Warnings:** None.

## codigo/adequacao_20261110/F11_figuras_resultados.py

- **Purpose:** Regenerates the result figures with a single visual identity (one panel per PDF).
- **Files referenced in the code:** `{CL}/confusao_RL.csv`, `{CL}/curva_treino_validacao.csv`, `{CL}/lime_casos.csv`, `{CL}/metricas_4modelos_dp.csv`, `{CL}/shap_global_top30.csv`, `{DC}/hst_frequencia_tabela.csv`, `{DC}/kcna_edges_{d}.csv`, `{DC}/mca_coordenadas_{d}.csv`, `{D}/coherence_scores_{d}.csv`, `{D}/lda_doc_topics_{d}.csv`, `{D}/lda_topics_{d}.csv`, `{OUT}/MANIFESTO_figuras.txt`, `{OUT}/codigos_termos.csv`, `{OUT}/fig_classif_aprendizagem.pdf`, `{OUT}/fig_classif_confusao.pdf`, `{OUT}/fig_classif_metricas.pdf`, `{OUT}/fig_classif_roc.pdf`, `{OUT}/fig_coerencia_{d}.pdf`, `{OUT}/fig_hst_box_{d}.pdf`, `{OUT}/fig_hst_termos_{d}.pdf`, `{OUT}/fig_kcna_{d}.pdf`, `{OUT}/fig_lda_beta_{d}_t{tid}.pdf`, `{OUT}/fig_lime_{cl.lower()}.pdf`, `{OUT}/fig_mapa_tematico_legenda.pdf`, `{OUT}/fig_mapa_tematico_{d}.pdf`, `{OUT}/fig_mca_legenda.pdf`, `{OUT}/fig_mca_{d}.pdf`, `{OUT}/fig_pca_legenda.pdf`, `{OUT}/fig_pca_{d}.pdf`, `{OUT}/fig_precisao_listas.pdf`, `{OUT}/fig_shap_global.pdf`, `{OUT}/fig_shap_{cl.lower()}.pdf`, `{OUT}/fig_temporal.pdf`, `{OUT}/fig_venn_hst_legenda.pdf`, `{OUT}/fig_venn_hst_{d}.pdf`, `{OUT}/fig_wss_benchmarks.pdf`, `{OUT}/lda_topicos_representativos.json`, `{OUT}/lime_confianca.json`, `{OUT}/mapa3/mapa_tematico_{d}.csv`, `{OUT}/mapa3/particao_{d}.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F11b_mapa_tres_comunidades.py

- **Purpose:** Builds the thematic map with three communities per domain from the keyword co-occurrence graph.
- **Files referenced in the code:** `{OUT}/mapa_tematico_{d}.csv`, `{OUT}/particao_{d}.csv`, `{OUT}/resolucao.json`, `{S}/dados_openalex/consolidado_todos_dominios.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F13a_resultados_complementares.py

- **Purpose:** Recomputes the complementary results from the raw data and checks them against the reported values.
- **Files referenced in the code:** `{EXT}/{plat}_{d}_busca_{e}.csv`, `{O}/P_k_por_estrategia.csv`, `{O}/P_k_por_lista.csv`, `{O}/conferencia.json`, `{O}/crescimento_por_estrategia.csv`, `{O}/delta_por_periodo.csv`, `{O}/distribuicao_rotulos_por_modelo.csv`, `{O}/juiz_LLM_vs_mediana_humana.csv`, `{O}/kw_matriz_avaliadores.csv`, `{O}/serie_anual_por_estrategia.csv`, `{O}/sobreposicao_externas_top100.csv`, `{O}/tamanho_pool_por_profundidade.csv`, `{R}/F2_corpus/corpus_canonico.csv`, `{R}/F2_corpus/crescimento_resumo.csv`, `{R}/F7_painel_llm/analise/J_metricas_cortes.csv`, `{R}/F7_painel_llm/analise/J_notas_3llm.csv`, `{R}/F7_painel_llm/analise/R_distribuicao_rotulos.csv`, `{R}/F7_painel_llm/analise/R_rotulos_3llm.csv`, `{R}/F7_painel_llm/listas_p100_com_jid.csv`, `{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/kw_pares.csv`, `{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F13b_figuras_complementares.py

- **Purpose:** Draws the complementary figures: growth by strategy and annual delta, P@k by strategy and weighted kappa matrix between assessors.
- **Files referenced in the code:** `F13_complementares/*.csv`, `{I}/P_k_por_estrategia.csv`, `{I}/kw_matriz_avaliadores.csv`, `{I}/serie_anual_por_estrategia.csv`, `{OUT}/MANIFESTO_figuras.csv`, `{OUT}/fig_crescimento_{d}.pdf`, `{OUT}/fig_delta_anual.pdf`, `{OUT}/fig_estrategias_legenda.pdf`, `{OUT}/fig_kw_avaliadores.pdf`, `{OUT}/fig_pk_{d}.pdf`
- **Warnings:** None.

## codigo/adequacao_20261110/F13c_sensibilidade_agrupamentos.py

- **Purpose:** Sensitivity and stability analysis of the clustering results without new data collection.
- **Files referenced in the code:** `{R}/F11_figuras/mapa3/resolucao.json`, `{R}/F13_complementares/sensibilidade_agrupamentos.json`, `{S}/dados_classificacao/mca_coordenadas_{d}.csv`, `{S}/dados_openalex/consolidado_todos_dominios.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F13d_incerteza_ablacao_wss.py

- **Purpose:** Re-runs the ablation with the same code, corpus and partitions to estimate its uncertainty and WSS@95%.
- **Files referenced in the code:** `{O}/ablacao_por_particao.csv`, `{O}/ablacao_resumo.csv`, `{O}/wss_ic.csv`, `{R}/F2_corpus/corpus_canonico.csv`, `{R}/F6_benchmarks/metricas_benchmarks.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F13e_verificacao_filtro_local.py

- **Purpose:** A posteriori verification of the Boolean filter on the retrieved records (not applied during collection).
- **Files referenced in the code:** `{B}/codigo/adequacao_20261110/consultas_v2.json`, `{R}/F13_complementares/verificacao_filtro_local.csv`, `{R}/F2_corpus/corpus_canonico.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F14a_wss_diferenca_pareada.py

- **Purpose:** 95% confidence interval of the paired WSS@95% difference between logistic regression and each other classifier.
- **Files referenced in the code:** `{O}/wss_diferenca_pareada.csv`, `{R}/F6_benchmarks/metricas_benchmarks.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F14b_callon_equivalencia.py

- **Purpose:** Thematic map with the Callon equivalence index, without new data collection.
- **Files referenced in the code:** `{O}/mapa_{d}_nova.csv`, `{O}/mapa_{d}_publicada.csv`, `{O}/particao_nova_{d}.csv`, `{O}/resumo.json`, `{R}/F11_figuras/mapa3/mapa_tematico_{d}.csv`, `{R}/F11_figuras/mapa3/particao_{d}.csv`, `{S}/dados_openalex/consolidado_todos_dominios.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F14c_figuras_callon_acp.py

- **Purpose:** Draws the KCNA and thematic-map figures with the equivalence-index partition and the PCA of the indicator matrix.
- **Files referenced in the code:** `{DC}/kcna_edges_{d}.csv`, `{DC}/mca_coordenadas_{d}.csv`, `{I}/mapa_{d}_nova.csv`, `{I}/particao_nova_{d}.csv`, `{OUT}/MANIFESTO_figuras.csv`, `{OUT}/fig_kcna_{d}.pdf`, `{OUT}/fig_mapa_tematico_legenda.pdf`, `{OUT}/fig_mapa_tematico_{d}.pdf`, `{OUT}/fig_mca_legenda.pdf`, `{OUT}/fig_mca_{d}.pdf`, `{OUT}/quadrantes_estritos.csv`, `{R}/F11_figuras/codigos_termos.csv`, `{R}/F11_figuras/mca_variancia_explicada.json`
- **Warnings:** None.

## codigo/adequacao_20261110/F14d_experimento_facetas.py

- **Purpose:** Controlled facet experiment: queries derived from the original ones are executed in OpenAlex to isolate the effect of each facet.
- **Files referenced in the code:** `{B}/codigo/adequacao_20261110/consultas_v2.json`, `{OUT}/consultas.json`, `{OUT}/contagens.json`, `{OUT}/execucao.log`, `{OUT}/{d}_{nome}.jsonl.gz`
- **Warnings:** Re-running queries the live APIs and needs API keys; results will differ from the archived collection of 2026-11-10 (use the files in dados/).

## codigo/adequacao_20261110/F14e_desenho_validacao_P100.py

- **Purpose:** Precision study and stratified sampling design of the human validation of P@100.
- **Files referenced in the code:** `{O}/estratos.csv`, `{O}/estudo_precisao.csv`, `{R}/F7_painel_llm/analise/J_notas_3llm.csv`, `{R}/F7_painel_llm/listas_p100_com_jid.csv`, `{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F14f_amostra_folhas_P100.py

- **Purpose:** Draws the stratified sample of positions 11-100 and produces the blind sheets of the human P@100 validation.
- **Files referenced in the code:** `{O}/amostra_posicoes_NAO_ENVIAR.csv`, `{O}/folhas/Folha_P100_{nome[d]}_avaliador{a}.xlsx`, `{O}/mapa_documentos_NAO_ENVIAR.csv`, `{R}/F7_painel_llm/listas_p100_com_jid.csv`, `{R}/F7_painel_llm/pool_relevancia_p100.csv`, `{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F14g_analise_facetas.py

- **Purpose:** Analyses the controlled facet experiment (F14d).
- **Files referenced in the code:** `{D}/consultas.json`, `{D}/{d}_{v}.jsonl.gz`, `{O}/{nm}.csv`, `{R}/F2_corpus/corpus_canonico.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F14h_verificacao_amostra_folhas_v2.py

- **Purpose:** Pre-dispatch checks of the P@100 sample and blind sheets (version 2); does not change the sample.
- **Files referenced in the code:** `{O}/amostra_posicoes_NAO_ENVIAR.csv`, `{O}/folhas_v2/Folha_P100_{nome[d]}_avaliador{a}.xlsx`, `{O}/mapa_documentos_NAO_ENVIAR.csv`, `{O}/mapa_documentos_v2_NAO_ENVIAR.csv`, `{O}/partilha.json`, `{O}/verificacao_desenho.csv`, `{R}/F7_painel_llm/analise/J_notas_3llm.csv`, `{R}/F7_painel_llm/listas_p100_com_jid.csv`, `{R}/F7_painel_llm/pool_relevancia_p100.csv`, `{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F14i_reproducao_simulacoes_reconciliacao.py

- **Purpose:** Read-only audit that reproduces the simulations and reconciles the P@100 sample and sheets.
- **Files referenced in the code:** `{A}/reconciliacao.csv`, `{A}/reconciliacao_folhas.csv`, `{A}/simulacoes_2000_replicas.csv`, `{A}/simulacoes_conferencia.csv`, `{O}/amostra_posicoes_NAO_ENVIAR.csv`, `{O}/mapa_documentos_v2_NAO_ENVIAR.csv`, `{O}/verificacao_desenho.csv`, `{R}/F7_painel_llm/analise/J_notas_3llm.csv`, `{R}/F7_painel_llm/listas_p100_com_jid.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F14j_conferencia_pre_envio.py

- **Purpose:** Read-only pre-dispatch check of the nine version-2 blind sheets.
- **Files referenced in the code:** `{O}/auditoria/SHA256_folhas_v2.txt`, `{O}/auditoria/conferencia_pre_envio.csv`, `{O}/mapa_documentos_v2_NAO_ENVIAR.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F14k_folhas_quarto_avaliador.py

- **Purpose:** Produces three complementary blind sheets (fourth assessor per domain) without changing the sample.
- **Files referenced in the code:** `{O}/auditoria/SHA256_folhas_v2_avaliador4.txt`, `{O}/auditoria/conferencia_avaliador4.csv`, `{O}/folhas_v2/Folha_P100_{nome[d]}_avaliador4.xlsx`, `{O}/folhas_v2/Folha_P100_{nome[d]}_avaliador{a}.xlsx`, `{O}/mapa_documentos_v2_NAO_ENVIAR.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F15a_controlo_recebimento.py

- **Purpose:** Quality control of the returned assessment sheets before any analysis.
- **Files referenced in the code:** `.xlsx`, `{OUT}/controlo_fichas.csv`, `{OUT}/controlo_problemas.csv`, `{OUT}/notas_consolidadas.csv`, `{V}/envio_P01B2/Folha_P100_{dom_nome}_{cod}.xlsx`, `{V}/folhas_v2/Folha_P100_{dom_nome}_avaliador1.xlsx`, `{V}/mapa_documentos_v2_NAO_ENVIAR.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F15b_analise_P100.py

- **Purpose:** Pre-specified analysis of the human P@100 (stratified estimator, confidence intervals and comparison with the LLM judges).
- **Files referenced in the code:** `{OUT}/correcoes_resumo.csv`, `{OUT}/resumo.json`, `{OUT}/{nm}.csv`, `{R}/F7_painel_llm/analise/J_metricas_cortes.csv`, `{R}/F7_painel_llm/analise/J_notas_3llm.csv`, `{R}/F7_painel_llm/listas_p100_com_jid.csv`, `{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv`, `{V}/amostra_posicoes_NAO_ENVIAR.csv`, `{V}/mapa_documentos_v2_NAO_ENVIAR.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F15c_montar_fichas_coladas.py

- **Purpose:** Assembles the returned P@100 sheets from the transcribed 'doc_id<TAB>grade' lines.
- **Files referenced in the code:** `RJ_completo_311_20261112_2325.txt`, `notas_P100_coladas_20261112_2251.txt`, `{OUT}/Folha_P100_{nome}.xlsx`, `{V}/envio_P01B2/Folha_P100_{nome}.xlsx`
- **Warnings:** None.

## codigo/adequacao_20261110/F15d_reproducao_independente.py

- **Purpose:** Independent reproduction of the human P@100 validation (calibration, bootstrap and differences).
- **Files referenced in the code:** `notas_coladas_alunos_20261112.txt`, `notas_conferidas_20261112_2104.txt`, `{F15}/analise/P100_diferencas.csv`, `{F15}/analise/P100_estrategias.csv`, `{F15}/analise/bootstrap.csv`, `{F15}/analise/calibracao.csv`, `{F15}/analise/humano_menos_LLM.csv`, `{F15}/analise/humano_vs_LLM_concordancia.csv`, `{F15}/analise/sensibilidade.csv`, `{F15}/controlo/notas_consolidadas.csv`, `{F15}/controlo/originais/Folha_P100_{nm}.xlsx`, `{NU}/notas_coladas_alunos_20261112.txt`, `{OUT}/V7_02_RJ_continuacao_rejeitada.csv`, `{OUT}/V7_02_radiomica_8_registos.csv`, `{OUT}/V7_04_calibracao.csv`, `{OUT}/V7_04_calibracao_referencia_sem_cada_avaliador.csv`, `{OUT}/V7_05_bootstrap_semente42_corrigido.csv`, `{OUT}/V7_05_comparacao_F15d_F15b.csv`, `{OUT}/V7_05_concordancia_humano_LLM.csv`, `{OUT}/V7_05_diferencas.csv`, `{OUT}/V7_05_estrategias_e_pareado.csv`, `{OUT}/V7_05_estratos_variancia_nula.csv`, `{OUT}/V7_verificacoes.csv`, `{REC}/RJ_completo_311_20261112_2325.txt`, `{REC}/notas_P100_coladas_20261112_2251.txt`, `{REC}/rj_continuacao_colada_20261112_2300.txt`, `{REC}/rj_restante_colado_20261112_2325.txt`, `{R}/F7_painel_llm/analise/J_notas_3llm.csv`, `{R}/F7_painel_llm/listas_p100_com_jid.csv`, `{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv`, `{R}/F8_julgamento/pool_mapa_NAO_ENVIAR.csv`, `{V}/amostra_posicoes_NAO_ENVIAR.csv`, `{V}/envio_P01B2/Folha_P100_{nm}.xlsx`, `{V}/mapa_documentos_v2_NAO_ENVIAR.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F15e_bootstrap_cobertura.py

- **Purpose:** Re-evaluates the bootstrap of the human P@100 (coverage and intervals) without changing the data.
- **Files referenced in the code:** `{OUT}/A_cobertura_por_simulacao.csv`, `{OUT}/A_cobertura_resumo.csv`, `{OUT}/B_intervalos_dados_reais.csv`, `{OUT}/B_replicas_{me}.csv`, `{R}/F7_painel_llm/analise/J_notas_3llm.csv`, `{R}/F7_painel_llm/listas_p100_com_jid.csv`, `{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv`, `{V}/F15_resultados_20261112/controlo/notas_consolidadas.csv`, `{V}/F15d_reproducao_20261113/V7_05_bootstrap_semente42_corrigido.csv`, `{V}/amostra_posicoes_NAO_ENVIAR.csv`, `{V}/mapa_documentos_v2_NAO_ENVIAR.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F15f_conferencia_M3.py

- **Purpose:** Checks the implementation of the document-level Bayesian bootstrap (M3) of the human P@100.
- **Files referenced in the code:** `{OUT}/F15f_conferencia_M3.csv`, `{OUT}/F15f_replicas_M3.csv`, `{R}/F7_painel_llm/listas_p100_com_jid.csv`, `{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv`, `{V}/F15_resultados_20261112/controlo/notas_consolidadas.csv`, `{V}/F15e_bootstrap_20261113/B_intervalos_dados_reais.csv`, `{V}/amostra_posicoes_NAO_ENVIAR.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F16_replicacao.py

- **Purpose:** Independent human replication by new assessor teams: control, calibration, P@100 with the new reference and stability.
- **Files referenced in the code:** `{D}/controlo/controlo_problemas.csv`, `{D}/controlo/controlo_replicacao.csv`, `{D}/controlo/notas_replicacao_consolidadas.csv`, `{D}/recebido/notas_replicacao_coladas_20261113_1245.txt`, `{OUT}/A_comparacao_old_new.csv`, `{OUT}/A_matrizes_old_new.csv`, `{OUT}/B_calibracao.csv`, `{OUT}/C1_P100_diferencas.csv`, `{OUT}/C1_P100_estrategias.csv`, `{OUT}/C2_restrita_documentos_novos.csv`, `{OUT}/C_replicas_M3_R_new.csv`, `{OUT}/E_estabilidade.csv`, `{OUT}/F_sensibilidade.csv`, `{R}/F7_painel_llm/analise/J_notas_3llm.csv`, `{R}/F7_painel_llm/listas_p100_com_jid.csv`, `{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv`, `{V}/F15_resultados_20261112/controlo/notas_consolidadas.csv`, `{V}/amostra_posicoes_NAO_ENVIAR.csv`, `{V}/mapa_documentos_v2_NAO_ENVIAR.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F16_replicacao_portatil.py

- **Purpose:** Portable version of F16 (paths given as command-line arguments).
- **Files referenced in the code:** `{D}/controlo/controlo_problemas.csv`, `{D}/controlo/controlo_replicacao.csv`, `{D}/controlo/notas_replicacao_consolidadas.csv`, `{OUT}/A_comparacao_old_new.csv`, `{OUT}/A_matrizes_old_new.csv`, `{OUT}/B_calibracao.csv`, `{OUT}/C1_P100_diferencas.csv`, `{OUT}/C1_P100_estrategias.csv`, `{OUT}/C2_restrita_documentos_novos.csv`, `{OUT}/C_replicas_M3_R_new.csv`, `{OUT}/E_estabilidade.csv`, `{OUT}/F_sensibilidade.csv`, `{PKG}/desenho/amostra_posicoes_NAO_ENVIAR.csv`, `{PKG}/desenho/mapa_documentos_v2_NAO_ENVIAR.csv`, `{PKG}/recebido/notas_replicacao_coladas_20261113_1245.txt`, `{PKG}/referencias/J_notas_3llm.csv`, `{PKG}/referencias/listas_p100_com_jid.csv`, `{PKG}/referencias/notas_R_old_consolidadas.csv`, `{PKG}/referencias/notas_humanos_LLM.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F16c_reproducao_e_mudancas.py

- **Purpose:** Reproduces F16 with an independent vectorized implementation and quantifies the grade changes between references.
- **Files referenced in the code:** `{D}/analise/A_comparacao_old_new.csv`, `{D}/analise/B_calibracao.csv`, `{D}/analise/C1_P100_diferencas.csv`, `{D}/analise/C1_P100_estrategias.csv`, `{D}/controlo/notas_replicacao_consolidadas.csv`, `{D}/recebido/notas_replicacao_coladas_20261113_1245.txt`, `{OUT}/A_concordancia_reproduzida.csv`, `{OUT}/B_calibracao_reproduzida.csv`, `{OUT}/C_P100_e_mudancas_entre_referencias.csv`, `{OUT}/verificacoes.csv`, `{R}/F7_painel_llm/analise/J_notas_3llm.csv`, `{R}/F7_painel_llm/listas_p100_com_jid.csv`, `{R}/F8_julgamento/analise_fichas_reais_20261112_13fichas/notas_humanos_LLM.csv`, `{V}/F15_resultados_20261112/controlo/notas_consolidadas.csv`, `{V}/amostra_posicoes_NAO_ENVIAR.csv`, `{V}/mapa_documentos_v2_NAO_ENVIAR.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F16c_reproducao_e_mudancas_portatil.py

- **Purpose:** Portable version of F16c (paths given as command-line arguments).
- **Files referenced in the code:** `{D}/analise/A_comparacao_old_new.csv`, `{D}/analise/B_calibracao.csv`, `{D}/analise/C1_P100_diferencas.csv`, `{D}/analise/C1_P100_estrategias.csv`, `{D}/controlo/notas_replicacao_consolidadas.csv`, `{OUT}/A_concordancia_reproduzida.csv`, `{OUT}/B_calibracao_reproduzida.csv`, `{OUT}/C_P100_e_mudancas_entre_referencias.csv`, `{OUT}/verificacoes.csv`, `{PKG}/desenho/amostra_posicoes_NAO_ENVIAR.csv`, `{PKG}/desenho/mapa_documentos_v2_NAO_ENVIAR.csv`, `{PKG}/recebido/notas_replicacao_coladas_20261113_1245.txt`, `{PKG}/referencias/J_notas_3llm.csv`, `{PKG}/referencias/listas_p100_com_jid.csv`, `{PKG}/referencias/notas_R_old_consolidadas.csv`, `{PKG}/referencias/notas_humanos_LLM.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F17_conciliacao_denominadores.py

- **Purpose:** Document-level reconciliation of the denominators of the retrieval metrics.
- **Files referenced in the code:** `{F}/**/*.csv`, `{F}/dados_classificacao/hst_frequencia_tabela.csv`, `{F}/dados_processados/corpus_{d}.csv`, `{F}/dados_processados/lda_doc_topics_{d}.csv`, `{OUT}/artefatos_com_7874_ou_9965_linhas.csv`, `{OUT}/conciliacao_por_id.csv`, `{OUT}/conciliacao_resumo.csv`, `{OUT}/fontes_sha256.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F18_matriz_artefatos.py

- **Purpose:** Builds the matrix linking the result tables and figures to the generating artefacts.
- **Files referenced in the code:** `.pdf`, `{B}/resultados/**/*.pdf`, `{RES}/**/*.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F19_matriz_rastreabilidade.py

- **Purpose:** Builds the traceability matrix of the result tables and figures to their source files and scripts.
- **Files referenced in the code:** `.csv`, `.json`, `.log`, `.pdf`, `F13_complementares/P_k_por_estrategia.csv`, `F13_complementares/P_k_por_lista.csv`, `F13_complementares/ablacao_resumo.csv`, `F13_complementares/crescimento_por_estrategia.csv`, `F13_complementares/delta_por_periodo.csv`, `F13_complementares/distribuicao_rotulos_por_modelo.csv`, `F13_complementares/juiz_LLM_vs_mediana_humana.csv`, `F13_complementares/sensibilidade_agrupamentos.json`, `F13_complementares/sobreposicao_externas_top100.csv`, `F13_complementares/verificacao_filtro_local.csv`, `F13_complementares/wss_ic.csv`, `F14_complementares_01A/callon_equivalencia/mapa_{d}_nova.csv`, `F14_complementares_01A/callon_equivalencia/particao_nova_{d}.csv`, `F14_complementares_01A/callon_equivalencia/resumo.json`, `F14_complementares_01A/facetas/desenho_2x2.csv`, `F14_complementares_01A/facetas/literal_vs_radicais.csv`, `F14_complementares_01A/facetas/temporal.csv`, `F14_complementares_01A/figuras/quadrantes_estritos.csv`, `F14_complementares_01A/validacao_P100/F15_resultados_20261112/analise/P100_diferencas.csv`, `F14_complementares_01A/validacao_P100/F15_resultados_20261112/analise/P100_estrategias.csv`, `F14_complementares_01A/validacao_P100/F15_resultados_20261112/analise/humano_menos_LLM.csv`, `F14_complementares_01A/validacao_P100/F15e_bootstrap_20261113/B_intervalos_dados_reais.csv`, `F14_complementares_01A/validacao_P100/replicacao_doutorandos_20261113/analise/A_comparacao_old_new.csv`, `F14_complementares_01A/validacao_P100/replicacao_doutorandos_20261113/analise/B_calibracao.csv`, `F14_complementares_01A/validacao_P100/replicacao_doutorandos_20261113/reproducao_F16c/C_P100_e_mudancas_entre_referencias.csv`, `F2_corpus/cobertura_oal_scopus.csv`, `F2_corpus/corpus_canonico.csv`, `F2_corpus/fluxo_corpus.csv`, `F2_corpus/sobreposicao_estrategias.csv`, `F3_classificacao/metricas_cenarios.csv`, `F3_classificacao/shap_top25_dominio_classe.csv`, `F3_classificacao/testes_pareados.csv`, `F4_F5/delta_por_base.csv`, `F4_F5/delta_variacao_entre_bases.csv`, `F4_F5/diversidade_tematica.csv`, `F4_F5/novidade_redundancia.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F20_verifica_metricas_SES.py

- **Purpose:** Verifies the denominators of R@l and the identifier sets of the external search engine lists.
- **Files referenced in the code:** `J_metricas_cortes_s2.csv`, `J_notas_3llm.csv`, `J_notas_3llm_s2_novos.csv`, `{A}/J_metricas_cortes_s2.csv`, `{A}/J_notas_3llm.csv`, `{A}/J_notas_3llm_s2_novos.csv`, `{OUT}/P03_PEND01_SES_36_linhas.csv`, `{R}/listas_s2_com_jid.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F21_reconstroi_rotulos_finais.py

- **Purpose:** Read-only reconstruction of the passage from the raw LLM labels to the final labels.
- **Files referenced in the code:** `{R}/rotulos_v2.csv`, `{R}/rotulos_v2_final.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F2a_coleta_openalex_v2.py

- **Purpose:** Collects the OpenAlex records of strategies A, B and C in the three domains (server-side Boolean search, cursor pagination).
- **Files referenced in the code:** `{BASE}/codigo/adequacao_20261110/consultas_v2.json`, `{OUT}/coleta_v2.log`, `{OUT}/raw_{dom}_{est}.jsonl.gz`, `{OUT}/resumo_coleta_v2.json`, `{OUT}/{dom}_{est}.csv`
- **Warnings:** Re-running queries the live APIs and needs API keys; results will differ from the archived collection of 2026-11-10 (use the files in dados/).

## codigo/adequacao_20261110/F2b_resumos_semantic_scholar.py

- **Purpose:** Completes missing abstracts through the Semantic Scholar batch API (by DOI).
- **Files referenced in the code:** `.csv`, `_antes_s2.csv`, `{OUT}/*_busca_*.csv`, `{OUT}/coleta_v2.log`
- **Warnings:** Re-running queries the live APIs and needs API keys; results will differ from the archived collection of 2026-11-10 (use the files in dados/).

## codigo/adequacao_20261110/F2c_complemento_e_resumos.py

- **Purpose:** Complementary collection pass for strategies with cursor losses and abstract completion.
- **Files referenced in the code:** `.csv`, `_antes_F2c.csv`, `{OUT}/raw_{dom}_{est}_complemento{passagem}.jsonl.gz`, `{OUT}/resumo_coleta_v2.json`, `{OUT}/{dom}_{est}.csv`
- **Warnings:** Re-running queries the live APIs and needs API keys; results will differ from the archived collection of 2026-11-10 (use the files in dados/).

## codigo/adequacao_20261110/F2d_rotulacao_v2.py

- **Purpose:** Labels the documents as Applied, Methodological or General with Claude Haiku 4.5 through the Message Batches API.
- **Files referenced in the code:** `{COL}/*_busca_[ABC].csv`, `{COL}/coleta_v2.log`, `{OUT}/batch_id.txt`, `{OUT}/metadados_rotulacao_v2.json`, `{OUT}/prompt_system_v2.txt`, `{OUT}/respostas_brutas.jsonl`, `{OUT}/rotulacao_v2.log`, `{OUT}/rotulos_v2.csv`
- **Warnings:** Calls paid LLM APIs and needs API keys; re-running incurs costs and may not return identical outputs (the archived outputs are in resultados/).

## codigo/adequacao_20261110/F2e_corpus_canonico.py

- **Purpose:** Builds the canonical corpus (deduplication, matching with Scopus by DOI or title, overlap and growth).
- **Files referenced in the code:** `{BASE}/resultados/adequacao_20261110/F2_rotulacao_v2/rotulos_v2_final.csv`, `{COL}/resumo_coleta_v2.json`, `{COL}/{d}_busca_{e}.csv`, `{EXT}/contagens_elicit.json`, `{EXT}/contagens_externas.json`, `{EXT}/contagens_scopus.json`, `{EXT}/scopus_todos_{d}_busca_{e}.csv`, `{EXT}/{pat}_{d}_busca_{e}.csv`, `{OUT}/cobertura_externas_no_pool.csv`, `{OUT}/cobertura_oal_scopus.csv`, `{OUT}/corpus_canonico.csv`, `{OUT}/crescimento_resumo.csv`, `{OUT}/crescimento_unicos.csv`, `{OUT}/documentos_multidominio.csv`, `{OUT}/fluxo_corpus.csv`, `{OUT}/sobreposicao_estrategias.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F3_classificacao_deduplicada.py

- **Purpose:** Leakage-free classification on the canonical corpus (one record per document): classifiers, cross-validation and metrics.
- **Files referenced in the code:** `{BASE}/resultados/adequacao_20261110/F2_corpus/corpus_canonico.csv`, `{OUT}/curva_aprendizagem.csv`, `{OUT}/matrizes_confusao.json`, `{OUT}/metadados_F3.json`, `{OUT}/metricas_cenarios.csv`, `{OUT}/metricas_por_classe.csv`, `{OUT}/shap_peso_termos_dominio.csv`, `{OUT}/shap_top25_dominio_classe.csv`, `{OUT}/testes_pareados.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F3b_continuacao.py

- **Purpose:** Continuation of F3 (learning curve, SHAP and metadata) after an interruption.
- **Files referenced in the code:** `{BASE}/resultados/adequacao_20261110/F2_corpus/corpus_canonico.csv`, `{OUT}/curva_aprendizagem.csv`, `{OUT}/metadados_F3.json`, `{OUT}/shap_peso_termos_dominio.csv`, `{OUT}/shap_top25_dominio_classe.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F4_F5_recuperacao_delta.py

- **Purpose:** Judgement-independent retrieval analyses and the delta ratio by platform, with purity and reintegration.
- **Files referenced in the code:** `{BASE}/codigo/adequacao_20261110/consultas_v2.json`, `{BASE}/resultados/adequacao_20261110/F2_corpus/corpus_canonico.csv`, `{COL}/*_busca_[ABC].csv`, `{COL}/resumo_coleta_v2.json`, `{EXT}/contagens_externas.json`, `{EXT}/contagens_scopus.json`, `{EXT}/{plat}_{d}_busca_{e}.csv`, `{OUT}/delta_por_base.csv`, `{OUT}/delta_variacao_entre_bases.csv`, `{OUT}/diversidade_tematica.csv`, `{OUT}/listas_ranqueadas.csv`, `{OUT}/novidade_redundancia.csv`, `{OUT}/pureza_dominio.csv`, `{OUT}/rankings_top100.csv`, `{OUT}/reintegracao_hst.csv`, `{OUT}/tamanho_pool.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F4a_coleta_externas.py

- **Purpose:** Collects the external platforms (Scopus, Web of Science, Semantic Scholar) on the same day as the OpenAlex collection.
- **Files referenced in the code:** `{BASE}/codigo/adequacao_20261110/consultas_v2.json`, `{OUT}/coleta_externas.log`, `{OUT}/contagens_externas.json`, `{OUT}/{nome}.csv`
- **Warnings:** Re-running queries the live APIs and needs API keys; results will differ from the archived collection of 2026-11-10 (use the files in dados/).

## codigo/adequacao_20261110/F4a_teste_apis.py

- **Purpose:** Syntax test of the external APIs (counts only).
- **Files referenced in the code:** none detected
- **Warnings:** Re-running queries the live APIs and needs API keys; results will differ from the archived collection of 2026-11-10 (use the files in dados/).

## codigo/adequacao_20261110/F4b_coleta_scopus.py

- **Purpose:** Scopus collection: counts, top-100 by relevance and full DOI lists.
- **Files referenced in the code:** `{BASE}/codigo/adequacao_20261110/consultas_v2.json`, `{OUT}/coleta_scopus.log`, `{OUT}/contagens_scopus.json`, `{OUT}/{nome}.csv`
- **Warnings:** Re-running queries the live APIs and needs API keys; results will differ from the archived collection of 2026-11-10 (use the files in dados/).

## codigo/adequacao_20261110/F4c_coleta_elicit.py

- **Purpose:** Elicit API v2 collection (semantic and keyword modes).
- **Files referenced in the code:** `{OUT}/coleta_elicit.log`, `{OUT}/contagens_elicit.json`, `{OUT}/elicit_bruto_{modo}_{tag}.json`, `{OUT}/elicit_{modo}_{tag}.csv`
- **Warnings:** Re-running queries the live APIs and needs API keys; results will differ from the archived collection of 2026-11-10 (use the files in dados/).

## codigo/adequacao_20261110/F6a_baixar_benchmarks.py

- **Purpose:** Downloads the public screening benchmarks (Cohen 2006 and Howard 2016 through SYNERGY).
- **Files referenced in the code:** `.csv`, `_ids.csv`, `{OUT}/baixar.log`, `{OUT}/ids/{nome}_ids.csv`, `{OUT}/{nome}.csv`
- **Warnings:** Re-running queries the live APIs and needs API keys; results will differ from the archived collection of 2026-11-10 (use the files in dados/).

## codigo/adequacao_20261110/F6b_validacao_externa_classificadores.py

- **Purpose:** External validation of the classifiers on public screening benchmarks.
- **Files referenced in the code:** `{IN}/*.csv`, `{OUT}/metricas_benchmarks.csv`, `{OUT}/resumo_por_modelo.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F6c_comparacao_van_dinter.py

- **Purpose:** Compares the WSS@95% of the four classifiers with published values (van Dinter et al.).
- **Files referenced in the code:** `{R}/comparacao_wss95_publicados.csv`, `{R}/comparacao_wss95_resumo.csv`, `{R}/metricas_benchmarks.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F7_painel_llm.py

- **Purpose:** Panel of three LLM judges at temperature 0: labelling task (R) and relevance judgement task (J).
- **Files referenced in the code:** `.csv`, `{OUT}/amostra_rotulacao.csv`, `{OUT}/listas_p100_com_jid.csv`, `{OUT}/metadados_F7.json`, `{OUT}/painel.log`, `{OUT}/pool_relevancia_p100.csv`, `{OUT}/respostas_J.jsonl`, `{OUT}/respostas_R.jsonl`, `{R}/F2_corpus/corpus_canonico.csv`, `{R}/F2_rotulacao_v2/prompt_system_v2.txt`, `{R}/F2_rotulacao_v2/rotulos_v2_final.csv`, `{R}/F4_F5/listas_ranqueadas.csv`
- **Warnings:** Calls paid LLM APIs and needs API keys; re-running incurs costs and may not return identical outputs (the archived outputs are in resultados/).

## codigo/adequacao_20261110/F7c_gpt_batch.py

- **Purpose:** GPT judgements through the OpenAI Batch API.
- **Files referenced in the code:** `respostas_J.jsonl`, `respostas_R.jsonl`, `respostas_gpt_batch.jsonl`, `{OUT}/gpt_batch_input.jsonl`, `{OUT}/respostas_gpt_batch.jsonl`
- **Warnings:** Calls paid LLM APIs and needs API keys; re-running incurs costs and may not return identical outputs (the archived outputs are in resultados/).

## codigo/adequacao_20261110/F7d_analise_painel.py

- **Purpose:** Analyses the three-LLM panel: agreement between judges, consensus and retrieval metrics.
- **Files referenced in the code:** `respostas_J.jsonl`, `respostas_R.jsonl`, `respostas_gpt_batch.jsonl`, `{D}/amostra_rotulacao.csv`, `{D}/listas_p100_com_jid.csv`, `{D}/pool_relevancia_p100.csv`, `{OUT}/J_concordancia_relevancia.csv`, `{OUT}/J_estabilidade_ranking_listas.csv`, `{OUT}/J_metricas_por_lista.csv`, `{OUT}/J_notas_3llm.csv`, `{OUT}/R_concordancia_rotulos.csv`, `{OUT}/R_distribuicao_rotulos.csv`, `{OUT}/R_rotulos_3llm.csv`, `{OUT}/metadados_F7d.json`
- **Warnings:** None.

## codigo/adequacao_20261110/F7e_robustez.py

- **Purpose:** Robustness of the relevance conclusions without human judgement (single judge and alternative consensus rules).
- **Files referenced in the code:** `{A}/J_metricas_por_lista.csv`, `{A}/J_notas_3llm.csv`, `{A}/robustez_juiz_unico.csv`, `{A}/robustez_ruido_juiz.csv`, `{R}/listas_p100_com_jid.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F7f_listas_s2.py

- **Purpose:** Judges the Semantic Scholar lists with the same three LLM judges.
- **Files referenced in the code:** `.csv`, `{OUT}/gpt_batch_input_s2.jsonl`, `{OUT}/listas_s2_com_jid.csv`, `{OUT}/pool_relevancia_p100.csv`, `{OUT}/pool_s2_novos.csv`, `{OUT}/respostas_J_s2.jsonl`, `{OUT}/respostas_gpt_batch_s2.jsonl`, `{R}/resultados/adequacao_20261110/F4_F5/listas_ranqueadas.csv`
- **Warnings:** Calls paid LLM APIs and needs API keys; re-running incurs costs and may not return identical outputs (the archived outputs are in resultados/).

## codigo/adequacao_20261110/F7g_metricas_s2.py

- **Purpose:** Retrieval metrics of the Semantic Scholar lists with the three LLM judges.
- **Files referenced in the code:** `respostas_J_s2.jsonl`, `respostas_gpt_batch_s2.jsonl`, `{A}/J_metricas_cortes_s2.csv`, `{A}/J_notas_3llm.csv`, `{A}/J_notas_3llm_s2_novos.csv`, `{R}/listas_s2_com_jid.csv`, `{R}/pool_s2_novos.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F8a_folhas_julgamento.py

- **Purpose:** Builds the human judgement pool (depth 10) and the first two blind sheets (assessors W and U).
- **Files referenced in the code:** `.csv`, `{BASE}/resultados/adequacao_20261110/F2_corpus/corpus_canonico.csv`, `{BASE}/resultados/adequacao_20261110/F4_F5/listas_ranqueadas.csv`, `{OUT}/Folha_julgamento_{av}.xlsx`, `{OUT}/pool_mapa_NAO_ENVIAR.csv`, `{OUT}/pool_resumo.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F8b_folhas_21.py

- **Purpose:** Produces the coded blind sheets (AV01-AV21) from the judgement pool.
- **Files referenced in the code:** `{OUT}/folhas_21/Folha_{cod}.xlsx`, `{OUT}/folhas_21/distribuicao.csv`, `{OUT}/pool_mapa_NAO_ENVIAR.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F8c_folha_super_bio.py

- **Purpose:** Produces an extra blind sheet with its own random order.
- **Files referenced in the code:** `{OUT}/folhas_nomeadas/Folha_Super_Bioengenheiro.xlsx`, `{OUT}/pool_mapa_NAO_ENVIAR.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F8d_analise_fichas_reais.py

- **Purpose:** Analyses the first three human sheets (W, U, V): consistency and agreement with the LLM judges.
- **Files referenced in the code:** `{F}/ficha_{k}.csv`, `{O}/P10_por_estrategia.csv`, `{O}/P10_por_lista.csv`, `{O}/concordancia.csv`, `{O}/conferencia.json`, `{O}/duplicados.csv`, `{O}/notas_humanos_LLM.csv`, `{O}/ordenacao_humanos_vs_LLM.csv`, `{R}/F7_painel_llm/analise/J_notas_3llm.csv`, `{R}/F8_julgamento/pool_mapa_NAO_ENVIAR.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F8e_sinal_preenchimento_automatico.py

- **Purpose:** Checks the returned human sheets for signs of automatic filling.
- **Files referenced in the code:** `{F}/ficha_{k}.csv`, `{R}/F7_painel_llm/analise/J_notas_3llm.csv`, `{R}/F8_julgamento/pool_mapa_NAO_ENVIAR.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F8f_analise_13_fichas.py

- **Purpose:** Analyses the 13 human sheets (K-W): agreement, P@10 by strategy and comparison with the LLM judges.
- **Files referenced in the code:** `{F}/ficha_{k}.csv`, `{O}/P10_por_estrategia.csv`, `{O}/P10_por_lista.csv`, `{O}/concordancia.csv`, `{O}/conferencia.json`, `{O}/kw_pares.csv`, `{O}/notas_humanos_LLM.csv`, `{O}/ordenacao_humanos_vs_LLM.csv`, `{O}/por_avaliador.csv`, `{R}/F7_painel_llm/analise/J_notas_3llm.csv`, `{R}/F8_julgamento/pool_mapa_NAO_ENVIAR.csv`
- **Warnings:** Reads the blinding maps (*_NAO_ENVIAR.csv; document codes only, no assessor data), distributed in resultados/ after the end of the assessments.

## codigo/adequacao_20261110/F8g_por_area.py

- **Purpose:** Breaks down the human-LLM agreement by assessor area.
- **Files referenced in the code:** `{O}/notas_humanos_LLM.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F8h_discordancia_detalhada.py

- **Purpose:** Detailed human-LLM disagreement by sheet, domain and type of disagreement.
- **Files referenced in the code:** `{O}/discordancia_por_ficha_dominio.csv`, `{O}/notas_humanos_LLM.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/F9_figuras.py

- **Purpose:** Draws result figures (vector PDF) from the F3, F5, F6 and F7d outputs.
- **Files referenced in the code:** `{OUT}/fig_curva_aprendizagem.pdf`, `{OUT}/fig_delta_bases.pdf`, `{OUT}/fig_precisao_listas.pdf`, `{OUT}/fig_wss_benchmarks.pdf`, `{R}/F3_classificacao/curva_aprendizagem.csv`, `{R}/F4_F5/delta_por_base.csv`, `{R}/F6_benchmarks/metricas_benchmarks.csv`, `{R}/F7_painel_llm/analise/J_metricas_por_lista.csv`
- **Warnings:** None.

## codigo/adequacao_20261110/estilo_figuras.py

- **Purpose:** Shared figure-style module (colours, markers, names and sizes).
- **Files referenced in the code:** none detected
- **Warnings:** None.

## codigo/adequacao_20261110/patch02.py

- **Purpose:** Patch applied to the legacy LDA preprocessing script for the F10 re-execution (LDA fitted on unique documents).
- **Files referenced in the code:** none detected
- **Warnings:** None.

## codigo/adequacao_20261110/patch02b.py

- **Purpose:** Second patch applied to the legacy LDA preprocessing script for the F10 re-execution.
- **Files referenced in the code:** none detected
- **Warnings:** None.

## resultados/adequacao_20261110/F10_reexec/02_preprocessamento_lda.py

- **Purpose:** Preprocessing and LDA topic modelling of each domain corpus (F10 re-execution).
- **Files referenced in the code:** `  Figura salva: {OUTPUT_DIR}/pca_{dominio}.png`, `dados_openalex/consolidado_todos_dominios.csv`, `{OUTPUT_DIR}/coherence_curve_{dominio}.png`, `{OUTPUT_DIR}/coherence_scores_{dominio}.csv`, `{OUTPUT_DIR}/corpus_{dominio}.csv`, `{OUTPUT_DIR}/lda_doc_topics_{dominio}.csv`, `{OUTPUT_DIR}/lda_topics_{dominio}.csv`, `{OUTPUT_DIR}/pca_variance_{dominio}.csv`, `{OUTPUT_DIR}/pca_{dominio}.png`
- **Warnings:** None.

## resultados/adequacao_20261110/F10_reexec/13_hst_analise.py

- **Purpose:** Comparative analyses of HST versus general terms (Venn diagrams, overlap and boxplots).
- **Files referenced in the code:** `[Tópico 1] CSV: dados_classificacao/hst_sobreposicao.csv`, `corpus_{dom}.csv`, `fig_boxplot_hst.pdf`, `fig_venn_hst.pdf`, `hst_estatisticas.csv`, `hst_estatisticas.tex`, `hst_frequencia_tabela.csv`, `hst_frequencia_tabela.tex`, `hst_sobreposicao.csv`, `{dom}_busca_A.csv`, `{dom}_busca_B.csv`
- **Warnings:** None.

## resultados/adequacao_20261110/F10_reexec/15_lda_visual.py

- **Purpose:** Bar charts of the LDA topics per domain (beta values).
- **Files referenced in the code:** `coherence_scores_{dom}.csv`, `fig_lda_beta_resumo.pdf`, `fig_lda_beta_{dom}.pdf`, `lda_topics_{dom}.csv`
- **Warnings:** None.

## resultados/adequacao_20261110/F10_reexec/16_kcna.py

- **Purpose:** Keyword co-occurrence network analysis (KCNA) from OpenAlex concepts.
- **Files referenced in the code:** `consolidado_todos_dominios.csv`, `fig_kcna_{dom}.pdf`, `kcna_edges_{dom}.csv`
- **Warnings:** None.

## resultados/adequacao_20261110/F10_reexec/17_mapa_tematico.py

- **Purpose:** Thematic map (motor, niche, basic and emerging themes) from centrality and density.
- **Files referenced in the code:** `consolidado_todos_dominios.csv`, `fig_mapa_tematico_{dom}.pdf`, `mapa_tematico_{dom}.csv`
- **Warnings:** None.

## resultados/adequacao_20261110/F10_reexec/18_mca.py

- **Purpose:** Multiple correspondence analysis of the presence matrix of concepts.
- **Files referenced in the code:** `consolidado_todos_dominios.csv`, `fig_mca_{dom}.pdf`, `mca_coordenadas_{dom}.csv`
- **Warnings:** None.

## resultados/adequacao_20261110/F10_reexec/19_crescimento_anual.py

- **Purpose:** Annual percentage growth per domain.
- **Files referenced in the code:** `consolidado_todos_dominios.csv`, `crescimento_anual.csv`, `crescimento_anual.tex`
- **Warnings:** None.

## codigo/adequacao_20261110/F2_correr_coleta.sh

- **Purpose:** Shell runner.
- **Files referenced in the code:** none detected
- **Warnings:** None.

## codigo/adequacao_20261110/F2c_correr.sh

- **Purpose:** Shell runner.
- **Files referenced in the code:** none detected
- **Warnings:** None.

## environment/criar_venv_gpu5070.sh

- **Purpose:** Shell runner.
- **Files referenced in the code:** none detected
- **Warnings:** None.

## resultados/adequacao_20261110/F10_reexec/correr_F10.sh

- **Purpose:** Shell runner.
- **Files referenced in the code:** none detected
- **Warnings:** None.
