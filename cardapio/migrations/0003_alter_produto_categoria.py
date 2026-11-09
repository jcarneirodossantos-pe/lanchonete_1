import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cardapio", "0002_areaentrega"),
    ]

    operations = [
        migrations.AlterField(
            model_name="produto",
            name="categoria",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="produtos",
                to="cardapio.categoria",
            ),
        ),
    ]
