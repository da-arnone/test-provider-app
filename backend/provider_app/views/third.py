from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Provider, ProviderForm
from ..serializers import ProviderFormPublicSerializer, ProviderSerializer, ProviderThirdDetailSerializer
from ..services.auth_client import (
    authorize_request,
    extract_bearer_token,
    validate_token,
    whois,
)
from ..services.subscription_client import has_handled_org_subscription


def _provider_contexts(provider_id: int) -> list[str]:
    return [f"provider-{provider_id}", f"provider-{provider_id:03d}"]


def _authorize_provider_third(token: str, provider_id: int) -> bool:
    for context in _provider_contexts(provider_id):
        if authorize_request(token, required_role="provider-third", context=context):
            return True
    # Fallback for global provider-third profile with no provider context.
    if authorize_request(token, required_role="provider-third", context=None):
        return True
    return False


def _parse_context_entity_id(context) -> int | None:
    if isinstance(context, int):
        return context
    if isinstance(context, str):
        digits = "".join(ch for ch in context if ch.isdigit())
        if digits:
            return int(digits)
    return None


def _organization_ids_from_profiles(profiles: list[dict]) -> list[int]:
    org_ids: list[int] = []
    for profile in profiles:
        if profile.get("appScope") != "org-app":
            continue
        org_id = _parse_context_entity_id(profile.get("context"))
        if org_id is not None:
            org_ids.append(org_id)
    return sorted(set(org_ids))


def _can_view_private_data(token: str, provider_id: int) -> bool:
    session = whois(token)
    profiles = (session or {}).get("profiles") or []
    organization_ids = _organization_ids_from_profiles(profiles)
    return has_handled_org_subscription(
        token,
        provider_id=provider_id,
        organization_ids=organization_ids,
    )


class PublicProviderFormsView(APIView):
    def get(self, request, provider_id):
        token = extract_bearer_token(request)
        if not token:
            return Response({"detail": "missing bearer token"}, status=401)
        claims = validate_token(token)
        if not claims:
            return Response({"detail": "invalid token"}, status=401)
        if not _authorize_provider_third(token, provider_id):
            return Response({"detail": "forbidden for third-party consultation"}, status=403)
        include_private = _can_view_private_data(token, provider_id)
        forms = ProviderForm.objects.filter(provider_id=provider_id).prefetch_related("questions")
        return Response(
            ProviderFormPublicSerializer(
                forms,
                many=True,
                context={"include_private": include_private},
            ).data
        )


class PublicProviderListView(APIView):
    def get(self, request):
        token = extract_bearer_token(request)
        if not token:
            return Response({"detail": "missing bearer token"}, status=401)
        claims = validate_token(token)
        if not claims:
            return Response({"detail": "invalid token"}, status=401)

        session = whois(token)
        profiles = (session or {}).get("profiles") or []
        has_provider_third_profile = any(
            profile.get("appScope") == "provider-app"
            and profile.get("role") == "provider-third"
            for profile in profiles
        )

        providers = Provider.objects.order_by("id")
        if has_provider_third_profile and authorize_request(
            token, required_role="provider-third", context=None
        ):
            return Response(ProviderSerializer(providers, many=True).data)

        visible_provider_ids = []
        for provider in providers:
            if _authorize_provider_third(token, provider.id):
                visible_provider_ids.append(provider.id)
        filtered = Provider.objects.filter(id__in=visible_provider_ids).order_by("name", "id")
        return Response(ProviderSerializer(filtered, many=True).data)


class PublicProviderDetailView(APIView):
    def get(self, request, provider_id):
        token = extract_bearer_token(request)
        if not token:
            return Response({"detail": "missing bearer token"}, status=401)
        claims = validate_token(token)
        if not claims:
            return Response({"detail": "invalid token"}, status=401)
        if not _authorize_provider_third(token, provider_id):
            return Response({"detail": "forbidden for third-party consultation"}, status=403)
        include_private = _can_view_private_data(token, provider_id)
        try:
            provider = Provider.objects.prefetch_related("forms__questions").get(pk=provider_id)
        except Provider.DoesNotExist:
            return Response({"detail": "provider not found"}, status=404)
        payload = ProviderThirdDetailSerializer(provider).data
        payload["private_access_granted"] = include_private
        return Response(payload)


class PublicProviderAnswersView(APIView):
    def get(self, request, provider_id):
        token = extract_bearer_token(request)
        if not token:
            return Response({"detail": "missing bearer token"}, status=401)
        claims = validate_token(token)
        if not claims:
            return Response({"detail": "invalid token"}, status=401)
        if not _authorize_provider_third(token, provider_id):
            return Response({"detail": "forbidden for third-party consultation"}, status=403)
        include_private = _can_view_private_data(token, provider_id)
        forms = ProviderForm.objects.filter(provider_id=provider_id).prefetch_related("questions")
        answers = []
        for form in forms:
            question_qs = form.questions.all() if include_private else form.questions.filter(is_public=True)
            for question in question_qs:
                answers.append(
                    {
                        "private_access_granted": include_private,
                        "provider_id": provider_id,
                        "form_id": form.id,
                        "form_name": form.name,
                        "question_id": question.id,
                        "question_label": question.label,
                        "answer": question.answer,
                        "order": question.order,
                    }
                )
        return Response(answers)


class PublicFormDetailView(APIView):
    def get(self, request, pk):
        try:
            form = ProviderForm.objects.prefetch_related("questions").get(pk=pk)
        except ProviderForm.DoesNotExist:
            return Response({"detail": "form not found"}, status=404)
        token = extract_bearer_token(request)
        if not token:
            return Response({"detail": "missing bearer token"}, status=401)
        claims = validate_token(token)
        if not claims:
            return Response({"detail": "invalid token"}, status=401)
        if not _authorize_provider_third(token, form.provider_id):
            return Response({"detail": "forbidden for third-party consultation"}, status=403)
        include_private = _can_view_private_data(token, form.provider_id)
        return Response(
            ProviderFormPublicSerializer(
                form,
                context={"include_private": include_private},
            ).data
        )
