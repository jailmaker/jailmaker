import re

import pandas as pd


class MatrixReader:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def read_matrix(self) -> pd.DataFrame:
        df = pd.read_excel(self.file_path)
        df["Unnamed: 0"] = df["Unnamed: 0"].ffill()
        df = df.T
        df[0] = df[0].ffill()
        df = self._generate_subjects(df)
        df = self._clean_data(df)
        df = self._rename_columns(df)
        df = self._combine_schedules(df)
        return df

    def _generate_subjects(self, df: pd.DataFrame) -> pd.DataFrame:
        lines = []
        if df.shape[0] < 3 or df.shape[1] < 3:
            return pd.DataFrame(lines)

        for i in range(2, df.shape[0]):
            weekday = df.iloc[i, 0]
            for col in range(1, df.shape[1], 2):
                if pd.isna(df.iloc[1, col]):
                    continue
                if col + 1 >= df.shape[1]:
                    break

                schedule = df.iloc[1, col]
                subject_name = df.iloc[i, col]
                class_teacher = df.iloc[i, col + 1]
                course_term = df.iloc[0, col]

                if pd.notna(subject_name) and pd.notna(class_teacher):
                    line = {
                        "Dia da Semana": weekday,
                        "Horário": schedule,
                        "Nome da UC": subject_name,
                        "Turma - Professor": class_teacher,
                        "Curso - Termo": course_term,
                    }
                    lines.append(line)

        return pd.DataFrame(lines)

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df[["Curso", "Termo"]] = (
            df["Curso - Termo"].str.replace("\n\n\n\n", "").apply(self._split_course_term).apply(pd.Series)
        )
        df[["Turma", "Professor"]] = df["Turma - Professor"].apply(self._split_class_teacher).apply(pd.Series)
        df["Horário"] = df["Horário"].apply(self._normalize_schedule)
        df.update(df.loc[:, df.columns != "ID"].apply(lambda x: x.str.strip() if x.dtype == "object" else x))
        return df

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df["ID"] = df.index
        df = df[["ID", "Nome da UC", "Professor", "Turma", "Horário", "Dia da Semana", "Curso", "Termo"]]
        df.columns = ["id", "subject", "teacher", "class", "schedule", "day", "course", "period"]
        return df

    def _combine_schedules(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.groupby(["subject", "teacher", "class"])
            .agg(
                {
                    "schedule": list,
                    "day": list,
                    "course": "first",
                    "period": "first",
                }
            )
            .reset_index()
        )

    @staticmethod
    def _split_course_term(text: str) -> tuple[str, str | None]:
        parts = re.split(r" \n|\n", text)
        course = parts[0]
        term = re.search(r"Termo (\d+)", parts[1]).group(1) if len(parts) > 1 else None
        return course, term

    @staticmethod
    def _split_class_teacher(text: str) -> tuple[str, str]:
        match = re.match(r"([A-Z]+[A-Z0-9]*)\s*-\s*(.+)", text)
        if match:
            class_code = match.group(1).strip()
            teacher = match.group(2).strip()
        else:
            class_code = MatrixReader._determine_class_code(text)
            teacher = text.strip()
        return class_code, teacher

    @staticmethod
    def _determine_class_code(text: str) -> str:
        if text.strip().isalpha():
            return "I"

        uppercase_match = re.search(r"[A-Z]+$", text)
        if uppercase_match:
            return uppercase_match.group(0)

        return "N"

    @staticmethod
    def _normalize_schedule(schedule: str) -> str:
        pattern = re.compile(r"(\d{1,2})[hH](\d{2})\s*-\s*(\d{1,2})[hH](\d{2})")
        match = pattern.match(schedule)
        if match:
            start_hour, start_minute, end_hour, end_minute = match.groups()
            return f"{int(start_hour):02d}h{start_minute} - {int(end_hour):02d}h{end_minute}"
        return schedule
