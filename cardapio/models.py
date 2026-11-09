from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=150)
    preco = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    disponivel = models.BooleanField(default=True)
    categoria = models.ForeignKey(
        Categoria,
        related_name="produtos",
        on_delete=models.PROTECT,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(preco__gte=0),
                name="produto_preco_nao_negativo",
            ),
        ]

    def __str__(self):
        return self.nome


class AreaEntrega(models.Model):
    municipio = models.CharField(max_length=150)
    codigo_ibge = models.PositiveIntegerField(unique=True)
    taxa_entrega = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = "Área de entrega"
        verbose_name_plural = "Áreas de entrega"

    def __str__(self):
        return f"{self.municipio} ({self.codigo_ibge})"
