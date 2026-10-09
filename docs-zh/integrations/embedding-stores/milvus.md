# Milvus

[Milvus](https://milvus.io/) 是一个开源向量数据库。LangChain4j 可以将其用作
`EmbeddingStore`，以持久化嵌入并对其进行相似性搜索。

## 两个 Milvus 模块

目前**有两个** Milvus 集成模块。它们相互独立，可以并排使用。

| 模块 | Milvus Java SDK | 功能 | 状态 |
|---|---|---|---|
| `langchain4j-milvus` | v1（`MilvusServiceClient`） | 稠密向量搜索 | 遗留（旧版）。基于已弃用的 v1 SDK 构建。 |
| `langchain4j-milvus-v2` | v2（`MilvusClientV2`） | 稠密 **+ 稀疏 + 混合** 搜索（含内置 BM25） | 当前版本。推荐新项目使用。 |

!!! note "过渡性命名 — 此命名将在 LangChain4j 2.0 中变更"
    `-v2` 后缀指的是 **Milvus SDK 版本**，而不是本模块的版本。它是临时的。

    在 **LangChain4j 2.0** 中，遗留的 `langchain4j-milvus` 模块将被**移除**，`langchain4j-milvus-v2`
    将被**重命名为 `langchain4j-milvus`**（Maven 构件、`...milvus.v2` 包以及 `MilvusV2*`
    类名将全部去掉 `v2`）。

    如果你现在就采用 `langchain4j-milvus-v2`，请注意升级到 2.0 时需要更新你的 Maven
    坐标、导入和类名。迁移指南将随 2.0 发布提供。

    **新项目应使用 `langchain4j-milvus-v2`。**

---

## `langchain4j-milvus-v2`（推荐）

基于当前 Milvus Java SDK v2 构建。支持稠密向量搜索、稀疏向量搜索和混合
（稠密 + 稀疏）搜索——包括 Milvus 内置的 BM25 全文稀疏向量。

### Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-milvus-v2</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

### API

- `MilvusV2EmbeddingStore`

### 基本用法 — 稠密向量搜索

这是标准的 `EmbeddingStore` 用法。搜索模式默认为 `VECTOR`（仅稠密）。

```java
MilvusV2EmbeddingStore store = MilvusV2EmbeddingStore.builder()
        .uri("http://localhost:19530")        // or .host("localhost").port(19530)
        .collectionName("my_collection")
        .dimension(384)                        // required when a new collection is created
        .build();

store.add(embedding, textSegment);

EmbeddingSearchResult<TextSegment> result = store.search(
        EmbeddingSearchRequest.builder()
                .queryEmbedding(queryEmbedding)
                .maxResults(5)
                .build());
```

### 混合搜索（稠密 + 稀疏）

混合搜索将稠密向量搜索与稀疏向量搜索相结合，并使用重排器（默认使用倒数排名融合，
Reciprocal Rank Fusion）合并结果。通过 `searchMode(HYBRID)` 启用。

有两种方式生成稀疏向量，通过 `sparseMode` 选择：

- **`BM25`（默认）** — Milvus 自动根据你的文本计算稀疏向量。你只需提供文本。
- **`CUSTOM`** — 你自己提供稀疏向量（例如来自 BGE-M3 模型）。

#### 选项 A — 内置 BM25（文本 → 稀疏，由 Milvus 计算）

```java
MilvusV2EmbeddingStore store = MilvusV2EmbeddingStore.builder()
        .uri("http://localhost:19530")
        .collectionName("bm25_collection")
        .dimension(384)
        .searchMode(MilvusV2EmbeddingStore.SearchMode.HYBRID)
        .sparseMode(MilvusV2EmbeddingStore.MilvusSparseMode.BM25)   // default
        .build();

// Insert: only dense embeddings are needed; Milvus builds the BM25 sparse index from the text.
store.addAll(ids, denseEmbeddings, textSegments);

// Search: provide the dense query embedding and the query text (used for BM25).
MilvusV2EmbeddingSearchRequest request = MilvusV2EmbeddingSearchRequest.milvusBuilder()
        .queryEmbedding(queryDenseEmbedding)
        .query("full-text keywords here")
        .maxResults(10)
        .build();

EmbeddingSearchResult<TextSegment> result = store.search(request);
```

#### 选项 B — 自定义稀疏向量（例如 BGE-M3）

```java
MilvusV2EmbeddingStore store = MilvusV2EmbeddingStore.builder()
        .uri("http://localhost:19530")
        .collectionName("hybrid_collection")
        .dimension(384)
        .searchMode(MilvusV2EmbeddingStore.SearchMode.HYBRID)
        .sparseMode(MilvusV2EmbeddingStore.MilvusSparseMode.CUSTOM) // you provide sparse vectors
        .build();

// Insert both dense and sparse embeddings.
List<SparseEmbedding> sparseEmbeddings = List.of(
        new SparseEmbedding(new long[]{1L, 42L, 300L}, new float[]{0.8f, 0.5f, 0.3f}),
        new SparseEmbedding(new long[]{7L, 99L},        new float[]{0.6f, 0.4f}));
store.addAllHybrid(ids, denseEmbeddings, sparseEmbeddings, textSegments);

// Search with a dense query embedding and a sparse query embedding.
MilvusV2EmbeddingSearchRequest request = MilvusV2EmbeddingSearchRequest.milvusBuilder()
        .queryEmbedding(queryDenseEmbedding)
        .sparseEmbedding(querySparseEmbedding)
        .maxResults(10)
        .build();

EmbeddingSearchResult<TextSegment> result = store.search(request);
```

!!! note
    搜索模式是**集合架构（collection schema）**的属性，在创建存储（和集合）时一次性设置。`HYBRID` 集合同时具有
    稠密和稀疏向量字段；`VECTOR` 集合只有稠密字段。两者不能互换——切换模式需要新建集合。

### 连接 Zilliz Cloud

```java
MilvusV2EmbeddingStore store = MilvusV2EmbeddingStore.builder()
        .uri("https://xxx.api.gcp-us-west1.zillizcloud.com")
        .token("your-api-key")
        .collectionName("my_collection")
        .dimension(384)
        .build();
```

你也可以通过 `.milvusClient(client)` 传入自己的 `MilvusClientV2` 实例。

### 兼容性

- 推荐使用 Milvus Server **2.5.x 或更高版本**（BM25 全文搜索需要 2.5+；混合搜索需要 2.4+）。
- Java 17+

---

## `langchain4j-milvus`（遗留，旧版）

基于 Milvus Java SDK v1 构建。仅支持稠密向量搜索。它将在 LangChain4j 2.0
中被移除（参见上面的说明）；新项目应优先使用 `langchain4j-milvus-v2`。

### Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-milvus</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

### API

- `MilvusEmbeddingStore`

### 创建

创建 `MilvusEmbeddingStore` 有 2 种方式：

1. 让存储根据主机、端口和认证信息在内部创建 `MilvusServiceClient`：

```java
MilvusEmbeddingStore store = MilvusEmbeddingStore.builder()
    .host("localhost")                         // Host for Milvus instance
    .port(19530)                               // Port for Milvus instance
    .collectionName("example_collection")      // Name of the collection
    .dimension(128)                            // Dimension of vectors
    .indexType(IndexType.FLAT)                 // Index type
    .metricType(MetricType.COSINE)             // Metric type
    .username("username")                      // Username for Milvus
    .password("password")                      // Password for Milvus
    .consistencyLevel(ConsistencyLevelEnum.EVENTUALLY)  // Consistency level
    .autoFlushOnInsert(true)                   // Auto flush after insert
    .idFieldName("id")                         // ID field name
    .textFieldName("text")                     // Text field name
    .metadataFieldName("metadata")             // Metadata field name
    .vectorFieldName("vector")                 // Vector field name
    .build();
```

2. 传入现有的 `MilvusServiceClient`：

```java
// Set up a custom MilvusServiceClient
MilvusServiceClient customMilvusClient = new MilvusServiceClient(
    ConnectParam.newBuilder()
        .withHost("localhost")
        .withPort(19530)
        .build()
);

// Use the custom client in the builder
MilvusEmbeddingStore store = MilvusEmbeddingStore.builder()
    .milvusClient(customMilvusClient)          // Use an existing Milvus client
    .collectionName("example_collection")      // Name of the collection
    .dimension(128)                            // Dimension of vectors
    .indexType(IndexType.FLAT)                 // Index type
    .metricType(MetricType.COSINE)             // Metric type
    .consistencyLevel(ConsistencyLevelEnum.EVENTUALLY)  // Consistency level
    .autoFlushOnInsert(true)                   // Auto flush after insert
    .idFieldName("id")                         // ID field name
    .textFieldName("text")                     // Text field name
    .metadataFieldName("metadata")             // Metadata field name
    .vectorFieldName("vector")                 // Vector field name
    .build();
```

---

## 示例

- [MilvusEmbeddingStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/milvus-example/src/main/java/MilvusEmbeddingStoreExample.java)
