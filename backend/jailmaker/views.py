from django.http import HttpRequest, JsonResponse
from ninja import NinjaAPI

from jailmaker.service.matrix_svc import MatrixReader

api = NinjaAPI()


@api.get("/get_available_classes")
def get_available_classes(request: HttpRequest) -> list[dict[str, str | None]]:
    matrix_reader = MatrixReader("./jailmaker/files/matriz_2024_2.xlsx")
    df = matrix_reader.read_matrix()

    return JsonResponse(df.to_dict(orient="records"), safe=False)
