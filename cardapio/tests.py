from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.test import TestCase
from rest_framework import serializers
from rest_framework.test import APIClient

from .models import AreaEntrega, Categoria, Produto
from .serializers import AreaEntregaSerializer


class CardapioApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.categoria = Categoria.objects.create(nome="Lanches")

    def autenticar(self):
        usuario = get_user_model().objects.create_user(
            username="gerente",
            password="senha-segura",
        )
        resposta = self.client.post(
            "/api/token/",
            {"username": "gerente", "password": "senha-segura"},
            format="json",
        )
        self.assertEqual(resposta.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {resposta.data['token']}")

    def test_models_exibem_nome_e_categoria_tem_relacionamento_reverso(self):
        produto = Produto.objects.create(
            nome="X-salada",
            preco=Decimal("18.50"),
            categoria=self.categoria,
        )

        self.assertEqual(str(self.categoria), "Lanches")
        self.assertEqual(str(produto), "X-salada")
        self.assertEqual(self.categoria.produtos.get(), produto)
        self.assertTrue(produto.disponivel)

    def test_leitura_publica_e_escrita_protegida(self):
        resposta = self.client.get("/api/categorias/")
        self.assertEqual(resposta.status_code, 200)

        resposta = self.client.post(
            "/api/categorias/",
            {"nome": "Bebidas", "descricao": ""},
            format="json",
        )
        self.assertEqual(resposta.status_code, 401)

    def test_token_permite_crud_e_preco_negativo_e_rejeitado(self):
        self.autenticar()

        resposta = self.client.post(
            "/api/produtos/",
            {
                "nome": "Suco",
                "preco": "-1.00",
                "disponivel": True,
                "categoria": self.categoria.id,
            },
            format="json",
        )
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("preco", resposta.data)

        resposta = self.client.post(
            "/api/produtos/",
            {
                "nome": "Suco",
                "preco": "8.50",
                "disponivel": True,
                "categoria": self.categoria.id,
            },
            format="json",
        )
        self.assertEqual(resposta.status_code, 201)
        produto_id = resposta.data["id"]
        self.assertEqual(resposta.data["categoria_nome"], "Lanches")

        resposta = self.client.get(f"/api/produtos/{produto_id}/")
        self.assertEqual(resposta.status_code, 200)

        resposta = self.client.put(
            f"/api/produtos/{produto_id}/",
            {
                "nome": "Suco natural",
                "preco": "9.00",
                "disponivel": False,
                "categoria": self.categoria.id,
            },
            format="json",
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data["nome"], "Suco natural")

        resposta = self.client.delete(f"/api/produtos/{produto_id}/")
        self.assertEqual(resposta.status_code, 204)

    def test_filtro_busca_paginacao_e_nome_da_categoria(self):
        for indice in range(11):
            Produto.objects.create(
                nome=f"Sanduiche {indice}",
                preco=Decimal("15.00"),
                disponivel=True,
                categoria=self.categoria,
            )
        Produto.objects.create(
            nome="Sanduiche indisponivel",
            preco=Decimal("15.00"),
            disponivel=False,
            categoria=self.categoria,
        )

        resposta = self.client.get(
            "/api/produtos/?disponivel=true&search=Sanduiche"
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data["count"], 11)
        self.assertEqual(len(resposta.data["results"]), 10)
        self.assertEqual(resposta.data["results"][0]["categoria_nome"], "Lanches")

        resposta = self.client.get("/api/produtos/?disponivel=false")
        self.assertEqual(resposta.data["count"], 1)

    def test_categoria_lista_seus_produtos(self):
        Produto.objects.create(
            nome="Suco",
            preco=Decimal("8.50"),
            categoria=self.categoria,
        )

        resposta = self.client.get(
            f"/api/categorias/{self.categoria.id}/produtos/"
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data["count"], 1)
        self.assertEqual(resposta.data["results"][0]["nome"], "Suco")

    def test_categoria_com_produtos_nao_pode_ser_excluida(self):
        Produto.objects.create(
            nome="Suco",
            preco=Decimal("8.50"),
            categoria=self.categoria,
        )

        with self.assertRaises(ProtectedError):
            self.categoria.delete()

    @patch("cardapio.views.requests.get")
    def test_municipios_por_uf_consulta_api_do_ibge(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.json.return_value = [
            {"id": 2611606, "nome": "Recife"},
            {"id": 2611705, "nome": "Jaboatão dos Guararapes"},
        ]

        resposta = self.client.get("/api/municipios/?uf=PE")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data["total"], 2)
        self.assertEqual(resposta.data["municipios"][0]["nome"], "Recife")
        mock_get.assert_called_once_with(
            "https://servicodados.ibge.gov.br/api/v1/localidades/estados/PE/municipios",
            timeout=15,
        )

    def test_municipios_retorna_400_quando_uf_vazia_ou_invalida(self):
        resposta = self.client.get("/api/municipios/")
        self.assertEqual(resposta.status_code, 400)

        resposta = self.client.get("/api/municipios/?uf=PE123")
        self.assertEqual(resposta.status_code, 400)

    @patch("cardapio.views.requests.get")
    def test_municipios_retorna_503_quando_ibge_fora_do_ar(self, mock_get):
        mock_get.side_effect = Exception("timeout")

        resposta = self.client.get("/api/municipios/?uf=PE")

        self.assertEqual(resposta.status_code, 503)
        self.assertIn("Não foi possível consultar os municípios", resposta.data["detail"])

    @patch("cardapio.serializers.requests.get")
    def test_serializer_area_entrega_valida_codigo_ibge_real(self, mock_get):
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.json.return_value = {"id": 2611606, "nome": "Recife"}

        serializer = AreaEntregaSerializer(
            data={
                "municipio": "Recife",
                "codigo_ibge": 2611606,
                "taxa_entrega": "8.50",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    @patch("cardapio.serializers.requests.get")
    def test_serializer_area_entrega_rejeita_codigo_ibge_invalido(self, mock_get):
        mock_get.return_value.raise_for_status.side_effect = Exception("err")

        serializer = AreaEntregaSerializer(
            data={
                "municipio": "Cidade Inexistente",
                "codigo_ibge": 9999999,
                "taxa_entrega": "8.50",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("codigo_ibge", serializer.errors)

    def test_documentacao_openapi_e_swagger_estao_disponiveis(self):
        resposta_schema = self.client.get("/api/schema/")
        self.assertEqual(resposta_schema.status_code, 200)
        self.assertIn("/api/produtos/", resposta_schema.data["paths"])

        resposta_swagger = self.client.get("/api/docs/")
        self.assertEqual(resposta_swagger.status_code, 200)
