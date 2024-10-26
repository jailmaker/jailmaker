import json
from pathlib import Path

from django.http import JsonResponse
from ninja import NinjaAPI

api = NinjaAPI()


with Path.open("./jailmaker/files/matriz_2024_2.json", encoding="utf-8") as f:
    available_classes = json.load(f)


@api.get("/get_available_classes")
def get_available_classes(request) -> list[dict[str, str | None]]:
    return JsonResponse(available_classes, safe=False)
