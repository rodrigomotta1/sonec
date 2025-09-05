# sonec

`sonec` é um coletor unificado de postagens de redes sociais com armazenamento canônico baseado em Django ORM e consultas internas via CLI/API — sem arquivos intermediários (CSV) como fluxo principal.


- **O que é:** Pacote Python (CLI e API) que coleta postagens de múltiplos provedores e as persiste em um modelo único. Por padrão, usa SQLite; pode operar com PostgreSQL via `--db` ou `DATABASE_URL` sem mudar a experiência de uso (não testado).  
- **Objetivo:** Reduzir o *overhead* de configuração para pesquisa/análise, oferecendo coleta + armazenamento + consulta direta no próprio `sonec` (consultas são refletidas em SQL no banco, ao invés de buscas manuais em CSVs e/ou Dataframes).  
- **O que não faz:** Download de mídia pesada; *scraping* fora dos escopos suportados; uso principal não é exportar CSV.  
- **Público‑alvo:** Pesquisadores(as), analistas de dados e desenvolvedores que precisam coletar e consultar dados de redes com facilidade.

## Utilização
Requisitos: Python ≥ 3.11.
```bash
# Instalar
pip install sonec

# Inicializar o banco (SQLite local por padrão)
sonec
```

Coleta e consulta são realizadas pela **API Python** (CLI adicional será disponibilizada em versões futuras):
```python
from sonec import api

info = api.configure("sqlite:///./sonec.sqlite3")

api.collect(provider="bluesky", q="evento2025", limit=100)
rows = api.query("posts", provider="bluesky", limit=50)
```

## Contribuição
```bash
# Clonar e instalar em modo desenvolvimento
git clone <URL_DO_REPOSITORIO>
cd sonec
pip install -e .[dev]  # ou: pip install -e .

# Inicialização do banco
sonec

# Execução de exemplos (Bluesky)
python examples/bluesky/collect_and_analyze.py --q "termo" --limit 50
python examples/bluesky/status_e_consulta.py status --provider bluesky
python examples/bluesky/status_e_consulta.py query --provider bluesky --limit 10 --project id,created_at,text
```

## Credenciais (Bluesky): Como obter e configurar

- BSKY_IDENTIFIER: seu identificador de login no Bluesky (handle ou e‑mail). Ex.: `seu‑usuario.bsky.social`.
- BSKY_APP_PASSWORD: App Password criada nas configurações do Bluesky (não é a senha principal).

Como obter a App Password:
- Acesse `https://bsky.app` e faça login.
- Vá em Settings → App passwords → Create app password.
- Dê um nome (ex.: "sonec") e copie o valor no formato `xxxx-xxxx-xxxx-xxxx`.

Como configurar no ambiente:
- Windows PowerShell (sessão atual):
  - `$env:BSKY_IDENTIFIER = "seu-handle.bsky.social"`
  - `$env:BSKY_APP_PASSWORD = "xxxx-xxxx-xxxx-xxxx"`
- Linux/macOS (bash/zsh):
  - `export BSKY_IDENTIFIER="seu-handle.bsky.social"`
  - `export BSKY_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"`

Observações:
- Utilize sempre uma App Password (pode ser revogada a qualquer momento), não a senha principal.
- Se preferir persistência no Windows, use `setx` e abra um novo terminal antes de executar os exemplos.

---

> Consulte a Wiki do projeto para cenários de uso, arquitetura, modelo de dados, glossário e manual detalhado.


