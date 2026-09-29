"""Rotina de atualização do Mapa Eleitoral.

    python3 coletor/atualizar.py            # com rede: TSE, Senado e texto vigente; depois análise e publicação
    python3 coletor/atualizar.py --sem-rede # só refaz análises e publicação a partir do estado gravado

Etapas com rede, cada uma isolada (a falha de uma não impede as outras e fica registrada):
1. candidaturas do TSE (coletor/tse/sincronizar.py); se o TSE recusar a conexão, o erro
   vai para estado/ingestoes.json e os dados da última sincronização são mantidos;
2. vagas do Senado em disputa (coletor/legislativo.py);
3. texto vigente dos fundamentos, a partir da publicação aberta do Mapa Normativo
   (coletor/normativo.py).
Sempre: análise de competência (coletor/analisar.py), publicação de docs/data/
(coletor/publicar.py) e montagem de docs/index.html (coletor/paginar.py).
"""
import argparse, json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, 'tse'))
import repositorio, normativo, legislativo, analisar, publicar, paginar  # noqa: E402
import cliente, sincronizar  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sem-rede', action='store_true')
    ap.add_argument('--eleicao', default='2026-geral')
    a = ap.parse_args()
    status = {}

    def etapa(nome, f):
        try:
            status[nome] = f()
        except Exception as e:  # noqa: BLE001 - registrar e seguir para as demais etapas
            status[nome] = f'falha ({e.__class__.__name__}: {str(e)[:160]})'

    if not a.sem_rede:
        def tse():
            lg = sincronizar.sincronizar(a.eleicao, cliente.TransporteHTTP())
            return 'ok' if not lg['errors'] else f"{lg['errors']} erro(s); mantidos os dados anteriores ({lg['erros'][0][:120]})"
        etapa('TSE, candidaturas', tse)
        etapa('Senado, vagas', lambda: 'ok' if not legislativo.sincronizar_vagas_senado()['errors'] else 'falha na leitura')
        etapa('Texto vigente (Mapa Normativo)', lambda: normativo.sincronizar(repositorio.carregar().tabelas['regras']))
    etapa('Análise de competência', lambda: (lambda lg: 'ok' if not lg['errors'] else lg['erros'][:3])(analisar.analisar_tudo(registrar_sem_mudanca=False)))
    etapa('Publicação', lambda: (lambda r: 'ok' if r['publicado'] else r['erros'][:3])(publicar.construir()))
    etapa('Página', lambda: f'{paginar.montar()} bytes')
    print(json.dumps(status, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
