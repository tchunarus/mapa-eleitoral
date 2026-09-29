"""Hook PreToolUse: impede edição manual dos dados gerados pelos scripts.

docs/ (dados publicados e página montada) e estado/ (candidaturas do TSE, snapshots,
texto vigente, análises e log de ingestão) só mudam pelos scripts de coletor/. Editar à
mão rompe a trilha de auditoria. Os scripts rodam pelo Bash e não passam por este hook.
"""
import json, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    evento = json.load(sys.stdin)
except ValueError:
    sys.exit(0)
caminho = (evento.get('tool_input') or {}).get('file_path') or ''
if not caminho:
    sys.exit(0)
rel = os.path.relpath(os.path.abspath(caminho), RAIZ).replace(os.sep, '/')
if rel.startswith(('docs/', 'estado/')):
    print('%s é gerado pelos scripts e não pode ser editado à mão. Altere conteudo/, coletor/ ou web/ '
          'e rode python3 coletor/atualizar.py --sem-rede.' % rel, file=sys.stderr)
    sys.exit(2)
