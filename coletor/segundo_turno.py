"""Segundo turno presidencial de 2026: validação e publicação da análise comparativa.

Dados curados em conteudo/segundo_turno/:

- eleicao.json        situação oficial (com fonte), candidaturas e cores de comparação;
- criterios.json      critérios, perguntas, indicadores e rubrica de notas (0 a 10);
- evidencias.json     evidências classificadas por tipo (fato, dado oficial, decisão, alegação...),
                      sentido (favorável, desfavorável, misto, contexto) e peso probatório;
- avaliacoes.json     nota por critério e candidatura, com justificativa que cita evidências;
- checagens.json      painel de verificação de fatos;
- linha_do_tempo.json marcos das trajetórias e da campanha;
- conclusao.json      síntese por dimensão, com as distinções exigidas pela metodologia.

As propostas de governo vêm das fichas (conteudo/fichas/) e da análise de competência já
existente; aqui só são reunidas por candidatura.

Nada é publicado se houver erro: evidência sem fonte, fonte sem URL ou data, critério
inexistente, nota sem evidência citada, critério sem avaliação para uma das candidaturas.

    python3 coletor/segundo_turno.py     # só valida e mostra contagens
"""
import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import repositorio  # noqa: E402

PASTA = os.path.join(repositorio.RAIZ, 'conteudo', 'segundo_turno')
ARQUIVOS = ('eleicao', 'criterios', 'evidencias', 'avaliacoes', 'checagens', 'linha_do_tempo', 'conclusao', 'agenda')

TIPO_EVIDENCIA = {
    'FATO_COMPROVADO': 'Fato comprovado', 'DADO_OFICIAL': 'Dado oficial',
    'DECISAO_JUDICIAL_DEFINITIVA': 'Decisão judicial definitiva', 'DECISAO_JUDICIAL_NAO_DEFINITIVA': 'Decisão judicial não definitiva',
    'INVESTIGACAO_OU_DENUNCIA': 'Investigação ou denúncia', 'ALEGACAO': 'Alegação', 'INTERPRETACAO': 'Interpretação',
    'OPINIAO': 'Opinião', 'PROMESSA': 'Promessa', 'INCONCLUSIVO': 'Inconclusivo'}
SENTIDO = {'FAVORAVEL': 'Favorável', 'DESFAVORAVEL': 'Desfavorável', 'MISTO': 'Misto', 'CONTEXTO': 'Contexto'}
PESO = {'ALTO': 'Alto', 'MEDIO': 'Médio', 'BAIXO': 'Baixo'}
TIPO_FONTE = {'PRIMARIA': 'Fonte primária', 'JORNALISTICA': 'Jornalística', 'CHECAGEM': 'Agência de checagem',
              'ACADEMICA': 'Acadêmica', 'CAMPANHA': 'Campanha'}
CLASSIF_CHECAGEM = {'VERDADEIRO': 'Verdadeiro', 'FALSO': 'Falso', 'ENGANOSO': 'Enganoso', 'DESCONTEXTUALIZADO': 'Descontextualizado',
                    'INCONCLUSIVO': 'Inconclusivo', 'PARCIALMENTE_VERDADEIRO': 'Parcialmente verdadeiro'}
SUFICIENCIA = {'ALTA': 'Evidência suficiente', 'MEDIA': 'Evidência parcial', 'BAIXA': 'Evidência insuficiente'}
CATEGORIA_TEMPO = {'cargo': 'Cargo', 'eleicao': 'Eleição', 'judicial': 'Judicial', 'governo': 'Governo',
                   'legislativo': 'Legislativo', 'campanha': 'Campanha'}
DATA = re.compile(r'^\d{4}(-\d{2}(-\d{2})?)?$')


def ler(nome, pasta=PASTA):
    cam = os.path.join(pasta, nome + '.json')
    if not os.path.exists(cam):
        return {} if nome in ('eleicao', 'conclusao') else []
    return json.load(open(cam, encoding='utf-8'))


def carregar(pasta=PASTA):
    return {n: ler(n, pasta) for n in ARQUIVOS}


