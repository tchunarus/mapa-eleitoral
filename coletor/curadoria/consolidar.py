"""Consolida as frentes de pesquisa do 2º turno em conteudo/segundo_turno/.

Entrada: pesquisa/segundo_turno/*.json, uma por frente (formato descrito em ESPEC.md),
e agenda_notas.json (ressalvas curadas sobre eventos da agenda, com data e fontes).
Saída: evidencias.json, checagens.json, linha_do_tempo.json e agenda.json.

Normalizações registradas aqui, para que toda nova rodada as reproduza:
- travessão vira vírgula e verbos em primeira pessoa ficam impessoais (IMPESSOAL);
- evidências que repetem o mesmo fato em duas frentes são descartadas (EXCLUIR, com motivo);
- cada checagem recebe `origem` (quem fez a declaração: uma das candidaturas ou terceiros);
- marcos da linha do tempo com mesma data, candidato e título são unificados, e eventos
  posteriores à data da análise (eleicao.json, atualizado_em) ficam só na agenda.

    python3 coletor/curadoria/consolidar.py
"""
import glob, json, os, re, sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PQ = os.path.join(RAIZ, 'pesquisa', 'segundo_turno')
OUT = os.path.join(RAIZ, 'conteudo', 'segundo_turno')

IMPESSOAL = [(r'\bnão localizei\b', 'não foi localizado'), (r'\bNão localizei\b', 'Não foi localizado'),
             (r'\bnão encontrei\b', 'não foi encontrado'), (r'\bNão encontrei\b', 'Não foi encontrado'),
             (r'\bnão consultei\b', 'não foram consultadas'), (r'\bnão confirmei\b', 'não foi confirmado'),
             (r'\bNão confirmei\b', 'Não foi confirmado'), (r'\bnão achei\b', 'não foi encontrado'),
             (r'\bnão verifiquei\b', 'não foi verificado'), (r'\blocalizei\b', 'foi localizado'),
             (r'\bencontrei\b', 'foi encontrado'), (r'\bconfirmei\b', 'foi confirmado'),
             (r'1 são diretrizes genéricas', '1 é diretriz genérica')]

# mesmo fato registrado por duas frentes da atualização de 21/10/2026; fica a versão indicada
EXCLUIR = {
    'atualizacao-fatos-lula-02': 'repete atualizacao-campanha-lula-03 (autorização de quebra de sigilos)',
    'atualizacao-fatos-lula-04': 'repete atualizacao-campanha-lula-08 (decisão de Bellizze de 21/10)',
    'atualizacao-fatos-flavio-03': 'repete atualizacao-campanha-flavio-08 (resposta à quebra de sigilos)',
    'atualizacao-campanha-lula-04': 'repete atualizacao-fatos-lula-03 (condição para o debate), mais completa',
}
CAMPOS_FONTE = ('titulo', 'veiculo', 'url', 'data', 'tipo_fonte')


def limpa(o):
    if isinstance(o, str):
        s = o.replace(' — ', ', ').replace('—', ', ')
        for a, b in IMPESSOAL:
            s = re.sub(a, b, s)
        return re.sub(r'\s+', ' ', s).strip()
    if isinstance(o, list):
        return [limpa(x) for x in o]
    if isinstance(o, dict):
        return {k: limpa(v) for k, v in o.items()}
    return o


def fonte(f):
    f = {k: f.get(k) for k in CAMPOS_FONTE}
    if f['data'] and len(f['data']) > 10:
        f['data'] = f['data'][:10]
    return f


def origem(autor):
    a = (autor or '').lower()
    return 'lula' if a.startswith(('luiz inácio', 'lula')) else 'flavio' if a.startswith(('flávio', 'flavio')) else 'terceiros'


def consolidar(pq=PQ, out=OUT):
    ev, chk, tl, ag = [], [], [], []
    for cam in sorted(glob.glob(os.path.join(pq, '*.json'))):
        fr = os.path.basename(cam)[:-5]
        if fr == 'agenda_notas':
            continue
        d = limpa(json.load(open(cam, encoding='utf-8')))
        for e in d.get('evidencias', []):
            if e.get('id') in EXCLUIR:
                continue
            e['fontes'] = [fonte(f) for f in e.get('fontes', [])]
            e['frente'] = fr
            ev.append(e)
        for c in d.get('checagens', []):
            c['fontes_verificacao'] = [fonte(f) for f in c.get('fontes_verificacao', [])]
            chk.append(c)
        for t in d.get('linha_do_tempo', []):
            t['fontes'] = [fonte(f) for f in t.get('fontes', [])]
            tl.append(t)
        for a in d.get('agenda', []):
            a['fontes'] = [fonte(f) for f in a.get('fontes', [])]
            ag.append(a)
    vistos = set()
    for e in ev:
        i = e.get('id') or f"{e['frente']}-{e['candidato']}"
        n, k = i, 2
        while n in vistos:
            n, k = f'{i}-{k}', k + 1
        e['id'] = n
        vistos.add(n)
    for i, c in enumerate(chk, 1):
        c['id'] = f'chk-{i:03d}'
        c['origem'] = origem(c.get('autor'))
    ref = json.load(open(os.path.join(out, 'eleicao.json'), encoding='utf-8')).get('atualizado_em') or '9999'
    vt, tl2 = set(), []
    for t in sorted(tl, key=lambda t: (t.get('data') or '', t.get('candidato') or '')):
        if (t.get('data') or '') > ref:
            continue  # evento ainda não ocorrido: pertence à agenda
        k = (t.get('data'), t.get('candidato'), re.sub(r'\W+', '', (t.get('titulo') or '').lower())[:30])
        if k not in vt:
            vt.add(k)
            tl2.append(t)
    ag.sort(key=lambda a: (a['data'], a.get('hora') or ''))
    cam = os.path.join(pq, 'agenda_notas.json')
    notas = limpa(json.load(open(cam, encoding='utf-8'))) if os.path.exists(cam) else {}
    for a in ag:
        if a['titulo'] in notas:
            nota = dict(notas[a['titulo']])
            nota['fontes_situacao'] = [fonte(f) for f in nota.get('fontes_situacao', [])]
            a.update(nota)
    for nome, dados in (('evidencias', ev), ('checagens', chk), ('linha_do_tempo', tl2), ('agenda', ag)):
        with open(os.path.join(out, nome + '.json'), 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=1)
    return {'evidencias': len(ev), 'checagens': len(chk), 'linha_do_tempo': len(tl2), 'agenda': len(ag),
            'por_criterio': dict(Counter(f"{e['candidato']}:{e['criterio']}" for e in ev))}


if __name__ == '__main__':
    print(json.dumps(consolidar(), ensure_ascii=False, indent=1))
