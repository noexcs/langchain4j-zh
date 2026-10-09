# CockroachDB

[CockroachDB](https://www.cockroachlabs.com/) 是一种分布式 SQL 数据库，
使用 PostgreSQL 线协议。自 v24.2 起，它原生提供 `VECTOR`
列类型；自 v25.2 起，它提供了一个名为 **C-SPANN** 的分布式近似最近邻
索引。`langchain4j-community-cockroachdb`
模块将两者与 LangChain4j 集成，作为：

- 向量 `EmbeddingStore<TextSegment>`（`CockroachDbEmbeddingStore`）
- `ChatMemoryStore`（`CockroachDbChatMemoryStore`）

该 Java 模块在存在对应 Java 实现的地方，
镜像了官方 Python 库
[`langchain-cockroachdb`](https://github.com/cockroachdb/langchain-cockroachdb)
的功能集。

## 版本要求

| 功能 | 最低 CockroachDB 版本 |
| --- | --- |
| `VECTOR(n)` 列类型 | v24.2 |
| `CREATE VECTOR INDEX`（C-SPANN） | v25.2 |
| 通过 `ttl_expiration_expression` 实现的行级 TTL | v23.1 |

在 CockroachDB v25.2 上，向量索引由一个集群设置控制。在创建带有 `CSpannIndex` 的存储之前，
每个集群只需启用一次：

```sql
SET CLUSTER SETTING feature.vector_index.enabled = true;
```

## Maven 依赖

!!! note
    由于 CockroachDB 支持是 `langchain4j-community` 的一部分，
    它将从 `1.22.0-beta32` 或更高版本开始可用。

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-cockroachdb</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

如果你导入了 Community BOM，可以省略版本号。

## API

该模块暴露了四个公共类：

### `CockroachDbEngine`

封装一个 HikariCP `DataSource` 并处理连接池。可以从
单独的 `host`/`port`/`database`/`username`/`password` 字段构建，从完整的
连接字符串构建（Python 风格的 `cockroachdb://` 协议会被自动重写为
`jdbc:postgresql://`），也可以通过 `CockroachDbEngine.from(dataSource)`
从现有的 `DataSource` 构建。

### `CockroachDbSchema`

封装嵌入表的布局：表和列名、向量维度、距离度量、用于多租户的可选命名空间列、
所选的向量索引策略，以及用于未来混合搜索的可选生成式 `tsvector` 列。

### `CockroachDbEmbeddingStore`

针对原生 CockroachDB `VECTOR` 列实现 LangChain4j 的 `EmbeddingStore<TextSegment>`。支持批量插入、
JSONB 元数据过滤、按 id / 按 `Filter` / 批量删除、可选的命名空间作用域，
以及针对 C-SPANN 的可选每查询 `vector_search_beam_size` 调优。

### `CockroachDbChatMemoryStore`

实现 LangChain4j 的 `ChatMemoryStore`。在一个 JSONB 列中按显式插入索引排序
持久化序列化后的聊天消息，支持可选的行级 TTL。

## 连接

`CockroachDbEngine` 封装一个 `HikariDataSource`。你可以从连接字符串
或从单独字段构建一个。

```java
import dev.langchain4j.community.store.embedding.cockroachdb.CockroachDbEngine;

CockroachDbEngine engine = CockroachDbEngine.builder()
        .host("localhost")
        .port(26257)
        .database("defaultdb")
        .username("root")
        .password("")
        .sslMode("disable")
        .build();
```

构建器也接受完整的连接字符串。Python 风格的
`cockroachdb://` 协议会被自动重写为 `jdbc:postgresql://`，
因此你可以粘贴 Python 库使用的相同 URL：

```java
CockroachDbEngine engine = CockroachDbEngine.fromConnectionString(
        "cockroachdb://root@localhost:26257/defaultdb?sslmode=disable");
```

如果你已经有了 `DataSource`，请使用 `CockroachDbEngine.from(dataSource)`。

## 向量存储

一个最小的向量存储使用顺序扫描（`NoIndex`），这适用于
小型数据集和测试：

```java
import dev.langchain4j.community.store.embedding.cockroachdb.CockroachDbEmbeddingStore;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.embedding.onnx.allminilml6v2q.AllMiniLmL6V2QuantizedEmbeddingModel;

EmbeddingModel model = new AllMiniLmL6V2QuantizedEmbeddingModel();

CockroachDbEmbeddingStore store = CockroachDbEmbeddingStore.builder()
        .engine(engine)
        .dimension(model.dimension())
        .tableName("embeddings")
        .build();

TextSegment segment = TextSegment.from("Cockroaches are surprisingly resilient.");
Embedding embedding = model.embed(segment).content();
store.add(embedding, segment);
```

对于 CockroachDB v25.2+ 上的生产工作负载，请添加一个 C-SPANN 向量索引：

```java
import dev.langchain4j.community.store.embedding.cockroachdb.index.CSpannIndex;

CockroachDbEmbeddingStore store = CockroachDbEmbeddingStore.builder()
        .engine(engine)
        .dimension(model.dimension())
        .vectorIndex(CSpannIndex.builder()
                .minPartitionSize(16)
                .maxPartitionSize(128)
                .build())
        .build();
```

为该索引发出的 DDL 是：

```sql
CREATE VECTOR INDEX IF NOT EXISTS embeddings_embedding_vector_idx
  ON public.embeddings (embedding)
  WITH (min_partition_size = 16, max_partition_size = 128);
```

C-SPANN 从查询操作符中选择距离函数（余弦用 `<=>`，
L2 用 `<->`，内积用 `<#>`），因此 `MetricType` 是在存储上查询时
选择的，而不是绑定到索引。

### 搜索

`EmbeddingSearchRequest` 与 LangChain4j 其他存储中的行为相同：

```java
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingSearchResult;

EmbeddingSearchResult<TextSegment> result = store.search(
        EmbeddingSearchRequest.builder()
                .queryEmbedding(model.embed("resilience").content())
                .maxResults(5)
                .minScore(0.6)
                .build());

result.matches().forEach(m ->
        System.out.printf("%s (%.3f) %s%n", m.embeddingId(), m.score(), m.embedded().text()));
```

### 在查询时调优 C-SPANN

CockroachDB 暴露了一个会话变量 `vector_search_beam_size`，用于
控制召回率/延迟之间的权衡。在存储构建器上设置它，以便将
每次搜索包裹在一个用 `SET LOCAL` 限定作用域的事务中：

```java
CockroachDbEmbeddingStore store = CockroachDbEmbeddingStore.builder()
        .engine(engine)
        .dimension(model.dimension())
        .vectorIndex(CSpannIndex.builder().build())
        .searchBeamSize(32)
        .build();
```

较高的值以延迟换取召回率。如果你不设置该字段，
默认 beam size 由 CockroachDB 决定。

### 元数据过滤

元数据存储在一个 JSONB 列中，并在查询时
使用 LangChain4j `Filter` 表达式进行过滤：

```java
import dev.langchain4j.store.embedding.filter.MetadataFilterBuilder;

EmbeddingSearchResult<TextSegment> result = store.search(
        EmbeddingSearchRequest.builder()
                .queryEmbedding(query)
                .maxResults(10)
                .filter(MetadataFilterBuilder.metadataKey("category").isEqualTo("biology")
                        .and(MetadataFilterBuilder.metadataKey("year").isGreaterThan(2020)))
                .build());
```

比较过滤器（`>`、`>=`、`<`、`<=`）会将 JSONB 值转换为 `numeric`。
字符串上的相等性比较的是 JSON 文本。过滤器键只能包含
字母数字字符、点、下划线或连字符。

### 通过命名空间列实现多租户

要按租户限定行的范围，在 schema 中添加 `namespaceColumn`，并在每个存储实例上
配置命名空间值。该列会作为前缀添加到 C-SPANN 索引中，因此按租户的查询保持快速：

```java
CockroachDbEmbeddingStore tenantA = CockroachDbEmbeddingStore.builder()
        .engine(engine)
        .dimension(model.dimension())
        .namespaceColumn("tenant_id")
        .namespace("acme")
        .vectorIndex(CSpannIndex.builder().build())
        .build();
```

生成的索引变成 `CREATE VECTOR INDEX ... ON embeddings (tenant_id, embedding)`，
通过此存储执行的每次读/写都会过滤为 `tenant_id = 'acme'`。

### 可选全文列

如果你打算之后将向量搜索与全文搜索结合，请在建表时
启用一个生成式的 `tsvector` 列。一个 GIN 索引会与之一起创建：

```java
CockroachDbEmbeddingStore store = CockroachDbEmbeddingStore.builder()
        .engine(engine)
        .dimension(model.dimension())
        .createTsvectorColumn(true)
        .build();
```

混合（向量 + FTS）查询执行尚未实现；该列的
创建是为了供应用代码或未来版本使用。

## 聊天记忆

`CockroachDbChatMemoryStore` 实现 `ChatMemoryStore`，并在一个 JSONB 列中按插入时间排序
持久化序列化后的聊天消息：

```java
import dev.langchain4j.community.store.memory.chat.cockroachdb.CockroachDbChatMemoryStore;

CockroachDbChatMemoryStore memory = CockroachDbChatMemoryStore.builder()
        .engine(engine)
        .tableName("chat_memory")
        .build();
```

Schema 如下：

```sql
CREATE TABLE chat_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT NOT NULL,
  message JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX chat_memory_session_idx ON chat_memory (session_id, created_at);
```

`updateMessages` 在一个事务内替换整个会话，因此部分
写入对读者不可见。

### 行级 TTL

CockroachDB 可以自动使行过期。传入一个 `ttl` 时长来启用
聊天记忆表上的[行级 TTL](https://www.cockroachlabs.com/docs/stable/row-level-ttl)：

```java
import java.time.Duration;

CockroachDbChatMemoryStore memory = CockroachDbChatMemoryStore.builder()
        .engine(engine)
        .tableName("chat_memory")
        .ttl(Duration.ofDays(7))
        .ttlJobCron("@daily")
        .build();
```

Schema 设置会发出：

```sql
ALTER TABLE chat_memory SET (
  ttl_expiration_expression = $$(created_at + '7 days')$$,
  ttl_job_cron = '@daily'
);
```

要在现有表上禁用 TTL：

```java
memory.disableTtl();
```

## 重试

在默认的 `SERIALIZABLE` 隔离级别下，当事务必须重试时，
CockroachDB 返回 SQLSTATE `40001`。存储将每个工作单元包裹在
一个带指数退避和抖动（默认 5 次尝试，从 100 ms 开始，翻倍直到 10 秒）的重试循环中。
无需额外配置。

## 连接字符串格式

以下形式均被 `CockroachDbEngine.fromConnectionString` 接受：

| 形式 | 示例 |
| --- | --- |
| Python 风格 | `cockroachdb://root@localhost:26257/defaultdb?sslmode=disable` |
| psycopg 风格 | `cockroachdb+psycopg://user:pw@host:26257/db` |
| libpq 风格 | `postgresql://user@host:26257/db` |
| JDBC 风格 | `jdbc:postgresql://localhost:26257/defaultdb` |

对于 CockroachDB Cloud，请使用集群控制台中的连接字符串，
通常形式为：

```
cockroachdb://USER:PASSWORD@HOST:26257/DATABASE?sslmode=verify-full
```

## 参数汇总

### `CockroachDbEngine` 参数

| 参数 | 说明 | 默认值 | 必填/可选 |
| --- | --- | --- | --- |
| `host` | CockroachDB 服务器的主机名 | `localhost` | 必填（如果没有 `connectionString`） |
| `port` | CockroachDB 服务器的端口号 | `26257` | 必填（如果没有 `connectionString`） |
| `database` | 要连接的数据库 | `defaultdb` | 必填（如果没有 `connectionString`） |
| `username` | 用于认证的用户名 | `root` | 必填 |
| `password` | 用于认证的密码 | `""`（空） | 可选 |
| `schema` | 默认 schema 名称 | `public` | 可选 |
| `sslMode` | SSL 模式（`disable`、`require`、`verify-full` 等） | `disable` | 可选 |
| `maxPoolSize` | HikariCP 池的最大大小 | `10` | 可选 |
| `minPoolSize` | 最小空闲连接数 | `5` | 可选 |
| `connectionTimeoutMs` | 连接超时（毫秒） | `10000` | 可选 |
| `idleTimeoutMs` | 空闲超时（毫秒） | `300000` | 可选 |
| `maxLifetimeMs` | 连接最大生命周期（毫秒） | `3600000` | 可选 |
| `connectionString` | 完整 URL；设置时会覆盖单独的 host/port/db | `null` | 可选 |

### `CockroachDbEmbeddingStore` 参数

| 参数 | 说明 | 默认值 | 必填/可选 |
| --- | --- | --- | --- |
| `engine` | `CockroachDbEngine` 实例 | 无 | **必填** |
| `dimension` | 嵌入向量维度 | 无 | **必填** |
| `tableName` | 嵌入表名 | `embeddings` | 可选 |
| `schemaName` | 数据库 schema 名称 | `public` | 可选 |
| `metricType` | 距离度量：`COSINE`、`EUCLIDEAN` 或 `DOT_PRODUCT` | `COSINE` | 可选 |
| `vectorIndex` | `CSpannIndex` 或 `NoIndex` | `NoIndex`（顺序扫描） | 可选 |
| `namespaceColumn` | 用于多租户的租户列名 | `null`（禁用） | 可选 |
| `namespace` | 应用于每次读写的租户值 | `null` | 可选，需要 `namespaceColumn` |
| `searchBeamSize` | 每查询 `vector_search_beam_size` 会话变量 | `null`（CockroachDB 默认值） | 可选 |
| `createTableIfNotExists` | 在构建时创建表 | `true` | 可选 |
| `createTsvectorColumn` | 添加生成式 `tsvector` 列 + GIN 索引 | `false` | 可选 |

### `CSpannIndex` 参数（CockroachDB v25.2+）

| 参数 | 说明 | 默认值 | 必填/可选 |
| --- | --- | --- | --- |
| `name` | 自定义索引名称 | `{table}_{column}_vector_idx` | 可选 |
| `minPartitionSize` | 最小分区大小（通过 `WITH` 发出） | CockroachDB 默认值 | 可选 |
| `maxPartitionSize` | 最大分区大小（通过 `WITH` 发出） | CockroachDB 默认值 | 可选 |

### `CockroachDbChatMemoryStore` 参数

| 参数 | 说明 | 默认值 | 必填/可选 |
| --- | --- | --- | --- |
| `engine` | `CockroachDbEngine` 实例 | 无 | **必填** |
| `tableName` | 聊天历史表名 | `message_store` | 可选 |
| `schemaName` | 数据库 schema 名称 | `public` | 可选 |
| `ttl` | 行级 TTL 时长；设置时启用 CockroachDB TTL | `null`（禁用） | 可选 |
| `ttlJobCron` | TTL 作业调度 | `@daily` | 可选，需要 `ttl` |
| `createTableIfNotExists` | 在构建时创建表 | `true` | 可选 |

## 示例

一个最小的端到端 RAG 演示，它启动一个 CockroachDB Testcontainer，
索引两个文本片段，并运行一次相似度搜索：

```java
import dev.langchain4j.community.store.embedding.cockroachdb.CockroachDbEmbeddingStore;
import dev.langchain4j.community.store.embedding.cockroachdb.CockroachDbEngine;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.embedding.onnx.allminilml6v2.AllMiniLmL6V2EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingMatch;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingStore;
import java.util.List;
import org.testcontainers.containers.CockroachContainer;

public class CockroachDbEmbeddingStoreExample {

    public static void main(String[] args) {
        try (CockroachContainer cockroach = new CockroachContainer("cockroachdb/cockroach:latest-v25.2")) {
            cockroach.start();

            CockroachDbEngine engine = CockroachDbEngine.builder()
                    .connectionString(cockroach.getJdbcUrl())
                    .username(cockroach.getUsername())
                    .password(cockroach.getPassword())
                    .build();

            EmbeddingModel embeddingModel = new AllMiniLmL6V2EmbeddingModel();

            EmbeddingStore<TextSegment> embeddingStore = CockroachDbEmbeddingStore.builder()
                    .engine(engine)
                    .dimension(embeddingModel.dimension())
                    .tableName("demo_embeddings")
                    .build();

            TextSegment segment1 = TextSegment.from("I like football.");
            Embedding embedding1 = embeddingModel.embed(segment1).content();
            embeddingStore.add(embedding1, segment1);

            TextSegment segment2 = TextSegment.from("The weather is good today.");
            Embedding embedding2 = embeddingModel.embed(segment2).content();
            embeddingStore.add(embedding2, segment2);

            Embedding queryEmbedding = embeddingModel.embed("What is your favourite sport?").content();
            EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
                    .queryEmbedding(queryEmbedding)
                    .maxResults(1)
                    .build();

            List<EmbeddingMatch<TextSegment>> matches = embeddingStore.search(request).matches();
            EmbeddingMatch<TextSegment> match = matches.get(0);

            System.out.println(match.score());           // ~0.81
            System.out.println(match.embedded().text()); // I like football.

            engine.close();
        }
    }
}
```

该示例使用默认的顺序扫描索引，因此可以在任何
CockroachDB v24.2 或更高版本上运行，无需额外的集群设置。要在 v25.2 或更高版本
上切换到 C-SPANN 分布式 ANN 索引，请每个集群启用一次
功能开关，并通过 `.vectorIndex(...)` 向存储传入 `CSpannIndex.builder().build()`：

```sql
SET CLUSTER SETTING feature.vector_index.enabled = true;
```

更完整的可运行版本位于
[langchain4j-examples/cockroachdb-example](https://github.com/langchain4j/langchain4j-examples/blob/main/cockroachdb-example/src/main/java/CockroachDbEmbeddingStoreExample.java)。

## 已知限制

- C-SPANN 向量索引要求 CockroachDB v25.2 或更高版本，并且
  必须启用 `feature.vector_index.enabled` 集群设置。
- 向量值以文本形式发送，并使用 `?::vector` 转换，因为
  CockroachDB 的 pgwire 层不接受 `VECTOR` 类型的二进制格式。
- 混合（向量 + 全文）查询执行尚未实现。
  tsvector 列和 GIN 索引可以通过 `createTsvectorColumn` 创建，
  供应用代码或未来版本使用。
- Python 的 `langchain-cockroachdb` 库还附带了一个 LangGraph
  检查点存储器（`CockroachDBSaver` 和 `AsyncCockroachDBSaver`）。
  对应的 Java 实现位于第三方 [langgraph4j](https://github.com/langgraph4j/langgraph4j)
  项目中的 `langgraph4j-cockroachdb-saver`。langgraph4j 的检查点
  契约没有异步 API，因此只提供同步的 `CockroachDBSaver`；
  使用 JDK 21 或更高版本的调用方可以从虚拟
  线程调用它以实现非阻塞并发。
