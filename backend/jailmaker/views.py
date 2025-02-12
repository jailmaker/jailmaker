import json
from pathlib import Path

from django.http import JsonResponse
from ninja import NinjaAPI

from jailmaker.service.grade_svc import monta_grade_ideal
from jailmaker.service.history_svc import LeitorHistoricoAcademico

api = NinjaAPI()


@api.get("/get_available_classes")
def get_available_classes(request) -> list[dict[str, str | None]]:
    file_path = Path(__file__).parent / "files" / "matriz_2024_2.json"
    with file_path.open(encoding="utf-8") as f:
        available_classes = json.load(f)
    return JsonResponse(available_classes, safe=False)


@api.post("/get_academic_history")
def get_academic_history(request):
    pdf = request.FILES["file"]
    academic_history = LeitorHistoricoAcademico.pdf_to_json(pdf)
    return JsonResponse(academic_history, safe=False)


@api.post("/generate_optimal_schedule")
def gera_grade_ideal(request):
    data = json.loads(request.body)

    grade_ideal = monta_grade_ideal(data["matriz"], data["historico"])

    return JsonResponse(grade_ideal, safe=False)
