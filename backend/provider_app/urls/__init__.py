from django.urls import include, path

urlpatterns = [
    path("admin/provider/", include("provider_app.urls.admin")),
    path("api/provider/", include("provider_app.urls.api")),
    path("third/provider/", include("provider_app.urls.third")),
]
