"""Monta docs/index.html a partir das peças versionadas em web/.

    python3 coletor/paginar.py

Peças: head.html (metatags), estilo_base.html (identidade visual do escritório),
estilo_eleitoral.html (componentes do Mapa Eleitoral), corpo.html (cabeçalho e rodapé,
com %%LOGO%% trocado pelo conteúdo de logo.txt), app.js (casca: rotas, abas, tema),
filtros.js (funções puras testadas em testes/js/) e eleitoral.js (páginas).
Não editar docs/index.html diretamente.
"""
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(RAIZ, 'web')
OUT = os.path.join(RAIZ, 'docs', 'index.html')
RESET = ('<style>:root{box-sizing:border-box}body{margin:0;padding:0;'
         'padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
         'img{max-width:100%}[hidden]{display:none!important}</style>')


def ler(nome):
    return open(os.path.join(WEB, nome), encoding='utf-8').read()


def montar():
    corpo = ler('corpo.html').replace('%%LOGO%%', ler('logo.txt').strip())
    scripts = ''.join(f'<script>\n{ler(n)}\n</script>\n' for n in ('filtros.js', 'app.js', 'eleitoral.js'))
    pagina = f"{ler('head.html')}\n{RESET}\n{ler('estilo_base.html')}\n{ler('estilo_eleitoral.html')}\n</head><body>\n{corpo}\n{scripts}</body></html>"
    if '\u2014' in pagina:
        raise SystemExit('Travessão encontrado na página montada; corrija antes de publicar.')
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(pagina)
    return len(pagina)


if __name__ == '__main__':
    print(f'docs/index.html montado ({montar()} bytes) a partir de web/')
