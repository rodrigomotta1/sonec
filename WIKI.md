# Breve Descrição

## Função principal
O `sonec` é um pacote Python baseado em Django, concebido para coletar postagens de diferentes redes sociais e armazená-las de forma padronizada em um banco de dados local, simplificando o acesso posterior a esses dados para análises e aplicações diversas. O objetivo principal é diminuir o *overhead* de trabalho que geralmente pesquisadores da área precisam ter para configurar onde armazenar e como consultar os dados coletados. Com sua arquitetura, o `sonec` tenta oferecer um meio mais simples de rapidamente começar a coletar e armazenar dados de redes sociais, com o mínimo de configuração necessária.

## Funções específicas relevantes

- Rotinas de coleta de postagens a partir de múltiplos provedores (ex.: Bluesky, X/Twitter, Reddit, YouTube...).

- Persistência automática e transparente dos dados em um banco de dados SQLite (ou outro banco compatível com Django).

- CLI para inicialização, coleta, monitoramento de status e exportação de dados.

- API Python que permite integrar coletores e dados em scripts e outros sistemas.

- Mecanismos internos de deduplicação, rastreamento de cursores e exportação em formatos comuns (CSV, NDJSON).

## Usuários alvo
O programa foi concebido primordialmente para pesquisadores da área de comunicação social e informática, analistas de dados e desenvolvedores interessados em coletar e organizar dados de redes sociais de forma unificada, com baixa barreira de entrada e sem necessidade de configurar manualmente bancos ou pipelines complexos.

## Natureza do programa
O `sonec` é uma **ferramenta utilitária modular**, com potencial de evoluir para uma biblioteca mais ampla de coletores de redes sociais. Inicialmente, pode ser encarado como uma **prova de conceito** (PoC) estruturada para coleta unificada de *posts*, mas já utilizável em cenários reais de pesquisa e prototipagem.

## Ressalvas

- A implementação inicial cobre apenas o provedor Bluesky, que por sua natureza é público e não exige autenticação para coleta. A coleta sobre outras redes exige a implementação de *providers* específicos para cada uma, de forma que a arquitetura do sistema está facilitada para receber essas implementações com o tempo

- O desempenho é adequado para coleta em pequena/média escala; para cargas muito grandes, será necessário adaptar a arquitetura para aceitar do usuário uma conexão a um banco de dados pessoal do utilizador. Sobre ele, seriam necessárias otimizações de armazenamento e consulta (índices) para viabilizar a análise sobre os dados (pensando na quantidade da ordem de dezenas de milhões de *posts* a serem consultados)

- A persistência padrão é em SQLite, o que simplifica a instalação mas não é ideal para ambientes de produção de grande porte.

- O projeto está em estágio inicial e sujeito a alterações na API, CLI e modelo de dados.

# Visão de Projeto


## Cenário Positivo 1 — Pesquisadora em Comunicação

Marina é doutoranda em comunicação social e precisa analisar postagens do Bluesky relacionadas a um evento político. Ela instala o sonec, executa sonec collect bluesky --source evento2025, e logo após acessa sonec query posts --provider bluesky --since 2025-05-01. O comando retorna diretamente as postagens relevantes em formato tabular na tela, e, pela API Python, ela consegue receber esses mesmos dados como objetos para usar em sua análise estatística. Marina percebe que não precisou lidar com exportações ou formatações intermediárias: o sonec cuida do armazenamento e expõe consultas diretas, prontas para análise.

## Cenário Positivo 2 — Desenvolvedor Extensível

Rafael é desenvolvedor e quer trabalhar com dados do Reddit. O sonec ainda não possui um provider oficial, mas a documentação mostra como estender a interface de coleta. Ele implementa uma classe derivada da base de coletores, registra o novo provider e executa sonec collect reddit --subreddit python. Depois, testa rapidamente com sonec query posts --provider reddit --limit 10, obtendo resultados já normalizados no modelo canônico. Ele integra isso em seu código Python chamando sonec.query("posts", provider="reddit"), sem jamais precisar interagir diretamente com o banco subjacente.

## Cenário Negativo 1 — Escala além do planejado

