"""Importa o texto extraído das propostas de governo para .cache/planos/ (fora do repositório).

O texto é extraído no navegador, com pdf.js, a partir do documento oficial publicado pelo
TSE (/divulga/rest/arquivo/doc/<idArquivo>), e exportado como lista de objetos
{id, url, http, bytes, sha256, capturado_em, paginas: [texto da página 1, ...]}.
O texto completo fica só no cache local, como material de trabalho; o que se publica
são as propostas extraídas, com trecho curto e página (conteudo/afirmacao_fontes.json).

    python3 coletor/tse/importar_planos.py <arquivo exportado>
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importar_captura import ler_captura  # noqa: E402
import cliente  # noqa: E402

PASTA = os.path.join(cliente.RAIZ, '.cache', 'planos')


def importar(caminho):
    dados = ler_captura(caminho)
    os.makedirs(PASTA, exist_ok=True)
    feitos = []
    for p in dados if isinstance(dados, list) else [dados]:
        with open(os.path.join(PASTA, f'{p["id"]}.json'), 'w', encoding='utf-8') as f:
            json.dump(p, f, ensure_ascii=False, indent=1)
        feitos.append((p['id'], len(p['paginas'])))
    return feitos


if __name__ == '__main__':
    print(importar(sys.argv[1]))
