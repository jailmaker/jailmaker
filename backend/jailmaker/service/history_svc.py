import json
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
    # Padrão para extrair os campos iniciais que sempre seguem o mesmo formato
    inicio_pattern = r"(\d{4})\s+(\d+)\s+(\d+)\s+([A-Z])\s+([A-Z][A-Z]?)\s+(\d+)\s+"

    inicio_match = re.match(inicio_pattern, line)
    if not inicio_match:
        return None

    # Extrai os campos iniciais
    ano, semestre, serie, turno, turma, codigo = inicio_match.groups()

    # Remove a parte inicial da linha que já foi processada
    resto_linha = line[inicio_match.end() :].strip()

    # Procura pela string "UNIDADE CURRICULAR" em toda a linha
    pos_unidade = -1
    partes = resto_linha.split("UNIDADE CURRICULAR")

    if len(partes) < 2:
        return None

    nome = partes[0].strip()
    info_restante = "UNIDADE CURRICULAR" + partes[1].strip()

    # Divide os campos restantes
    campos = info_restante.split()

    if campos[-1] == "CURSO":
        return None

    # Ajusta campos faltantes
    if len(campos) == 8:
        campos.insert(4, "-")

    # Identifica o grupo
    grupo = "UNIDADE CURRICULAR"
    i = 2  # Começa após "UNIDADE CURRICULAR"
    while i < len(campos) and campos[i] not in ["FIXAS", "ELETIVAS"]:
        grupo += " " + campos[i]
        i += 1

    try:
        disciplina = {
            "ano_letivo": ano,
            "semestre": semestre,
            "serie_termo": serie,
            "turno": turno,
            "turma": turma,
            "codigo": codigo,
            "nome": nome,
            "grupo": grupo,
            "categoria": campos[i] if i < len(campos) else "",
            "faltas": campos[i + 1] if i + 1 < len(campos) else "0",
            "frequencia": "" if i + 2 >= len(campos) or campos[i + 2] == "-" else campos[i + 2].replace("%", ""),
            "creditos": campos[i + 3] if i + 3 < len(campos) else "",
            "carga_horaria": campos[i + 4] if i + 4 < len(campos) else "",
            "conceito": "-" if i + 5 >= len(campos) or campos[i + 5] == "-" else campos[i + 5],
            "situacao": campos[i + 6] if i + 6 < len(campos) else "",
        }

        return disciplina
    except IndexError:
        return None


def pdf_to_json(pdf_path, json_path):
    reader = PdfReader(pdf_path)

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

    # Salva o JSON
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(output_data, json_file, ensure_ascii=False, indent=4)

    print(f"Dados do histórico acadêmico salvos em {json_path}")


# Chamada da função
pdf_to_json("backend/jailmaker/service/history.pdf", "historico8.json")
