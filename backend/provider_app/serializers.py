from rest_framework import serializers

from .models import Provider, ProviderForm, Question


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ["id", "name"]


class ProviderThirdDetailSerializer(ProviderSerializer):
    """Third-party provider detail: public-safe + metadata about private data (no private answers)."""

    private_data_summary = serializers.SerializerMethodField()

    class Meta(ProviderSerializer.Meta):
        fields = ["id", "name", "private_data_summary"]

    def get_private_data_summary(self, obj):
        forms = obj.forms.prefetch_related("questions").all()
        private_question_count = 0
        forms_detail = []
        for form in forms:
            priv_qs = form.questions.filter(is_public=False)
            cnt = priv_qs.count()
            private_question_count += cnt
            if cnt:
                forms_detail.append(
                    {
                        "form_id": form.id,
                        "form_name": form.name,
                        "private_question_count": cnt,
                        "private_question_labels": list(priv_qs.values_list("label", flat=True)),
                    }
                )
        return {
            "has_private_data": private_question_count > 0,
            "private_question_count": private_question_count,
            "forms_with_private_questions": forms_detail,
        }


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
    private_access_granted = serializers.SerializerMethodField()

    class Meta:
        model = ProviderForm
        fields = ["id", "provider", "name", "description", "private_access_granted", "questions"]

    def get_private_access_granted(self, _obj):
        return bool(self.context.get("include_private"))

    def get_questions(self, obj):
        include_private = bool(self.context.get("include_private"))
        questions = obj.questions.all() if include_private else obj.questions.filter(is_public=True)
        serializer_class = QuestionSerializer if include_private else PublicQuestionSerializer
        return serializer_class(questions, many=True).data
