from django.urls import path

from ..views.third import (
    PublicFormDetailView,
    PublicProviderAnswersView,
    PublicProviderDetailView,
    PublicProviderFormsView,
    PublicProviderListView,
)

urlpatterns = [
    path("providers/", PublicProviderListView.as_view(), name="provider-app-third-providers"),
    path(
        "providers/<int:provider_id>/",
        PublicProviderDetailView.as_view(),
        name="provider-app-third-provider",
    ),
    path(
        "providers/<int:provider_id>/forms/",
        PublicProviderFormsView.as_view(),
        name="provider-app-third-provider-forms",
    ),
    path(
        "providers/<int:provider_id>/answers/",
        PublicProviderAnswersView.as_view(),
        name="provider-app-third-provider-answers",
    ),
    path("forms/<int:pk>/", PublicFormDetailView.as_view(), name="provider-app-third-form"),
]
