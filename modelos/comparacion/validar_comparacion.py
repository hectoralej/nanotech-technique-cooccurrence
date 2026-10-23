import sys
sys.dont_write_bytecode=True
import json,hashlib,unittest
import numpy as np
import pandas as pd
import fusion
from fusion import HERE,ROOT,LABELS,PCOLS,weight_for_fold,probabilities,assert_origin,run,csv
from control import checkpoint,write_json,guard

class Tests(unittest.TestCase):
    def test_manifest_unico_y_folds(self):
        d=csv(HERE/'conjunto_comparacion.csv');assert d.pmcid.is_unique and d.fold.astype(int).between(0,4).all()
        official=csv(ROOT/'curation'/'v0.1'/'tabla_modelo.csv').drop_duplicates('pmcid').set_index('pmcid').fold.astype(int)
        np.testing.assert_array_equal(d.fold.astype(int),d.pmcid.map(official))
    def test_confianza_y_probabilidades_parciales(self):
        f=pd.DataFrame({'prediccion':['lipidico','polimerico'],'confianza':[.8,.7]});p,note=probabilities(f);assert np.allclose(p.sum(axis=1),1) and 'solo confianza' in note
        with self.assertRaises(AssertionError):probabilities(f.assign(p_lipidico=.3))
    def test_sintetico_rechazado_en_real(self):
        with self.assertRaises(AssertionError):assert_origin(pd.DataFrame({'sintetico':[True]}),False)
    def test_peso_no_mira_etiquetas_test(self):
        rng=np.random.default_rng(2);y=np.asarray(LABELS*20);folds=np.tile(np.arange(5),16);a=rng.dirichlet(np.ones(4),80);b=rng.dirichlet(np.ones(4),80)
        for held in range(5):
            original=weight_for_fold(y,a,b,folds,held);perturbed=y.copy();perturbed[folds==held]=np.roll(perturbed[folds==held],1)
            self.assertEqual(original,weight_for_fold(perturbed,a,b,folds,held))
    def test_sintetico_aislado_y_poblacion_comun(self):
        real=HERE/'resultados'/'comparacion_justa.json';before=real.read_bytes() if real.exists() else None
        result=run(True);assert result['sintetico']
        self.assertEqual(before,real.read_bytes() if real.exists() else None)
        for exp in result['experimentos']:
            self.assertEqual(len({m['pmcid_hash'] for m in exp['metodos'].values()}),1)
            self.assertEqual(len({m['folds_hash'] for m in exp['metodos'].values()}),1)
            self.assertTrue(all(m['n_articulos']==result['n_articulos_comunes'] for m in exp['metodos'].values()))
    def test_real_ausente_no_inventa_json(self):
        entries=list((HERE/'entrada_kabre').glob('predicciones_*.csv'))
        if not entries:
            path=HERE/'resultados'/'comparacion_justa.json';before=path.read_bytes() if path.exists() else None
            self.assertIsNone(run(False));self.assertEqual(before,path.read_bytes() if path.exists() else None)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests);r=unittest.TextTestRunner(verbosity=2).run(suite)
    if not r.wasSuccessful():raise SystemExit(1)
    guard();write_json(HERE/'VALIDACION_C.json',{'estado':'PASS','tests':r.testsRun,'datos_reales_kabre_disponibles':bool(list((HERE/'entrada_kabre').glob('predicciones_*.csv'))),'sinteticos':'resultados_sintetico/comparacion_justa.json, etiquetados true y aislados','limitacion_anidamiento':'La prueba verifica selección directa con etiquetas de entrenamiento; no demuestra procedencia estrictamente anidada de las predicciones OOF suministradas.'})
    checkpoint('C',f'PASS: conjunto único, mismos artículos/folds en los métodos; {r.testsRun} pruebas, incluidos aislamiento sintético, confianza y peso sin etiquetas test. Sin predicciones Kabré no hay resultados reales; no se generaron embeddings.')
