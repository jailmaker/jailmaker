CURRICULO_CCOMP = {
    "CÁLCULO EM UMA VARIÁVEL",
    "CIÊNCIA TECNOLOGIA E SOCIEDADE",
    "LÓGICA DE PROGRAMAÇÃO",
    "QUÍMICA GERAL",
    "FUNDAMENTOS DA BIOLOGIA MODERNA",
    "FENÔMENOS MECÂNICOS",
    "CIÊNCIA, TECNOLOGIA, SOCIEDADE E AMBIENTE",
    "SÉRIES E EQUAÇÕES DIFERENCIAIS",
    "MATEMÁTICA DISCRETA",
    "ALGORITMOS E ESTRUTURAS DE DADOS I",
    "GEOMETRIA ANALÍTICA",
    "PROBABILIDADE E ESTATÍSTICA",
    "CÁLCULO EM VÁRIAS VARIÁVEIS",
    "CIRCUITOS DIGITAIS",
    "ALGORITMOS E ESTRUTURAS DE DADOS II",
    "ÁLGEBRA LINEAR",
    "BANCO DE DADOS",
    "PROGRAMAÇÃO ORIENTADA A OBJETOS",
    "ARQUITETURA E ORGANIZAÇÃO DE COMPUTADORES",
    "PROJETO E ANÁLISE DE ALGORITMOS",
    "CÁLCULO NUMÉRICO",
    "INTELIGÊNCIA ARTIFICIAL",
    "PROJETO ORIENTADO A OBJETOS",
    "LINGUAGENS FORMAIS E AUTÔMATOS",
    "TEORIA DOS GRAFOS",
    "SISTEMAS OPERACIONAIS",
    "REDES DE COMPUTADORES",
    "ENGENHARIA DE SOFTWARE",
    "COMPUTAÇÃO GRÁFICA",
    "PROGRAMAÇÃO CONCORRENTE E DISTRIBUÍDA",
    "COMPILADORES",
    "INTERAÇÃO HUMANO-COMPUTADOR E EXPERIÊNCIA DO USUÁRIO",
}


PREREQUISITOS_MAP = {
    "ALGORITMOS E ESTRUTURAS DE DADOS I": ["LÓGICA DE PROGRAMAÇÃO"],
    "SÉRIES E EQUAÇÕES DIFERENCIAIS": ["CÁLCULO EM UMA VARIÁVEL"],
    "ALGORITMOS E ESTRUTURAS DE DADOS II": ["ALGORITMOS E ESTRUTURAS DE DADOS I"],
    "CÁLCULO EM VÁRIAS VARIÁVEIS": ["CÁLCULO EM UMA VARIÁVEL", "GEOMETRIA ANALÍTICA"],
    "PROBABILIDADE E ESTATÍSTICA": ["CÁLCULO EM UMA VARIÁVEL"],
    "CALCULO NUMÉRICO": ["CÁLCULO EM UMA VARIÁVEL", "GEOMETRIA ANALÍTICA"],
    "ÁLGEBRA LINEAR": ["GEOMETRIA ANALÍTICA"],
    "ARQUITETURA E ORGANIZAÇÃO DE COMPUTADORES": ["LÓGICA DE PROGRAMAÇÃO", "CIRCUITOS DIGITAIS"],
    "BANCO DE DADOS": ["ALGORITMOS E ESTRUTURAS DE DADOS I"],
    "PROGRAMAÇÃO ORIENTADA A OBJETOS": ["ALGORITMOS E ESTRUTURAS DE DADOS I"],
    "PROJETO E ANÁLISE DE ALGORITMOS": ["MATEMÁTICA DISCRETA", "ALGORITMOS E ESTRUTURAS DE DADOS II"],
    "LINGUAGENS FORMAIS E AUTÔMATOS": ["MATEMÁTICA DISCRETA", "LÓGICA DE PROGRAMAÇÃO"],
    "INTELIGÊNCIA ARTIFICIAL": ["ALGORITMOS E ESTRUTURAS DE DADOS I"],
    "INTERAÇÃO HUMANO-COMPUTADOR E EXPERIÊNCIA DO USUÁRIO": ["PROGRAMAÇÃO ORIENTADA A OBJETOS"],
    "PROJETO ORIENTADO A OBJETOS": ["PROGRAMAÇÃO ORIENTADA A OBJETOS"],
    "SISTEMAS OPERACIONAIS": ["ALGORITMOS E ESTRUTURAS DE DADOS I"],
    "TEORIA DOS GRAFOS": ["PROJETO E ANÁLISE DE ALGORITMOS"],
    "COMPILADORES": ["LINGUAGENS FORMAIS E AUTÔMATOS"],
    "COMPUTAÇÃO GRÁFICA": ["ALGORITMOS E ESTRUTURAS DE DADOS I"],
    "ENGENHARIA DE SOFTWARE": ["PROGRAMAÇÃO ORIENTADA A OBJETOS"],
    "PROGRAMAÇÃO CONCORRENTE E DISTRIBUÍDA": ["SISTEMAS OPERACIONAIS"],
    "REDES DE COMPUTADORES": ["SISTEMAS OPERACIONAIS"],
}
