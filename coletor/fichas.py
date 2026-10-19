"""Fichas de proposta: registro padronizado que o script normaliza nas tabelas do esquema.

Cada arquivo conteudo/fichas/<qualquer nome>.json descreve as propostas de uma
candidatura. Formato:

    {"candidatura_id": "tse-240002553718",
     "fonte_id": "tse-documento-240017123645",     # fonte padrão (ex.: proposta de governo no TSE)
     "data": "2026-08-15",                          # data da manifestação, se conhecida (opcional)
     "verificado_em": "2026-09-29T13:00:00+00:00",  # última conferência da ficha contra a fonte
     "propostas": [
       {"id": "tarifa-zero",                        # identificador curto, único na ficha
        "tema": "mobilidade", "temas_extras": ["direitos-sociais"], "subtema": "transporte coletivo",
        "titulo": "Síntese objetiva da proposta",
        "resumo": "Descrição do que a candidatura pretende realizar.",
        "trecho": "Trecho literal da fonte (até 400 caracteres).",
        "pagina": 12,                               # página do documento (ou "localizador": "minuto 12:30")
        "fonte_id": "...", "data": "...",           # substituem os padrões da ficha, se preciso
        "outras_fontes": [{"fonte_id": "...", "localizador": "...", "trecho": "...", "relacao": "SUPPORTS"}],
        "materia": "servicos-saude", "natureza": "PUBLIC_WORK_OR_SERVICE",
        "detalhamento": "HIGH|MEDIUM|LOW", "impacto_orcamentario": true,
        "condicionantes": [{"tipo": "FISCAL", "texto": "...", "regra_id": "cf-165"}],
        "observacao": "..."}]}

A ficha gera: `propostas`, `proposta_temas`, `afirmacoes` (tipo PROPOSAL), `afirmacao_fontes`
(com trecho e página) e `condicionantes`, todas em estado/, com identificadores `pr-...`.
Propostas que saem da ficha saem também das tabelas.

    python3 coletor/fichas.py
"""
import glob, json, os, re, sys, unicodedata
from datetime import datetime, timezone

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import repositorio  # noqa: E402

TABELAS = ('propostas', 'proposta_temas', 'afirmacoes', 'afirmacao_fontes', 'condicionantes')


def slug(s):
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def normalizar(ficha, banco):
    cand = banco.por_id('candidaturas').get(ficha['candidatura_id'])
    if not cand:
        raise ValueError(f'candidatura {ficha["candidatura_id"]} inexistente')
    base = 'pr-' + ficha['candidatura_id'].replace('tse-', '')
    out = {t: [] for t in TABELAS}
    vistos = set()
    for p in ficha['propostas']:
        if p['id'] in vistos:
            raise ValueError(f'{base}: proposta {p["id"]} repetida na ficha')
        vistos.add(p['id'])
        pid = f'{base}-{slug(p["id"])}'
        out['propostas'].append({
            'id': pid, 'candidatura_id': cand['id'], 'titulo': p['titulo'], 'descricao': p['resumo'], 'subtema': p.get('subtema'),
            'materia_id': p.get('materia'), 'natureza_medida': p.get('natureza') or 'UNSPECIFIED',
            'nivel_detalhamento': p.get('detalhamento'), 'impacto_orcamentario': p.get('impacto_orcamentario'),
            'observacao': p.get('observacao'), 'status_revisao': 'AUTO_GENERATED',
            'verificado_em': p.get('verificado_em') or ficha.get('verificado_em'), 'origem_dado': 'CURATED'})
        for i, t in enumerate([p['tema']] + list(p.get('temas_extras') or [])):
            out['proposta_temas'].append({'id': f'{pid}--{t}', 'proposta_id': pid, 'tema_id': t, 'principal': i == 0, 'origem_dado': 'CURATED'})
        aid = f'{pid}--af'
        out['afirmacoes'].append({'id': aid, 'candidatura_id': cand['id'], 'proposta_id': pid, 'tipo': 'PROPOSAL', 'texto': p['resumo'],
                                  'data_evento': p.get('data') or ficha.get('data'), 'confianca': 'HIGH' if p.get('trecho') else 'MEDIUM',
                                  'status_revisao': 'AUTO_GENERATED', 'origem_dado': 'CURATED'})
        loc = p.get('localizador') or (f'p. {p["pagina"]}' if p.get('pagina') else None)
        fontes = [{'fonte_id': p.get('fonte_id') or ficha['fonte_id'], 'localizador': loc, 'trecho': p.get('trecho'), 'relacao': 'SUPPORTS'}]
        fontes += list(p.get('outras_fontes') or [])
        for j, f in enumerate(fontes, 1):
            out['afirmacao_fontes'].append({'id': f'{aid}--{j}', 'afirmacao_id': aid, 'fonte_id': f['fonte_id'], 'relacao': f.get('relacao') or 'SUPPORTS',
                                            'localizador': f.get('localizador'), 'trecho': f.get('trecho'), 'origem_dado': 'CURATED'})
        for j, c in enumerate(p.get('condicionantes') or [], 1):
            out['condicionantes'].append({'id': f'{pid}--c{j}', 'proposta_id': pid, 'tipo': c['tipo'], 'texto': c['texto'],
                                          'regra_id': c.get('regra_id'), 'origem_dado': 'CURATED'})
    return out


def processar(raiz=repositorio.RAIZ, agora=None):
    agora = agora or datetime.now(timezone.utc).isoformat(timespec='seconds')
    banco = repositorio.carregar(raiz)
    novos = {t: [] for t in TABELAS}
    erros = []
    for cam in sorted(glob.glob(os.path.join(raiz, 'conteudo', 'fichas', '*.json'))):
        try:
            r = normalizar(json.load(open(cam, encoding='utf-8')), banco)
        except (ValueError, KeyError) as e:
            erros.append(f'{os.path.basename(cam)}: {e}'); continue
        for t in TABELAS:
            novos[t].extend(r[t])
    cont = {}
    for t in TABELAS:
        ids = {x['id'] for x in novos[t]}
        c, _ = banco.sincronizar(t, novos[t], agora)
        # registros de fichas removidas deixam de existir (são derivados das fichas)
        banco.tabelas[t] = [x for x in banco.tabelas[t] if not (x['_origem'] == 'estado' and x['id'].startswith('pr-') and x['id'] not in ids)]
        cont[t] = {k: c[k] for k in ('created', 'updated', 'unchanged')}
    e, _ = banco.validar()
    erros += [x for x in e if x.split('.')[0] in TABELAS]
    if not erros:
        for t in TABELAS:
            banco.gravar(t)
    return {'erros': erros[:30], 'contagens': cont, 'propostas': len(novos['propostas'])}


if __name__ == '__main__':
    r = processar()
    print(json.dumps(r, ensure_ascii=False, indent=1))
    sys.exit(1 if r['erros'] else 0)
