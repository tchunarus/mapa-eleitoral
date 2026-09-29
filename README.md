# Mapa Eleitoral

Ferramenta do Guedes Pinto Advogados que responde, para cada proposta de candidatura:
o que o candidato propôs, se o cargo disputado tem competência para realizar a medida e,
se não puder fazê-lo sozinho, de quem depende. Site estático (`docs/`, GitHub Pages).

Projeto independente do Mapa Normativo. A única ligação é de fonte: o texto vigente dos
artigos citados como fundamento vem da publicação aberta do Mapa Normativo
(`coletor/normativo.py`), guardado em snapshot com data e hash, e cada fundamento leva
link para o artigo no site do Mapa Normativo.

## Como funciona

```
ingestão (TSE, Senado, texto vigente) -> normalização -> análise por regras -> validação -> publicação -> página
```

A página não consulta o TSE nem faz análise jurídica: lê os arquivos de `docs/data/`.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `coletor/esquema.py` | Esquema das tabelas: campos, enumerações, chaves, unicidade |
| `coletor/repositorio.py` | Carga, validação de integridade e gravação (faz as vezes de banco) |
| `coletor/migrar.py` | Migrações do esquema (versão em `estado/_esquema.json`) |
| `coletor/tse/` | Integração com o TSE: cliente, parser, normalizador, sincronização, importação de captura |
| `coletor/legislativo.py` | Vagas do Senado em disputa (dados abertos do Senado) |
| `coletor/normativo.py` | Texto vigente dos fundamentos e conferência de dispositivo e localizador |
| `coletor/analise/` | Interface do analisador, `AnalisadorPorRegras`, revisão humana, `AnalisadorLLM` (previsto) |
| `coletor/analisar.py`, `publicar.py`, `paginar.py`, `atualizar.py` | Análise, publicação, montagem da página e rotina completa |
| `coletor/entes.py` | Estados e Municípios acompanhados |
| `conteudo/` | Conteúdo curado: cargos, instituições, competências, fundamentos, instrumentos, temas, propostas, revisões |
| `conteudo/fixtures/` | Dados fictícios de demonstração (DEVELOPMENT_FIXTURE), isolados dos reais |
| `estado/` | Dados gerados: candidaturas, snapshots do TSE, texto vigente, análises, log de ingestão |
| `web/` | Peças da página (casca, estilos, filtros, páginas) |
| `testes/` | Testes em Python (`unittest`) e JavaScript (`node:test`) |

## Comandos

```
python3 coletor/atualizar.py                               # rotina completa (com rede)
python3 coletor/atualizar.py --sem-rede                    # só análise, publicação e página
python3 coletor/tse/sincronizar.py --transporte snapshot   # reprocessa os snapshots do TSE sem rede
python3 coletor/tse/importar_captura.py <arquivo>          # importa captura da API do TSE feita no navegador
python3 coletor/repositorio.py                             # valida a integridade
python3 -m unittest discover -s testes && node --test testes/js/
python3 serve.py                                           # http://127.0.0.1:8766
```

Os textos legais são reprodução das fontes oficiais. As análises são automatizadas,
indicam o status de revisão e não constituem parecer jurídico.
