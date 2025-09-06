# sonec: Social Network Collectors

## Descrição inicial

O `sonec` é um pacote Python baseado em Django destinado à coleta de postagens de redes sociais e ao armazenamento em modelo canônico, simplificando o acesso posterior para análise. O objetivo é reduzir o esforço de configuração normalmente necessário para definir persistência e consultas. A arquitetura visa uma experiência de início rápido, com configuração mínima.

### Funções específicas relevantes
- Coleta por meio de providers. Na versão atual, há implementação para o Bluesky; novos providers podem ser adicionados seguindo o contrato do projeto.

- Persistência automática e transparente dos dados em um banco de dados SQLite (ou outro banco compatível com Django).

- CLI em evolução (não estável). Recomenda‑se utilizar a API Python para inicialização e demais operações; comandos adicionais serão incorporados em versões futuras.

- API Python que permite integrar coletores e dados em scripts e outros sistemas.

- Mecanismos internos de deduplicação e rastreamento de cursores. Exportação em arquivos não constitui o fluxo principal.

### Usuários alvo
Destina-se a pesquisadoras(es), analistas de dados e desenvolvedoras(es) interessados em coletar e organizar dados de redes sociais de forma unificada, com baixa barreira de entrada e sem necessidade de configurar manualmente bancos ou pipelines complexos.

### Natureza do programa
O `sonec` é uma ferramenta utilitária modular, com potencial de evolução para uma biblioteca mais ampla de coletores. A versão atual constitui uma prova de conceito estruturada para coleta unificada de postagens, utilizável em cenários reais de pesquisa e prototipagem.

### Ressalvas
- A implementação atual cobre o provider Bluesky. O endpoint público pode impor restrições e exigir autenticação; o provider suporta autenticação via App Password. A coleta em outras redes requer a implementação de providers específicos.

- O desempenho é adequado para pequena e média escala. Para cargas muito grandes, recomenda-se utilizar bancos mais robustos (por exemplo, PostgreSQL) e aplicar otimizações adicionais (índices e ajustes de consulta).

- A persistência padrão é em SQLite, o que simplifica a instalação mas não é ideal para ambientes de produção de grande porte.

- O projeto está em estágio inicial e sujeito a alterações na API, CLI e modelo de dados.


