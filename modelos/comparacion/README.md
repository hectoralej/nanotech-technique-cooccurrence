# Comparación justa por artículo

1. `python modelos/comparacion/conjunto_comparacion.py`: fija los artículos con imagen existente no vacía, clase/fold y al menos una medición válida. Guarda también el inventario de imágenes para evitar cambios de población durante una evaluación.
2. Colocar predicciones OOF auténticas en `entrada_kabre/predicciones_<modelo>.csv`: pmcid, image_file, real, prediccion, confianza, fold; opcionalmente p_inorganico, p_lipidico, p_nanomaterial, p_polimerico. No se necesitan ni se calculan embeddings aquí.
3. `python modelos/comparacion/fusion.py`: promedio de probabilidades por artículo y comparación sobre la intersección común a todos los modelos recibidos y al tabular. Se reportan artículos excluidos por falta de predicciones, IDs/folds compartidos, exactitud, F1 macro, matrices e IC95 con 1.000 bootstrap de artículos.

El tabular predeterminado es `clase4_mediciones_logistica`: solo tamaño, zeta y PDI con faltantes; no incluye texto, clases ni metadatos de técnicas. Los clasificadores de B enriquecidos con texto no se renombran como «solo mediciones».

Fusión: media 50/50 y peso en rejilla 0–1 (paso 0,1), elegido por F1 macro solo sobre otros folds; ningún artículo test participa directamente en esa selección. Sin probabilidades por clase se asigna confianza a la predicha y se reparte el resto uniformemente: son scores reconstruidos, no probabilidades verificadas/calibradas. El JSON identifica este caso. Las entradas con probabilidades parciales, folds/etiquetas inconsistentes o imágenes duplicadas se rechazan.

Advertencia metodológica: los OOF de otros folds podrían proceder de modelos entrenados con los artículos del fold externo actual. El contrato de entrada no permite comprobar un anidamiento completo del entrenamiento. Para una fusión estrictamente anidada se necesitan scores de validación interna por outer-fold de ambos proveedores; el JSON lo advierte. No presentar esta evaluación exploratoria como validación externa.

`python modelos/comparacion/fusion.py --sintetico` genera exclusivamente predicciones falsas de prueba y métricas en `resultados_sintetico/`, todas con `sintetico: true`. Nunca alimenta la figura 11 ni el directorio real. `validar_comparacion.py` prueba cohortes, folds, aislamiento, falta de datos reales y selección de pesos.
