# Hibernate

LangChain4j 与 [Hibernate](https://github.com/hibernate/hibernate-orm) 无缝集成，使开发人员能够直接在 Hibernate 支持的所有数据库中存储和查询向量嵌入。该集成非常适合语义搜索、RAG 等应用。

## Maven 依赖

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-hibernate</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## Gradle 依赖

```implementation 'dev.langchain4j:langchain4j-hibernate:1.22.0-beta32'```

## API

- `HibernateEmbeddingStore`

## 参数汇总

### 通用存储

当只想使用 `EmbeddingStore` API，而不想担心 Hibernate 的细节（如实体类定义和 Hibernate 的配置）时，推荐使用这种类型的存储。

要配置它，请使用 `HibernateEmbeddingStore.dynamicBuilder()` 或 `HibernateEmbeddingStore.dynamicDatasourceBuilder()`。

| Java 属性 | 描述 | 默认值 | 必填/可选 |
|-----------|------|--------|-----------|
| `datasource` | 用于数据库连接的 `DataSource` 对象。仅在 `HibernateEmbeddingStore.dynamicDatasourceBuilder()` 构建器变体中可用。如果未提供，则必须在 `HibernateEmbeddingStore.dynamicBuilder()` 构建器变体中分别提供 `jdbcUrl`、`user` 和 `password`。 | 无 | 如果未分别提供 `jdbcUrl`、`user` 和 `password`，则为必填。 |
| `jdbcUrl` | 数据库服务器的 JDBC URL。如果未提供 `DataSource` 以及 `host`、`port`、`database`，则为必填。仅在 `HibernateEmbeddingStore.dynamicBuilder()` 构建器变体中可用。 | 无 | 如果未提供 `DataSource` 或 `host`、`port`、`database`，则为必填 |
| `host` | 数据库服务器的主机名。如果 `DataSource` 和 `jdbcUrl` 都未提供，则为必填。仅在 `HibernateEmbeddingStore.dynamicBuilder()` 构建器变体中可用。 | 无 | 如果 `DataSource` 和 `jdbcUrl` 都未提供，则为必填 |
| `port` | 数据库服务器的端口号。如果 `DataSource` 和 `jdbcUrl` 都未提供，则为必填。仅在 `HibernateEmbeddingStore.dynamicBuilder()` 构建器变体中可用。 | 无 | 如果 `DataSource` 和 `jdbcUrl` 都未提供，则为必填 |
| `database` | 要连接的数据库名称。如果 `DataSource` 和 `jdbcUrl` 都未提供，则为必填。仅在 `HibernateEmbeddingStore.dynamicBuilder()` 构建器变体中可用。 | 无 | 如果 `DataSource` 和 `jdbcUrl` 都未提供，则为必填 |
| `databaseKind` | 数据库类型。如果提供了 `DataSource`，或无法从 `jdbcUrl` 推断出类型，则为必填。 | 无 | 如果提供了 `DataSource`，或无法从 `jdbcUrl` 推断出类型，则为必填 |
| `user` | 用于数据库身份验证的用户名。如果未提供 `DataSource`，则为必填。仅在 `HibernateEmbeddingStore.dynamicBuilder()` 构建器变体中可用。 | 无 | 如果未提供 `DataSource`，则为必填 |
| `password` | 用于数据库身份验证的密码。如果未提供 `DataSource`，则为必填。仅在 `HibernateEmbeddingStore.dynamicBuilder()` 构建器变体中可用。 | 无 | 如果未提供 `DataSource`，则为必填 |
| `table` | 用于存储嵌入的数据库表名。 | 无 | 必填 |
| `dimension` | 嵌入向量的维度。这应与所使用的嵌入模型相匹配。使用 `embeddingModel.dimension()` 动态设置。 | 无 | 必填 |
| `createIndex` | 指定是否为向量嵌入自动创建索引。 | `false` | 可选 |
| `indexType` | 要使用的数据库特定的索引类型，例如 `ivfflat`、`hnsw`。IVFFlat 索引将向量划分为若干列表，然后在与查询向量最接近的列表子集中进行搜索。与 HNSW 相比，其构建时间更短、内存占用更少，但查询性能较低（就速度-召回率权衡而言）。应使用 [IVFFlat](https://github.com/pgvector/pgvector#ivfflat) 索引。 | 无 | 可选。默认为首选的索引类型，例如在 PostgreSQL 上为 `ivfflat` |
| `indexOptions` | 用于配置向量嵌入索引的选项。 | 无 | 必填时：如果 `createIndex` 为 `true` 且索引类型为 `ivfflat`，在 PostgreSQL 上必须提供 `lists = 1` 选项，且必须大于零。否则，程序在表初始化期间会抛出异常。可选时：如果 `createIndex` 为 `false`，则忽略此属性，无需设置。 |
| `createTable` | 指定是否自动创建嵌入表。 | `false` | 可选 |
| `dropTableFirst` | 指定在重新创建表之前是否先删除该表（对测试有用）。 | `false` | 可选 |
| `distanceFunction` | 用于向量搜索的距离函数。支持情况因数据库而异：<ul><li>**COSINE**</li><li>**EUCLIDEAN**</li><li>**EUCLIDEAN_SQUARED**</li><li>**MANHATTAN**</li><li>**INNER_PRODUCT**</li><li>**NEGATIVE_INNER_PRODUCT**</li><li>**HAMMING**</li><li>**JACCARD**</li></ul> | `COSINE` | 可选。如果未设置，将使用采用 `COSINE` 的默认配置。 |

### 实体存储

要在 `EmbeddingStore` API 中利用现有的 Hibernate 实体模型，或应用数据模型自定义，推荐使用实体存储。

要配置它，请使用 `HibernateEmbeddingStore.builder()`。

| Java 属性 | 描述 | 默认值 | 必填/可选 |
|-----------|------|--------|-----------|
| `sessionFactory` | `entityClass` 所属的 `SessionFactory` 对象。 | 无 | 必填 |
| `databaseKind` | 数据库类型。如果无法从 Hibernate ORM 方言推断出类型，则为必填。 | 无 | 如果无法从 Hibernate ORM 方言推断出类型，则为必填 |
| `entityClass` | 指定 `EmbeddingStore` 要使用的 `SessionFactory` 的实体类。 | 无 | 必填 |
| `embeddingAttributeName` | 指定表示向量嵌入的实体属性名称。 | 无 | 可选。如果未设置，将扫描实体以查找带有 `@EmbeddingVector` 注解的属性 |
| `embeddedTextAttributeName` | 指定表示向量嵌入源文本的实体属性名称。 | 无 | 可选。如果未设置，将扫描实体以查找带有 `@EmbeddedText` 注解的属性 |
| `unmappedMetadataAttributeName` | 指定表示存储未映射元数据的 JSON 列的实体属性名称。 | 无 | 可选。如果未设置，将扫描实体以查找带有 `@UnmappedMetadata` 注解的属性 |
| `metadataAttributeNames` | 指定显式映射到文本元数据的实体属性名称。 | 无 | 可选。如果未设置，将扫描实体以查找带有 `@MetadataAttribute` 注解的属性 |
| `distanceFunction` | 用于向量搜索的距离函数。支持情况因数据库而异：<ul><li>**COSINE**</li><li>**EUCLIDEAN**</li><li>**EUCLIDEAN_SQUARED**</li><li>**MANHATTAN**</li><li>**INNER_PRODUCT**</li><li>**NEGATIVE_INNER_PRODUCT**</li><li>**HAMMING**</li><li>**JACCARD**</li></ul> | `COSINE` | 可选。如果未设置，将扫描实体以查找带有 `@EmbeddingVector` 注解的属性并使用其 `distance` 值，如果该值缺失，则使用采用 `COSINE` 的默认配置。 |

## 示例

为了展示其功能，例如可以使用容器化的 PostgreSQL 配置。它利用 Testcontainers 来运行带有 PGVector 的 PostgreSQL。

#### 使用 Docker 快速上手

要快速设置一个带有 PGVector 扩展的 PostgreSQL 实例，你可以使用以下 Docker 命令：

```
docker run --rm --name langchain4j-postgres-test-container -p 5432:5432 -e POSTGRES_USER=my_user -e POSTGRES_PASSWORD=my_password pgvector/pgvector
```

#### 命令说明：

- ```docker run```: 运行一个新容器。
- ```--rm```: 容器停止后自动将其移除，确保没有残留数据。
- ```--name langchain4j-postgres-test-container```: 将容器命名为 langchain4j-postgres-test-container，便于识别。
- ```-p 5432:5432```: 将你本地机器上的 5432 端口映射到容器内的 5432 端口。
- ```-e POSTGRES_USER=my_user```: 将 PostgreSQL 用户名设置为 my_user。
- ```-e POSTGRES_PASSWORD=my_password```: 将 PostgreSQL 密码设置为 my_password。
- ```pgvector/pgvector```: 指定要使用的 Docker 镜像，已预装 PGVector 扩展。

以下是两个代码示例，展示了如何创建 `HibernateEmbeddingStore`。第一个示例只使用必填参数，第二个示例则配置了所有可用参数。

1. 仅使用必填参数

```java
HibernateEmbeddingStore embeddingStore = HibernateEmbeddingStore.dynamicBuilder()
        .databaseKind(DatabaseKind.POSTGRESQL)                  // Required: The database kind
        .host("localhost")                                      // Required: Host of the database server
        .port(5432)                                             // Required: Port of the database server
        .database("postgres")                                   // Required: Database name
        .user("my_user")                                        // Required: Database user
        .password("my_password")                                // Required: Database password
        .table("my_embeddings")                                 // Required: Table name to store embeddings
        .dimension(embeddingModel.dimension())                  // Required: Dimension of embeddings
        .build();
```

2. 设置所有参数

在此变体中，我们包含了所有常用的可选参数，如 createIndex、indexOptions、
createTable、dropTableFirst 和 distanceFunction。请根据需要调整这些值：

 ```java
HibernateEmbeddingStore embeddingStore = HibernateEmbeddingStore.dynamicBuilder()
        // Required parameters
        .databaseKind(DatabaseKind.POSTGRESQL)
        .host("localhost")
        .port(5432)
        .database("postgres")
        .user("my_user")
        .password("my_password")
        .table("my_embeddings")
        .dimension(embeddingModel.dimension())

        // Optional parameters
        .createIndex(true)                              // Enable vector index creation
        .indexType("ivfflat")                           // Index type IVFFlat
        .indexOptions("lists = 100")                    // Number of lists for IVFFlat index
        .createTable(true)                              // Automatically create the table if it doesn't exist
        .dropTableFirst(false)                          // Don't drop the table first (set to true if you want a fresh start)
        .distanceFunction(DistanceFunction.MANHATTEN)   // Use MANHATTAN distance function for vector search

        .build();
```

如果你只想用最小配置快速上手，请使用第一个示例。
第二个示例展示了如何利用所有可用的构建器参数，以获得更多的控制和自定义。

当你不再需要 `HibernateEmbeddingStore` 时，别忘了关闭它，以释放底层的 Hibernate 资源。

#### 自定义 Hibernate 实体

当你想自定义数据模型，或想复用已有实体作为 `EmbeddingStore` 的数据源时，
可以使用注解 `@EmbeddingVector`、`@EmbeddedText`、`@UnmappedMetadata` 和 `@MetadataAttribute` 来标记
Hibernate `EmbeddingStore` 实现要使用的实体属性。

```java
@Entity
public class MyEmbeddingEntity {
    @Id
    UUID id;
    @EmbeddingVector
    @Array(length = 384)                // The dimension of the embedding vector based on the embedding model
    float[] embedding;
    @EmbeddedText
    String text;
    @UnmappedMetadata
    Map<String, Object> metadata;       // Can be either a Map<String, Object> or a String
    
    @MetadataAttribute
    String mimeType;                    // Explicitly mapped. Synchronizes TextSegment#metadata with this attribute
    @MetadataAttribute
    String fileName;                    // Explicitly mapped. Synchronizes TextSegment#metadata with this attribute
}
```

然后，构建器会查找这些注解并推导出属性名称。

```java
HibernateEmbeddingStore embeddingStore = HibernateEmbeddingStore.builder()
        .sessionFactory(sessionFactory)         // Required: The SessionFactory containing your entity class
        .entityClass(MyEmbeddingEntity.class)   // Required: The embedding entity class
        .build();
```

或者，如果不想在实体模型上使用注解，也可以显式提供属性名称。

```java
HibernateEmbeddingStore embeddingStore = HibernateEmbeddingStore.builder()
        .sessionFactory(sessionFactory)
        .entityClass(MyEmbeddingEntity.class)
        .embeddingAttributeName("embedding")
        .embeddedTextAttributeName("text")
        .unmappedMetadataAttributeName("metadata")
        .metadataAttributeNames("mimeType", "fileName")
        .build();
```

元数据还可以嵌套在同样带有 `@MetadataAttribute` 注解的 `@OneToOne`、`@ManyToOne` 或 `@Embedded` 属性中，
也可以通过使用 `.`（点）分隔符指定显式的属性路径。

```java
@Entity
public class Book {
    @Id
    private Long id;
    private String title;
    private String content;
    @MetadataAttribute
    @Embedded
    private BookDetails details = new BookDetails();
    @MetadataAttribute
    @ManyToOne(fetch = FetchType.LAZY)
    private Author author;

    @EmbeddingVector
    @Array(length = 384)
    private float[] embedding;
    @UnmappedMetadata
    private Map<String, Object> metadata;
}
@Entity
public class Author {
    @Id
    @MetadataAttribute
    @GeneratedValue
    private Long id;
    private String firstname;
    private String lastname;
}
@Embeddable
public class BookDetails {
    @MetadataAttribute
    private String language;
    private String abstractText;
}
```

等效的属性路径是 `details.language` 和 `author.id`，然后将这些路径作为元数据键指定，即可用于过滤，例如

```java
MetadataFilterBuilder.metadataKey("details.language").isEqualTo("English")
```

或者

```java
MetadataFilterBuilder.metadataKey("author.id").isEqualTo(2L)
```

此外，`HibernateEmbeddingStore` API 还提供了 `search` 方法，允许你使用类型安全的 Hibernate ORM `Restriction` API。

```java
HibernateEmbeddingStore<Book> embeddingStore = embeddingStore();
embeddingStore.search(
        embedding,
        Path.from(Book.class)
            .to(Book_.details)
            .to(BookDetails_.language)
            .equalTo("English"));
```

或者

```java
HibernateEmbeddingStore<Book> embeddingStore = embeddingStore();
embeddingStore.search(
        embedding,
        Path.from(Book.class)
            .to(Book_.author)
            .to(Author_.id)
            .equalTo(2L));
```

## 使用 Hibernate 的完整 RAG 示例

本节演示如何使用 Hibernate 集成（结合带有 PGVector 扩展的 PostgreSQL）进行语义搜索，构建一个完整的
检索增强生成（RAG）系统。

### 概述

RAG 系统由两个主要阶段组成：
1. **索引阶段（离线）**：加载文档、切分为块、生成嵌入，并存储到 pgvector
2. **检索阶段（在线）**：将用户查询向量化、搜索相似的块、将上下文注入 LLM 提示词

### 前提条件

确保你有一个正在运行且带有 PGVector 的 PostgreSQL 实例（参见上面的 Docker 设置）。

### 1. 文档摄入（索引阶段）

本示例展示了如何加载文档、将它们切分为块，并将嵌入存储到 pgvector 中：

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
HibernateEmbeddingStore embeddingStore = HibernateEmbeddingStore.dynamicBuilder()
        .databaseKind(DatabaseKind.POSTGRESQL)
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

本示例展示了如何使用用户问题查询 RAG 系统：

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
EmbeddingSearchResult<TextSegment> result = embeddingStore.search(
        EmbeddingSearchRequest.builder()
                .queryEmbedding(questionEmbedding)
                .maxResults(3)  // Retrieve top 3 most similar chunks
                .build()
);

// Build context from retrieved segments
String context = result.matches().stream()
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

根据实际使用情况，以下是生产部署中需要重点考虑的事项：

#### 1. 连接池
在生产环境中，请使用带连接池的 `DataSource`，而不是单独的连接参数：

```java
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;

HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:postgresql://localhost:5432/postgres");
config.setUsername("my_user");
config.setPassword("my_password");
config.setMaximumPoolSize(10);

HikariDataSource dataSource = new HikariDataSource(config);

EmbeddingStore<TextSegment> embeddingStore = HibernateEmbeddingStore.dynamicDatasourceBuilder()
        .databaseKind(DatabaseKind.POSTGRESQL)
        .datasource(dataSource)
        .table("document_embeddings")
        .dimension(384)
        .build();
```

#### 2. 索引优化
对于大型数据集（>100k 条嵌入），在 PostgreSQL 上启用 IVFFlat 索引以提高查询性能：

```java
HibernateEmbeddingStore embeddingStore = HibernateEmbeddingStore.dynamicBuilder()
        // ... other config ...
        .createIndex(true)
        .indexOptions("lists = 100")  // Adjust based on dataset size
        .build();
```

**注意**：在大型数据集上创建索引可能需要较长时间。需要在查询速度和索引构建时间之间取得平衡。
**注意**：索引维护可能会拖慢数据摄入速度，因此在摄入大量数据时，可以考虑先删除索引再重建。

#### 3. 块大小调优
根据你的使用场景尝试不同的块大小：
- **较小的块（200-300 tokens）**：精度更高，答案更具体
- **较大的块（500-800 tokens）**：上下文更多，但可能降低相关性

#### 4. 错误处理
始终妥善地处理数据库连接失败：

```java
try {
    embeddingStore.add(embedding, textSegment);
} catch (Exception e) {
    logger.error("Failed to store embedding", e);
    // Implement retry logic or fallback behavior
}
```

#### 5. 自定义 Hibernate 实体的 DDL
使用自定义 Hibernate 实体时，由你负责管理 DDL。
可以考虑创建一个 `import.sql` 文件来创建索引，例如针对 PostgreSQL：

```sql
create index if not exists my_entity_ivfflat_index 
    on my_entity using ivfflat(embedding vector_cosine_ops) with (lists = 1);
```

有关 `SessionFactory` 配置的详细信息，请参阅 [Hibernate ORM 文档](https://docs.hibernate.org/orm/7.2/userguide/html_single/)。

其他数据库的向量索引具有不同的语法和选项。有关详细信息，请参阅相应数据库提供商的文档。

##### DB2

有关详细信息，请参阅[向量索引文章](https://community.ibm.com/community/user/blogs/christian-garcia-arellano/2025-10-04/vector-indexes-in-db2-an-early-preview)。

```sql
create vector index my_entity_vector_index 
    on my_entity(embedding) with distance cosine;
```

##### MariaDB

有关详细信息，请参阅[`create index` 语句文档](https://mariadb.com/docs/server/reference/sql-statements/data-definition/create/create-index)。

```sql
create vector index if not exists my_entity_vector_index 
    on my_entity(embedding) distance=cosine;
```

##### MySQL

MySQL HeatWave[会自动创建索引](https://dev.mysql.com/doc/heatwave/en/mys-hw-genai-vector-index-creation.html)，无需手动创建索引。

##### PostgreSQL

有关详细信息，请参阅 [pgvector 文档](https://github.com/pgvector/pgvector?tab=readme-ov-file#indexing)。

```sql
create index if not exists my_entity_ivfflat_index
    on my_entity using ivfflat(embedding vector_cosine_ops) with (lists = 1);
```

##### CockroachDB

有关详细信息，请参阅 [CockroachDB 文档](https://www.cockroachlabs.com/docs/v26.2/vector-indexes)。

```sql
create vector index if not exists my_entity_ivfflat_index
    on my_entity (embedding vector_cosine_ops);
```

##### Oracle

有关详细信息，请参阅[`create index` 语句文档](https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/create-vector-index.html)。

```sql
create vector index my_entity_vector_index 
    on my_entity(embedding) organization neighbor partitions with distance cosine;
```

##### SQL Server

有关详细信息，请参阅[`create vector index` 语句文档](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-vector-index-transact-sql?view=sql-server-ver17)。

```sql
create vector index my_entity_vector_index 
    on my_entity(embedding) with (metric='cosine');
```

##### SAP HANA

有关详细信息，请参阅[`create vector index` 语句文档](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-sql-reference-guide/create-vector-index-statement-data-definition?locale=en-US)。

```sql
create hnsw vector index my_entity_vector_index 
    on my_entity(embedding) with similarity function cosine_similarity;
```