## Visão de projeto
Esta seção inclui cenários de uso, positivo e negativos, seguindo o proposto pelo [artigo de Carroll](https://pdf.sciencedirectassets.com/271616/1-s2.0-S0953543800X00276/1-s2.0-S0953543800000230/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEBEaCXVzLWVhc3QtMSJIMEYCIQDenZ9gGsrTl3mz5G01PT8ZCj5LyQ%2F%2BgqPPvVDeIe1QUgIhAKgaCSaE2GsPLjZyLRLIl5LqWShYpWduVPiJ11NjGHaCKrMFCHoQBRoMMDU5MDAzNTQ2ODY1Igwtn067Hkf7G5RJnAEqkAXgxTyiBi7HIiH%2B2I1H6VpF%2Bh3kKpqKDAjOh18GMuXv7q3%2BE%2F03srxKrgRgEhZOCEZINGyPAbVEc1UPavNNBcRSfRQbZDotM7VFhe3nRRFrTPxgKTtUim1McgCacFxKf3IE0Vil%2BypPKcaI1kt2TWsFG%2BBvTpYzLd0Dh4AjFZ81RanwgwrgHH%2BJRe6rgASwAM5X8PQN%2BMKOJqJnJpYfDlNm8a67oOmtR%2BxTimI%2BnLI4ZahaB3wtQ9hRk5cI2sBG9DKuvX9gzmYeXupyW1PL9BGjFLHipLYWlt6byZ%2F9LBlDey5dwQl1gYveNZCozoVnT372wPqAXJuJRj692zwHUahNP7e7%2FieDut%2BspdDL5fMjGyW1BAT5x0sYlm6P07a337gOS7wo0oJ4ZpPBB5gIlXaUfjJoeNiiJsG89qWjR%2FBY6noSvpZxtVD7lo%2Bzd7IfrY7E1Kw9g9Wz0KOyTp1QTBeP2isV9sM3d7f%2FLMEePLK8MfMnQR0FP%2B6bkOLEtOsLeKjfzEcRZYUJ997KJ6zeW4onnzL%2BZ3JFhOReJsUgfWyMzqCWBRlrMFeNmpuluE%2F4dquX1PbpK%2Boa8R4rkL%2BQ9goBrJdvfuvkkC8OhF6QDoYM7zCn8dzJuFB7DVTY%2Fwhsjp9tB13z%2F8emjqBYHd2Gw%2ByZDgmC56Yyt5omF48yFOWIC3cV1F4zQL%2Fv2et2TGoR7iXqvDBU%2Fw0uzvlMJiuAiicqjx7TC6lTAVxDFqWHZGRFjmL4BJHO2pnNqRwEK0PoWu23KwL1vaGXm9UgEcf8MwuOCwYwHgz%2BQMg68ZX%2FShhgfGMAdbEdEeOlzIEvtKEv2Og4bPWp582iR66AEc7o3JV3iEphXRwKUNTAWWvoZNzH7TDdpuzFBjqwAVknTQ9tsu6P3W1XH49H7ii%2BJ%2F3hvbejGg2%2BtPb89dc%2F16Tv8gkS7nuaPdntzyQmM3B%2FOI9UqaDWgjK64RJ94l9788v2aW5JSzAv5ujif%2FF1CKsYnkNb6ZEOYfdHRyqAxFrPGsm6omqGnKRJ6aUYJ1uJ8TlMTH3HyBwfe1cg%2FriGh%2B77C31L0BMmviCCQIXtrle8liPiF%2F6pckxpI95slSdfbKGkdeHJHELq0OQf0EYf&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250905T170346Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTYTNFX5LHS%2F20250905%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=339fe31d1b79b78cb29c7fe1881df5e39d9b5c2bf9e2923b75117c22543db4fe&hash=a48cdb5aaa9c476d9f2f6c5069055e7db84f266023832613698308abc5793fd5&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S0953543800000230&tid=spdf-5e296463-fe25-4757-bbed-5b5895f496f3&sid=df3370593777e242f57bb0904f7dfcb3e892gxrqa&type=client&tsoh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&rh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&ua=181d5751065052045756&rr=97a74d49cf63e29d&cc=br)

### Cenário Positivo 1 — Pesquisadora em Comunicação

Uma pesquisadora de comunicação precisa analisar postagens do Bluesky relacionadas a um evento político. Ela prepara o ambiente de dados por meio da API Python, realiza uma coleta orientada por termo de busca e, em seguida, consulta o repositório canônico para obter os registros normalizados mais recentes. Os resultados são acessados diretamente como objetos/linhas projetadas via ORM, prontos para análise estatística, sem a necessidade de exportações intermediárias.

### Cenário Positivo 2 — Desenvolvedor Extensível

Um desenvolvedor deseja trabalhar com dados de uma rede ainda não suportada oficialmente. Com base no contrato de provider, ele implementa um conector para a nova rede, realiza o registro no mecanismo interno de providers e valida a coleta e a consulta por meio da API Python. Os dados passam a ser normalizados segundo o modelo canônico e ficam imediatamente disponíveis para análise, sem manipulação direta do banco.

### Cenário Negativo 1 — Escala além do planejado

Uma pesquisadora sênior da comunicação social decide usar o sonec para coletar dezenas de milhões de postagens em múltiplos provedores. Ela roda a coleta em seu notebook, mas logo nota lentidão nas consultas devido às limitações do SQLite. A documentação já a orienta: em cenários de grande volume é esperado configurar o sonec para apontar para um banco PostgreSQL, garantindo melhor escalabilidade e performance. Sem isso, as consultas continuam funcionando, mas podem ficar muito lentas.

### Cenário Negativo 2 — Uso inesperado de API

Um estudante de informática, tenta usar o sonec para coletar vídeos completos do YouTube. Ele executa a coleta utilizando o *provider* do YouTube, esperando baixar a mídia, mas recebe uma mensagem clara de erro: o programa informa que apenas metadados das postagens estão disponíveis para consulta, e não os arquivos de mídia. Carlos compreende a limitação e redireciona seu esforço para analisar títulos, descrições e estatísticas, usando o sonec para consultas de dados estruturados.

## Requisitos
Esta seção lista os requisitos funcionais e não-funcionais especificados pro projeto

### Requisitos funcionais
- **RF01:** O sistema deve permitir a coleta de postagens de diferentes redes sociais por meio de *providers* especializados
- **RF02:** Inicialmente, o sistema deve dar suporte à coleta e armazenamento de postagens realizadas na rede Bluesky
- **RF03:** A coleta deve registrar também metadados relevantes como autor, data de publicação, métricas de engajamento, e qualquer outra informação adicional que estiver disponível em cada rede
- **RF04:** O sistema deve persistir postagens coletadas em um modelo canônico único, independente do provedor
- **RF05:** O sistema deve oferecer meios de consulta ao banco de dados que persiste os dados coletados de cada rede
- **RF06:** O sistema deve oferecer meios de observar o status de execuções de coleta (jobs) e o volume de dados corrente
- **RF07:** O sistema deve expor funções para integração com scripts externos, visando facilidade de uso em diferentes ambientes de pesquisa
- **RF08:** Os resultados de consultas sobre o banco devem ser retornados como objetos Python/Django, de forma que o usuário possa posteriormente decidir o que fazer com os dados retornados
- **RF09:** O sistema deve registrar cursores de coleta para suportar coletas incrementais
- **RF10:** Cada *job* de coleta deve ser identificado, armazenando estatísticas da coleta, como tempo estimado, tempo passado, volume de itens, status e falhas.
- **RF11:** O sistema deve permitir consultas sobre entidades canônicas via API, abstraindo manipulação direta do banco (comandos de CLI adicionais estão planejados)
- **RF12:** As consultas devem recomendar, no mínimo, um filtro por provider e/ou uma janela temporal. A API permite maior flexibilidade; futuras superfícies de CLI podem impor essas restrições por padrão

### Requisitos Não-Funcionais
- **RNF01:** O sistema deve ser portável, funcionando de forma autônoma em qualquer máquina com Python ≥ 3.11 e dependências instaladas.
- **RNF02:** O banco SQLite deve ser inicializado automaticamente, sem configuração manual do usuário.
- **RNF03:** A arquitetura deve ser extensível, permitindo criação de novos providers de forma modular.
- **RNF04:** O sistema deve suportar até centenas de milhares de registros com desempenho razoável em SQLite.
- **RNF05:** A CLI deve ser simples e clara, com comandos intuitivos e mensagens de erro compreensíveis.
- **RNF06:** A API deve seguir convenções Python, com funções diretas e bem documentadas.
- **RNF07:** Os processos de coleta devem ser transacionais, garantindo que falhas não corrompam o banco.
- **RNF08:** A deduplicação deve ser reforçada por *constraints* no banco e lógica de ingestão.
- **RNF09:** O código deve seguir boas práticas de modularidade, separando núcleo, provedores e interfaces (CLI/API).
- **RNF10:** Deve haver documentação mínima para orientar contribuições de novos providers.

## Documentação técnica
Esta seção contempla documentações mais detalhadas sobre arquitetura, organização e funcionamento do sistema

### Visão integrada
O sonec organiza a coleta, normalização, persistência e consulta de postagens por meio de um núcleo de domínio (core) que orquestra providers especializados. Na versão atual, a inicialização do ambiente, a coleta, o status e a consulta são realizados pela API Python (ou pelos scripts de exemplo). As consultas operam diretamente sobre o repositório canônico via ORM do Django, sem necessidade de arquivos intermediários. O core aplica deduplicação, mantém cursores incrementais e registra jobs de coleta. A persistência padrão é em SQLite com inicialização autônoma.

### Módulos e responsabilidades
Esta seção resume, de forma direta, o que cada módulo faz.

- `sonec/api.py` (API Python): ponto de integração para scripts.
  - `configure(db_url)`: configura o Django e o banco (SQLite por padrão).
  - `collect(...)`: chama o provider, converte itens para o modelo canônico e grava no banco; atualiza `Cursor` e `FetchJob`.
  - `query("posts", ...)`: retorna posts ordenados por recência com paginação por keyset.
  - `status(...)`: retorna um resumo de cursores e jobs recentes.
- `sonec/core/models.py`: define o esquema canônico (tabelas, chaves e índices) e migrações do Django.
- `sonec/providers/base.py`: define o contrato de provider, estruturas canônicas e exceções padronizadas.
- `sonec/providers/registry.py`: registra e resolve providers por nome.
- `sonec/providers/bluesky.py`: provider do Bluesky (busca por termo e feed de autor); suporta autenticação via App Password quando disponível.
- `sonec/utils/time.py`: análise e formatação de timestamps (UTC/RFC 3339).
- `sonec/utils/pagination.py`: codificação/decodificação de tokens de paginação por keyset (`after_key`).
- `sonec/cli.py` (opcional/experimental): interface de linha de comando em evolução; recomenda‑se usar a API.

Diagrama de organização (módulos implementados)

```mermaid
flowchart LR
  %% API
  api_cfg["sonec.api.configure"]
  api_col["sonec.api.collect"]
  api_qry["sonec.api.query"]
  api_st["sonec.api.status"]

  %% Core / ORM / Utils
  core_models["sonec.core.models"]
  util_time["sonec.utils.time"]
  util_pag["sonec.utils.pagination"]
  db["Django ORM / sqlite3"]

  %% Providers
  prov_reg["sonec.providers.registry"]
  prov_base["sonec.providers.base"]
  prov_bsky["sonec.providers.bluesky.BlueskyProvider"]

  %% Ligações
  api_cfg --> core_models
  api_col --> prov_reg
  prov_reg --> prov_bsky
  api_col --> core_models
  api_qry --> core_models
  api_st  --> core_models
  core_models --> db

  %% Utilidades usadas por API/Providers
  api_qry -. keyset .- util_pag
  api_qry -. tempo .- util_time
  prov_bsky -. tempo .- util_time
```

### Entidades principais
A modelagem canônica busca representar postagens e metadados de forma uniforme, independentemente do provedor de origem. A seguir, descrevem-se as entidades, seus propósitos, atributos essenciais e invariantes de integridade.

- **Provider**
Identifica a rede de origem e suas capacidades operacionais, mantendo o vínculo conceitual dos dados.
  - `name` (identificador lógico)
  - `version`
  - `capabilities` (indicador de funcionalidades disponíveis)

- **Source**
Define o escopo de coleta por provedor (por exemplo, handle, termo de busca, lista). A unicidade do par (`provider`, `descriptor`) assegura associação inequívoca a um escopo.
  - `provider` (FK), 
  - `external_id` ou `descriptor` (identidade no provedor), 
  - `label` (descrição).


- **Author**
Registra a autoria de forma canônica. Deve existir antes da criação do `Post` que o referencia; unicidade por (`provider`, `external_id`).
    - `provider` (FK)
    - `external_id`, 
    - `handle`, 
    - `display_name`, 
    - `metadata` (JSON).

- **Post**
Entidade central que representa a postagem e seus metadados essenciais. Deduplicação por `UNIQUE(provider, external_id)`; `created_at` em UTC; referência válida a `Author`.
Índices mínimos: (`provider`, `created_at` DESC) e (`author`, `created_at` DESC).
  - `id` (BigAuto), 
  - `provider` (FK), 
  - `external_id` (único por provedor), 
  - `author` (FK Author), 
  - `text`, 
  - `lang`, 
  - `created_at` (UTC), 
  - `collected_at` (UTC), 
  - `metrics` (JSON), 
  - `entities` (JSON com hashtags, links, menções).

- **Media**
Armazena metadados de mídia associada a um `Post`. Não armazena binários; registra referência e descrição.
  - `post` (FK), 
  - `kind` (imagem, vídeo, etc.), 
  - `url`, 
  - `metadata` (JSON).

- **FetchJob**
Registra execuções de coleta para diagnóstico e auditoria. Deve manter integridade temporal (início ≤ fim quando concluído) e consistência com o cursor correspondente.
  - `id`, 
  - `provider`, 
  - `source`, 
  - `started_at`, 
  - `finished_at`, 
  - `status`, 
  - `stats` (JSON com inseridos, conflitos, janelas temporais).

- **Cursor**
Controla a coleta incremental, garantindo continuidade e evitando lacunas (avanço monotônico; o cursor não retrocede sem ação corretiva explícita).
  - `provider`, 
  - `source`, 
  - `position` (string/JSON conforme política do provedor), 
  - `updated_at`

### Modelo de dados
O diagrama abaixo expressa o núcleo relacional do `sonec`, destacando chaves naturais e cardinalidades.

```mermaid
erDiagram
    PROVIDER ||--o{ SOURCE : has
    PROVIDER ||--o{ AUTHOR : has
    PROVIDER ||--o{ POST : has
    SOURCE   ||--o{ CURSOR : defines
    AUTHOR   ||--o{ POST : writes
    POST     ||--o{ MEDIA : contains
    SOURCE   ||--o{ FETCHJOB : triggers
    PROVIDER ||--o{ FETCHJOB : records

    PROVIDER {
        string name PK
        string version
        json   capabilities
    }

    SOURCE {
        int    id PK
        string provider FK
        string descriptor
        string label
    }

    AUTHOR {
        int    id PK
        string provider FK
        string external_id
        string handle
        string display_name
        json   metadata
    }

    POST {
        bigint id PK
        string provider FK
        string external_id
        int    author_id FK
        text   text
        string lang
        datetime created_at
        datetime collected_at
        json   metrics
        json   entities
    }

    MEDIA {
        int    id PK
        bigint post_id FK
        string kind
        string url
        json   metadata
    }

    FETCHJOB {
        int      id PK
        string   provider FK
        int      source_id FK
        datetime started_at
        datetime finished_at
        string   status
        json     stats
    }

    CURSOR {
        int      id PK
        string   provider FK
        int      source_id FK
        string   position
        datetime updated_at
    }
```

### Fluxo de uso por um usuário
O fluxo de uso consolida a experiência esperada. Na versão atual, a inicialização do ambiente, a coleta, o status e a consulta são realizados pela API Python (ou pelos scripts de exemplo). O núcleo gerencia a normalização e a persistência, deixando o repositório imediatamente consultável após cada ciclo de coleta.

```mermaid
flowchart TD
    START[Usuário inicia]
    DECIDE{Interface}
    
    API_COLLECT[API: collect]
    CONF[Configurar ambiente]
    CUR[Carregar cursor]
    FETCH[Provider.fetch_since]
    NORM[Normalizar canônico]
    PERSIST[Persistência e deduplicação]
    UPDATE[Atualizar cursor e FetchJob]
    DECIDE2{Consulta}
    API_Q[API: query]
    OUT2[Linhas/Objetos ORM]

    START --> DECIDE
    
    DECIDE -->|API| API_COLLECT
    
    API_COLLECT --> CONF
    CONF --> CUR
    CUR --> FETCH
    FETCH --> NORM
    NORM --> PERSIST
    PERSIST --> UPDATE
    UPDATE --> DECIDE2
    DECIDE2 -->|API| API_Q
    API_Q --> OUT2
```

### Ciclo de coleta
Para reforçar a operação interna, o ciclo de coleta segue etapas definidas e idempotentes, de forma transacional e com métricas claras.

1. Resolução de configuração operacional (provedor, fonte/escopo, limites e filtros).

2. Carregamento do cursor associado ao par (provider, source) como ponto incremental.

3. Invocação do provider para obter lote desde o cursor, respeitando paginação e limites de taxa.

4. Normalização de cada item para o modelo canônico com projeções de campos e saneamento mínimo.

5. Persistência em transação, com deduplicação aplicada por UNIQUE(provider, external_id) e contagem de conflitos.

6. Atualização do cursor com a posição de continuidade e registro do FetchJob com estatísticas.

7. Disponibilização imediata dos dados para consulta pela API.

### Observações
A deduplicação em `Post` é garantida por restrição natural e aplicada no momento da persistência. O runner opera com lotes normalizados para reduzir a sobrecarga de transações. Recomenda-se que consultas especifiquem, no mínimo, o provider e/ou um intervalo temporal, evitando varreduras extensas; é priorizada paginação por keyset (ordenada por `created_at` e `id`). As entidades `FetchJob` e `Cursor` asseguram rastreabilidade e incrementalidade do processo, permitindo auditoria do que foi coletado, quando e com qual resultado.

## Manual de Utilização (Usuários Contemplados)

```
Guia de Instruções:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Para Inicializar o ambiente e o banco de dados faça o seguinte:
Passo 1: Prepare o ambiente Python (ver README.md) e instale o projeto no modo de desenvolvimento ou como pacote:
- `python -m pip install -e .` ou `python -m pip install -e .[dev]`
Passo 2: Escolha o banco de dados. Por padrão, usa-se SQLite local em `./sonec.sqlite3`. Para outro banco, defina a variável `DATABASE_URL` (ex.: PostgreSQL).
- Windows PowerShell: `$env:DATABASE_URL = "sqlite:///./sonec.sqlite3"`
- bash/zsh: `export DATABASE_URL="sqlite:///./sonec.sqlite3"`
Passo 3: Configure o runtime por API (uma vez por processo) antes de qualquer operação:
- Python: `from sonec import api; info = api.configure()`

>>> Alternativas: usar `api.configure("sqlite:///./sonec.sqlite3")` para definirem explicitamente um arquivo SQLite em disco.
>>> Em ambientes de produção/escala, prefira PostgreSQL via `DATABASE_URL`.

Exceções ou potenciais problemas:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Se ocorrer `RuntimeError: Django settings are not configured` {
  Então faça: chame `api.configure(...)` no início do script antes de `collect`, `query` ou `status`.
}
Se ocorrer erro de permissão no arquivo SQLite {
  Então faça: aponte `DATABASE_URL` para um caminho com permissão de escrita (ex.: `sqlite:///C:/.../sonec.sqlite3`).
}
```
```
Guia de Instruções:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Para Coletar postagens do Bluesky por termo de busca faça:
Passo 1: Defina as credenciais do Bluesky (App Password - ver README.md) para evitar 403 no endpoint público.
- PowerShell: `$env:BSKY_IDENTIFIER="seu-handle.bsky.social"; $env:BSKY_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"`
- bash/zsh: `export BSKY_IDENTIFIER=...; export BSKY_APP_PASSWORD=...`
Passo 2: Configure o runtime: `api.configure(...)`.
Passo 3: Chame `api.collect` com `provider="bluesky"` e `q="<termo>"` (e parâmetros opcionais):
- Ex.: `api.collect(provider="bluesky", q="evento2025", limit=500, page_limit=50)`
Passo 4: (Opcional) Defina uma janela temporal local com `since_utc`/`until_utc` (RFC3339/UTC). O sonec aplica o filtro no momento da persistência.
- Ex.: `api.collect(provider="bluesky", q="evento2025", since_utc="2025-05-01T00:00:00Z", until_utc="2025-05-07T23:59:59Z", limit=2000)`

