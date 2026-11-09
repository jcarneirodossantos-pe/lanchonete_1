import re

import requests
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from .models import Categoria, Produto
from .serializers import CategoriaSerializer, ProdutoSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    @action(detail=True, methods=["get"], url_path="produtos")
    def produtos(self, request, pk=None):
        categoria = self.get_object()
        produtos = Produto.objects.filter(categoria=categoria).select_related("categoria")
        page = self.paginate_queryset(produtos)
        if page is not None:
            serializer = ProdutoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProdutoSerializer(produtos, many=True)
        return Response(serializer.data)


class ProdutoViewSet(viewsets.ModelViewSet):
    serializer_class = ProdutoSerializer
    filter_backends = [SearchFilter]
    search_fields = ["nome"]

    def get_queryset(self):
        produtos = Produto.objects.select_related("categoria").all()
        disponivel = self.request.query_params.get("disponivel")
        if disponivel in {"true", "false"}:
            produtos = produtos.filter(disponivel=(disponivel == "true"))
        return produtos


@api_view(["GET"])
def municipios_por_uf(request):
    uf = (request.query_params.get("uf") or "").strip()
    if not uf:
        return Response(
            {"detail": "O parâmetro 'uf' é obrigatório."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not re.fullmatch(r"[A-Za-z]{2}", uf):
        return Response(
            {"detail": "UF inválida. Informe duas letras, como PE ou SP."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    uf = uf.upper()
    url = (
        "https://servicodados.ibge.gov.br/api/v1/localidades/estados/"
        f"{uf}/municipios"
    )

    try:
        resposta = requests.get(url, timeout=15)
        resposta.raise_for_status()
    except Exception:
        return Response(
            {"detail": "Não foi possível consultar os municípios no momento. Tente novamente mais tarde."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    municipios = [
        {"codigo_ibge": item.get("id"), "nome": item.get("nome")}
        for item in resposta.json()
    ]
    return Response({"total": len(municipios), "municipios": municipios})
