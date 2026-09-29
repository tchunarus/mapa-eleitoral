"""Entes federativos acompanhados pelo Mapa Eleitoral (além da União, identificada por 'BR').

Chave no formato 'UF' para Estados e 'UF/Município' para Municípios.
"""

ENTES = {
  'SC': {'nome': 'Santa Catarina', 'tipo': 'estado', 'capital': 'SC/Florianópolis'},
  'SC/Florianópolis': {'nome': 'Florianópolis', 'tipo': 'municipio', 'uf': 'SC'},
  'SC/São José': {'nome': 'São José', 'tipo': 'municipio', 'uf': 'SC'},
}