>>> Maneiras alternativas: coletar por autor com `source="@handle"` em vez de `q`. Em cenários focados em contas específicas, `source` tende a produzir amostras mais coerentes que busca aberta por termo.
>>> Em janelas curtas (e recentes), um `limit` menor pode ser suficiente. Para períodos mais longos, aumente `limit` para percorrer páginas suficientes “para trás”.

Exceções ou potenciais problemas:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Se o retorno for `403 Forbidden` sem Bearer {
  Então faça: autentique com App Password (variáveis de ambiente) ou passe programaticamente `extras={"auth":{"identifier":"...","password":"..."}}`.
}
Se o retorno for `401` na autenticação {
  É porque: credenciais inválidas; gere uma nova App Password em `bsky.app` → Settings → App passwords.
}
Se não houver itens na janela temporal definida {
  Então faça: verifique o termo/handle e a janela (`since_utc`/`until_utc`); aumente `limit` para garantir que a paginação alcance o período desejado.
}
```
```
Guia de Instruções:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Para Consultar postagens persistidas faça:
Passo 1: Configure o runtime: `api.configure(...)`.
Passo 2: Use `api.query("posts", ...)` com filtros mínimos recomendados: `provider` e/ou intervalo `since_utc`/`until_utc`.
- Ex.: `page = api.query("posts", provider="bluesky", since_utc="2025-05-01", limit=50, as_dict=True)`
Passo 3: Pagine por keyset usando `after_key` retornado:
- Ex.: `next_page = api.query("posts", provider="bluesky", after_key=page["next_after_key"], limit=50, as_dict=True)`
Passo 4: (Opcional) Projete colunas com `project=[...]` para reduzir o payload.
- Ex.: `project=["id","created_at","text"]`.

