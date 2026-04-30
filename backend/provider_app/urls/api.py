from django.urls import path

from ..views.api import (
    FormDetailView,
    FormListView,
    IncomingSubmissionDecisionView,
    IncomingSubmissionListView,
    LoginView,
    PublicProviderFormsView,
    QuestionAnswerUpdateView,
    SessionView,
)

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="provider-app-login"),
    path("auth/session/", SessionView.as_view(), name="provider-app-session"),
    path("forms/", FormListView.as_view(), name="provider-app-forms"),
    path(
        "consultation/providers/<int:provider_id>/forms/",
        PublicProviderFormsView.as_view(),
        name="provider-app-consultation-provider-forms",
    ),
    path("forms/<int:pk>/", FormDetailView.as_view(), name="provider-app-form"),
    path(
        "subscriptions/incoming/",
        IncomingSubmissionListView.as_view(),
        name="provider-app-subscriptions-incoming",
    ),
    path(
        "subscriptions/incoming/<int:pk>/decision/",
        IncomingSubmissionDecisionView.as_view(),
        name="provider-app-subscriptions-incoming-decision",
    ),
    path(
        "questions/<int:pk>/answer/",
        QuestionAnswerUpdateView.as_view(),
        name="provider-app-question-answer",
    ),
]
