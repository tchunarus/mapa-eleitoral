"""Apoio à curadoria das fichas: extrai trechos literais dos planos capturados.

O texto de cada plano fica em .cache/planos/<id do documento>.json (páginas extraídas
com pdf.js ou por OCR). `trecho(doc, pagina, inicio, fim)` devolve o texto exato entre as
duas expressões, podendo atravessar para a página seguinte; se a expressão não for
encontrada, a extração falha, o que impede citar texto que não está na fonte.
"""
import json, os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANOS = os.path.join(RAIZ, '.cache', 'planos')
MAX = 400
_cache = {}


def _n(s):
    s = re.sub(r'-\n(?=[a-zà-ú])', '', s)  # hifenização de fim de linha
    return re.sub(r'\s+', ' ', s.replace('\xa0', ' ')).strip()


def plano(doc):
    if doc not in _cache:
        _cache[doc] = json.load(open(os.path.join(PLANOS, f'{doc}.json'), encoding='utf-8'))
    return _cache[doc]


def via_ocr(doc):
    return 'OCR' in (plano(doc).get('via') or '')


def trecho(doc, pagina, inicio, fim=None):
    pags = plano(doc)['paginas']
    texto = _n(' '.join(pags[pagina - 1:pagina + 1]))
    i = texto.find(_n(inicio))
    if i < 0:
        raise ValueError(f'{doc} p. {pagina}: início não encontrado: {inicio!r}')
    if fim:
        j = texto.find(_n(fim), i)
        if j < 0:
            raise ValueError(f'{doc} p. {pagina}: fim não encontrado: {fim!r}')
        t = texto[i:j + len(_n(fim))]
    else:
        t = texto[i:i + MAX]
    if len(t) > MAX:
        t = t[:MAX - 6].rsplit(' ', 1)[0].rstrip(',;:') + ' [...]'
    return t
