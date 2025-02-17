import re

import pandas as pd


class LeitorMatrizHoraria:
    def __init__(self, path: str) -> None:
        self.path = path

    def ler(self) -> pd.DataFrame:
        df = pd.read_excel(self.path)
        df["Unnamed: 0"] = df["Unnamed: 0"].ffill()
        df = df.T
        df[0] = df[0].ffill()
        df = self._gerar_disciplinas(df)
        df = self._limpar_dados(df)
        df = self._renomear_colunas(df)
        df = self._combinar_horarios(df)
        return df

    def _gerar_disciplinas(self, df: pd.DataFrame) -> pd.DataFrame:
        linhas = []
        if df.shape[0] < 3 or df.shape[1] < 3:
            return pd.DataFrame(linhas)

        for i in range(2, df.shape[0]):
            dia_semana = df.iloc[i, 0]
            for col in range(1, df.shape[1], 2):
                if pd.isna(df.iloc[1, col]):
                    continue
                if col + 1 >= df.shape[1]:
                    break

                horario = df.iloc[1, col]
                nome_disciplina = df.iloc[i, col]
                turma_professor = df.iloc[i, col + 1]
                curso_periodo = df.iloc[0, col]

                if pd.notna(nome_disciplina) and pd.notna(turma_professor):
                    linha = {
                        "Dia da Semana": dia_semana,
                        "Horário": horario,
                        "Nome da Disciplina": nome_disciplina,
                        "Turma - Professor": turma_professor,
                        "Curso - Período": curso_periodo,
                    }
                    linhas.append(linha)

        return pd.DataFrame(linhas)

    def _limpar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        df[["Curso", "Período"]] = (
            df["Curso - Período"].str.replace("\n\n\n\n", "").apply(self._separar_curso_periodo).apply(pd.Series)
        )
        df[["Turma", "Professor"]] = df["Turma - Professor"].apply(self._separar_turma_professor).apply(pd.Series)
        df["Horário"] = df["Horário"].apply(self._normalizar_horario)
        df.update(df.loc[:, df.columns != "ID"].apply(lambda x: x.str.strip() if x.dtype == "object" else x))
        return df

    def _renomear_colunas(self, df: pd.DataFrame) -> pd.DataFrame:
        df["ID"] = df.index
        df = df[["ID", "Nome da Disciplina", "Professor", "Turma", "Horário", "Dia da Semana", "Curso", "Período"]]
        df.columns = ["id", "disciplina", "professor", "turma", "horario", "dia", "curso", "periodo"]
        return df

    def _combinar_horarios(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.groupby(["disciplina", "professor", "turma"])
            .agg(
                {
                    "horario": list,
                    "dia": list,
                    "curso": "first",
                    "periodo": "first",
                }
            )
            .reset_index()
        )

    @staticmethod
    def _separar_curso_periodo(texto: str) -> tuple[str, str | None]:
        partes = re.split(r" \n|\n", texto)
        curso = partes[0]
        periodo = re.search(r"Período (\d+)", partes[1]).group(1) if len(partes) > 1 else None
        return curso, periodo

    @staticmethod
    def _separar_turma_professor(texto: str) -> tuple[str, str]:
        correspondencia = re.match(r"([A-Z]+[A-Z0-9]*)\s*-\s*(.+)", texto)
        if correspondencia:
            codigo_turma = correspondencia.group(1).strip()
            professor = correspondencia.group(2).strip()
        else:
            codigo_turma = LeitorMatrizHoraria._determinar_codigo_turma(texto)
            professor = texto.strip()
        return codigo_turma, professor

    @staticmethod
    def _determinar_codigo_turma(texto: str) -> str:
        if texto.strip().isalpha():
            return "I"

        correspondencia_maiuscula = re.search(r"[A-Z]+$", texto)
        if correspondencia_maiuscula:
            return correspondencia_maiuscula.group(0)

        return "N"

    @staticmethod
    def _normalizar_horario(horario: str) -> str:
        padrao = re.compile(r"(\d{1,2})[hH](\d{2})\s*-\s*(\d{1,2})[hH](\d{2})")
        correspondencia = padrao.match(horario)
        if correspondencia:
            hora_inicio, minuto_inicio, hora_fim, minuto_fim = correspondencia.groups()
            return f"{int(hora_inicio):02d}h{minuto_inicio} - {int(hora_fim):02d}h{minuto_fim}"
        return horario
