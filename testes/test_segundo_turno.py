"""Validação dos dados do 2º turno: fonte obrigatória, notas justificadas, simetria e redação."""
import copy, os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'coletor'))
import segundo_turno as st  # noqa: E402

F = {'titulo': 'Documento', 'veiculo': 'TSE', 'url': 'https://www.tse.jus.br/x', 'data': '2026-10-05', 'tipo_fonte': 'PRIMARIA'}


def base():
    crit = [{'id': 'experiencia', 'nome': 'Experiência', 'ordem': 1}]
    ev = [{'id': f'e-{k}', 'candidato': k, 'criterio': 'experiencia', 'tipo': 'FATO_COMPROVADO', 'sentido': 'CONTEXTO',
           'peso_probatorio': 'ALTO', 'afirmacao': 'Exerceu mandato.', 'data_fato': '2019-02-01', 'fontes': [dict(F)]} for k in ('a', 'b')]
    av = [{'criterio': 'experiencia', 'candidato': k, 'nota': 5, 'suficiencia': 'ALTA', 'justificativa': 'Conforme a rubrica.',
           'evidencias': [f'e-{k}']} for k in ('a', 'b')]
    return {'eleicao': {'candidatos': [{'id': 'a'}, {'id': 'b'}], 'situacao': {'texto': 'x', 'fontes': [dict(F)]}},
            'criterios': crit, 'evidencias': ev, 'avaliacoes': av, 'checagens': [], 'linha_do_tempo': [], 'conclusao': {}}


class TestSegundoTurno(unittest.TestCase):
    def erros(self, d):
        return st.validar(d)[0]

    def test_base_valida(self):
        self.assertEqual(self.erros(base()), [])

    def test_evidencia_sem_fonte(self):
        d = base(); d['evidencias'][0]['fontes'] = []
        self.assertTrue(any('sem fonte' in e for e in self.erros(d)))

    def test_fonte_sem_data_ou_url(self):
        d = base(); d['evidencias'][0]['fontes'][0].pop('data'); d['evidencias'][1]['fontes'][0]['url'] = 'tse.jus.br'
        e = self.erros(d)
        self.assertTrue(any('sem data' in x for x in e) and any('sem URL' in x for x in e))

    def test_nota_sem_evidencia_ou_de_outro_candidato(self):
        d = base(); d['avaliacoes'][0]['evidencias'] = []
        self.assertTrue(any('sem evidência' in e for e in self.erros(d)))
        d = base(); d['avaliacoes'][0]['evidencias'] = ['e-b']
        self.assertTrue(any('outra candidatura' in e for e in self.erros(d)))

    def test_criterio_sem_avaliacao_de_um_candidato(self):
        d = base(); d['avaliacoes'].pop()
        self.assertTrue(any('falta experiencia para b' in e for e in self.erros(d)))

    def test_nota_fora_da_escala(self):
        d = base(); d['avaliacoes'][0]['nota'] = 11
        self.assertTrue(any('0 a 10' in e for e in self.erros(d)))

    def test_travessao_bloqueia(self):
        d = base(); d['evidencias'][0]['afirmacao'] = 'Exerceu mandato — e outro.'
        self.assertTrue(any('travessão' in e for e in self.erros(d)))

    def test_checagem_exige_classificacao_e_fonte(self):
        d = base(); d['checagens'] = [{'id': 'c1', 'alvo': 'a', 'classificacao': 'MEIO_VERDADE', 'declaracao': 'x', 'autor': 'y',
                                       'veiculo': 'z', 'explicacao': 'w', 'data': '2026-10-10', 'fontes_verificacao': []}]
        e = self.erros(d)
        self.assertTrue(any('classificação inválida' in x for x in e) and any('sem fonte' in x for x in e))

    def test_aviso_de_assimetria(self):
        d = base(); d['evidencias'] = d['evidencias'][:1]; d['avaliacoes'] = []
        self.assertTrue(any('sem evidência para' in a for a in st.validar(d)[1]))

    def test_evidencia_de_outro_criterio(self):
        d = base(); d['criterios'].append({'id': 'coerencia', 'nome': 'Coerência', 'ordem': 2})
        d['evidencias'][0]['criterio'] = 'coerencia'
        self.assertTrue(any('pertence ao critério coerencia' in e for e in self.erros(d)))

    def test_agenda_exige_data_titulo_e_fonte(self):
        d = base(); d['agenda'] = [{'data': '2026-10-23', 'titulo': '', 'fontes': []}]
        e = self.erros(d)
        self.assertTrue(any('sem data ou título' in x for x in e) and any('agenda.1: sem fonte' in x for x in e))

    def test_ressalva_da_agenda_exige_fonte_e_data_da_atualizacao(self):
        d = base(); d['eleicao']['atualizado_em'] = '2026-10-21'
        d['agenda'] = [{'data': '2026-10-23', 'titulo': 'Debate', 'fontes': [dict(F)], 'situacao': 'Condicionado.', 'situacao_em': '2026-10-20'}]
        e = self.erros(d)
        self.assertTrue(any('agenda.1.situacao: sem fonte' in x for x in e) and any('revise a ressalva' in x for x in e))
        d['agenda'][0].update(situacao_em='2026-10-21', fontes_situacao=[dict(F)])
        self.assertEqual(self.erros(d), [])

    def test_atualizado_em_nao_pode_ser_anterior_aos_dados(self):
        d = base(); d['eleicao']['atualizado_em'] = '2026-10-01'
        self.assertTrue(any('anterior ao dado mais recente' in e for e in self.erros(d)))
        d['eleicao']['atualizado_em'] = '2026-10-05'
        self.assertEqual(self.erros(d), [])

    def test_dados_publicados_validos(self):
        e, _ = st.validar(st.carregar())
        self.assertEqual(e, [])


if __name__ == '__main__':
    unittest.main()
