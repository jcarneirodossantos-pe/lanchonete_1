from rest_framework.routers import DefaultRouter

from .views import CategoriaViewSet, ProdutoViewSet

router = DefaultRouter()
router.register("categorias", CategoriaViewSet)
router.register("produtos", ProdutoViewSet, basename="produto")

urlpatterns = router.urls
