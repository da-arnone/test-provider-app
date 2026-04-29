from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Provider",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
            ],
            options={"ordering": ["name", "id"]},
        ),
        migrations.CreateModel(
            name="ProviderForm",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "provider",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="forms", to="provider_app.provider"),
                ),
            ],
            options={"ordering": ["provider_id", "name", "id"]},
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(max_length=255)),
                ("answer", models.TextField(blank=True)),
                ("is_public", models.BooleanField(default=False)),
                ("order", models.PositiveIntegerField(default=0)),
                (
                    "form",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="provider_app.providerform"),
                ),
            ],
            options={"ordering": ["order", "id"]},
        ),
    ]
