# Valkey

https://valkey.io/


## Maven 依赖

你可以在纯 Java 或 Spring Boot 应用中将 Valkey 与 LangChain4j 一起使用。

### 纯 Java

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-valkey</artifactId>
    <version>${latest version here}</version>
</dependency>
```

### Spring Boot

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-valkey-spring-boot-starter</artifactId>
    <version>${latest version here}</version>
</dependency>
```

或者，你可以使用 BOM 来统一管理依赖：

```xml
<dependencyManagement>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-community-bom</artifactId>
        <version>${latest version here}</version>
        <type>pom</type>
        <scope>import</scope>
    </dependency>
</dependencyManagement>
```


## 概述

`langchain4j-community-valkey` 模块提供了将 [Valkey](https://valkey.io/) 用作嵌入存储的集成，
使用 Valkey 内置的向量搜索功能（Valkey 8+）。

它使用官方的 [valkey-glide](https://github.com/valkey-io/valkey-glide) 客户端连接到 Valkey 服务器。
嵌入、文本和元数据以结构化 JSON 文档的形式存储，并采用 HNSW 索引实现亚毫秒级相似度搜索。

### 前提条件

需要 Valkey 9.1+。`valkey-bundle` 镜像包含向量索引所需的 JSON 和 Search 模块。

```bash
docker run -d --name valkey -p 6379:6379 valkey/valkey-bundle:latest
```


## API

- `ValkeyEmbeddingStore`

### 创建 ValkeyEmbeddingStore

```java
import dev.langchain4j.community.store.embedding.valkey.ValkeyEmbeddingStore;
import glide.api.GlideClient;
import glide.api.models.configuration.GlideClientConfiguration;
import glide.api.models.configuration.NodeAddress;

// 1. Create a GlideClient connection
GlideClientConfiguration config = GlideClientConfiguration.builder()
        .address(NodeAddress.builder().host("localhost").port(6379).build())
        .build();

GlideClient client = GlideClient.createClient(config).get();

// 2. Build the embedding store
ValkeyEmbeddingStore embeddingStore = ValkeyEmbeddingStore.builder()
        .client(client)
        .dimension(384)          // Must match your embedding model's output dimension
        .indexName("my-index")   // Optional, defaults to "embedding-index"
        .prefix("docs:")         // Optional, defaults to "embedding:"
        .build();
```

在 `build()` 时，存储会检查 Valkey 中索引是否存在。如果不存在，它会创建一个使用 HNSW 索引和 COSINE 距离度量（默认值）的索引。

### 配置选项

| 参数 | 描述 | 默认值 |
|-----------|-------------|---------|
| `client` | `GlideClient` 实例（必填） | — |
| `dimension` | 嵌入向量维度（如果索引不存在则必填） | — |
| `indexName` | Valkey 搜索索引的名称 | `"embedding-index"` |
| `prefix` | 所存嵌入的键前缀（应以 `:` 结尾） | `"embedding:"` |
| `metadataKeys` | 作为 Tag 字段持久化的元数据键集合 | — |
| `metadataConfig` | 从元数据键到 `FieldInfo` 的映射，用于自定义字段类型 | — |
| `operationTimeoutSeconds` | 每个 Valkey 操作的超时时间（秒） | `60` |

### 距离度量

Valkey 通过 `MetricType` 枚举支持三种距离度量：

- `COSINE` — 余弦相似度（默认）
- `IP` — 内积
- `L2` — 欧氏距离

### 存储和搜索嵌入

```java
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.embedding.onnx.allminilml6v2.AllMiniLmL6V2EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingMatch;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingSearchResult;

import java.util.List;

EmbeddingModel embeddingModel = new AllMiniLmL6V2EmbeddingModel();

// Batch ingest
List<TextSegment> docs = List.of(
        TextSegment.from("Valkey is a high-performance in-memory data store."),
        TextSegment.from("Vector search finds similar items by embedding distance."),
        TextSegment.from("HNSW is an algorithm for approximate nearest neighbors.")
);
List<Embedding> embeddings = embeddingModel.embedAll(docs).content();
List<String> ids = embeddingStore.addAll(embeddings, docs);

// Search
Embedding queryEmbedding = embeddingModel.embed("How does similarity search work?").content();
EmbeddingSearchResult<TextSegment> results = embeddingStore.search(
        EmbeddingSearchRequest.builder()
                .queryEmbedding(queryEmbedding)
                .maxResults(3)
                .minScore(0.5)
                .build()
);

for (EmbeddingMatch<TextSegment> match : results.matches()) {
    System.out.printf("%.3f: %s%n", match.score(), match.embedded().text());
}
```

### 元数据过滤

Valkey 支持对元数据使用以下过滤类型：

- **数值字段**：`eq`、`neq`、`gt`、`gte`、`lt`、`lte`
- **Tag/文本字段**：`eq`、`neq`、`in`、`notIn`

要启用元数据过滤，请在构建存储时配置元数据字段。对于简单的基于 tag 的过滤，使用 `metadataKeys`：

```java
ValkeyEmbeddingStore store = ValkeyEmbeddingStore.builder()
        .client(client)
        .dimension(384)
        .metadataKeys(List.of("category", "author"))
        .build();
```

对于带类型的字段（例如数值与 tag 之分），使用 `metadataConfig`：

```java
import glide.api.models.commands.FT.FTCreateOptions.FieldInfo;
import glide.api.models.commands.FT.FTCreateOptions.NumericField;
import glide.api.models.commands.FT.FTCreateOptions.TagField;

Map<String, FieldInfo> metadataConfig = Map.of(
        "category", new FieldInfo("$.category", "category", new TagField(',', true)),
        "year", new FieldInfo("$.year", "year", new NumericField())
);

ValkeyEmbeddingStore store = ValkeyEmbeddingStore.builder()
        .client(client)
        .dimension(384)
        .indexName("filtered-docs")
        .prefix("filtered:")
        .metadataConfig(metadataConfig)
        .build();
```

然后在搜索请求中使用过滤器：

```java
import static dev.langchain4j.store.embedding.filter.MetadataFilterBuilder.metadataKey;

// TAG filter
Filter securityFilter = metadataKey("category").isEqualTo("security");

// NUMERIC filter
Filter recentFilter = metadataKey("year").isGreaterThanOrEqualTo(2025);

// Combined AND filter
Filter combined = metadataKey("category").isEqualTo("security")
        .and(metadataKey("year").isGreaterThanOrEqualTo(2025));

// OR filter
Filter either = metadataKey("category").isEqualTo("security")
        .or(metadataKey("category").isEqualTo("performance"));

EmbeddingSearchResult<TextSegment> results = store.search(
        EmbeddingSearchRequest.builder()
                .queryEmbedding(queryEmbedding)
                .maxResults(5)
                .filter(combined)
                .build()
);
```


## 示例

- [ValkeyEmbeddingStoreIT](https://github.com/langchain4j/langchain4j-community/blob/main/embedding-stores/langchain4j-community-valkey/src/test/java/dev/langchain4j/community/store/embedding/valkey/ValkeyEmbeddingStoreIT.java)
