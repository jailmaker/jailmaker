from django.urls import path

from jailmaker.views import api

urlpatterns = [
    path("api/", api.urls),
]