Ana, pesquisadora sênior, decide usar o sonec para coletar dezenas de milhões de postagens em múltiplos provedores. Ela roda a coleta em seu notebook, mas logo nota lentidão nas consultas sonec query devido às limitações do SQLite. A documentação já a orienta: em cenários de grande volume é esperado configurar o sonec para apontar para um banco PostgreSQL, garantindo melhor escalabilidade e performance. Sem isso, as consultas continuam funcionando, mas podem ficar muito lentas.

## Cenário Negativo 2 — Uso inesperado de API

Carlos, estudante, tenta usar o sonec para coletar vídeos completos do YouTube. Ele executa sonec collect youtube esperando baixar a mídia, mas recebe uma mensagem clara de erro: o programa informa que apenas metadados das postagens estão disponíveis para consulta via sonec query, e não os arquivos de mídia. Carlos compreende a limitação e redireciona seu esforço para analisar títulos, descrições e estatísticas, usando o sonec para consultas de dados estruturados.

# Requisitos Funcionais e Não-Funcionais

## Requisitos Funcionais
- **RF01:** O sistema deve permitir a coleta de postagens de diferentes redes sociais por meio de *providers* especializados
- **RF02:** Inicialmente, o sistema deve dar suporte a coleta e armazenamento de postagens realizadas na rede Blueksy
- **RF03:** A coleta deve registrar também metadados relevantes como autor, data de publicação, métricas de engajamento, e qualquer outra informação adicional que estiver disponível em cada rede
- **RF04:** O sistema deve persistir postagens coletadas em um modelo canônico único, independente do provedor
- **RF05:** O sistema deve oferecer meios de consulta ao banco de dados que persiste os dados coletados de cada rede
- **RF06:** O sistema deve oferecer meios de observar o status de consultas agendas e volume de dados corrente
- **RF07:** O sistema deve expor funções para integração com scripts externos, visando facilidade de uso em diferentes ambientes de pesquisa
- **RF08:** Os resultados de consultas sobre o banco devem ser retornados como objetos Python/Django, de forma que o usuário possa posteriormente decidir o que fazer com os dados retornados
- **RF09:** O sistema deve registrar cursores de coleta para suportar coletas incrementais
- **RF10:** Cada *job* de coleta deve ser identificado, armazenando estatísticas da coleta, como tempo estimado, tempo passado, volume de itens, status e falhas.
- **RF11:** O sistema deve permitir consultas sobre entidades canônicas via CLI/API, abstraindo manipulação direta do banco (ainda que seja possível realizar manipulação direta)
- **RF12:** O sistema não pode aceitar consultas que não especifiquem um Provider e uma janela de tempo em uma consulta padrão

## Requisitos Não-Funcionais
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

# Documentação Técnica

## Visão integrada
O sonec organiza a coleta, normalização, persistência e consulta de postagens de redes sociais por meio de um núcleo de domínio (core) que orquestra providers especializados, expondo funcionalidades por CLI e API Python. As consultas operam diretamente sobre o repositório canônico via ORM do Django, sem necessidade de arquivos intermediários. A arquitetura enfatiza uma superfície de uso única: o usuário opera pela CLI ou pela API, enquanto o core aplica deduplicação, mantém cursores incrementais e registra jobs de coleta. A persistência padrão é em SQLite com inicialização autônoma.

## Módulos e responsabilidades
O desenho modular foi concebido para garantir isolamento de responsabilidades, previsibilidade de uso e coerência semântica dos dados.

- **CLI:** ponto de entrada para operação; expõe coleta, consulta e diagnóstico com retorno direto ao usuário. É adequada para uso interativo e automações simples por linha de comando.

- **API Python:** superfície programática equivalente à CLI; expõe coleta e consulta retornando iteráveis/objetos compatíveis com o ORM, facilitando integrações em pipelines analíticos.

- **Core (Domínio e Serviços):** coordena configuração, execução do runner, normalização, deduplicação, transações de persistência, avanço de cursores e registro de jobs com métricas.

- **Providers (plug-ins por rede):** encapsulam autenticação quando aplicável, paginação, respeito a limites de taxa e conversão para o modelo canônico. Entregam lotes já normalizados ao core.

- **Models (Django)**: provê o modelo canônico e a persistência transacional; inicializa SQLite sem configuração externa.

