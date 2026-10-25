"""Registra entrega parcial comprobada, sin dar por cumplida la cobertura pendiente."""
import json
import ajuste1 as a

s=json.loads((a.OUT/'RESUMEN_AJUSTE1.json').read_text(encoding='utf-8'))
v=json.loads((a.OUT/'VALIDACION_GLOBAL_AJUSTE1.json').read_text(encoding='utf-8'))
assert v['validacion_artefactos']=='PASS' and not v['fallos']
assert not v['lotes_sin_procesar']
p=json.loads((a.OUT/'progreso.json').read_text(encoding='utf-8'))
p['estado']='primera_pasada_local_entregada_con_pendientes'
p['cierre_total']=False
p['ultimo_lote']['siguiente_paso']='Claude: recuperar imágenes pendientes; reextraer solo artículos cambiados y revalidar. Lotes 8/11 excluidos por calidad; lote 18 pendiente de mezcla mínima. No hay lote 19.'
p['pendientes_entrega']={
 'primeros_400_sin_recorte':s['primeros_400_pendientes_imagen_o_lote'],
 'articulos_sin_imagen_local':s['articulos_sin_imagen_local'],
 'lotes_calidad_insuficiente':[8,11],
 'lotes_mezcla_insuficiente':[18],
 'etiquetas_humanas':'pendientes de Héctor; ninguna inventada',
 'vista_html_navegador':'no verificada: file:// bloqueado; pruebas funcionales PASS'}
a.dump(a.OUT/'progreso.json',p)
a.checkpoint(
 f"ENTREGA PARCIAL VERIFICADA, no cierre total: inventario {s['articulos_inventariados']} artículos; "
 f"18 lotes recorridos, {len(s['lotes_aprobados'])} aprobados; {s['recortes_extraidos']} recortes totales y "
 f"{s['recortes_lotes_aprobados']} en lotes aprobados. Tablas: {s['micrografias_provisionales_aprobadas']} micrografías probables "
 f"y {s['espectros_tecnica_panel_aprobados']} espectros con técnica de panel. Figuras enteras: {s['porcentaje_compuesta_sin_separar']}%. "
 f"Primeros 400: {s['primeros_400_con_recorte']}, faltan {s['primeros_400_pendientes_imagen_o_lote']} imágenes/artículos. "
 "Lotes 8 y 11 excluidos (2/5); lote 18 excluido (3/5 pero sin gráficas elegibles). "
 "Global PASS, pruebas de bloqueo PASS, sin archivos nuevos pendientes de reproceso al comprobar. "
 "Hoja humana: 300 casos fijos, 600 rutas y funciones PASS; vista en navegador no verificada. "
 "Se conservaron las mismas muestras y se reintegraron sus veredictos tras la migración de metadatos; no se repitió la extracción. "
 "PMC10605403/Fig3: pie contradictorio, técnicas retiradas y abstención auditada por hash. "
 "Siguiente: recibir imágenes de Claude y revalidar cambios; decidir revisión alternativa del lote 18 si no aparecen gráficas. "
 "Sin descargas propias, git, redes neuronales ni edición de fuentes protegidas.")
print('Checkpoint de entrega parcial guardado; cierre_total=False.')
