from django.urls import path

from ..views.third import PublicFormDetailView, PublicProviderFormsView

urlpatterns = [
    path("providers/<int:provider_id>/forms/", PublicProviderFormsView.as_view(), name="provider-app-third-provider-forms"),
    path("forms/<int:pk>/", PublicFormDetailView.as_view(), name="provider-app-third-form"),
]