def _fontes(lugar, fontes, erros, obrigatoria=True):
    if not fontes:
        if obrigatoria:
            erros.append(f'{lugar}: sem fonte')
        return
    for i, f in enumerate(fontes, 1):
        if not str(f.get('url') or '').startswith(('https://', 'http://')):
            erros.append(f'{lugar}: fonte {i} sem URL')
        if not DATA.match(str(f.get('data') or '')):
            erros.append(f'{lugar}: fonte {i} sem data AAAA-MM-DD')
        if f.get('tipo_fonte') not in TIPO_FONTE:
            erros.append(f'{lugar}: fonte {i} com tipo_fonte inválido ({f.get("tipo_fonte")})')
        if not f.get('veiculo'):
            erros.append(f'{lugar}: fonte {i} sem veículo')


def validar(d):
    erros, avisos = [], []
    texto = json.dumps(d, ensure_ascii=False)
    if '—' in texto:
        erros.append('travessão (em dash) encontrado nos dados do 2º turno')
    el = d['eleicao']
    cands = {c['id'] for c in el.get('candidatos', [])}
    if len(cands) != 2:
        erros.append('eleicao: são esperadas exatamente duas candidaturas')
    _fontes('eleicao.situacao', (el.get('situacao') or {}).get('fontes'), erros)
    crit = {c['id']: c for c in d['criterios']}
    ev = {}
    for e in d['evidencias']:
        lugar = f'evidencias.{e.get("id")}'
        if e.get('id') in ev:
            erros.append(f'{lugar}: id repetido')
        ev[e.get('id')] = e
        if e.get('candidato') not in cands:
            erros.append(f'{lugar}: candidato inválido')
        if e.get('criterio') not in crit:
            erros.append(f'{lugar}: critério inexistente ({e.get("criterio")})')
        for campo, dom in (('tipo', TIPO_EVIDENCIA), ('sentido', SENTIDO), ('peso_probatorio', PESO)):
            if e.get(campo) not in dom:
                erros.append(f'{lugar}: {campo} inválido ({e.get(campo)})')
        if not (e.get('afirmacao') or '').strip():
            erros.append(f'{lugar}: sem afirmação')
        if e.get('data_fato') and not DATA.match(e['data_fato']):
            erros.append(f'{lugar}: data_fato inválida')
        _fontes(lugar, e.get('fontes'), erros)
    vistos = set()
    for a in d['avaliacoes']:
        lugar = f'avaliacoes.{a.get("criterio")}.{a.get("candidato")}'
        vistos.add((a.get('criterio'), a.get('candidato')))
        if a.get('criterio') not in crit or a.get('candidato') not in cands:
            erros.append(f'{lugar}: critério ou candidato inválido')
        n = a.get('nota')
        if not isinstance(n, (int, float)) or not 0 <= n <= 10:
            erros.append(f'{lugar}: nota fora de 0 a 10')
        if a.get('suficiencia') not in SUFICIENCIA:
            erros.append(f'{lugar}: suficiência inválida')
        citadas = a.get('evidencias') or []
        if not citadas:
            erros.append(f'{lugar}: nota sem evidência citada')
        for x in citadas:
            if x not in ev:
                erros.append(f'{lugar}: evidência inexistente {x}')
            elif ev[x]['candidato'] != a.get('candidato'):
                erros.append(f'{lugar}: evidência {x} é de outra candidatura')
        if not (a.get('justificativa') or '').strip():
            erros.append(f'{lugar}: sem justificativa')
    if d['avaliacoes']:
        for c in crit:
            for k in cands:
                if (c, k) not in vistos:
                    erros.append(f'avaliacoes: falta {c} para {k}')
    ids = set()
    for ch in d['checagens']:
        lugar = f'checagens.{ch.get("id")}'
        if ch.get('id') in ids:
            erros.append(f'{lugar}: id repetido')
        ids.add(ch.get('id'))
        if ch.get('alvo') not in cands | {'ambos'}:
            erros.append(f'{lugar}: alvo inválido')
        if ch.get('origem') not in cands | {'terceiros'}:
            erros.append(f'{lugar}: origem inválida (quem fez a declaração: candidatura ou terceiros)')
        if ch.get('classificacao') not in CLASSIF_CHECAGEM:
            erros.append(f'{lugar}: classificação inválida')
        for campo in ('declaracao', 'autor', 'veiculo', 'explicacao'):
            if not (ch.get(campo) or '').strip():
                erros.append(f'{lugar}: sem {campo}')
        if not DATA.match(str(ch.get('data') or '')):
            erros.append(f'{lugar}: data inválida')
        _fontes(lugar, ch.get('fontes_verificacao'), erros)
    for i, t in enumerate(d['linha_do_tempo'], 1):
        lugar = f'linha_do_tempo.{i}'
        if t.get('candidato') not in cands | {'ambos'}:
            erros.append(f'{lugar}: candidato inválido')
        if t.get('categoria') not in CATEGORIA_TEMPO:
            erros.append(f'{lugar}: categoria inválida')
        if not DATA.match(str(t.get('data') or '')):
            erros.append(f'{lugar}: data inválida')
        _fontes(lugar, t.get('fontes'), erros)
    for i, a in enumerate(d.get('agenda') or [], 1):
        lugar = f'agenda.{i}'
        if not DATA.match(str(a.get('data') or '')) or not a.get('titulo'):
            erros.append(f'{lugar}: sem data ou título')
        _fontes(lugar, a.get('fontes'), erros)
        if a.get('situacao'):
            _fontes(lugar + '.situacao', a.get('fontes_situacao'), erros)
    if el.get('atualizado_em') and not DATA.match(el['atualizado_em']):
        erros.append('eleicao.atualizado_em inválida')
    for dim in (d['conclusao'] or {}).get('dimensoes', []):
        for x in dim.get('evidencias') or []:
            if x not in ev:
                erros.append(f'conclusao.{dim.get("id")}: evidência inexistente {x}')
    # simetria: avisa quando um critério tem evidências só de uma candidatura
    for c in crit:
        por = {k: sum(1 for e in d['evidencias'] if e['criterio'] == c and e['candidato'] == k) for k in cands}
        if d['evidencias'] and min(por.values()) == 0:
            avisos.append(f'critério {c} sem evidência para {[k for k, v in por.items() if not v]}')
    return erros, avisos


