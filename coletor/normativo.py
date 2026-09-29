"""Texto vigente dos dispositivos citados como fundamento jurídico.

O Mapa Eleitoral não mantém base normativa nem extrator de legislação próprios. O texto
vigente vem da publicação aberta do Mapa Normativo (projeto separado, que extrai a
compilação oficial do Planalto e confere cada artigo por hash):

    https://tchunarus.github.io/mapa-normativo/data/diplomas/<diploma>.json

`sincronizar()` baixa esse arquivo e guarda em estado/normativo/<diploma>.json só os
artigos citados em conteudo/regras.json, com a URL, a data da captura, o SHA-256 da
resposta e a data da última conferência feita pelo Mapa Normativo. A partir daí tudo
roda sem rede:

- confere que o dispositivo existe, não foi revogado e contém o localizador
  ("III", "§ 1º", "§ 2º, I", "III, b");
- publica o trecho vigente correspondente (nunca escrito de memória);
- grava na análise o hash do artigo, para acusar quando o texto mudar depois dela.

Cada fundamento também leva o link para o artigo no site do Mapa Normativo.

    python3 coletor/normativo.py
"""
import hashlib, json, os, re, subprocess, sys
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIPLOMAS = os.path.join(RAIZ, 'estado', 'normativo')
SITE_MAPA_NORMATIVO = 'https://tchunarus.github.io/mapa-normativo/'
FONTE = SITE_MAPA_NORMATIVO + 'data/diplomas/{id}.json'
ROMANO = re.compile(r'^[IVXLCDM]+$')
_cache = {}


def url_artigo(dispositivo):
    return f'{SITE_MAPA_NORMATIVO}#d.{dispositivo}'


def diploma(did, pasta=DIPLOMAS):
    chave = (pasta, did)
    if chave not in _cache:
        cam = os.path.join(pasta, did + '.json')
        _cache[chave] = json.load(open(cam, encoding='utf-8')) if os.path.exists(cam) else None
    return _cache[chave]


def artigo(dispositivo, pasta=DIPLOMAS):
    did, _, num = dispositivo.partition('.')
    d = diploma(did, pasta)
    return (d, d['artigos'].get(num)) if d else (None, None)


def sincronizar(regras, pasta=DIPLOMAS, obter=None):
    """Atualiza os snapshots dos diplomas citados. Devolve {diploma: resultado}."""
    obter = obter or _baixar
    por_diploma = {}
    for r in regras:
        if r.get('dispositivo') and not r.get('fora_da_base'):
            did, _, num = r['dispositivo'].partition('.')
            por_diploma.setdefault(did, set()).add(num)
    out = {}
    for did, nums in sorted(por_diploma.items()):
        url = FONTE.format(id=did)
        bruto = obter(url)
        if bruto is None:
            out[did] = 'falha na leitura; mantido o snapshot anterior'; continue
        try:
            d = json.loads(bruto.decode('utf-8'))
        except ValueError:
            out[did] = 'resposta inválida; mantido o snapshot anterior'; continue
        artigos = {n: d['artigos'][n] for n in sorted(nums) if n in d.get('artigos', {})}
        faltam = sorted(nums - set(artigos))
        snap = {k: d.get(k) for k in ('id', 'sigla', 'nome', 'norma', 'url', 'urn', 'verificado_em', 'fonte')}
        snap.update({'fonte_dados': url, 'capturado_em': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                     'sha256': hashlib.sha256(bruto).hexdigest(), 'artigos': artigos})
        anterior = diploma(did, pasta)
        if anterior and anterior.get('artigos') == artigos and anterior.get('verificado_em') == snap['verificado_em']:
            out[did] = 'sem alteração'; continue
        os.makedirs(pasta, exist_ok=True)
        with open(os.path.join(pasta, did + '.json'), 'w', encoding='utf-8') as f:
            json.dump(snap, f, ensure_ascii=False, indent=1)
            f.write('\n')
        _cache.pop((pasta, did), None)
        out[did] = 'atualizado' + (f'; artigos ausentes na fonte: {", ".join(faltam)}' if faltam else '')
    return out


def _baixar(url):
    r = subprocess.run(['curl', '-sSL', '--fail', '--max-time', '90', '-A', 'Mozilla/5.0', url], capture_output=True)
    return r.stdout if r.returncode == 0 and r.stdout else None


def _norm(s):
    return re.sub(r'\s+', ' ', s.replace('\xa0', ' ')).strip()


def _nivel(linha):
    """Nível estrutural de uma linha do artigo: 'par', 'inc', 'ali' ou None."""
    t = _norm(linha)
    if t.startswith('§') or t.lower().startswith('parágrafo único'):
        return 'par'
    if re.match(r'^[IVXLCDM]+\s*(?:[-–.]|\s)', t):
        return 'inc'
    if re.match(r'^[a-z]\)', t):
        return 'ali'
    return None


