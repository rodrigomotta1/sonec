# sonec

Coletor unificado de postagens de redes sociais com **armazenamento canônico** (Django ORM) e **consultas internas** via CLI/API — sem arquivos intermediários (CSV) como fluxo principal.

## O que é, objetivo, o que **não** faz e público‑alvo
**O que é.** Pacote Python (CLI e API) que coleta postagens de múltiplos provedores e as persiste em um **modelo único**. Por padrão, usa **SQLite**; pode operar com **PostgreSQL** via `--db` ou `DATABASE_URL` sem mudar a experiência de uso.  
**Objetivo.** Reduzir o overhead de configuração para pesquisa/análise, oferecendo coleta + armazenamento + **consulta direta** no próprio sonec.  
**Não faz.** Download de mídia pesada; *scraping* fora dos escopos suportados; uso principal **não** é exportar CSV.  
**Público‑alvo.** Pesquisadores(as), analistas de dados e desenvolvedores que precisam coletar e **consultar** dados de redes com baixa fricção.

## Como começar (usuários)
Requisitos: Python ≥ 3.11.
```bash
# Instalar e inicializar
pip install sonec
sonec init
sonec status

# Coletar (ex.: Bluesky por escopo)
sonec collect bluesky --source evento2025 --since 2025-05-01

# Consultar diretamente (sem arquivos intermediários)
sonec query posts --provider bluesky --since 2025-05-01 --limit 50

# Dicas: sempre filtre por --provider e por janela temporal.
# Opcional: usar PostgreSQL mantendo a mesma CLI
sonec status --db postgresql://user:pass@host:5432/sonec
# ou exporte DATABASE_URL no ambiente
```
Consultas também podem ser feitas pela **API Python** (objetos/iteráveis ORM):
```python
import sonec
sonec.collect(provider="bluesky", source="evento2025", since="2025-05-01", limit=100)
rows = sonec.query("posts", provider="bluesky", since="2025-05-01", limit=50)
```

## Como desenvolver (devs)
```bash
# Clonar e instalar em modo desenvolvimento
git clone <URL_DO_REPOSITORIO>
cd sonec
pip install -e .[dev]  # ou: pip install -e .

# Teste rápido de ponta a ponta
sonec init
sonec collect bluesky --source exemplo --limit 10
sonec query posts --provider bluesky --limit 5
```

### Providers (extensão)
- Implementar o contrato mínimo do coletor: `configure(...)`, `fetch_since(cursor, limit, **filtros)` e **normalização** para o modelo canônico (`Post`, `Author`, `Media`, etc.).  
- Registrar o nome do provider no **registry** do sonec para habilitar `sonec collect <nome>` e `sonec query --provider <nome>`.

### Boas práticas
- Deduplicação garantida por `UNIQUE(provider, external_id)`; a ingestão deve respeitar essa chave.  
- Consultas internas com filtros mínimos (`provider` e/ou intervalo `created_at`) e **paginação por keyset** (em vez de `OFFSET`) para conjuntos grandes.

---

> Consulte a Wiki do projeto para cenários de uso, arquitetura, modelo de dados, glossário e manual detalhado.
