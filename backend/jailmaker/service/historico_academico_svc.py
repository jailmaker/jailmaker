import re

from pypdf import PdfReader


class LeitorHistoricoAcademico:
    """
    Classe para parsing de histórico acadêmico de PDF.
    Extrai informações do aluno e disciplinas de forma estruturada.
    """

    @staticmethod
    def _extrair_informacoes_aluno(texto: str) -> dict[str, str | float]:
        """Extrai informações básicas do aluno usando expressões regulares."""
        padroes = {
            "matricula": r"Matrícula: (\d+)",
            "nome": r"Nome: ([^\n]+)",
            "curso": r"Curso: ([^\n]+)",
            "coeficiente_rendimento": r"Coeficiente de Rendimento: ([\d.]+)",
        }

        info = {}
        for chave, padrao in padroes.items():
            resultado = re.search(padrao, texto)
            if resultado:
                info[chave] = (
                    resultado.group(1).strip() if chave != "coeficiente_rendimento" else float(resultado.group(1))
                )

        return info

    @staticmethod
    def _mesclar_linhas_quebradas(linhas: list[str]) -> list[str]:
        """Combina linhas quebradas em linhas completas de disciplinas."""
        linhas_mescladas = []
        linha_atual = ""

        for linha in linhas:
            if re.match(r"^\d{4}\s", linha):
                if linha_atual:
                    linhas_mescladas.append(linha_atual.strip())
                linha_atual = linha
            elif linha.strip() and not re.match(r"^\d", linha) and linha_atual:
                linha_atual = f"{linha_atual.strip()} {linha.strip()}"
            elif not linha.strip() or "Ano" in linha or "HISTÓRICO" in linha:
                if linha_atual:
                    linhas_mescladas.append(linha_atual.strip())
                linha_atual = ""

        if linha_atual:
            linhas_mescladas.append(linha_atual.strip())

        return linhas_mescladas

    @staticmethod
    def _analisar_disciplina(linha: str) -> dict[str, str] | None:
        """Converte uma linha de disciplina em um dicionário estruturado."""
        padrao_inicio = r"(\d{4})\s+(\d+)\s+(\d+)\s+([A-Z])\s+([A-Z][A-Z]?)\s+(\d+)\s+"
        resultado_inicio = re.match(padrao_inicio, linha)

        if not resultado_inicio:
            return None

        # Extrai campos iniciais
        campos = ["ano", "semestre", "termo", "turno", "turma", "codigo"]
        info_inicial = dict(zip(campos, resultado_inicio.groups(), strict=False))

        resto_linha = linha[resultado_inicio.end() :].strip()
        partes = resto_linha.split("UNIDADE CURRICULAR")

        if len(partes) < 2:
            return None

        info_inicial["nome"] = partes[0].strip()
        info_restante = "UNIDADE CURRICULAR " + partes[1].strip()
        campos = info_restante.split()

        # Encontra o índice final
        marcadores_final = ["CURSO", "APROVADO", "REPROV./FREQ", "CUMPRIDO", "REPROVADO"]
        final = next((campos.index(marcador) for marcador in marcadores_final if marcador in campos), len(campos))
        campos = campos[: final + 1]

        # Processa grupo e campos específicos
        marcadores_grupo = ["INTERDISCIPLINAR"] if "INTERDISCIPLINAR" in campos else []
        tamanho_grupo = 4 if marcadores_grupo else 3
        info_inicial["grupo"] = " ".join(campos[:tamanho_grupo])
        campos = campos[tamanho_grupo:]

        # Normalização de alguns campos específicos
        casos_especiais = {("NÃO", "CUMPRIDO"): "NÃO CUMPRIDO", ("EM", "CURSO"): "EM CURSO"}
        for caso, substituicao in casos_especiais.items():
            if campos[-2:] == list(caso):
                campos[-2:] = [substituicao]

        # Ajustes para garantir a estrutura correta
        if campos[-2] in ("36", "72", "108"):
            campos.insert(-1, "-")
        if len(campos) == 6:
            campos.insert(2, "-")

        # Mapeamento de situações
        mapeamento_situacao = {"REPROV./FREQ": "REPROVADO", "CUMPRIDO": "APROVADO", "NÃO CUMPRIDO": "REPROVADO"}
        campos[6] = mapeamento_situacao.get(campos[6], campos[6])

        # Campos finais
        campos_finais = ["categoria", "faltas", "frequencia", "creditos", "carga_horaria", "conceito", "situacao"]
        info_inicial.update(zip(campos_finais, campos, strict=False))

        return info_inicial

    @classmethod
    def from_pdf(cls, path: str) -> dict[str, dict | list[dict]]:
        """Converte um PDF de histórico acadêmico para um dicionário JSON."""
        leitor = PdfReader(path)
        texto_completo = "\n".join(pagina.extract_text() for pagina in leitor.pages)

        info_aluno = cls._extrair_informacoes_aluno(texto_completo)
        linhas = texto_completo.split("\n")
        linhas_mescladas = cls._mesclar_linhas_quebradas(linhas)

        disciplinas = [
            disciplina
            for linha in linhas_mescladas
            if re.match(r"^\d{4}\s+\d+\s+\d+", linha)
            if (disciplina := cls._analisar_disciplina(linha))
        ]

        return {"informacoes_aluno": info_aluno, "disciplinas": disciplinas}
