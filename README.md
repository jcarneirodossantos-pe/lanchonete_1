# Cardápio da Lanchonete


- Python 3.12 ou superior (compatível com a versão Django fixada no projeto)
- Dependências listadas em `requirements.txt`

## Instalação e execução


```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

O painel administrativo fica em <http://127.0.0.1:8000/admin/>. Entre com a conta
criada para cadastrar categorias e produtos.

## Modelos

- **Categoria**: nome obrigatório e único, e descrição opcional.
- **Produto**: nome, preço não negativo, disponibilidade (iniciando como `True`)
  e categoria obrigatória. A categoria pode ser acessada pelo relacionamento
  `categoria.produtos`.

O preço também é protegido por uma restrição no banco. Ao excluir uma categoria,
seus produtos são excluídos junto com ela.

## API

Todos os recursos ficam sob `/api/`. As consultas são públicas; para criar, editar
ou excluir dados, autentique-se. Os endpoints de categorias e produtos oferecem
listar, detalhar, criar, atualizar e excluir.

| Método | Caminho | Uso |
| --- | --- | --- |
| `GET`, `POST` | `/api/categorias/` | Listar ou criar categorias |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/categorias/{id}/` | Consultar ou alterar uma categoria |
| `GET` | `/api/categorias/{id}/produtos/` | Listar produtos da categoria |
| `GET`, `POST` | `/api/produtos/` | Listar ou criar produtos |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/produtos/{id}/` | Consultar ou alterar um produto |
| `POST` | `/api/token/` | Obter um token de acesso |
| `GET` | `/api/schema/` | Obter o documento OpenAPI |
| `GET` | `/api/docs/` | Abrir a documentação Swagger |

Para obter um token, envie as credenciais de uma conta cadastrada:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"seu_usuario","password":"sua_senha"}'
```

Envie o token nas requisições que alteram dados:

```bash
curl http://127.0.0.1:8000/api/produtos/ \
  -H "Authorization: Token SEU_TOKEN"
```

O campo `categoria` recebe o identificador da categoria. As respostas dos produtos
também incluem `categoria_nome`. É possível filtrar disponibilidade, buscar pelo
nome e avançar entre páginas:

```text
/api/produtos/?disponivel=true
/api/produtos/?search=suco
/api/produtos/?page=2
```

A paginação retorna até 10 produtos por página. Se um preço negativo for enviado,
a API responde com erro de validação.

## Testes

Execute os testes automatizados com:

```bash
python manage.py test
```
