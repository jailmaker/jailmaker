import json
from http import HTTPStatus
from pathlib import Path

from ninja import NinjaAPI

from jailmaker.service.grade_ideal_svc import GeradorGradeIdeal
from jailmaker.service.historico_academico_svc import LeitorHistoricoAcademico

api = NinjaAPI(title="Jailmaker API", version="1.0")


@api.get("/matriz-horaria")
def listar_matriz_horaria(request):
    """
    Carrega e retorna a matriz horária atual a partir do seu arquivo JSON.
    """
    try:
        path = Path(__file__).parent / "files" / "matriz_2024_2.json"
        with path.open(encoding="utf-8") as f:
            matriz_horaria = json.load(f)
        return matriz_horaria
    except Exception as exc:
        return api.create_response(request, {"erro": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


@api.post("/historico-academico")
def ler_historico_academico(request):
    """
    Recebe um arquivo PDF do histórico acadêmico, converte para JSON e retorna o resultado.
    """
    try:
        historico_academico_pdf = request.FILES["historico_academico"]
        historico_academico_json = LeitorHistoricoAcademico.from_pdf(historico_academico_pdf)
        return historico_academico_json
    except Exception as exc:
        return api.create_response(request, {"erro": str(exc)}, status=HTTPStatus.BAD_REQUEST)


@api.post("/grade-ideal")
def gerar_grade_ideal(request):
    """
    Recebe os dados da matriz curricular e do histórico acadêmico, gera e retorna a grade ideal.
    """
    try:
        data = json.loads(request.body)
        grade_ideal = GeradorGradeIdeal(data["matriz_horaria"], data["historico_academico"]).gerar()
        return grade_ideal
    except Exception as exc:
        return api.create_response(request, {"erro": str(exc)}, status=HTTPStatus.BAD_REQUEST)
