from django.conf import settings
from django.urls import include, path
from django.views.generic.base import RedirectView

import provider_app.urls

urlpatterns = [
    path("", RedirectView.as_view(url=settings.FRONTEND_URL, permanent=False)),
    path("", include(provider_app.urls)),
]
