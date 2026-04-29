from django.db import models


class Provider(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self) -> str:
        return self.name


class ProviderForm(models.Model):
    provider = models.ForeignKey(
        Provider,
        related_name="forms",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["provider_id", "name", "id"]

    def __str__(self) -> str:
        return f"{self.provider_id} - {self.name}"


class Question(models.Model):
    form = models.ForeignKey(
        ProviderForm,
        related_name="questions",
        on_delete=models.CASCADE,
    )
    label = models.CharField(max_length=255)
    answer = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.label
