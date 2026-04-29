import json

from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import ProviderForm, Question
from ..serializers import ProviderFormSerializer, QuestionAnswerUpdateSerializer
from ..services.auth_client import (
    ALLOWED_PROVIDER_ROLES,
    APP_SCOPE,
    authorize_request,
    extract_bearer_token,
    has_provider_admin_profile,
    issue_token,
    provider_ids_from_profiles,
    validate_token,
    whois,
)


def _authorized_provider_ids(request):
    token = extract_bearer_token(request)
    if not token:
        return None, None, Response({"detail": "missing bearer token"}, status=401)
    claims = validate_token(token)
    if not claims:
        return None, None, Response({"detail": "invalid token"}, status=401)
    session = whois(token)
    if not session:
        return None, None, Response({"detail": "failed to load session from auth-app"}, status=502)

    profiles = session.get("profiles") or []
    is_provider_admin = has_provider_admin_profile(profiles)
    provider_ids = provider_ids_from_profiles(profiles)
    if not provider_ids and not is_provider_admin:
        return None, None, Response({"detail": "no provider-app profile is assigned"}, status=403)

    if is_provider_admin:
        # provider-admin is global in provider-app and can manage all providers/forms.
        provider_ids = list(
            ProviderForm.objects.order_by("provider_id")
            .values_list("provider_id", flat=True)
            .distinct()
        )

    for provider_id in provider_ids:
        context = f"provider-{provider_id:03d}"
        if any(authorize_request(token, role, context=context) for role in ALLOWED_PROVIDER_ROLES):
            return token, provider_ids, None
    if is_provider_admin and authorize_request(token, "provider-admin", context=None):
        return token, provider_ids, None
    return None, None, Response({"detail": "forbidden for provider context"}, status=403)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            data = json.loads((request.body or b"{}").decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            data = {}
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return Response({"detail": "username and password are required"}, status=400)

        token = issue_token(username, password)
        if not token:
            return Response({"detail": "invalid credentials"}, status=401)

        session = whois(token)
        if not session:
            return Response({"detail": "login succeeded but profile lookup failed"}, status=502)

        profiles = session.get("profiles") or []
        provider_ids = provider_ids_from_profiles(profiles)
        if not provider_ids:
            return Response({"detail": "no provider-app profile is assigned"}, status=403)

        return Response(
            {
                "accessToken": token,
                "user": {
                    "userId": session.get("userId"),
                    "username": session.get("username"),
                    "profiles": profiles,
                    "providerIds": provider_ids,
                    "appScope": APP_SCOPE,
                },
            }
        )


class SessionView(APIView):
    def get(self, request):
        token, provider_ids, error = _authorized_provider_ids(request)
        if error:
            return error
        session = whois(token)
        return Response(
            {
                "userId": session.get("userId"),
                "username": session.get("username"),
                "profiles": session.get("profiles") or [],
                "providerIds": provider_ids,
            }
        )


class FormListView(APIView):
    def get(self, request):
        _token, provider_ids, error = _authorized_provider_ids(request)
        if error:
            return error
        forms = ProviderForm.objects.filter(provider_id__in=provider_ids).prefetch_related("questions")
        return Response(ProviderFormSerializer(forms, many=True).data)


class FormDetailView(APIView):
    def get(self, request, pk):
        _token, provider_ids, error = _authorized_provider_ids(request)
        if error:
            return error
        try:
            form = ProviderForm.objects.prefetch_related("questions").get(pk=pk, provider_id__in=provider_ids)
        except ProviderForm.DoesNotExist:
            return Response({"detail": "form not found"}, status=404)
        return Response(ProviderFormSerializer(form).data)


class QuestionAnswerUpdateView(APIView):
    def patch(self, request, pk):
        _token, provider_ids, error = _authorized_provider_ids(request)
        if error:
            return error
        try:
            question = Question.objects.select_related("form").get(
                pk=pk, form__provider_id__in=provider_ids
            )
        except Question.DoesNotExist:
            return Response({"detail": "question not found"}, status=404)

        serializer = QuestionAnswerUpdateSerializer(
            question, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "id": question.id,
                "form": question.form_id,
                "label": question.label,
                "answer": question.answer,
                "is_public": question.is_public,
                "order": question.order,
            }
        )
