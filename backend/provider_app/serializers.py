from rest_framework import serializers

from .models import Provider, ProviderForm, Question


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ["id", "name"]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "form", "label", "answer", "is_public", "order"]
        read_only_fields = ["id"]


class QuestionAnswerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["answer"]


class PublicQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "label", "answer", "order"]


class ProviderFormSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = ProviderForm
        fields = ["id", "provider", "name", "description", "questions"]
        read_only_fields = ["id"]


class ProviderFormPublicSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = ProviderForm
        fields = ["id", "provider", "name", "description", "questions"]

    def get_questions(self, obj):
        public_questions = obj.questions.filter(is_public=True)
        return PublicQuestionSerializer(public_questions, many=True).data
