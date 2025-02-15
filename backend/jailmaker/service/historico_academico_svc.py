import re

from pypdf import PdfReader


class LeitorHistoricoAcademico:
    """
    Classe para parsing de histórico acadêmico de PDF.
    Extrai informações do aluno e disciplinas de forma estruturada.
    """

    @staticmethod
    def _extract_student_info(text: str) -> dict[str, str | float]:
        """Extrai informações básicas do aluno usando expressões regulares."""
        patterns = {
            "matricula": r"Matrícula: (\d+)",
            "nome": r"Nome: ([^\n]+)",
            "curso": r"Curso: ([^\n]+)",
            "coeficiente_rendimento": r"Coeficiente de Rendimento: ([\d.]+)",
        }

        info = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                info[key] = match.group(1).strip() if key != "coeficiente_rendimento" else float(match.group(1))

        return info

    @staticmethod
    def _merge_broken_lines(lines: list[str]) -> list[str]:
        """Combina linhas quebradas em linhas completas de disciplinas."""
        merged_lines = []
        current_line = ""

        for line in lines:
            if re.match(r"^\d{4}\s", line):
                if current_line:
                    merged_lines.append(current_line.strip())
                current_line = line
            elif line.strip() and not re.match(r"^\d", line) and current_line:
                current_line = f"{current_line.strip()} {line.strip()}"
            elif not line.strip() or "Ano" in line or "HISTÓRICO" in line:
                if current_line:
                    merged_lines.append(current_line.strip())
                current_line = ""

        if current_line:
            merged_lines.append(current_line.strip())

        return merged_lines

    @staticmethod
    def _parse_disciplina(line: str) -> dict[str, str] | None:
        """Converte uma linha de disciplina em um dicionário estruturado."""
        inicio_pattern = r"(\d{4})\s+(\d+)\s+(\d+)\s+([A-Z])\s+([A-Z][A-Z]?)\s+(\d+)\s+"
        inicio_match = re.match(inicio_pattern, line)

        if not inicio_match:
            return None

        # Extrai campos iniciais
        fields = ["ano", "semestre", "termo", "turno", "turma", "codigo"]
        initial_info = dict(zip(fields, inicio_match.groups(), strict=False))

        resto_linha = line[inicio_match.end() :].strip()
        partes = resto_linha.split("UNIDADE CURRICULAR")

        if len(partes) < 2:
            return None

        initial_info["nome"] = partes[0].strip()
        info_restante = "UNIDADE CURRICULAR " + partes[1].strip()
        campos = info_restante.split()

        # Encontra o índice final
        final_markers = ["CURSO", "APROVADO", "REPROV./FREQ", "CUMPRIDO", "REPROVADO"]
        final = next((campos.index(marker) for marker in final_markers if marker in campos), len(campos))
        campos = campos[: final + 1]

        # Processa grupo e campos específicos
        grupo_markers = ["INTERDISCIPLINAR"] if "INTERDISCIPLINAR" in campos else []
        grupo_length = 4 if grupo_markers else 3
        initial_info["grupo"] = " ".join(campos[:grupo_length])
        campos = campos[grupo_length:]

        # Normalização de alguns campos específicos
        special_cases = {("NÃO", "CUMPRIDO"): "NÃO CUMPRIDO", ("EM", "CURSO"): "EM CURSO"}
        for case, replacement in special_cases.items():
            if campos[-2:] == list(case):
                campos[-2:] = [replacement]

        # Ajustes para garantir a estrutura correta
        if campos[-2] in ("36", "72", "108"):
            campos.insert(-1, "-")
        if len(campos) == 6:
            campos.insert(2, "-")

        # Mapeamento de situações
        situacao_mapping = {"REPROV./FREQ": "REPROVADO", "CUMPRIDO": "APROVADO", "NÃO CUMPRIDO": "REPROVADO"}
        campos[6] = situacao_mapping.get(campos[6], campos[6])

        # Campos finais
        final_fields = ["categoria", "faltas", "frequencia", "creditos", "carga_horaria", "conceito", "situacao"]
        initial_info.update(zip(final_fields, campos, strict=False))

        return initial_info

    @classmethod
    def pdf_to_json(cls, pdf_path: str) -> dict[str, dict | list[dict]]:
        """Converte um PDF de histórico acadêmico para um dicionário JSON."""
        reader = PdfReader(pdf_path)
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        student_info = cls._extract_student_info(full_text)
        lines = full_text.split("\n")
        merged_lines = cls._merge_broken_lines(lines)

        disciplinas = [
            disciplina
            for line in merged_lines
            if re.match(r"^\d{4}\s+\d+\s+\d+", line)
            if (disciplina := cls._parse_disciplina(line))
        ]

        return {"informacoes_aluno": student_info, "disciplinas": disciplinas}
