from ortools.sat.python import cp_model

from jailmaker.constants import CURRICULO_CCOMP, PREREQUISITOS_MAP


def monta_grade_ideal(matriz_horaria: list[dict], historico: list[dict]) -> list[dict]:
    """Monta a grade baseada no histórico do aluno e na matriz horária atual."""

    # considera apenas disciplinas do currículo de ciência da computação
    disciplinas_disponiveis = [disciplina for disciplina in matriz_horaria if disciplina["subject"] in CURRICULO_CCOMP]

    if not disciplinas_disponiveis:
        return []

    model = cp_model.CpModel()
    disciplina_vars = {}

    # cria uma variável para cada disciplina
    for disciplina in disciplinas_disponiveis:
        chave = f"{disciplina['subject']}_{disciplina['teacher']}"
        disciplina_vars[chave] = model.NewBoolVar(chave)

    # descarta disciplinas já feias ou em andamento
    disciplinas_indisponiveis = set()
    disciplinas_feitas = set()
    for disciplina in historico:
        if disciplina["situacao"] == "APROVADO":
            disciplinas_feitas.add(disciplina["nome"])
            disciplinas_indisponiveis.add(disciplina["nome"])
        elif disciplina["situacao"] == "EM CURSO":
            disciplinas_indisponiveis.add(disciplina["nome"])

    # adiciona restrições
    for disciplina in disciplinas_disponiveis:
        chave = f"{disciplina['subject']}_{disciplina['teacher']}"

        # restrição 1: não pode escolher disciplinas concluídas ou em progresso
        if disciplina["subject"] in disciplinas_indisponiveis:
            model.Add(disciplina_vars[chave] == 0)

        # restrição 2: as disciplinas pré-requisitadas já devem ter sido feitas
        if disciplina["subject"] in PREREQUISITOS_MAP:
            prereqs = PREREQUISITOS_MAP[disciplina["subject"]]
            if not all(prereq in disciplinas_feitas for prereq in prereqs):
                model.Add(disciplina_vars[chave] == 0)

    # restrição 3: não pode escolher disciplinas com conflitos de dia ou horário
    for i, disciplina1 in enumerate(disciplinas_disponiveis):
        for j, disciplina2 in enumerate(disciplinas_disponiveis):
            if i < j and _tem_conflito_de_dia_ou_horario(disciplina1, disciplina2):
                chave1 = f"{disciplina1['subject']}_{disciplina1['teacher']}"
                chave2 = f"{disciplina2['subject']}_{disciplina2['teacher']}"
                model.Add(disciplina_vars[chave1] + disciplina_vars[chave2] <= 1)

    # restrição 4: não pode escolhera mesma disciplinas para mais de um professor
    nome = {}
    for disciplina in disciplinas_disponiveis:
        if disciplina["subject"] not in nome:
            nome[disciplina["subject"]] = []
        nome[disciplina["subject"]].append(disciplina)

    for _nome, disciplinas in nome.items():
        if len(disciplinas) > 1:
            model.Add(
                sum(disciplina_vars[f"{disciplina['subject']}_{disciplina['teacher']}"] for disciplina in disciplinas)
                <= 1
            )

    # objetivo: maximizar a quantidade de disciplinas
    model.Maximize(sum(disciplina_vars.values()))

    # roda a otimização do modelo
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # processa resultados
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return [
            disciplina
            for disciplina in disciplinas_disponiveis
            if solver.Value(disciplina_vars[f"{disciplina['subject']}_{disciplina['teacher']}"]) == 1
        ]
    return []


def _tem_conflito_de_dia_ou_horario(disciplina1: dict, disciplina2: dict) -> bool:
    """Checa se duas disciplinas possuem conflito de dia ou horário."""
    dias_em_comum = set(disciplina1["day"]).intersection(set(disciplina2["day"]))
    if not dias_em_comum:
        return False

    def horario_em_minutos(time_str):
        hora, minuto = map(int, time_str.split("h"))
        return hora * 60 + minuto

    for dia in dias_em_comum:
        dia_idx1 = disciplina1["day"].index(dia)
        dia_idx2 = disciplina2["day"].index(dia)

        horario1_start, horaria1_end = disciplina1["schedule"][dia_idx1].split(" - ")
        horario2_start, horario2_end = disciplina2["schedule"][dia_idx2].split(" - ")

        horario1_start = horario_em_minutos(horario1_start)
        horaria1_end = horario_em_minutos(horaria1_end)
        horario2_start = horario_em_minutos(horario2_start)
        horario2_end = horario_em_minutos(horario2_end)

        if not (horaria1_end <= horario2_start or horario2_end <= horario1_start):
            return True

    return False