>>> Alternativas: retorne ORM (`as_dict=False`) para integrações mais ricas; combine filtros por `author` (`@handle`, `external_id` ou id numérico) e `contains` (substring no texto) para refinar a seleção.
>>> Em análises exploratórias, scripts utilitários estão disponíveis em `examples/bluesky/status_e_consulta.py`.

Exceções ou potenciais problemas:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Se `after_key` inválido for informado {
  Então faça: reinicie a paginação sem `after_key` e regenere o fluxo.
}
Se o conjunto for muito grande em SQLite {
  Então faça: restrinja filtros (provider/tempo) e/ou migre para PostgreSQL via `DATABASE_URL`.
}
```
```
Guia de Instruções:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Para Ver o status de cursores e jobs faça:
Passo 1: Configure o runtime: `api.configure(...)`.
Passo 2: Chame `api.status(provider=?, source=?, limit_jobs=10)` e interprete os resultados.
- Cursors: (provider, source, cursor, updated_at)
- Jobs: (id, provider, source, started_at, finished_at, status, stats)

>>> Alternativas: utilize `examples/bluesky/status_e_consulta.py status --provider bluesky` para saída tabular rápida na linha de comando.
>>> Em ambientes de produção, monitore `status` após execuções de coleta para auditoria e diagnóstico.