Abaixo segue um diagramático que ilustra a organização modular do projeto

```mermaid
flowchart LR
    subgraph User["Usuário / Sistemas Integradores"]
        CLI[CLI]:::iface
        API[API Python]:::iface
    end

    CLI --> CORE
    API --> CORE

    subgraph CORE["Core (Domínio e Serviços)"]
        CORE[Runner / Orquestração]
        NORM[Normalização & Deduplicação]
        CJ[Cursores & Jobs]
    end

    subgraph PROV["Providers (por rede)"]
        P1[Bluesky]:::prov
        Pn[Outros]:::prov
    end

    CORE --> P1
    CORE --> Pn
    P1 --> NORM
    Pn --> NORM
    NORM --> CJ

    subgraph DB["Repositório (ORM Django)"]
        SQLITE[(SQLite - padrão)]:::db
    end

    NORM --> SQLITE
    CJ --> SQLITE

    classDef iface fill:#f7f7ff,stroke:#666,stroke-width:1px;
    classDef prov fill:#fff7e6,stroke:#a86700,stroke-width:1px;
    classDef db fill:#eef2f7,stroke:#1f4e79,stroke-width:1px;
```

## Entidades principais
A modelagem canônica busca representar postagens e metadados de forma uniforme, independentemente do provedor de origem. A seguir, descrevem-se as entidades, seus propósitos, atributos essenciais e invariantes de integridade.

- **Provider**
Deve identificar a rede de origem e suas capacidades operacionais. Mantém o vínculo conceitual de todos os dados de origem.
  - `name` (identificador lógico)
  - `version`
  - `capabilities` (indicador de funcionalidades disponíves para o provider)

- **Source**
Serve para definir o escopo de coleta por provedor (por exemplo, handle, query, lista, subreddit). unicidade do par (provider, external_id|descriptor) e associação inequívoca a um escopo.
  - `provider` (FK), 
  - `external_id` ou `descriptor` (identidade no provedor), 
  - `label` (descrição).


- **Author**
Tem o objetivo de registrar a autoria das postagens de forma canônica. existência antes da criação do Post que referencia seu autor; unicidade por (provider, external_id).
    - `provider` (FK)
    - `external_id`, 
    - `handle`, 
    - `display_name`, 
    - `metadata` (JSON).

- **Post**
Funciona como núcleo informacional; representa a postagem e seus metadados essenciais. deduplicação por UNIQUE(provider, external_id); created_at em UTC; referência válida a Author.
Índices mínimos: (provider, created_at DESC) e (author, created_at DESC).
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
Armazena metadados de mídia associada a um Post. não armazena binários pesados; registra referência e descrição.
  - `post` (FK), 
  - `kind` (imagem, vídeo, etc.), 
  - `url`, 
  - `metadata` (JSON).

- **FetchJob**
Objetivo de rastrear execuções de coleta para diagnóstico e auditoria. integridade temporal (início ≤ fim quando concluído) e consistência com o cursor correspondente.
  - `id`, 
  - `provider`, 
  - `source`, 
  - `started_at`, 
  - `finished_at`, 
  - `status`, 
  - `stats` (JSON com inseridos, conflitos, janelas temporais).

- **Cursor**
Serve para controlar a coleta incremental garantindo continuidade e evitando lacunas. avanço monotônico (o cursor não retrocede sem ação corretiva explícita).
  - `provider`, 
  - `source`, 
  - `position` (string/JSON conforme política do provedor), 
  - `updated_at`

## Modelo de dados
O diagrama abaixo expressa o núcleo relacional do sonec, destacando chaves naturais e cardinalidades.

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
        string descriptor  "identidade do escopo (handle/query/etc.)"
        string label
        UNIQUE(provider, descriptor)
    }

    AUTHOR {
        int    id PK
        string provider FK
        string external_id
        string handle
        string display_name
        json   metadata
        UNIQUE(provider, external_id)
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
        UNIQUE(provider, external_id)
        INDEX(provider, created_at)
        INDEX(author_id, created_at)
    }

    MEDIA {
        int    id PK
        bigint post_id FK
        string kind
        string url
        json   metadata
    }

    FETCHJOB {
        int     id PK
        string  provider FK
        int     source_id FK
        datetime started_at
        datetime finished_at
        string  status
        json    stats
    }

    CURSOR {
        int     id PK
        string  provider FK
        int     source_id FK
        string  position
        datetime updated_at
        UNIQUE(provider, source_id)
    }
