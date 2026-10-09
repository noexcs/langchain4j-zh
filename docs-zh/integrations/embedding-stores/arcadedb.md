# ArcadeDB

https://arcadedb.com/

ArcadeDB 是一种多模型 NoSQL 数据库，支持图、文档、键值、时间序列和向量数据。它内置了 LSM_VECTOR 索引（由 JVector/HNSW 提供支持），用于高性能的近似最近邻（ANN）向量搜索。

LangChain4j 集成支持两种运行模式：

- **远程模式** — 通过 HTTP 连接 ArcadeDB 服务器。适合生产部署和共享基础设施。
- **嵌入式模式** — 在同一个 JVM 内进程内运行 ArcadeDB。无需服务器或 Docker 容器；数据库存储在本机文件系统上。适合测试、桌面应用或单进程工作负载。

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-arcadedb</artifactId>
    <version>${latest version here}</version>
</dependency>
```

注意：这是一个社区集成模块。你可能需要在项目配置中添加 langchain4j-community 仓库。

## API

- `ArcadeDBEmbeddingStore`

## 功能

- **两种运行模式**：远程（通过 HTTP 客户端连接 ArcadeDB 服务器）或嵌入式（ArcadeDB 进程内运行，无需服务器）
- **多模型数据库**：在 ArcadeDB 的图模型中，将嵌入作为顶点与文档、键值和时间序列数据一起存储
- **HNSW 向量索引**：使用 ArcadeDB 的 LSM_VECTOR 索引（基于 JVector）进行快速的近似最近邻搜索
- **元数据过滤**：支持使用比较运算符和逻辑运算符按元数据过滤搜索结果
- **持久化存储**：远程模式和嵌入式模式下，数据在重启后均持久保留
- **自动创建架构**：首次使用时自动创建顶点类型、属性和向量索引
- **多种相似度函数**：支持 COSINE（默认）、EUCLIDEAN 和 SQUARED_EUCLIDEAN 距离度量（远程模式）
- **批量操作**：一次调用添加多个嵌入
- **灵活的删除**：按 ID、按过滤器删除嵌入，或清空全部

## 基本用法

### 远程模式

远程模式连接到一个正在运行的 ArcadeDB 服务器。要本地启动一个服务器，请参见 [使用 Docker 运行 ArcadeDB](#使用-docker-运行-arcadedb)。

#### 连接现有数据库

```java
EmbeddingStore<TextSegment> embeddingStore = ArcadeDBEmbeddingStore.builder()
    .host("localhost")
    .port(2480)
    .databaseName("my_database")
    .username("root")
    .password("playwithdata")
    .dimension(384)           // Must match your embedding model's dimension
    .build();
```

#### 自动创建数据库

```java
EmbeddingStore<TextSegment> embeddingStore = ArcadeDBEmbeddingStore.builder()
    .host("localhost")
    .port(2480)
    .databaseName("my_database")
    .username("root")
    .password("playwithdata")
    .dimension(384)
    .createDatabase(true)     // Create database if it doesn't exist
    .build();
```

### 嵌入式模式

嵌入式模式在同一个 JVM 内运行 ArcadeDB。无需服务器——只需提供本地文件系统中数据库应存储的路径即可。如果数据库尚不存在，它会被自动创建。

使用完毕后请务必调用 `close()` 以释放资源。

```java
ArcadeDBEmbeddingStore embeddingStore = ArcadeDBEmbeddingStore.embeddedBuilder()
    .databasePath("/path/to/my-database")
    .dimension(384)           // Must match your embedding model's dimension
    .build();

// ... use the store ...

embeddingStore.close();
```

请使用 try-finally（或通过包装类使用 try-with-resources）确保 `close()` 总是被调用：

```java
ArcadeDBEmbeddingStore embeddingStore = ArcadeDBEmbeddingStore.embeddedBuilder()
    .databasePath("/path/to/my-database")
    .dimension(384)
    .build();
try {
    // ... use the store ...
} finally {
    embeddingStore.close();
}
```

### 添加和搜索嵌入

两种模式下的搜索 API 完全相同：

```java
// Add a text segment with its embedding
TextSegment segment = TextSegment.from("Hello, world!", Metadata.from("source", "example"));
Embedding embedding = embeddingModel.embed(segment).content();
embeddingStore.add(embedding, segment);

// Search for similar embeddings
EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
    .queryEmbedding(queryEmbedding)
    .maxResults(5)
    .minScore(0.7)
    .build();

List<EmbeddingMatch<TextSegment>> matches = embeddingStore.search(request).matches();
```

## 配置选项

### 远程模式

```java
EmbeddingStore<TextSegment> embeddingStore = ArcadeDBEmbeddingStore.builder()
    .host("localhost")              // Required: ArcadeDB server hostname
    .port(2480)                     // Default: 2480 (HTTP port)
    .databaseName("my_database")   // Required: database name
    .username("root")               // Required: username
    .password("playwithdata")       // Required: password
    .typeName("EmbeddingDocument") // Default: "EmbeddingDocument" — vertex type name
    .dimension(384)                 // Required: embedding vector dimension
    .similarityFunction("COSINE")  // Default: "COSINE" — similarity metric
    .maxConnections(16)             // Default: 16 — HNSW graph connections per node
    .beamWidth(100)                 // Default: 100 — HNSW search beam width
    .createDatabase(false)          // Default: false — auto-create the database
    .metadataPrefix("meta_")       // Default: "meta_" — prefix for metadata properties
    .build();