Exceções ou potenciais problemas:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Se nenhuma linha for exibida em `cursors` ou `jobs` {
  Então faça: execute uma coleta para o par (provider, source) e repita o `status`.
}
```
```
Guia de Instruções:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Para Realizar análise com visualização faça:
Passo 1: Instale a biblioteca de gráficos (opcional): `pip install matplotlib`.
Passo 2: Defina credenciais do Bluesky (recomendado) e configure o runtime.
Passo 3: Execute `examples/bluesky/collect_and_visualize.py` informando o termo e, se desejado, uma janela temporal bem definida (`--since/--until`).
- Ex.: `python examples/bluesky/collect_and_visualize.py --q "termo" --since 2025-05-01T00:00:00Z --until 2025-05-07T23:59:59Z --limit-collect 1000`
Passo 4: Inspecione os PNGs salvos no diretório `--out` (padrão: `examples/out`).

>>> Alternativas: use `examples/bluesky/collect_and_analyze.py` para um resumo textual (“Top accounts by total likes”) quando gráficos não forem necessários.
>>> Para recortes temporais finos, prefira passar `--since/--until` (RFC3339/UTC) em vez de somente `--days`.

Exceções ou potenciais problemas:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Se `matplotlib` não estiver instalado {
  Então faça: instale com `pip install matplotlib` ou execute o exemplo de análise textual.
}
Se os gráficos saírem vazios ou com poucos dados {
  Então faça: amplie o período temporal e/ou aumente `--limit-collect` para que a paginação percorra a janela.
}
```
```
Guia de Instruções:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Para Estender com um novo provider (desenvolvedoras/es) faça:
Passo 1: Implemente uma classe que cumpra o contrato em `sonec.providers.base.Provider` (`configure`, `fetch_since`) e produza itens canônicos (Author, Post, Metrics, Entities).
Passo 2: Registre o provider no `sonec.providers.registry` (nome → classe).
Passo 3: Configure o runtime e teste a coleta: `api.collect(provider="<nome>", ...)`.
Passo 4: Valide a persistência/consulta: `api.query("posts", provider="<nome>", limit=10)`.

