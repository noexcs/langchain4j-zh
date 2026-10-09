# PGVector

LangChain4j 与 [PGVector](https://github.com/pgvector/pgvector) 无缝集成，使开发人员能够直接在 PostgreSQL 中存储和查询向量嵌入。该集成非常适合语义搜索、RAG 等应用。

## Maven 依赖

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-pgvector</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## Gradle 依赖

```implementation 'dev.langchain4j:langchain4j-pgvector:1.22.0-beta32'```

## API

- `PgVectorEmbeddingStore`

## 参数汇总

| 纯 Java 属性            | 描述 | 默认值 | 必填/可选 |
|-------------------------|------|--------|-----------|
| `datasource` | 用于数据库连接的 `DataSource` 对象。仅在 `PgVectorEmbeddingStore.datasourceBuilder()` 构建器变体中可用。如果未提供，则必须在 `PgVectorEmbeddingStore.builder()` 构建器变体中单独提供 `host`、`port`、`user`、`password` 和 `database`。 | 无 | 如果未单独提供 `host`、`port`、`user`、`password` 和 `database`，则必填。 |
| `host` | PostgreSQL 服务器的主机名。如果未提供 `DataSource`，则必填。 | 无 | 如果未提供 `DataSource` 则必填 |
| `port` | PostgreSQL 服务器的端口号。如果未提供 `DataSource`，则必填。 | 无 | 如果未提供 `DataSource` 则必填 |
| `user` | 用于数据库认证的用户名。如果未提供 `DataSource`，则必填。 | 无 | 如果未提供 `DataSource` 则必填 |
| `password` | 用于数据库认证的密码。如果未提供 `DataSource`，则必填。 | 无 | 如果未提供 `DataSource` 则必填 |
| `database` | 要连接的数据库名称。如果未提供 `DataSource`，则必填。 | 无 | 如果未提供 `DataSource` 则必填 |
| `table` | 用于存储嵌入的数据库表名。 | 无 | 必填 |
| `dimension` | 嵌入向量的维度。应与所使用的嵌入模型匹配。使用 `embeddingModel.dimension()` 动态设置。 | 无 | 必填 |
| `useIndex` | IVFFlat 索引将向量划分为若干列表，然后搜索其中与查询向量最接近的列表子集。与 HNSW 相比，它的构建时间更短、内存占用更少，但查询性能较低（就速度-召回率权衡而言）。应使用 [IVFFlat](https://github.com/pgvector/pgvector#ivfflat) 索引。 | `false` | 可选 |
| `indexListSize` | IVFFlat 索引的列表数量。 | 无 | 必填时：如果 `useIndex` 为 `true`，必须提供 `indexListSize` 且必须大于零。否则，程序将在表初始化期间抛出异常。可选时：如果 `useIndex` 为 `false`，该属性将被忽略，无需设置。 |
| `createTable` | 指定是否自动创建嵌入表。 | `true` | 可选 |
| `dropTableFirst` | 指定是否在重建表之前先删除该表（对测试有用）。 | `false` | 可选 |
| `searchMode` | 要使用的搜索模式。选项：<ul><li>**VECTOR**：使用余弦距离的标准向量相似度搜索。</li><li>**HYBRID**：使用倒数排名融合（RRF）将向量搜索与全文关键词搜索相结合。</li></ul> | `VECTOR` | 可选 |
| `rrfK` | RRF（倒数排名融合）算法中使用的常数 `k`：`Score = 1/(k + rank_vector) + 1/(k + rank_keyword)`。较低的取值（20-40）更强调头部结果；较高的取值（80-100）产生更均衡的排名。仅当 `searchMode` 设置为 `HYBRID` 时相关。 | `60` | 可选。仅在 HYBRID 搜索模式下使用。 |
| `textSearchConfig` | 用于关键词搜索的 PostgreSQL 文本搜索配置名称（例如 `simple`、`english`、`german`）。仅当 `searchMode` 为 `HYBRID` 时适用。 | `simple` | 可选。仅在 HYBRID 搜索模式下使用。 |
| `metadataStorageConfig` | 用于处理与嵌入关联的元数据的配置对象。支持三种存储模式：<ul><li>**COLUMN_PER_KEY**：用于预先知道元数据键的静态元数据。</li><li>**COMBINED_JSON**：用于不预先知道元数据键的动态元数据。以 JSON 格式存储数据。（默认）</li><li>**COMBINED_JSONB**：与 JSON 类似，但以二进制格式存储，以优化大数据集上的查询。</li></ul> | `COMBINED_JSON` | 可选。如果未设置，将使用基于 `COMBINED_JSON` 的默认配置。 |

## 示例

要演示 PGVector 的功能，你可以使用容器化的 PostgreSQL 环境。它利用 Testcontainers 运行带有 PGVector 的 PostgreSQL。

#### 使用 Docker 快速开始

要快速搭建一个带 PGVector 扩展的 PostgreSQL 实例，你可以使用以下 Docker 命令：

```
docker run --rm --name langchain4j-postgres-test-container -p 5432:5432 -e POSTGRES_USER=my_user -e POSTGRES_PASSWORD=my_password pgvector/pgvector
```

#### 命令说明：

- ```docker run```: 运行一个新容器。
- ```--rm```: 容器停止后自动将其删除，确保没有残留数据。
- ```--name langchain4j-postgres-test-container```: 将容器命名为 langchain4j-postgres-test-container，以便于识别。
- ```-p 5432:5432```: 将本地机器的 5432 端口映射到容器内的 5432 端口。
- ```-e POSTGRES_USER=my_user```: 将 PostgreSQL 用户名设置为 my_user。
- ```-e POSTGRES_PASSWORD=my_password```: 将 PostgreSQL 密码设置为 my_password。
- ```pgvector/pgvector```: 指定要使用的 Docker 镜像，该镜像已预配置了 PGVector 扩展。

下面是两个代码示例，展示如何创建 `PgVectorEmbeddingStore`。第一个示例仅使用必填参数，
第二个示例配置了所有可用参数。

1. 仅必填参数

```java
EmbeddingStore<TextSegment> embeddingStore = PgVectorEmbeddingStore.builder()
        .host("localhost")                           // Required: Host of the PostgreSQL instance
        .port(5432)                                  // Required: Port of the PostgreSQL instance
        .database("postgres")                        // Required: Database name
        .user("my_user")                             // Required: Database user
        .password("my_password")                     // Required: Database password
        .table("my_embeddings")                      // Required: Table name to store embeddings
        .dimension(embeddingModel.dimension())       // Required: Dimension of embeddings
        .build();
```

2. 设置所有参数

在该变体中，我们包含了所有常用的可选参数，例如 useIndex、indexListSize、
createTable、dropTableFirst 和 metadataStorageConfig。请根据需要调整这些值：

 ```java
EmbeddingStore<TextSegment> embeddingStore = PgVectorEmbeddingStore.builder()
        // Required parameters
        .host("localhost")
        .port(5432)
        .database("postgres")
        .user("my_user")
        .password("my_password")
        .table("my_embeddings")
        .dimension(embeddingModel.dimension())

        // Optional parameters
        .useIndex(true)                             // Enable IVFFlat index
        .indexListSize(100)                         // Number of lists for IVFFlat index
        .createTable(true)                          // Automatically create the table if it doesn’t exist
        .dropTableFirst(false)                      // Don’t drop the table first (set to true if you want a fresh start)
        .metadataStorageConfig(MetadataStorageConfig.combinedJsonb()) // Store metadata as a combined JSONB column

        .build();
```

如果你只想以最小配置快速开始，请使用第一个示例。
第二个示例展示了如何利用所有可用的构建器参数以获得更多的控制和自定义。

## 使用 PGVector 的完整 RAG 示例

本节演示如何使用带 PGVector 扩展的 PostgreSQL 进行语义搜索，构建一个完整的检索增强生成（RAG）系统。

### 概述

RAG 系统由两个主要阶段组成：
1. **索引阶段（离线）**：加载文档、切分为分块、生成嵌入并存入 pgvector
2. **检索阶段（在线）**：嵌入用户查询、搜索相似分块、将上下文注入 LLM 提示词

### 前置条件

确保你有一个带 PGVector 且正在运行的 PostgreSQL 实例（参见上面的 Docker 设置）。

### 1. 文档摄入（索引阶段）

本示例展示如何加载文档、将其切分为分块，并将嵌入存储到 pgvector 中：

```java
import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.DocumentParser;
import dev.langchain4j.data.document.DocumentSplitter;
import dev.langchain4j.data.document.parser.apache.pdfbox.ApachePdfBoxDocumentParser;
import dev.langchain4j.data.document.splitter.DocumentSplitters;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.embedding.onnx.allminilml6v2.AllMiniLmL6V2EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;

import static dev.langchain4j.data.document.loader.FileSystemDocumentLoader.loadDocument;

// Load document (PDF, TXT, etc.)
Document document = loadDocument("/path/to/document.pdf", new ApachePdfBoxDocumentParser());

// Split document into smaller chunks
// 300 tokens per chunk, 50 tokens overlap for context continuity
DocumentSplitter splitter = DocumentSplitters.recursive(300, 50);

// Create embedding model (384 dimensions for AllMiniLmL6V2)
EmbeddingModel embeddingModel = new AllMiniLmL6V2EmbeddingModel();

// Create pgvector embedding store
EmbeddingStore<TextSegment> embeddingStore = PgVectorEmbeddingStore.builder()
        .host("localhost")
        .port(5432)
        .database("postgres")
        .user("my_user")
        .password("my_password")
        .table("document_embeddings")
        .dimension(embeddingModel.dimension())  // 384 for AllMiniLmL6V2
        .build();

// Ingest: split document, generate embeddings, and store in pgvector
EmbeddingStoreIngestor.builder()
        .documentSplitter(splitter)
        .embeddingModel(embeddingModel)
        .embeddingStore(embeddingStore)
        .build()
        .ingest(document);

System.out.println("Document ingested successfully!");
```

### 2. 查询（检索阶段）

本示例展示如何使用用户问题查询 RAG 系统：

```java
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.store.embedding.EmbeddingMatch;

import java.util.List;
import java.util.stream.Collectors;

// User's question
String question = "What is the refund policy?";

// Generate embedding for the question
Embedding questionEmbedding = embeddingModel.embed(question).content();

// Search for the most similar text segments (top 3 results)
List<EmbeddingMatch<TextSegment>> relevantSegments = embeddingStore.findRelevant(
        questionEmbedding,
        3  // Retrieve top 3 most similar chunks
);

// Build context from retrieved segments
String context = relevantSegments.stream()
        .map(match -> match.embedded().text())
        .collect(Collectors.joining("\n\n"));

// Create prompt with retrieved context
String promptWithContext = String.format("""
        Answer the question based on the following context.
        If the context doesn't contain relevant information, say "I don't have enough information to answer."

        Context:
        %s

        Question: %s

        Answer:
        """, context, question);

// Send to LLM with context
ChatModel chatModel = OpenAiChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4")
        .build();

String answer = chatModel.generate(promptWithContext);
System.out.println("Answer: " + answer);
```

### 生产环境注意事项

根据实际使用情况，以下是生产部署的重要注意事项：

#### 1. 连接池
在生产环境中，请使用带连接池的 `DataSource`，而不是逐个连接参数：

```java
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;

HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:postgresql://localhost:5432/postgres");
config.setUsername("my_user");
config.setPassword("my_password");
config.setMaximumPoolSize(10);

HikariDataSource dataSource = new HikariDataSource(config);

EmbeddingStore<TextSegment> embeddingStore = PgVectorEmbeddingStore.datasourceBuilder()
        .datasource(dataSource)
        .table("document_embeddings")
        .dimension(384)
        .build();
```

#### 2. 索引优化
对于大数据集（>100k 条嵌入），请启用 IVFFlat 索引以提升查询性能：

```java
EmbeddingStore<TextSegment> embeddingStore = PgVectorEmbeddingStore.builder()
        // ... other config ...
        .useIndex(true)
        .indexListSize(100)  // Adjust based on dataset size
        .build();
```

**注意**：在大数据集上创建索引可能需要较长时间。请在查询速度与索引构建时间之间取得平衡。

#### 3. 元数据存储
为了在大数据集上获得更好的查询性能，请使用 JSONB 进行元数据存储：

```java
import dev.langchain4j.store.embedding.pgvector.MetadataStorageConfig;

EmbeddingStore<TextSegment> embeddingStore = PgVectorEmbeddingStore.builder()
        // ... other config ...
        .metadataStorageConfig(MetadataStorageConfig.combinedJsonb())
        .build();
```

#### 4. 分块大小调整
根据你的用例尝试不同的分块大小：
- **较小的分块（200-300 token）**：精度更好，答案更具体
- **较大的分块（500-800 token）**：上下文更多，但可能降低相关性

#### 5. 错误处理
始终妥善处理数据库连接失败：

```java
try {
    embeddingStore.add(embedding, textSegment);
} catch (Exception e) {
    logger.error("Failed to store embedding", e);
    // Implement retry logic or fallback behavior
}
```

### 混合搜索（向量 + 关键词）

PGVector 支持**混合搜索**，它将向量相似度搜索与 PostgreSQL 的全文关键词搜索相结合。这种方式通常比仅向量搜索能提供更好的结果，因为它同时利用了语义理解和精确关键词匹配。

#### 何时使用混合搜索

- 当你同时需要语义相似性和精确关键词匹配时
- 对于包含领域特定术语、产品名称或技术行话的查询
- 提高 RAG 应用中的检索准确率

#### 配置

通过设置 `searchMode` 参数启用混合搜索：

```java
import dev.langchain4j.store.embedding.pgvector.SearchMode;

EmbeddingStore<TextSegment> embeddingStore = PgVectorEmbeddingStore.builder()
        .host("localhost")
        .port(5432)
        .database("postgres")
        .user("my_user")
        .password("my_password")
        .table("document_embeddings")
        .dimension(embeddingModel.dimension())
        .searchMode(SearchMode.HYBRID)  // Enable hybrid search (default: SearchMode.VECTOR)
        .textSearchConfig("english")    // Optional: PostgreSQL text search config (default: "simple")
        .rrfK(60)    // Optional: RRF algorithm parameter (default: 60)
        .build();
```

#### 用法

使用混合搜索时，必须同时提供**嵌入**和**查询文本**：

```java
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;

String question = "How to configure PostgreSQL vector search?";

// Generate embedding for the query
Embedding questionEmbedding = embeddingModel.embed(question).content();

// Search with both embedding and text (required for HYBRID mode)
EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
        .queryEmbedding(questionEmbedding)  // For vector similarity search
        .query(question)                    // For keyword search (REQUIRED in HYBRID mode)
        .maxResults(3)
        .build();

List<EmbeddingMatch<TextSegment>> results = embeddingStore.search(request);
```

#### 工作原理

混合搜索使用**倒数排名融合（RRF）**来合并结果：

1. **向量搜索**：使用余弦相似度查找语义相似的文本
2. **关键词搜索**：使用 PostgreSQL 的 `tsvector` 查找包含匹配关键词的文本
3. **RRF 融合**：使用以下公式合并排名：

```
RRF_Score = 1/(k + rank_vector) + 1/(k + rank_keyword)
```

其中：
- `k` 是常数（可通过 `rrfK()` 配置，默认值：60）
- `rank_vector` 是向量搜索中的排名位置（1 = 最佳匹配）
- `rank_keyword` 是关键词搜索中的排名位置（1 = 最佳匹配）

**分数计算示例**（k = 80，与测试中使用的相同）：

如果一个文档在向量搜索和关键词搜索中都排名第 1：
```
Score = 1/(80+1) + 1/(80+1)
      = 1/81 + 1/81
      ≈ 0.0247
```

**分数范围说明**
- 当某个结果在两种搜索中都排名第 1 时，最大分数为 `2/(k+1)`（例如 k=60 → 约 0.0328；k=80 → 约 0.0247）。
- 随着排名增大，分数向 0 衰减；它们**不会**达到 1.0。
- RRF 分数基于排名，不能与仅向量搜索的余弦相似度（0.0–1.0）直接比较。

#### 与仅向量搜索的主要区别

| 方面 | 向量搜索 | 混合搜索 |
|--------|--------------|---------------|
| **查询输入** | 仅 `queryEmbedding` | 同时提供 `queryEmbedding` 和 `query` 文本 |
| **分数类型** | 余弦相似度（0.0-1.0） | RRF 基于排名的分数（最大 `≈ 2/(k+1)`；k=60 时约 0.033） |
| **最适合** | 语义相似度、同义改写 | 精确关键词 + 语义含义 |

#### 调整 RRF 参数

调整 `rrfK` 参数以控制排名敏感度：

```java
.rrfK(40)   // More weight to top-ranked results (higher scores for top matches)
.rrfK(80)   // More balanced between top and lower-ranked results
```

- **较低的 k（20-40）**：更强调排名靠前的结果
- **较高的 k（80-100）**：排名分布更均衡
- **默认值（60）**：对大多数用例都能取得良好的平衡

### Spring Boot 集成

要查看将 pgvector 与 Spring Boot 微服务集成的完整生产就绪示例，
请参阅 [pgvector RAG Spring Boot 示例](https://github.com/langchain4j/langchain4j-examples/tree/main/pgvector-rag-springboot)。

该示例演示了：
- PgVectorEmbeddingStore 的 Spring Boot 自动配置
- 用于文档摄入和查询的 REST API 端点
- 适当的连接池和错误处理
- 用于本地开发的 Docker Compose 设置

- [更多示例](https://github.com/langchain4j/langchain4j-examples/tree/main/pgvector-example/src/main/java)
