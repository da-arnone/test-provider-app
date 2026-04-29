from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import ProviderForm
from ..serializers import ProviderFormPublicSerializer
from ..services.auth_client import authorize_request, extract_bearer_token, validate_token


def _require_provider_third_access(request, context=None):
    token = extract_bearer_token(request)
    if not token:
        return Response({"detail": "missing bearer token"}, status=401)
    claims = validate_token(token)
    if not claims:
        return Response({"detail": "invalid token"}, status=401)
    if not authorize_request(token, required_role="provider-third", context=context):
        return Response({"detail": "forbidden for third-party consultation"}, status=403)
    return None


class PublicProviderFormsView(APIView):
    def get(self, request, provider_id):
        error = _require_provider_third_access(request, context=f"provider-{provider_id:03d}")
        if error:
            return error
        forms = ProviderForm.objects.filter(provider_id=provider_id).prefetch_related("questions")
        return Response(ProviderFormPublicSerializer(forms, many=True).data)


class PublicFormDetailView(APIView):
    def get(self, request, pk):
        try:
            form = ProviderForm.objects.prefetch_related("questions").get(pk=pk)
        except ProviderForm.DoesNotExist:
            return Response({"detail": "form not found"}, status=404)
        error = _require_provider_third_access(
            request, context=f"provider-{form.provider_id:03d}"
        )
        if error:
            return error
        return Response(ProviderFormPublicSerializer(form).data)
