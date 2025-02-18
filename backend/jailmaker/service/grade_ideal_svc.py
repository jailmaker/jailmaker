import re

from ortools.sat.python import cp_model

from jailmaker.constants import CURRICULO_CCOMP, PREREQUISITOS_MAP


class GeradorGradeIdeal:
    """
    Classe responsável por montar grades horárias ideais para estudantes
    com base no histórico acadêmico e na matriz horária disponível.
    """

    def __init__(self, matriz_horaria: list[dict], historico_academico: list[dict]):
        """
        Inicializa o GeradorGradeIdeal com a matriz horária disponível e o histórico do estudante.

        Args:
            matriz_horaria: Lista de dicionários contendo as disciplinas disponíveis.
            historico_academico: Lista de dicionários contendo as disciplinas já cursadas pelo estudante.
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
            Lista de disciplinas que compõem a grade ideal.
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

        # Calcula quantas vezes cada disciplina é pré-requisito de outras disciplinas.
        frequencia_prereq = {}
        for prereqs in PREREQUISITOS_MAP.values():
            for prereq in prereqs:
                nome_normalizadoalizado = self._normalizar_nome(prereq)
                frequencia_prereq[nome_normalizadoalizado] = frequencia_prereq.get(nome_normalizadoalizado, 0) + 1

        # Cada disciplina recebe um peso = 1 (valor base) + quantidade de vezes que ela aparece como pré-requisito.
        objetivo = []
        for disciplina in self._disciplinas_disponiveis:
            chave = f"{disciplina['nome']}_{disciplina['professor']}"
            nome_normalizadoalizado = self._normalizar_nome(disciplina["nome"])
            peso = 1 + frequencia_prereq.get(nome_normalizadoalizado, 0)
            objetivo.append(peso * disciplina_vars[chave])

        # Objetivo: maximizar a soma ponderada das disciplinas selecionadas.
        model.Maximize(sum(objetivo))

        # Executa a otimização do modelo.
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # Processa os resultados.
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return [
                disciplina
                for disciplina in self._disciplinas_disponiveis
                if solver.Value(disciplina_vars[f"{disciplina['nome']}_{disciplina['professor']}"]) == 1
            ]
        return []

    def _filtrar_disciplinas_disponiveis(self) -> None:
        """
        Filtra as disciplinas disponíveis conforme o currículo de Ciência da Computação.
        Utiliza o nome normalizado para comparar com o currículo.
        """
        self._disciplinas_disponiveis = [
            disciplina
            for disciplina in self.matriz_horaria
            if self._normalizar_nome(disciplina["nome"]) in CURRICULO_CCOMP
        ]

    def _processar_historico(self) -> None:
        """
        Processa o histórico do estudante para identificar disciplinas já concluídas
        ou em andamento, utilizando o nome normalizado para garantir a comparação correta.
        """
        for disciplina in self.historico_academico:
            nome_normalizadoalizado = self._normalizar_nome(disciplina["nome"])
            if disciplina["situacao"] == "APROVADO":
                self._disciplinas_feitas.add(nome_normalizadoalizado)
                self._disciplinas_indisponiveis.add(nome_normalizadoalizado)
            elif disciplina["situacao"] == "EM CURSO":
                self._disciplinas_indisponiveis.add(nome_normalizadoalizado)

    def _criar_variaveis_disciplinas(self, model: cp_model.CpModel) -> dict[str, cp_model.IntVar]:
        """
        Cria variáveis booleanas para cada disciplina disponível.

        Args:
            model: O modelo de programação por restrições.

        Returns:
            Dicionário que mapeia uma chave única para cada disciplina à sua variável booleana.
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
        Impõe a restrição de que disciplinas já concluídas ou em andamento não podem ser escolhidas.

        Args:
            model: O modelo de programação por restrições.
            disciplina_vars: Dicionário com as variáveis de decisão.
        """
        for disciplina in self._disciplinas_disponiveis:
            chave = f"{disciplina['nome']}_{disciplina['professor']}"
            if self._normalizar_nome(disciplina["nome"]) in self._disciplinas_indisponiveis:
                model.Add(disciplina_vars[chave] == 0)

    def _aplicar_restricao_pre_requisitos(
        self, model: cp_model.CpModel, disciplina_vars: dict[str, cp_model.IntVar]
    ) -> None:
        """
        Impõe a restrição para garantir que os pré-requisitos das disciplinas foram cumpridos.
        Utiliza o nome normalizado para realizar a verificação com o PREREQUISITOS_MAP.

        Args:
            model: O modelo de programação por restrições.
            disciplina_vars: Dicionário com as variáveis de decisão.
        """
        for disciplina in self._disciplinas_disponiveis:
            chave = f"{disciplina['nome']}_{disciplina['professor']}"
            nome_normalizado = self._normalizar_nome(disciplina["nome"])
            if nome_normalizado in PREREQUISITOS_MAP:
                prereqs = PREREQUISITOS_MAP[nome_normalizado]
                if not all(prereq in self._disciplinas_feitas for prereq in prereqs):
                    model.Add(disciplina_vars[chave] == 0)

    def _aplicar_restricao_conflitos(
        self, model: cp_model.CpModel, disciplina_vars: dict[str, cp_model.IntVar]
    ) -> None:
        """
        Impõe restrição para evitar conflitos de dias ou horários entre as disciplinas.

        Args:
            model: O modelo de programação por restrições.
            disciplina_vars: Dicionário com as variáveis de decisão.
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
        Impõe restrição para não escolher a mesma disciplina ministrada por professores diferentes.

        Args:
            model: O modelo de programação por restrições.
            disciplina_vars: Dicionário com as variáveis de decisão.
        """
        nome_para_disciplinas: dict[str, list[dict]] = {}
        for disciplina in self._disciplinas_disponiveis:
            nome_normalizado = self._normalizar_nome(disciplina["nome"])
            if nome_normalizado not in nome_para_disciplinas:
                nome_para_disciplinas[nome_normalizado] = []
            nome_para_disciplinas[nome_normalizado].append(disciplina)

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
            disciplina1: Primeira disciplina para verificação.
            disciplina2: Segunda disciplina para verificação.

        Returns:
            True se houver conflito, False caso contrário.
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
            horario_str: String no formato "HHhMM" (ex: "14h30").

        Returns:
            Quantidade total de minutos.
        """
        hora, minuto = map(int, horario_str.split("h"))
        return hora * 60 + minuto

    @staticmethod
    def _normalizar_nome(nome: str) -> str:
        """
        Remove sufixos indesejados, como as variações de "(REOF)", do nome da disciplina.

        Args:
            nome: Nome original da disciplina.

        Returns:
            Nome normalizado.
        """
        # Remove qualquer ocorrência de "(REOF)" com possíveis espaços antes ou depois.
        nome = re.sub(r"\s*\(\s*REOF\s*\)", "", nome, flags=re.IGNORECASE)
        return nome.strip()