def _casa(linha, parte):
    t = _norm(linha)
    p = _norm(parte)
    if p.lower() == 'parágrafo único':
        return t.lower().startswith('parágrafo único')
    if p.startswith('§'):
        num = re.sub(r'[^\dA-Z-]', '', p[1:].replace('º', '').replace('°', ''))
        m = re.match(r'^§\s*(\d+(?:-[A-Z])?)\s*[º°o]?', t)
        return bool(m) and m.group(1) == num
    if ROMANO.match(p):
        return bool(re.match(r'^' + p + r'(?:\s*[-–.]|\s)', t))
    if re.match(r'^[a-z]$', p):
        return t.startswith(p + ')')
    return False


def localizar(art, localizador):
    """Índices das linhas do artigo que correspondem ao localizador, ou None.

    "caput" ou vazio devolve a primeira linha. Cada parte procura a partir da anterior e
    não atravessa um marcador de nível igual ou superior ao da parte anterior."""
    linhas = [l[0] for l in art['l']]
    if not localizador or localizador.strip().lower() == 'caput':
        return [0]
    partes = [p.strip() for p in localizador.split(',') if p.strip()]
    ordem = {'par': 0, 'inc': 1, 'ali': 2}
    ini, limite_nivel, achado = 1, None, None
    for p in partes:
        nivel_p = 'par' if (p.startswith('§') or p.lower() == 'parágrafo único') else 'inc' if ROMANO.match(p) else 'ali'
        achado = None
        for i in range(ini, len(linhas)):
            n = _nivel(linhas[i])
            if n == nivel_p and _casa(linhas[i], p):
                achado = i; break
            if limite_nivel is not None and n is not None and ordem[n] <= ordem[limite_nivel]:
                break  # saiu do parágrafo ou inciso da parte anterior
        if achado is None:
            return None
        ini, limite_nivel = achado + 1, nivel_p
    # o trecho vai da linha achada até o próximo marcador de nível igual ou superior
    fim = achado + 1
    while fim < len(linhas):
        n = _nivel(linhas[fim])
        if n is not None and ordem[n] <= ordem[limite_nivel]:
            break
        fim += 1
    return list(range(achado, fim))


def conferir_regra(r, pasta=DIPLOMAS):
    """Confere uma regra contra o texto vigente. Devolve (erros, informações publicáveis)."""
    if r.get('fora_da_base'):
        return [], {'fora_da_base': True}
    d, a = artigo(r['dispositivo'], pasta)
    if d is None:
        return [f'regras.{r["id"]}: sem texto vigente de "{r["dispositivo"].split(".")[0]}" em estado/normativo/; rode python3 coletor/normativo.py'], {}
    if a is None:
        return [f'regras.{r["id"]}: dispositivo {r["dispositivo"]} ausente do texto vigente; rode python3 coletor/normativo.py'], {}
    if r['diploma_id'] != d['id']:
        return [f'regras.{r["id"]}: diploma_id "{r["diploma_id"]}" não confere com o dispositivo {r["dispositivo"]}'], {}
    erros = []
    if a.get('rev'):
        erros.append(f'regras.{r["id"]}: {r["dispositivo"]} está revogado na compilação oficial')
    idx = localizar(a, r.get('localizador'))
    if idx is None:
        erros.append(f'regras.{r["id"]}: localizador "{r.get("localizador")}" não encontrado no texto vigente de {r["dispositivo"]}')
        idx = []
    info = {'hash': a['hash'], 'rotulo_artigo': a['r'], 'diploma': d['sigla'], 'diploma_nome': d['nome'],
            'url_oficial': d['url'], 'verificado_em': d.get('verificado_em'), 'url_mapa_normativo': url_artigo(r['dispositivo']),
            'trecho_vigente': [a['l'][i][0] for i in idx][:12], 'caput': a['l'][0][0] if a['l'] else ''}
    return erros, info


def conferir_todas(regras, pasta=DIPLOMAS):
    erros, info = [], {}
    for r in regras:
        e, i = conferir_regra(r, pasta)
        erros.extend(e)
        info[r['id']] = i
    return erros, info


if __name__ == '__main__':
    regras = json.load(open(os.path.join(RAIZ, 'conteudo', 'regras.json'), encoding='utf-8'))
    print(json.dumps(sincronizar(regras), ensure_ascii=False))
    erros, _ = conferir_todas(regras)
    print(json.dumps({'erros': erros}, ensure_ascii=False))
    sys.exit(1 if erros else 0)