```

### 嵌入式模式

```java
ArcadeDBEmbeddingStore embeddingStore = ArcadeDBEmbeddingStore.embeddedBuilder()
    .databasePath("/path/to/my-database") // Required: local filesystem path for the database
    .typeName("EmbeddingDocument")        // Default: "EmbeddingDocument" — vertex type name
    .dimension(384)                        // Default: 384 — embedding vector dimension
    .maxConnections(16)                    // Default: 16 — HNSW graph connections per node
    .beamWidth(100)                        // Default: 100 — HNSW search beam width
    .metadataPrefix("")                    // Default: "" (no prefix) — prefix for metadata properties
    .build();
```

### 参数指南

**共享参数（两种模式）：**

- **typeName**：用于存储嵌入文档的顶点类型。更改此值可在同一数据库内使用多个向量存储
- **dimension**：必须与嵌入模型的输出维度完全一致
- **maxConnections**：控制 HNSW 索引中图的连接度。较高的值会提高召回率，但会增加内存和索引构建时间。推荐：16–128
- **beamWidth**：控制 HNSW 索引构建和搜索的质量。较高的值会以速度为代价获得更好的召回率。推荐：100–500
- **metadataPrefix**：元数据键存储为顶点属性时应用的前缀。如果元数据键与内置属性冲突，请更改此值

**仅远程模式的参数：**

- **host**：ArcadeDB 服务器的主机名或 IP 地址（必填）
- **port**：ArcadeDB REST API 的 HTTP 端口（默认：2480）
- **databaseName**：要连接或创建的数据库（必填）
- **username / password**：ArcadeDB 凭据（必填）
- **similarityFunction**：
  - `COSINE` — 余弦相似度；最适合归一化向量（默认）
  - `EUCLIDEAN` — 欧几里得距离
  - `SQUARED_EUCLIDEAN` — 欧几里得距离的平方；比 EUCLIDEAN 更快
- **createDatabase**：设为 `true` 后，若数据库不存在则自动创建

**仅嵌入式模式的参数：**

- **databasePath**：嵌入式数据库所在目录的路径。如果不存在会自动创建
- **database**：也可以直接提供一个现有的 `com.arcadedb.database.Database` 实例，而不是路径

## 元数据过滤

ArcadeDB 支持按元数据过滤搜索结果。过滤器在向量索引查找之后应用。

```java
// Filter by a single metadata value
Filter filter = new IsEqualTo("source", "wikipedia");

EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
    .queryEmbedding(queryEmbedding)
    .maxResults(5)
    .filter(filter)
    .build();

List<EmbeddingMatch<TextSegment>> matches = embeddingStore.search(request).matches();
```

### 支持的过滤器类型

**比较运算符：**
- `IsEqualTo`, `IsNotEqualTo`
- `IsGreaterThan`, `IsGreaterThanOrEqualTo`
- `IsLessThan`, `IsLessThanOrEqualTo`
- `IsIn`, `IsNotIn`

**逻辑运算符：**
- `And`, `Or`, `Not`

## 删除操作

```java
// Remove by list of IDs
embeddingStore.removeAll(List.of("id1", "id2"));

// Remove by metadata filter
embeddingStore.removeAll(new IsEqualTo("source", "old-source"));

// Remove all embeddings
embeddingStore.removeAll();
```

## 当前限制

- **近似搜索**：HNSW 索引是近似的。当结果集非常大且包含许多近乎相同的向量时，某些文档可能不会被返回
- **内存中应用过滤器**：元数据过滤器在向量搜索之后在内存中应用，而不是在索引级别应用。该存储会获取最多 5 倍于请求结果数的候选，以应对过滤器带来的缩减
- **浮点精度**：ArcadeDB 以 JSON double 的形式返回向量，与原始存储值相比可能引入微小的浮点精度差异。`Double.MIN_VALUE`（4.9E-324）会下溢为 0.0，无法精确存储
- **不支持字符串内容过滤器**：基于字符串的内容过滤器（例如 `ContainsString`）不受支持；只能使用上面列出的元数据过滤器类型
- **嵌入式模式下无法选择相似度函数**：嵌入式构建器没有暴露 `similarityFunction` 选项；索引使用其默认度量

## 使用 Docker 运行 ArcadeDB

远程模式的必备条件。最简单的启动方式：

```bash
docker run -d \
  --name arcadedb \
  -p 2480:2480 \
  -e JAVA_OPTS="-Darcadedb.server.rootPassword=playwithdata" \
  arcadedata/arcadedb:latest
```

然后连接你的存储：

```java
EmbeddingStore<TextSegment> embeddingStore = ArcadeDBEmbeddingStore.builder()
    .host("localhost")
    .port(2480)
    .databaseName("embeddings")
    .username("root")
    .password("playwithdata")
    .dimension(384)
    .createDatabase(true)
    .build();
```

## 示例

- 集成测试示例请查看 [langchain4j-community-arcadedb 模块](https://github.com/langchain4j/langchain4j-community/tree/main/embedding-stores/langchain4j-community-arcadedb/src/test/java) 中的测试文件
- 你也可以在 [langchain4j-examples 项目](https://github.com/langchain4j/langchain4j-examples) 中找到一些示例
