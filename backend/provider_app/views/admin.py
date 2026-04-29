from rest_framework.viewsets import ModelViewSet

from ..models import Provider, ProviderForm, Question
from ..serializers import ProviderFormSerializer, ProviderSerializer, QuestionSerializer


class ProviderAdminViewSet(ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer


class ProviderFormAdminViewSet(ModelViewSet):
    queryset = ProviderForm.objects.all()
    serializer_class = ProviderFormSerializer


class QuestionAdminViewSet(ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
