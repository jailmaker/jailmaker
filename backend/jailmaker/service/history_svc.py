import re

from pypdf import PdfReader


def extract_student_info(text):
    """Extrai informações do aluno do texto"""
    info = {}

    # Usando regex para extrair informações básicas
    matricula_match = re.search(r"Matrícula: (\d+)", text)
    nome_match = re.search(r"Nome: ([^\n]+)", text)
    curso_match = re.search(r"Curso: ([^\n]+)", text)
    cr_match = re.search(r"Coeficiente de Rendimento: ([\d.]+)", text)

    if matricula_match:
        info["matricula"] = matricula_match.group(1)
    if nome_match:
        info["nome"] = nome_match.group(1).strip()
    if curso_match:
        info["curso"] = curso_match.group(1).strip()
    if cr_match:
        info["coeficiente_rendimento"] = float(cr_match.group(1))

    return info


def merge_broken_lines(lines):
    """Combina linhas quebradas em uma única linha de disciplina"""
    merged_lines = []
    current_line = ""

    for line in lines:
        # Se a linha começa com o padrão de ano/semestre (4 dígitos seguidos de espaço)
        if re.match(r"^\d{4}\s", line):
            if current_line:
                merged_lines.append(current_line.strip())
            current_line = line
        # Se a linha não começa com dígitos e não é vazia, é continuação
        elif line.strip() and not re.match(r"^\d", line) and current_line:
            # Remove possíveis espaços extras entre palavras
            current_line = current_line.strip() + " " + line.strip()
        # Se é uma linha vazia ou linha de cabeçalho, finaliza a linha atual
        elif not line.strip() or "Ano" in line or "HISTÓRICO" in line:
            if current_line:
                merged_lines.append(current_line.strip())
            current_line = ""

    # Adiciona a última linha se existir
    if current_line:
        merged_lines.append(current_line.strip())

    return merged_lines


def parse_disciplina(line):
    """Converte uma linha de disciplina em um dicionário estruturado"""
    info = {}
    # Padrão para extrair os campos iniciais que sempre seguem o mesmo formato
    inicio_pattern = r"(\d{4})\s+(\d+)\s+(\d+)\s+([A-Z])\s+([A-Z][A-Z]?)\s+(\d+)\s+"

    inicio_match = re.match(inicio_pattern, line)
    if not inicio_match:
        return None

    # Extrai os campos iniciais
    ano, semestre, serie, turno, turma, codigo = inicio_match.groups()
    info["ano"] = ano
    info["semestre"] = semestre
    info["serie"] = serie
    info["turno"] = turno
    info["turma"] = turma
    info["codigo"] = codigo

    # Remove a parte inicial da linha que já foi processada
    resto_linha = line[inicio_match.end() :].strip()

    # Procura pela string "UNIDADE CURRICULAR" em toda a linha
    partes = resto_linha.split("UNIDADE CURRICULAR")

    if len(partes) < 2:
        return None

    nome = partes[0].strip()
    info["nome"] = nome
    info_restante = "UNIDADE CURRICULAR " + partes[1].strip()

    # Divide os campos restantes
    campos = info_restante.split()

    final = 0

    try:
        final = campos.index("CURSO")
    except ValueError:
        pass

    try:
        final = campos.index("APROVADO")
    except ValueError:
        pass

    try:
        final = campos.index("REPROV./FREQ")
    except ValueError:
        pass

    try:
        final = campos.index("CUMPRIDO")
    except ValueError:
        pass

    try:
        final = campos.index("REPROVADO")
    except ValueError:
        pass

    campos = campos[: final + 1]

    if campos[3] == "INTERDISCIPLINAR":
        grupo = " ".join(campos[0:4])
        del campos[0:4]
    else:
        grupo = " ".join(campos[0:3])
        del campos[0:3]

    if campos[-2:] == ["NÃO", "CUMPRIDO"]:
        campos[-2] = "NÃO CUMPRIDO"
        del campos[-1]

    if campos[-2:] == ["EM", "CURSO"]:
        campos[-2] = "EM CURSO"
        del campos[-1]

    # se o penúltimo campo for a carga horária e não o conceito
    if campos[-2] in ("36", "72", "108"):
        campos.insert(-1, "-")

    # se ainda sim faltar um campo, que é a frequência
    if len(campos) == 6:
        campos.insert(2, "-")

    if campos[6] == "REPROV./FREQ":
        campos[6] = "REPROVADO"
    if campos[6] == "CUMPRIDO":
        campos[6] = "APROVADO"
    if campos[6] == "NÃO CUMPRIDO":
        campos[6] = "REPROVADO"

    info["grupo"] = grupo
    info["categoria"] = campos[0]
    info["faltas"] = campos[1]
    info["frequencia"] = campos[2]
    info["creditos"] = campos[3]
    info["carga_horaria"] = campos[4]
    info["conceito"] = campos[5]
    info["situacao"] = campos[6]

    return info


def pdf_to_json(pdf):
    reader = PdfReader(pdf)

    # Extrai todo o texto do PDF
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    # Extrai informações do aluno
    student_info = extract_student_info(full_text)

    # Divide o texto em linhas e faz o merge das linhas quebradas
    lines = full_text.split("\n")
    merged_lines = merge_broken_lines(lines)

    # Lista para armazenar as disciplinas
    disciplinas = []

    # Processa cada linha
    for line in merged_lines:
        # Verifica se a linha contém dados de disciplina
        if re.match(r"^\d{4}\s+\d+\s+\d+", line):
            disciplina = parse_disciplina(line)
            if disciplina:
                disciplinas.append(disciplina)

    # Cria o objeto JSON final
    output_data = {"informacoes_aluno": student_info, "disciplinas": disciplinas}

    return output_data
