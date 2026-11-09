from django.contrib import admin

from .models import AreaEntrega, Categoria, Produto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao")
    search_fields = ("nome",)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco", "disponivel", "categoria")
    list_filter = ("disponivel", "categoria")
    search_fields = ("nome",)
    autocomplete_fields = ("categoria",)


@admin.register(AreaEntrega)
class AreaEntregaAdmin(admin.ModelAdmin):
    list_display = ("municipio", "codigo_ibge", "taxa_entrega")
    search_fields = ("municipio",)
    list_filter = ("codigo_ibge",)
