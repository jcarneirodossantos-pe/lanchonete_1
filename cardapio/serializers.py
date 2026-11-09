import requests
from rest_framework import serializers

from .models import AreaEntrega, Categoria, Produto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nome", "descricao"]


class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source="categoria.nome", read_only=True)
    preco = serializers.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        model = Produto
        fields = ["id", "nome", "preco", "disponivel", "categoria", "categoria_nome"]

    def validate_preco(self, value):
        if value < 0:
            raise serializers.ValidationError("O preço não pode ser negativo.")
        return value


class AreaEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaEntrega
        fields = ["id", "municipio", "codigo_ibge", "taxa_entrega"]

    def _consultar_ibge(self, codigo_ibge):
        url = (
            "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/"
            f"{codigo_ibge}"
        )
        try:
            resposta = requests.get(url, timeout=15)
            resposta.raise_for_status()
        except Exception:
            raise serializers.ValidationError(
                "Não foi possível validar o código IBGE no momento. Tente novamente."
            )

        dados = resposta.json()
        if not isinstance(dados, dict) or "id" not in dados or "nome" not in dados:
            raise serializers.ValidationError("Código IBGE inválido ou não encontrado.")
        return dados

    def validate_codigo_ibge(self, value):
        self._consultar_ibge(value)
        return value

    def validate(self, attrs):
        codigo_ibge = attrs.get("codigo_ibge")
        municipio = (attrs.get("municipio") or "").strip()

        if codigo_ibge is None:
            return attrs

        dados = self._consultar_ibge(codigo_ibge)
        nome_ibge = (dados.get("nome") or "").strip()
        if municipio and nome_ibge and municipio.lower() != nome_ibge.lower():
            raise serializers.ValidationError(
                {"municipio": "O município informado não corresponde ao código IBGE informado."}
            )

        return attrs
