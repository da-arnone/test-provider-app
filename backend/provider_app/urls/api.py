from django.urls import path

from ..views.api import (
    FormDetailView,
    FormListView,
    LoginView,
    QuestionAnswerUpdateView,
    SessionView,
)

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="provider-app-login"),
    path("auth/session/", SessionView.as_view(), name="provider-app-session"),
    path("forms/", FormListView.as_view(), name="provider-app-forms"),
    path("forms/<int:pk>/", FormDetailView.as_view(), name="provider-app-form"),
    path(
        "questions/<int:pk>/answer/",
        QuestionAnswerUpdateView.as_view(),
        name="provider-app-question-answer",
    ),
]
