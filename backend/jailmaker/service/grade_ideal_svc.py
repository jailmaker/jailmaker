from ortools.sat.python import cp_model

from jailmaker.constants import CURRICULO_CCOMP, PREREQUISITOS_MAP


class GeradorGradeIdeal:
    """
    Classe responsável por montar grades horárias ideais para estudantes
    baseadas em seus históricos e na matriz horária disponível.
    """

    def __init__(self, matriz_horaria: list[dict], historico_academico: list[dict]):
        """
        Inicializa o GeradorGradeIdeal com a matriz horária disponível e o histórico do estudante.

        Args:
            matriz_horaria: Lista de dicionários contendo as disciplinas disponíveis
            historico_academico: Lista de dicionários contendo as disciplinas já cursadas pelo estudante
        """
        self.matriz_horaria = matriz_horaria
        self.historico_academico = historico_academico
        self._disciplinas_feitas: set[str] = set()
        self._disciplinas_disponiveis: list[dict] = []
        self._disciplinas_indisponiveis: set[str] = set()

    def gerar(self) -> list[dict]:
        """
        Monta a grade ideal baseada no histórico do estudante e na matriz horária atual.

        Returns:
            Lista de disciplinas que compõem a grade ideal
        """
        self._filtrar_disciplinas_disponiveis()

        if not self._disciplinas_disponiveis:
            return []

        self._processar_historico()

        model = cp_model.CpModel()
        disciplina_vars = self._criar_variaveis_disciplinas(model)

        self._aplicar_restricao_disciplinas_indisponiveis(model, disciplina_vars)
        self._aplicar_restricao_pre_requisitos(model, disciplina_vars)
        self._aplicar_restricao_conflitos(model, disciplina_vars)
        self._aplicar_restricao_mesma_disciplina(model, disciplina_vars)

        # Objetivo: maximizar a quantidade de disciplinas
        model.Maximize(sum(disciplina_vars.values()))

        # Roda a otimização do modelo
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # Processa resultados
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return [
                disciplina
                for disciplina in self._disciplinas_disponiveis
                if solver.Value(disciplina_vars[f"{disciplina['nome']}_{disciplina['professor']}"]) == 1
            ]
        return []

    def _filtrar_disciplinas_disponiveis(self) -> None:
        """Filtra as disciplinas disponíveis conforme o currículo de Ciência da Computação."""
        self._disciplinas_disponiveis = [
            disciplina for disciplina in self.matriz_horaria if disciplina["nome"] in CURRICULO_CCOMP
        ]

    def _processar_historico(self) -> None:
        """Processa o histórico do estudante para identificar disciplinas feitas e em andamento."""
        for disciplina in self.historico_academico:
            if disciplina["situacao"] == "APROVADO":
                self._disciplinas_feitas.add(disciplina["nome"])
                self._disciplinas_indisponiveis.add(disciplina["nome"])
            elif disciplina["situacao"] == "EM CURSO":
                self._disciplinas_indisponiveis.add(disciplina["nome"])

    def _criar_variaveis_disciplinas(self, model: cp_model.CpModel) -> dict[str, cp_model.IntVar]:
        """
        Cria variáveis booleanas para cada disciplina no modelo.

        Args:
            model: O modelo de programação por restrições

        Returns:
            Dicionário mapeando chaves de disciplinas para variáveis do modelo
        """
        disciplina_vars = {}
        for disciplina in self._disciplinas_disponiveis:
            chave = f"{disciplina['nome']}_{disciplina['professor']}"
            disciplina_vars[chave] = model.NewBoolVar(chave)
        return disciplina_vars

    def _aplicar_restricao_disciplinas_indisponiveis(
        self, model: cp_model.CpModel, disciplina_vars: dict[str, cp_model.IntVar]
    ) -> None:
        """
        Aplica restrição para não escolher disciplinas já concluídas ou em progresso.

        Args:
            model: O modelo de programação por restrições
            disciplina_vars: Dicionário com as variáveis de decisão
        """
        for disciplina in self._disciplinas_disponiveis:
            chave = f"{disciplina['nome']}_{disciplina['professor']}"
            if disciplina["nome"] in self._disciplinas_indisponiveis:
                model.Add(disciplina_vars[chave] == 0)

    def _aplicar_restricao_pre_requisitos(
        self, model: cp_model.CpModel, disciplina_vars: dict[str, cp_model.IntVar]
    ) -> None:
        """
        Aplica restrição para garantir que os pré-requisitos foram cumpridos.

        Args:
            model: O modelo de programação por restrições
            disciplina_vars: Dicionário com as variáveis de decisão
        """
        for disciplina in self._disciplinas_disponiveis:
            chave = f"{disciplina['nome']}_{disciplina['professor']}"
            if disciplina["nome"] in PREREQUISITOS_MAP:
                prereqs = PREREQUISITOS_MAP[disciplina["nome"]]
                if not all(prereq in self._disciplinas_feitas for prereq in prereqs):
                    model.Add(disciplina_vars[chave] == 0)

    def _aplicar_restricao_conflitos(
        self, model: cp_model.CpModel, disciplina_vars: dict[str, cp_model.IntVar]
    ) -> None:
        """
        Aplica restrição para evitar conflitos de dia ou horário entre disciplinas.

        Args:
            model: O modelo de programação por restrições
            disciplina_vars: Dicionário com as variáveis de decisão
        """
        for i, disciplina1 in enumerate(self._disciplinas_disponiveis):
            for j, disciplina2 in enumerate(self._disciplinas_disponiveis):
                if i < j and self._tem_conflito_de_dia_ou_horario(disciplina1, disciplina2):
                    chave1 = f"{disciplina1['nome']}_{disciplina1['professor']}"
                    chave2 = f"{disciplina2['nome']}_{disciplina2['professor']}"
                    model.Add(disciplina_vars[chave1] + disciplina_vars[chave2] <= 1)

    def _aplicar_restricao_mesma_disciplina(
        self, model: cp_model.CpModel, disciplina_vars: dict[str, cp_model.IntVar]
    ) -> None:
        """
        Aplica restrição para não escolher a mesma disciplina com professores diferentes.

        Args:
            model: O modelo de programação por restrições
            disciplina_vars: Dicionário com as variáveis de decisão
        """
        nome_para_disciplinas: dict[str, list[dict]] = {}
        for disciplina in self._disciplinas_disponiveis:
            if disciplina["nome"] not in nome_para_disciplinas:
                nome_para_disciplinas[disciplina["nome"]] = []
            nome_para_disciplinas[disciplina["nome"]].append(disciplina)

        for _nome, disciplinas in nome_para_disciplinas.items():
            if len(disciplinas) > 1:
                model.Add(
                    sum(
                        disciplina_vars[f"{disciplina['nome']}_{disciplina['professor']}"] for disciplina in disciplinas
                    )
                    <= 1
                )

    @staticmethod
    def _tem_conflito_de_dia_ou_horario(disciplina1: dict, disciplina2: dict) -> bool:
        """
        Verifica se duas disciplinas possuem conflito de dia ou horário.

        Args:
            disciplina1: Primeira disciplina para verificação
            disciplina2: Segunda disciplina para verificação

        Returns:
            True se houver conflito, False caso contrário
        """
        dias_em_comum = set(disciplina1["dias"]).intersection(set(disciplina2["dias"]))
        if not dias_em_comum:
            return False

        for dia in dias_em_comum:
            dia_idx1 = disciplina1["dias"].index(dia)
            dia_idx2 = disciplina2["dias"].index(dia)

            horario1_start, horario1_end = disciplina1["horarios"][dia_idx1].split(" - ")
            horario2_start, horario2_end = disciplina2["horarios"][dia_idx2].split(" - ")

            horario1_start_min = GeradorGradeIdeal._horario_para_minutos(horario1_start)
            horario1_end_min = GeradorGradeIdeal._horario_para_minutos(horario1_end)
            horario2_start_min = GeradorGradeIdeal._horario_para_minutos(horario2_start)
            horario2_end_min = GeradorGradeIdeal._horario_para_minutos(horario2_end)

            if not (horario1_end_min <= horario2_start_min or horario2_end_min <= horario1_start_min):
                return True

        return False

    @staticmethod
    def _horario_para_minutos(horario_str: str) -> int:
        """
        Converte uma string de horário no formato "HHhMM" para minutos.

        Args:
            horario_str: String no formato "HHhMM" (ex: "14h30")

        Returns:
            Quantidade total de minutos
        """
        hora, minuto = map(int, horario_str.split("h"))
        return hora * 60 + minuto
