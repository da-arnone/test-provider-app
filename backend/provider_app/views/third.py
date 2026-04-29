from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Provider, ProviderForm
from ..serializers import ProviderFormPublicSerializer, ProviderSerializer
from ..services.auth_client import authorize_request, extract_bearer_token, validate_token


def _provider_contexts(provider_id: int) -> list[str]:
    return [f"provider-{provider_id}", f"provider-{provider_id:03d}"]


def _authorize_provider_third(token: str, provider_id: int) -> bool:
    for context in _provider_contexts(provider_id):
        if authorize_request(token, required_role="provider-third", context=context):
            return True
    return False


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
        forms = ProviderForm.objects.filter(provider_id=provider_id).prefetch_related("questions")
        return Response(ProviderFormPublicSerializer(forms, many=True).data)


class PublicProviderListView(APIView):
    def get(self, request):
        token = extract_bearer_token(request)
        if not token:
            return Response({"detail": "missing bearer token"}, status=401)
        claims = validate_token(token)
        if not claims:
            return Response({"detail": "invalid token"}, status=401)

        providers = Provider.objects.order_by("id")
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
        try:
            provider = Provider.objects.get(pk=provider_id)
        except Provider.DoesNotExist:
            return Response({"detail": "provider not found"}, status=404)
        return Response(ProviderSerializer(provider).data)


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
        forms = ProviderForm.objects.filter(provider_id=provider_id).prefetch_related("questions")
        answers = []
        for form in forms:
            for question in form.questions.filter(is_public=True):
                answers.append(
                    {
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
        return Response(ProviderFormPublicSerializer(form).data)