>>> Alternativas: consulte o `IMPLEMENTATION_GUIDE.md` para detalhes do contrato (capabilities, erros padronizados, paginação e formato canônico).
>>> Em redes com limites estritos, projete `fetch_since` para respeitar orçamentos de rate limit e produzir `next_cursor` consistente.

Exceções ou potenciais problemas:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Se itens duplicados aparecerem {
  É porque: a chave natural `(provider, external_id)` não está estável; corrija o mapeamento de `external_id` na normalização.
}
Se o registro do provider falhar em `resolve(name)` {
  Então faça: verifique o `registry.register(...)` e colisões de nome; use nomes em minúsculas coerentes com a convenção do projeto.
}
```

### Glossário
- **API Python**
Superfície programática do sonec para integração em scripts e aplicações. Expõe operações de coleta e consulta, retornando objetos/iteráveis compatíveis com o ORM.

- **Author**
Entidade canônica que representa o autor de uma postagem. Identificado por (provider, external_id). Deve existir antes do Post que o referencia.

- **Batch (Lote)**
Conjunto de itens retornados por um provider em uma chamada de coleta. Processado de forma transacional para normalização e persistência.

- **Bulk insert**
Inserção em lote no banco, reduzindo round-trips e sobrecarga de transação. Usado em conjunto com deduplicação por constraint.

- **CLI (Command-Line Interface)**
Interface de linha de comando do `sonec`, em evolução e não estável. Recomenda‑se utilizar a API Python para inicialização e demais operações. Comandos adicionais para coleta, consulta e diagnóstico estão previstos.

- **Collected_at**
Timestamp de coleta local atribuído a um Post, em UTC. Diferencia-se de created_at (tempo de criação no provedor).

- **Core (Domínio e Serviços)**
Núcleo do sonec responsável por orquestrar coleta, normalização, deduplicação, transações, manutenção de cursores e registro de jobs.

- **Cursor**
Posição incremental de coleta associada a (provider, source). Garante continuidade entre execuções sem duplicações ou lacunas.

- **Deduplicação**
Garantia de unicidade de Post por meio da constraint UNIQUE(provider, external_id). Conflitos são tratados durante a persistência.

- **Entities** (JSON)
Campo JSON em Post contendo entidades extraídas (hashtags, menções, links). Padroniza a representação semântica para consultas.

- **FetchJob**
Registro de execução de coleta com informações de início/fim, status e estatísticas (itens inseridos, conflitos de dedup, janelas temporais processadas).

- **Filtro** **mínimo** (consultas)
Política de consulta que exige ao menos provider e/ou intervalo temporal (created_at BETWEEN ...) para evitar varreduras extensas.

- **Handle**
Identificador textual de um autor ou fonte no provedor (por exemplo, @nome). Normalizado em Author e referenciado por Post.

- **Idempotência** (coleta)
Propriedade operacional pela qual repetidas execuções de coleta sobre o mesmo intervalo não geram duplicatas, assegurada por deduplicação.

- **Incrementalidade**
Capacidade de avançar a coleta a partir do último ponto conhecido (cursor), reduzindo reprocessamento e riscos de perda.

- **Job** **Status**
Estado de um FetchJob (ex.: running, succeeded, failed). Usado para diagnóstico e auditoria operacional.

- **JSONField**
Tipo de campo utilizado para armazenar estruturas flexíveis (por exemplo, metrics, entities), mantendo portabilidade entre SQLite e outros SGBDs compatíveis com Django.

- **Keyset** **pagination**
Estratégia de paginação baseada em marcadores estáveis (por exemplo, created_at, id) em vez de OFFSET. Evita degradação de desempenho em conjuntos grandes.

- **Lang**
Código do idioma do conteúdo de um Post. Campo opcional, útil para filtragem semântica.

- **Media**
Entidade associada a Post para metadados de mídia (tipo, URL, informações descritivas). Não armazena binários.

- **Métricas** (metrics, JSON)
Conjunto de contadores associados a um Post (ex.: curtidas, reposts). Formato flexível, dependente do provedor, mas padronizado em JSON.

- **Modelo canônico**
Esquema unificado aplicado a todas as postagens, autores e fontes, independentemente do provedor de origem. Fundamento para consultas consistentes.

- **Normalização**
Processo de conversão de dados brutos do provedor para o modelo canônico (Author, Post, Media, etc.), padronizando campos e semântica.

- **ORM** (Django ORM)
Camada de mapeamento objeto-relacional utilizada para definir entidades, regras de integridade, consultas e operações transacionais.

- **Post**
Entidade central que representa uma postagem. Identificada por UNIQUE(provider, external_id) e associada a um Author. Contém text, lang, created_at, collected_at, metrics e entities.

- **Provider**
Identidade da rede social de origem (por exemplo, Bluesky). Também se refere ao componente de software (provider plug-in) que implementa a coleta e a normalização.

- **Query** (consulta interna)
Operação exposta pela API para recuperar entidades do repositório canônico. Recomenda‑se fornecer filtros mínimos (provider e/ou intervalo temporal). Prioriza paginação por keyset.

- **Rate** **limit**
Limitação imposta por provedores de API quanto a número de chamadas por intervalo de tempo. Gerenciada no nível do provider.

- **Registry** (de providers)
Mecanismo interno de descoberta e registro de providers, permitindo endereçamento por nome (ex.: bluesky, reddit) e carregamento do coletor correspondente.

- **Repositório** (banco de dados)
Armazenamento unificado das entidades canônicas via ORM. Padrão inicial: SQLite com inicialização autônoma.

- **Runner**
Componente de orquestração que resolve configuração, carrega o cursor, chama o provider, coordena normalização, realiza persistência e registra o FetchJob.

- **Source**
Escopo de coleta dentro de um provider (por exemplo, um handle, um termo de busca ou um identificador de coleção). Vincula-se a Cursor e FetchJob.

- **SQLite**
SGBD padrão utilizado para execução autônoma local. Adequado para pequena e média escala, com zero configuração adicional.

- **Status** (comando)
Operação de diagnóstico que exibe estado de cursores, jobs recentes e métricas operacionais. Disponível via API; comando de CLI correspondente está planejado.

- **Transação**
Unidade atômica de persistência usada na coleta e na inserção em lote. Garante consistência mesmo em caso de falhas intermediárias.

- **UNIQUE**(provider, external_id)
Restrição de unicidade aplicada a `Post` para garantir deduplicação e idempotência da coleta.

- **UTC**
Padrão de fuso horário para created_at e collected_at, assegurando consistência temporal nas consultas e comparações.