```

## Fluxo de uso por um usuário
O fluxo de uso consolida a experiência esperada: o usuário interage apenas com a CLI ou com a API Python; o core gerencia o trabalho pesado e o repositório fica imediatamente consultável após cada ciclo de coleta.

```mermaid
flowchart TD
    A[Usuário inicia ação] --> B{Escolha da interface}
    B -->|CLI| C[Executa 'sonec collect <provider> ...']
    B -->|API Python| D[Chama collect(provider, ...)]
    C --> E[Core resolve configuração]
    D --> E
    E --> F[Carrega Cursor (provider, source)]
    F --> G[Provider.fetch_since(cursor,...)]
    G --> H[Normalização para modelo canônico]
    H --> I[Persistência transacional + dedup]
    I --> J[Atualiza Cursor e registra FetchJob]
    J --> K{Usuário consulta dados}
    K -->|CLI|' L[Executa 'sonec query posts ...']
    K -->|API|' M[Chama query('posts', **filtros)]
    L --> N[Resultados em saída padrão]
    M --> O[Objetos/iteráveis ORM]
```

## Ciclo de coleta
Para reforçar a operação interna, o ciclo de coleta segue etapas definidas e idempotentes, de forma transacional e com métricas claras.

1. Resolução de configuração operacional (provedor, fonte/escopo, limites e filtros).

2. Carregamento do cursor associado ao par (provider, source) como ponto incremental.

3. Invocação do provider para obter lote desde o cursor, respeitando paginação e limites de taxa.

4. Normalização de cada item para o modelo canônico com projeções de campos e saneamento mínimo.

5. Persistência em transação, com deduplicação aplicada por UNIQUE(provider, external_id) e contagem de conflitos.

6. Atualização do cursor com a posição de continuidade e registro do FetchJob com estatísticas.

7. Disponibilização imediata dos dados para consulta na CLI e na API.

## Observações
A deduplicação em Post é garantida por constraint natural e aplicada no momento da persistência; o runner trabalha com lotes normalizados para reduzir a sobrecarga de round-trips e torná-la previsível. As consultas recomendadas exigem pelo menos provider e/ou intervalo temporal para evitar varreduras extensas, sendo priorizada paginação por keyset (ordenada por created_at e id) nas superfícies de CLI e API. As entidades FetchJob e Cursor asseguram rastreabilidade e incrementalidade do processo, permitindo auditoria do que foi coletado, quando e com qual resultado.

## Glossário
- **API Python**
Superfície programática do sonec para integração em scripts e aplicações. Expõe operações de coleta e consulta, retornando objetos/iteráveis compatíveis com o ORM.

- **Author**
Entidade canônica que representa o autor de uma postagem. Identificado por (provider, external_id). Deve existir antes do Post que o referencia.

- **Batch (Lote)**
Conjunto de itens retornados por um provider em uma chamada de coleta. Processado de forma transacional para normalização e persistência.

- **Bulk insert**
Inserção em lote no banco, reduzindo round-trips e sobrecarga de transação. Usado em conjunto com deduplicação por constraint.

- **CLI (Command-Line Interface)**
Interface de linha de comando do sonec. Ponto de entrada para coleta, consulta e diagnóstico, com resultados diretamente utilizáveis na saída padrão.

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
Operação exposta por CLI/API para recuperar entidades do repositório canônico. Deve respeitar filtros mínimos e prioriza paginação por keyset.

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
Comando da CLI que exibe estado de cursores, jobs recentes e métricas operacionais, auxiliando diagnóstico e acompanhamento da coleta.

- **Transação**
Unidade atômica de persistência usada na coleta e na inserção em lote. Garante consistência mesmo em caso de falhas intermediárias.

- **UNIQUE**(provider, external_id)
Restrição de unicidade aplicada a Post para garantir deduplicação e idempotência da coleta.

- **UTC**
Padrão de fuso horário para created_at e collected_at, assegurando consistência temporal nas consultas e comparações.