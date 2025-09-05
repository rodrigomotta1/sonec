# django-sonec — Social Network Collectors

Pacote Django plugável para coleta genérica de posts em redes sociais. O projeto é focado nas postagens e extensível para outros provedores de postagens.


## Contexto
Objetivo: oferecer uma base mínima para ingestão e armazenamento de posts com foco em idempotência e modelo de dados enxuto.

## Requisitos
- Python >= 3.11
- Django >= 5.0, < 6.0
- Django REST Framework >= 3.15, < 4.0
- Requests >= 2.31, < 3.0

Extras opcionais (fila/worker): `celery`, `rq`, `dramatiq` (com `redis`).
Extras de desenvolvimento: `pytest`, `ruff`, `black`, `isort`, `requests-mock`.

## Instalação
Instale a partir do repositório (recomendado utilizar um ambiente virtual):

```bash
git clone <URL_DO_REPO> && cd sonec
pip install -e .

# opcional
pip install -e .[dev]
```

## Configuração inicial
Adicione o app e rode as migrações:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "sonec",
]
```

```bash
python manage.py migrate
```

Se desejar expor a API REST, inclua as rotas:

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    path("api/sonec/", include("sonec.api.urls")),
]
```

## Licença
MIT. Veja o arquivo de licença do repositório.

