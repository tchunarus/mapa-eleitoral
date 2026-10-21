# Rodada de reforço de fontes (21/10/2026). Complementa ESPEC.md, cujas regras valem integralmente.

Objetivo: ampliar a pluralidade de fontes da base, sobretudo com veículos de referência hoje ausentes,
sem alterar o que já foi apurado. A base está em
/Users/carolinaguedespinto/Desktop/mapa-eleitoral/conteudo/segundo_turno/evidencias.json (campos id, candidato,
criterio, afirmacao, data_fato, fontes, peso_probatorio).

Tarefa 1, reforço: para as evidências dos critérios da sua frente, priorizando peso_probatorio ALTO e MEDIO e
temas mais relevantes, procure reportagem dos veículos indicados no seu pedido que trate do MESMO fato.
- Se a reportagem confirma o fato: registre em "reforcos" com "confirma": true.
- Se diverge (números, datas, estágio processual, contexto): registre com "confirma": false e explique em "nota".
- Não registre reportagem que apenas mencione o tema sem tratar do fato.
- Veículos com paywall: vale o que estiver visível na página ou no resultado de busca; anote em "nota" se só viu o
  resumo. Nunca deduza o conteúdo de um texto que não leu.
- Mesmo esforço para os dois candidatos: mire em 15 a 25 reforços por candidato.

Tarefa 2, evidências novas (opcional): só se a reportagem trouxer fato relevante ainda ausente na base. Use ids
"reforco-<frente>-<candidato>-<nn>" e o formato normal de evidência.

Formato de saída (JSON, UTF-8, sem travessão), no caminho indicado no pedido:
{"frente": "...",
 "reforcos": [{"evidencia_id": "<id existente>", "confirma": true|false, "nota": "<1 frase; obrigatória se confirma=false>",
               "fonte": {"titulo": "...", "veiculo": "...", "url": "https://...", "data": "AAAA-MM-DD", "tipo_fonte": "JORNALISTICA"}}],
 "evidencias": [],
 "lacunas": []}
Valide com python3 -m json.tool. Responda ao final com resumo de 5 linhas, incluindo quantos reforços por candidato e por veículo.
