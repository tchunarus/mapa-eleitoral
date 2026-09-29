# Mapa Eleitoral

Ferramenta do Guedes Pinto Advogados sobre cargos, candidaturas, propostas e competência
de cada cargo, publicada como site estático (`docs/`). Estrutura e comandos no `README.md`.

## Separação do Mapa Normativo

- Projeto independente do Mapa Normativo (`~/Desktop/mapa-normativo`). Não alterar
  aquele repositório a partir daqui nem importar código dele.
- A única dependência é de fonte: `coletor/normativo.py` lê a publicação aberta do Mapa
  Normativo para obter o texto vigente dos artigos citados e o guarda em `estado/normativo/`.

## Fontes e dados

- Prioridade para fontes oficiais e primárias (TSE, Senado, Câmara, Planalto). Toda
  informação factual leva fonte (tabela `fontes`, ligada por `afirmacoes`/`afirmacao_fontes`).
- Nunca atribuir proposta a candidatura real sem fonte que a sustente; proposta sem fonte
  não é publicada.
- Nunca reproduzir texto legal de memória. Fundamento jurídico é sempre uma entrada de
  `conteudo/regras.json`, conferida contra o texto vigente (dispositivo e localizador).
  Norma sem texto conferido entra como `fora_da_base`.
- O TSE recusa requisições diretas por script (HTTP 403 em 29/09/2026). Não contornar
  bloqueios nem políticas de segurança de sites; a alternativa documentada é a captura
  pela API pública num navegador (`coletor/tse/importar_captura.py`).
- Dados pessoais do TSE: só os campos da lista branca de `coletor/tse/cliente.py` (nunca
  CPF, título de eleitor, data de nascimento, cor ou raça, estado civil, bens).
- Dados fictícios só em `conteudo/fixtures/`; o validador recusa cruzamento com dado real.
- Neutralidade: sem recomendação de voto, ranking, classificação ideológica ou previsão.

## Dados gerados

`docs/` e `estado/` só mudam pelos scripts de `coletor/` (hook bloqueia edição manual).
Depois de mudar `conteudo/`, `coletor/` ou `web/`, rodar `python3 coletor/atualizar.py --sem-rede`.

## Redação

- Português formal, com acentuação correta. Sem travessões (em dash); usar vírgulas ou
  parênteses. Meia-risca é permitida.
- Nunca chamar o escritório de "GPA": usar "escritório", "Guedes Pinto" ou
  "Guedes Pinto Advogados".

## Git e credenciais

- Execução local: preparar o commit; a usuária roda `git push`. Nunca usar credencial,
  token ou keychain deste computador.
- Código compatível com Python 3.9, só com a biblioteca padrão.
