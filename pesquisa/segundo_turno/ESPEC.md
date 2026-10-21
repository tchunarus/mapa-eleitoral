# Especificação comum da pesquisa: Mapa Eleitoral, 2º turno presidencial 2026

Contexto confirmado: o TSE informou que Flávio Bolsonaro (PL, nº 22) e Luiz Inácio Lula da Silva (PT, nº 13)
disputam o 2º turno em 25/10/2026 (1º turno em 04/10/2026: Flávio 47,03%, Lula 45,16% dos válidos).
Fonte: https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/flavio-bolsonaro-e-lula-vao-disputar-o-2o-turno-para-a-presidencia-da-republica
Data de hoje: 19/10/2026.

## Regras inegociáveis
1. NUNCA inventar fato, número, data, URL, citação, número de processo ou decisão. Só registre o que você
   encontrou numa fonte que de fato abriu (WebFetch) ou cujo resultado de busca mostra claramente a informação.
   Se não conseguir confirmar, não registre, ou registre com tipo "INCONCLUSIVO" explicando a lacuna.
2. Simetria: aplique exatamente o mesmo roteiro de perguntas aos dois candidatos. Para cada pergunta, procure
   evidências favoráveis E desfavoráveis para cada um. Não force equivalência: se um tem mais ou menos
   evidência, isso deve aparecer; registre também quando a busca não encontrou nada (campo "lacunas").
3. Pluralidade: para temas controversos, confronte veículos de linhas editoriais diferentes (ex.: Folha, Estadão,
   O Globo, Valor, CNN Brasil, Gazeta do Povo, Revista Oeste, CartaCapital, Poder360, Metrópoles, BBC Brasil,
   Reuters, AFP, Bloomberg, Financial Times, The Economist, El País). Prefira fontes primárias: TSE, STF, STJ,
   Câmara, Senado, Portal da Transparência, IBGE, Banco Central, Tesouro, IPEA, Diário Oficial, planos de governo.
4. Diferencie rigorosamente: FATO_COMPROVADO, DADO_OFICIAL, DECISAO_JUDICIAL_DEFINITIVA (transitada em julgado),
   DECISAO_JUDICIAL_NAO_DEFINITIVA, INVESTIGACAO_OU_DENUNCIA (sem decisão), ALEGACAO, INTERPRETACAO (jornalística
   ou acadêmica), OPINIAO, PROMESSA. Em matéria judicial, indique sempre o estágio atual (arquivado, anulado,
   absolvido, condenado, em curso) e quem decidiu. Presunção de inocência: investigação não é culpa.
5. Escreva as afirmações com suas próprias palavras, em português formal, tom técnico e não partidário.
   Citações literais só curtas (até 25 palavras), entre aspas, e somente se copiadas da fonte.
   Proibido usar travessão (—). Use vírgulas ou parênteses.
6. Toda evidência leva pelo menos uma fonte com URL direta e data de publicação (ou de atualização / acesso).
   Data no formato AAAA-MM-DD; se só souber o mês, AAAA-MM.
7. Nada de juízo de "melhor/pior". Você coleta e classifica evidências; a nota é atribuída depois.

## Critérios (use exatamente estes ids)
- experiencia: Competência administrativa e experiência política
- economia_fiscal: Resultados econômicos e responsabilidade fiscal
- propostas: Qualidade, viabilidade e consistência das propostas
- integridade: Integridade, transparência e histórico institucional
- democracia: Compromisso com a Constituição, as instituições democráticas e o Estado de Direito
- governabilidade: Capacidade de articulação política e governabilidade
- impactos: Impactos sociais, econômicos e ambientais das políticas defendidas
- coerencia: Coerência entre discurso, histórico e atuação concreta

## Formato de saída: um arquivo JSON (UTF-8) no caminho indicado no seu pedido
{
 "frente": "<nome da frente>",
 "evidencias": [
  {"id": "<frente>-<candidato>-<nn>",
   "candidato": "lula" | "flavio",
   "criterio": "<id do critério>",
   "tema": "<subtema curto, ex.: inflação, rachadinha, PEC da Transição>",
   "tipo": "<uma das categorias da regra 4>",
   "sentido": "FAVORAVEL" | "DESFAVORAVEL" | "MISTO" | "CONTEXTO",
   "peso_probatorio": "ALTO" | "MEDIO" | "BAIXO",   // ALTO = fonte primária ou dado oficial ou decisão; BAIXO = alegação isolada
   "afirmacao": "<1 a 3 frases, objetivas>",
   "data_fato": "AAAA-MM-DD",
   "fontes": [{"titulo": "...", "veiculo": "...", "url": "https://...", "data": "AAAA-MM-DD",
               "tipo_fonte": "PRIMARIA" | "JORNALISTICA" | "CHECAGEM" | "ACADEMICA" | "CAMPANHA"}],
   "contraponto": "<o que a outra parte, a defesa ou outro veículo diz, se houver>",
   "limitacoes": "<o que a evidência não prova>"}
 ],
 "linha_do_tempo": [ {"candidato": "lula|flavio|ambos", "data": "AAAA-MM-DD", "titulo": "...", "descricao": "...",
                      "categoria": "cargo|eleicao|judicial|governo|legislativo|campanha", "fontes": [ ... ]} ],
 "lacunas": ["<pergunta do roteiro sem resposta confiável, por candidato>"]
}
Valide o JSON (python3 -m json.tool) antes de terminar. Mire em qualidade: cerca de 12 a 25 evidências por
candidato na sua frente, cada uma realmente sustentada. Ao final, responda apenas com um resumo de 5 linhas e
o caminho do arquivo.
