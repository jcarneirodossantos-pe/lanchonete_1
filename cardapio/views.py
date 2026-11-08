from rest_framework import viewsets
from rest_framework.decorators import action
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
