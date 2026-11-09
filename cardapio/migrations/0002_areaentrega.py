from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cardapio", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AreaEntrega",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("municipio", models.CharField(max_length=150)),
                ("codigo_ibge", models.PositiveIntegerField(unique=True)),
                (
                    "taxa_entrega",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=8,
                        validators=[MinValueValidator(0)],
                    ),
                ),
            ],
            options={
                "verbose_name": "Área de entrega",
                "verbose_name_plural": "Áreas de entrega",
            },
        ),
    ]
