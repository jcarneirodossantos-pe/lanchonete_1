from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CategoriaViewSet, ProdutoViewSet, municipios_por_uf

router = DefaultRouter()
router.register("categorias", CategoriaViewSet)
router.register("produtos", ProdutoViewSet, basename="produto")

urlpatterns = [
    path("municipios/", municipios_por_uf, name="municipios-por-uf"),
    *router.urls,
]