def gerar(pub, salvar):
    """Grava docs/data/segundo-turno.json. `pub` é o Publicador (para as propostas e análises)."""
    d = carregar()
    if not d['eleicao']:
        return None
    propostas = {}
    for c in d['eleicao']['candidatos']:
        lista = []
        for p in pub.idx['propostas'].get(c['candidatura_id'], []):
            if not pub.publicavel(p):
                continue
            a = pub.analise(p) or {}
            af = next((pub.afirmacao(x) for x in pub.afirm_por_proposta.get(p['id'], []) if x['tipo'] == 'PROPOSAL'), None)
            fonte = (af or {}).get('fontes', [{}])[0]
            lista.append({'id': p['id'], 'titulo': p['titulo'], 'resumo': p['descricao'], 'subtema': p.get('subtema'),
                          'temas': pub.temas_de(p['id']), 'detalhamento': p.get('nivel_detalhamento'),
                          'impacto_orcamentario': p.get('impacto_orcamentario'),
                          'classificacao': a.get('classificacao'), 'rotulo': a.get('rotulo'),
                          'instrumento': (a.get('instrumento') or {}).get('nome'),
                          'dependencias': sorted({x['instituicao'] for x in a.get('dependencias') or []}),
                          'trecho': fonte.get('trecho'), 'localizador': fonte.get('localizador'),
                          'fonte': {k: (fonte.get('fonte') or {}).get(k) for k in ('titulo', 'url', 'publicador')}})
        propostas[c['id']] = lista
    out = dict(d)
    out['eleicao'] = dict(d['eleicao'], candidatos=[dict(c, foto_url=(pub.t['candidaturas'].get(c['candidatura_id']) or {}).get('foto_url'))
                                                   for c in d['eleicao']['candidatos']])
    out['propostas'] = propostas
    out['gerado_em'] = pub.agora
    out['rotulos'] = {'tipo': TIPO_EVIDENCIA, 'sentido': SENTIDO, 'peso': PESO, 'tipo_fonte': TIPO_FONTE,
                      'checagem': CLASSIF_CHECAGEM, 'suficiencia': SUFICIENCIA, 'categoria_tempo': CATEGORIA_TEMPO}
    salvar('segundo-turno.json', out)
    return {k: len(v) if isinstance(v, list) else None for k, v in d.items()}


if __name__ == '__main__':
    d = carregar()
    e, a = validar(d)
    print(json.dumps({'erros': e[:40], 'n_erros': len(e), 'avisos': a, 'contagens': {k: len(v) for k, v in d.items() if isinstance(v, list)}},
                     ensure_ascii=False, indent=1))
    sys.exit(1 if e else 0)
